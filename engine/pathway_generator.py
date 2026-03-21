"""
Adaptive Pathway Generator
Original adaptive logic that creates personalized learning pathways.

This module implements our custom weighted scoring algorithm that considers:
1. Skill gap severity
2. Prerequisite dependencies (topological ordering)
3. Transferable skills (reduced learning time)
4. Role priority (position-based importance)

The algorithm generates a time-optimized, dependency-respecting learning pathway.
"""
import json
import os
from config import PATHWAY_WEIGHTS, HOURS_PER_LEVEL

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_course_catalog():
    """Load the course catalog."""
    with open(os.path.join(DATA_DIR, "course_catalog.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def load_prerequisites():
    """Load skill prerequisites."""
    with open(os.path.join(DATA_DIR, "skill_prerequisites.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def generate_pathway(gap_analysis, resume_metadata=None):
    """
    Generate an adaptive, personalized learning pathway based on gap analysis.
    
    This is our ORIGINAL ADAPTIVE LOGIC.
    
    Algorithm:
    1. Score each gap using weighted formula
    2. Resolve prerequisite dependencies
    3. Apply transferable skill bonuses (reduced time)
    4. Topologically sort modules
    5. Build phased pathway with time estimates
    
    Args:
        gap_analysis: Output from gap_analyzer.analyze_gaps()
        resume_metadata: Resume metadata dict
    
    Returns:
        dict with pathway phases, modules, time estimates, and metrics
    """
    catalog = load_course_catalog()
    prereqs_data = load_prerequisites()
    dependencies = prereqs_data.get("dependencies", {})
    transferable = prereqs_data.get("transferable_skills", {})
    
    gaps = gap_analysis["gaps"]
    candidate_skills = gap_analysis["candidate_skills"]
    
    if not gaps:
        return {
            "phases": [],
            "total_modules": 0,
            "total_hours": 0,
            "total_hours_saved": 0,
            "efficiency_score": 100,
            "message": "Congratulations! No skill gaps detected. The candidate meets all requirements."
        }
    
    # Step 1: Score each gap with our adaptive weighted formula
    scored_gaps = []
    for gap in gaps:
        score = calculate_adaptive_score(gap, candidate_skills, transferable, dependencies)
        scored_gaps.append({**gap, "adaptive_score": score})
    
    # Sort by adaptive score (highest priority first)
    scored_gaps.sort(key=lambda x: x["adaptive_score"], reverse=True)
    
    # Step 2: Map gaps to learning modules
    module_assignments = map_gaps_to_modules(scored_gaps, catalog)
    
    # Step 3: Resolve dependencies and build ordered module list
    ordered_modules = resolve_module_dependencies(module_assignments, catalog)
    
    # Step 4: Apply transferable skill time reductions
    adjusted_modules = apply_transferable_bonuses(ordered_modules, candidate_skills, transferable)
    
    # Step 5: Build phased pathway
    phases = build_phases(adjusted_modules, scored_gaps)
    
    # Step 6: Calculate metrics
    total_hours = sum(m["adjusted_duration"] for m in adjusted_modules)
    generic_hours = sum(m["original_duration"] for m in adjusted_modules)
    hours_saved = generic_hours - total_hours
    
    # Calculate a generic curriculum estimate (all modules in catalog)
    generic_curriculum_hours = sum(m["duration_hours"] for m in catalog["modules"])
    efficiency_score = round((1 - (total_hours / max(generic_curriculum_hours, 1))) * 100, 1)
    
    return {
        "phases": phases,
        "all_modules": adjusted_modules,
        "total_modules": len(adjusted_modules),
        "total_hours": round(total_hours, 1),
        "total_hours_saved": round(hours_saved, 1),
        "generic_curriculum_hours": generic_curriculum_hours,
        "efficiency_score": efficiency_score,
        "scored_gaps": scored_gaps,
        "metrics": {
            "pathway_efficiency_index": round(total_hours / max(generic_curriculum_hours, 1), 3),
            "personalization_ratio": round(len(adjusted_modules) / max(len(catalog["modules"]), 1), 3),
            "critical_gaps_addressed": len([g for g in scored_gaps if g["severity"] == "critical"]),
            "total_gaps_addressed": len(scored_gaps),
            "avg_time_per_module": round(total_hours / max(len(adjusted_modules), 1), 1),
        }
    }


def calculate_adaptive_score(gap, candidate_skills, transferable, dependencies):
    """
    Calculate the adaptive priority score for a skill gap.
    
    This is the core of our ORIGINAL ADAPTIVE LOGIC.
    
    Formula:
        score = w1 * gap_severity_normalized 
              + w2 * prerequisite_depth_normalized
              + w3 * transferable_bonus
              + w4 * role_priority
    
    Where weights are defined in config.PATHWAY_WEIGHTS.
    """
    weights = PATHWAY_WEIGHTS
    
    # Factor 1: Gap severity (0-1)
    gap_severity = gap["gap_score"] / 100.0
    
    # Factor 2: Prerequisite depth - skills with many dependents should be learned first
    skill = gap["skill"]
    dependents = count_dependents(skill, dependencies)
    max_dependents = 10  # normalizing factor
    prereq_depth = min(dependents / max_dependents, 1.0)
    
    # Factor 3: Transferable skill bonus - if candidate has related skills, prioritize
    # (they'll learn faster, so it's a quick win)
    has_transfer = gap.get("has_transferable", False)
    transfer_count = len(gap.get("transferable_from", []))
    transferable_bonus = min(transfer_count * 0.3, 1.0) if has_transfer else 0
    
    # Factor 4: Role priority (from JD position-based weighting)
    role_priority = gap.get("priority", 0.5)
    
    # Weighted combination
    score = (
        weights["gap_severity"] * gap_severity
        + weights["prerequisite_depth"] * prereq_depth
        + weights["transferable_bonus"] * transferable_bonus
        + weights["role_priority"] * role_priority
    )
    
    return round(score, 4)


def count_dependents(skill, dependencies):
    """Count how many other skills depend on this skill."""
    count = 0
    for dep_skill, prereqs in dependencies.items():
        if skill in prereqs:
            count += 1
    return count


def map_gaps_to_modules(scored_gaps, catalog):
    """Map skill gaps to appropriate learning modules."""
    modules = catalog["modules"]
    assigned = []
    assigned_ids = set()
    
    for gap in scored_gaps:
        skill = gap["skill"]
        best_module = None
        best_match_score = 0
        
        for module in modules:
            if module["id"] in assigned_ids:
                continue
            
            if skill in module["skills_covered"]:
                # Calculate match score based on proficiency alignment
                match_score = calculate_module_match(gap, module)
                if match_score > best_match_score:
                    best_match_score = match_score
                    best_module = module
        
        if best_module:
            assigned.append({
                "module": best_module,
                "gap": gap,
                "match_score": best_match_score,
            })
            assigned_ids.add(best_module["id"])
    
    return assigned


def calculate_module_match(gap, module):
    """Calculate how well a module matches a gap."""
    from config import PROFICIENCY_LEVELS
    
    target_prof = PROFICIENCY_LEVELS.get(module["proficiency_target"], 55)
    required_prof = gap["required_proficiency"]
    current_prof = gap["current_proficiency"]
    
    # Module should bridge from current to required proficiency
    if target_prof >= current_prof and target_prof <= required_prof + 20:
        return 1.0
    elif target_prof >= current_prof:
        return 0.7
    else:
        return 0.3


def resolve_module_dependencies(module_assignments, catalog):
    """
    Resolve module prerequisites and return topologically sorted list.
    """
    modules_by_id = {m["id"]: m for m in catalog["modules"]}
    assigned_modules = []
    assigned_ids = set()
    
    for assignment in module_assignments:
        module = assignment["module"]
        gap = assignment["gap"]
        
        # Add prerequisites first
        prereq_chain = get_prerequisite_chain(module, modules_by_id, assigned_ids)
        for prereq in prereq_chain:
            if prereq["id"] not in assigned_ids:
                assigned_modules.append({
                    "module_id": prereq["id"],
                    "title": prereq["title"],
                    "skills_covered": prereq["skills_covered"],
                    "original_duration": prereq["duration_hours"],
                    "adjusted_duration": prereq["duration_hours"],
                    "format": prereq["format"],
                    "provider": prereq["provider"],
                    "description": prereq["description"],
                    "proficiency_target": prereq["proficiency_target"],
                    "is_prerequisite": True,
                    "for_skill": gap["skill"],
                    "gap_severity": "prerequisite",
                })
                assigned_ids.add(prereq["id"])
        
        # Add the module itself
        if module["id"] not in assigned_ids:
            assigned_modules.append({
                "module_id": module["id"],
                "title": module["title"],
                "skills_covered": module["skills_covered"],
                "original_duration": module["duration_hours"],
                "adjusted_duration": module["duration_hours"],
                "format": module["format"],
                "provider": module["provider"],
                "description": module["description"],
                "proficiency_target": module["proficiency_target"],
                "is_prerequisite": False,
                "for_skill": gap["skill"],
                "gap_severity": gap["severity"],
            })
            assigned_ids.add(module["id"])
    
    return assigned_modules


def get_prerequisite_chain(module, modules_by_id, already_assigned):
    """Get the chain of prerequisites for a module."""
    chain = []
    prereqs = module.get("prerequisites", [])
    
    for prereq_id in prereqs:
        if prereq_id in already_assigned:
            continue
        prereq_module = modules_by_id.get(prereq_id)
        if prereq_module:
            # Recursively get prerequisites of prerequisites
            sub_chain = get_prerequisite_chain(prereq_module, modules_by_id, already_assigned)
            chain.extend(sub_chain)
            chain.append(prereq_module)
    
    return chain


def apply_transferable_bonuses(modules, candidate_skills, transferable):
    """
    Reduce learning time for modules where the candidate has transferable skills.
    This is a key part of the adaptive logic.
    """
    for module in modules:
        transfer_bonus = 0
        for skill in module["skills_covered"]:
            related = transferable.get(skill, [])
            for related_skill in related:
                if related_skill in candidate_skills:
                    # Candidate knows a related skill — reduce time
                    candidate_prof = candidate_skills[related_skill]["proficiency"]
                    # Higher proficiency in related skill = bigger time reduction
                    reduction = (candidate_prof / 100) * 0.25  # up to 25% reduction
                    transfer_bonus = max(transfer_bonus, reduction)
        
        if transfer_bonus > 0:
            original = module["original_duration"]
            module["adjusted_duration"] = round(original * (1 - transfer_bonus), 1)
            module["time_saved"] = round(original - module["adjusted_duration"], 1)
            module["transfer_applied"] = True
        else:
            module["time_saved"] = 0
            module["transfer_applied"] = False
    
    return modules


def build_phases(modules, scored_gaps):
    """
    Build a phased learning pathway from ordered modules.
    
    Phases:
    1. Foundation: Prerequisites and critical gaps
    2. Core: Important skill development
    3. Advanced: Nice-to-have and specialization
    4. Mastery: Expert-level refinement (if needed)
    """
    phases = [
        {
            "id": 1,
            "name": "Foundation",
            "description": "Essential prerequisites and critical skill development",
            "icon": "🏗️",
            "modules": [],
            "total_hours": 0,
        },
        {
            "id": 2,
            "name": "Core Development",
            "description": "Building core competencies for the role",
            "icon": "🎯",
            "modules": [],
            "total_hours": 0,
        },
        {
            "id": 3,
            "name": "Advanced Skills",
            "description": "Advanced capabilities and specialization",
            "icon": "🚀",
            "modules": [],
            "total_hours": 0,
        },
        {
            "id": 4,
            "name": "Mastery & Polish",
            "description": "Expert-level refinement and integration",
            "icon": "⭐",
            "modules": [],
            "total_hours": 0,
        },
    ]
    
    for module in modules:
        if module["is_prerequisite"] or module["gap_severity"] == "critical":
            phase_idx = 0
        elif module["gap_severity"] == "important":
            phase_idx = 1
        elif module["gap_severity"] == "nice_to_have":
            phase_idx = 2
        else:
            phase_idx = 3
        
        phases[phase_idx]["modules"].append(module)
        phases[phase_idx]["total_hours"] += module["adjusted_duration"]
    
    # Round hours and remove empty phases
    active_phases = []
    for phase in phases:
        if phase["modules"]:
            phase["total_hours"] = round(phase["total_hours"], 1)
            active_phases.append(phase)
    
    return active_phases
