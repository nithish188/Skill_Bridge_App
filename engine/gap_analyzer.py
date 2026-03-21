"""
Gap Analysis Engine
Compares candidate skills against job requirements to identify skill gaps.
"""
from engine.skill_extractor import extract_skills, estimate_proficiency, load_prerequisites


def analyze_gaps(resume_skills, jd_skills, resume_text, jd_text, resume_metadata=None):
    """
    Perform skill gap analysis between resume and job description.
    
    Args:
        resume_skills: Output from extract_skills on resume
        jd_skills: Output from extract_skills on JD
        resume_text: Full resume text
        jd_text: Full JD text
        resume_metadata: Resume metadata dict
    
    Returns:
        dict with gap analysis results
    """
    prereqs_data = load_prerequisites()
    transferable = prereqs_data.get("transferable_skills", {})
    
    # Build candidate skill map: skill_name -> proficiency
    candidate_skill_map = {}
    for skill_info in resume_skills["found_skills"]:
        skill = skill_info["skill"]
        prof = estimate_proficiency(skill, resume_text, resume_metadata)
        candidate_skill_map[skill] = {
            "proficiency": prof["score"],
            "proficiency_label": prof["label"],
            "confidence": skill_info["confidence"],
            "category": skill_info["category"],
        }
    
    # Build required skill map from JD
    required_skill_map = {}
    for idx, skill_info in enumerate(jd_skills["found_skills"]):
        skill = skill_info["skill"]
        # Position-based priority: earlier mentions = higher priority
        position_weight = max(0.5, 1.0 - (idx * 0.03))
        required_skill_map[skill] = {
            "category": skill_info["category"],
            "confidence": skill_info["confidence"],
            "priority": round(position_weight, 2),
            "required_proficiency": estimate_required_proficiency(skill, jd_text),
        }
    
    # Identify gaps
    gaps = []
    matched_skills = []
    missing_skills = []
    
    for skill, req_info in required_skill_map.items():
        required_prof = req_info["required_proficiency"]
        
        if skill in candidate_skill_map:
            candidate_prof = candidate_skill_map[skill]["proficiency"]
            gap_score = max(0, required_prof - candidate_prof)
            
            if gap_score > 10:
                gaps.append({
                    "skill": skill,
                    "category": req_info["category"],
                    "current_proficiency": candidate_prof,
                    "required_proficiency": required_prof,
                    "gap_score": gap_score,
                    "priority": req_info["priority"],
                    "severity": classify_gap_severity(gap_score),
                    "has_transferable": check_transferable(skill, candidate_skill_map, transferable),
                    "transferable_from": get_transferable_skills(skill, candidate_skill_map, transferable),
                })
            else:
                matched_skills.append({
                    "skill": skill,
                    "category": req_info["category"],
                    "current_proficiency": candidate_prof,
                    "required_proficiency": required_prof,
                    "status": "met" if gap_score <= 0 else "nearly_met",
                })
        else:
            # Skill not found in resume
            transferable_from = get_transferable_skills(skill, candidate_skill_map, transferable)
            has_transfer = len(transferable_from) > 0
            
            # If candidate has transferable skills, lower the effective gap
            effective_gap = 80 if not has_transfer else 60
            
            missing_skills.append({
                "skill": skill,
                "category": req_info["category"],
                "current_proficiency": 0,
                "required_proficiency": required_prof,
                "gap_score": effective_gap,
                "priority": req_info["priority"],
                "severity": classify_gap_severity(effective_gap),
                "has_transferable": has_transfer,
                "transferable_from": transferable_from,
            })
    
    # Combine gaps and missing skills
    all_gaps = gaps + missing_skills
    all_gaps.sort(key=lambda x: (severity_order(x["severity"]), -x["gap_score"]))
    
    # Calculate summary metrics
    total_required = len(required_skill_map)
    total_matched = len(matched_skills)
    total_gaps = len(all_gaps)
    
    match_percentage = round((total_matched / max(total_required, 1)) * 100, 1)
    
    # Category-level analysis
    category_gaps = {}
    for gap in all_gaps:
        cat = gap["category"]
        if cat not in category_gaps:
            category_gaps[cat] = {"count": 0, "total_gap": 0, "skills": []}
        category_gaps[cat]["count"] += 1
        category_gaps[cat]["total_gap"] += gap["gap_score"]
        category_gaps[cat]["skills"].append(gap["skill"])
    
    return {
        "gaps": all_gaps,
        "matched_skills": matched_skills,
        "candidate_skills": candidate_skill_map,
        "required_skills": required_skill_map,
        "summary": {
            "total_required_skills": total_required,
            "skills_matched": total_matched,
            "skills_with_gaps": total_gaps,
            "match_percentage": match_percentage,
            "critical_gaps": len([g for g in all_gaps if g["severity"] == "critical"]),
            "important_gaps": len([g for g in all_gaps if g["severity"] == "important"]),
            "nice_to_have_gaps": len([g for g in all_gaps if g["severity"] == "nice_to_have"]),
        },
        "category_gaps": category_gaps,
    }


def estimate_required_proficiency(skill, jd_text):
    """
    Estimate the required proficiency for a skill mentioned in a JD.
    """
    import re
    text_lower = jd_text.lower()
    skill_lower = skill.lower()
    
    # Expert-level indicators
    expert_patterns = [
        rf"(?i)(?:expert|mastery|deep|extensive|thorough)\s+(?:knowledge|experience|understanding)?\s*(?:of\s+|in\s+|with\s+)?{re.escape(skill_lower)}",
        rf"(?i){re.escape(skill_lower)}\s*[-–:]\s*(?:expert|master)",
    ]
    
    for pattern in expert_patterns:
        if re.search(pattern, text_lower):
            return 85
    
    # Advanced-level indicators
    advanced_patterns = [
        rf"(?i)(?:strong|advanced|solid|significant)\s+(?:knowledge|experience|proficiency|skills?)?\s*(?:of\s+|in\s+|with\s+)?{re.escape(skill_lower)}",
        rf"(?i){re.escape(skill_lower)}\s*[-–:]\s*(?:advanced|strong)",
    ]
    
    for pattern in advanced_patterns:
        if re.search(pattern, text_lower):
            return 70
    
    # Basic/familiar indicators
    basic_patterns = [
        rf"(?i)(?:basic|familiarity|awareness|understanding|knowledge)\s+(?:of\s+|in\s+|with\s+)?{re.escape(skill_lower)}",
        rf"(?i)(?:nice\s+to\s+have|preferred|bonus).*{re.escape(skill_lower)}",
    ]
    
    for pattern in basic_patterns:
        if re.search(pattern, text_lower):
            return 40
    
    # Default: intermediate
    return 60


def classify_gap_severity(gap_score):
    """Classify the severity of a skill gap."""
    if gap_score >= 60:
        return "critical"
    elif gap_score >= 35:
        return "important"
    else:
        return "nice_to_have"


def severity_order(severity):
    """Return sort order for severity levels."""
    return {"critical": 0, "important": 1, "nice_to_have": 2}.get(severity, 3)


def check_transferable(skill, candidate_skills, transferable_map):
    """Check if candidate has transferable skills."""
    related = transferable_map.get(skill, [])
    return any(r in candidate_skills for r in related)


def get_transferable_skills(skill, candidate_skills, transferable_map):
    """Get list of transferable skills the candidate has."""
    related = transferable_map.get(skill, [])
    return [r for r in related if r in candidate_skills]
