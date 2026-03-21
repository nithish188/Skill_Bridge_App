"""
Skill Extraction Engine
Uses NLP-based keyword matching against the O*NET skill taxonomy to extract
skills from resume and JD text.
"""
import json
import os
import re

# Load skill taxonomy
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_skill_taxonomy():
    """Load the O*NET-based skill taxonomy."""
    with open(os.path.join(DATA_DIR, "onet_skills.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def load_prerequisites():
    """Load skill prerequisites and transferable skills."""
    with open(os.path.join(DATA_DIR, "skill_prerequisites.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(text):
    """Normalize text for skill matching."""
    # Keep periods for abbreviations like ASP.NET, Node.js
    text = re.sub(r"[,;:!?\"'()\[\]{}<>]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def extract_skills(text, taxonomy=None):
    """
    Extract skills from text using taxonomy-based matching.
    
    Args:
        text: Input text (resume or JD)
        taxonomy: Skill taxonomy dict (loads default if None)
    
    Returns:
        dict with:
            - 'found_skills': list of {skill, category, confidence}
            - 'skill_categories': dict of category -> [skills]
            - 'total_skills_found': int
    """
    if taxonomy is None:
        taxonomy = load_skill_taxonomy()
    
    normalized = normalize_text(text)
    text_lower = normalized.lower()
    
    found_skills = []
    skill_categories = {}
    seen_skills = set()
    
    for category, data in taxonomy["categories"].items():
        category_skills = []
        for skill in data["skills"]:
            skill_lower = skill.lower()
            
            # Skip if already found
            if skill_lower in seen_skills:
                continue
            
            # Multi-word skills: exact phrase matching
            # Single-word skills: word boundary matching
            if " " in skill or "." in skill:
                # For multi-word / dotted skills, do case-insensitive search
                pattern = re.escape(skill_lower).replace(r"\ ", r"\s+")
                if re.search(pattern, text_lower):
                    confidence = calculate_confidence(skill, text, text_lower)
                    found_skills.append({
                        "skill": skill,
                        "category": category,
                        "confidence": confidence,
                    })
                    category_skills.append(skill)
                    seen_skills.add(skill_lower)
            else:
                # Word boundary match for single-word skills
                pattern = r"\b" + re.escape(skill_lower) + r"\b"
                if re.search(pattern, text_lower):
                    confidence = calculate_confidence(skill, text, text_lower)
                    found_skills.append({
                        "skill": skill,
                        "category": category,
                        "confidence": confidence,
                    })
                    category_skills.append(skill)
                    seen_skills.add(skill_lower)
        
        if category_skills:
            skill_categories[category] = category_skills
    
    # Sort by confidence descending
    found_skills.sort(key=lambda x: x["confidence"], reverse=True)
    
    return {
        "found_skills": found_skills,
        "skill_categories": skill_categories,
        "total_skills_found": len(found_skills),
    }


def calculate_confidence(skill, original_text, text_lower):
    """
    Calculate confidence score for a skill match.
    Factors: frequency, proximity to skills section, context clues.
    """
    skill_lower = skill.lower()
    base_confidence = 0.6
    
    # Frequency bonus
    count = len(re.findall(re.escape(skill_lower), text_lower))
    freq_bonus = min(count * 0.05, 0.2)  # max 0.2 bonus
    
    # Skills section bonus
    skills_section_patterns = [
        r"(?i)(?:technical\s+)?skills?\s*[:|\n]",
        r"(?i)core\s+competenc",
        r"(?i)technologies?\s*[:|\n]",
        r"(?i)proficienc",
        r"(?i)tools?\s+(?:and|&)\s+technologies",
    ]
    
    section_bonus = 0
    for pattern in skills_section_patterns:
        match = re.search(pattern, original_text)
        if match:
            # Check if skill appears near the skills section
            section_start = match.start()
            skill_match = re.search(re.escape(skill_lower), text_lower[section_start:section_start + 1000])
            if skill_match:
                section_bonus = 0.15
                break
    
    # Context clues bonus
    context_patterns = [
        rf"(?i)(?:proficient|experienced|expertise|skilled|strong|expert)\s+(?:in\s+|with\s+)?.*{re.escape(skill_lower)}",
        rf"(?i){re.escape(skill_lower)}\s*[-–:]\s*(?:advanced|expert|proficient|intermediate)",
        rf"(?i)(?:built|developed|designed|implemented|created|managed|led).*{re.escape(skill_lower)}",
    ]
    
    context_bonus = 0
    for pattern in context_patterns:
        if re.search(pattern, text_lower):
            context_bonus = 0.1
            break
    
    confidence = min(base_confidence + freq_bonus + section_bonus + context_bonus, 1.0)
    return round(confidence, 2)


def estimate_proficiency(skill, text, metadata=None):
    """
    Estimate proficiency level for a skill based on context clues.
    
    Returns a score from 0-100 and a label.
    """
    text_lower = text.lower()
    skill_lower = skill.lower()
    score = 30  # Base: beginner
    
    # Check for explicit proficiency indicators
    proficiency_patterns = {
        90: [
            rf"(?i)expert\s+(?:in\s+|level\s+)?(?:.*\s+)?{re.escape(skill_lower)}",
            rf"(?i){re.escape(skill_lower)}\s*[-–:]\s*expert",
            rf"(?i)(?:deep|extensive)\s+(?:expertise|experience|knowledge)\s+(?:in\s+|with\s+)?{re.escape(skill_lower)}",
        ],
        75: [
            rf"(?i)advanced\s+(?:knowledge|experience|proficiency)\s+(?:in\s+|with\s+)?{re.escape(skill_lower)}",
            rf"(?i){re.escape(skill_lower)}\s*[-–:]\s*advanced",
            rf"(?i)(?:lead|architect|designed)\s+.*{re.escape(skill_lower)}",
        ],
        55: [
            rf"(?i)(?:proficient|experienced|strong)\s+(?:in\s+|with\s+)?{re.escape(skill_lower)}",
            rf"(?i){re.escape(skill_lower)}\s*[-–:]\s*(?:intermediate|proficient)",
            rf"(?i)(?:built|developed|implemented)\s+.*{re.escape(skill_lower)}",
        ],
        35: [
            rf"(?i)(?:basic|beginner|familiar|exposure)\s+(?:to\s+|in\s+|with\s+)?{re.escape(skill_lower)}",
            rf"(?i){re.escape(skill_lower)}\s*[-–:]\s*(?:basic|beginner)",
            rf"(?i)(?:learning|studying|coursework)\s+.*{re.escape(skill_lower)}",
        ],
    }
    
    for level_score, patterns in proficiency_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                score = level_score
                break
        else:
            continue
        break
    
    # Frequency-based adjustment
    count = len(re.findall(re.escape(skill_lower), text_lower))
    if count >= 5:
        score = max(score, 55)
    elif count >= 3:
        score = max(score, 45)
    
    # Experience-based adjustment
    if metadata and metadata.get("estimated_years", 0) > 0:
        years = metadata["estimated_years"]
        if years >= 8:
            score = min(score + 15, 95)
        elif years >= 5:
            score = min(score + 10, 85)
        elif years >= 3:
            score = min(score + 5, 75)
    
    # Determine label
    if score >= 80:
        label = "Expert"
    elif score >= 60:
        label = "Advanced"
    elif score >= 40:
        label = "Intermediate"
    elif score >= 25:
        label = "Beginner"
    else:
        label = "Novice"
    
    return {"score": score, "label": label}
