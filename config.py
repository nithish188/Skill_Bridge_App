"""Configuration constants for SkillBridge."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

# Proficiency levels
PROFICIENCY_LEVELS = {
    "novice": 20,
    "beginner": 35,
    "intermediate": 55,
    "advanced": 75,
    "expert": 95,
}

# Gap severity thresholds
GAP_SEVERITY = {
    "critical": 60,    # Gap score >= 60 is critical
    "important": 35,   # Gap score >= 35 is important
    "nice_to_have": 0, # Gap score < 35 is nice-to-have
}

# Adaptive pathway weights (our original adaptive logic)
PATHWAY_WEIGHTS = {
    "gap_severity": 0.35,       # How large the skill gap is
    "prerequisite_depth": 0.20, # How many prerequisites exist
    "transferable_bonus": 0.20, # Bonus for related skills already known
    "role_priority": 0.25,      # How important is this skill for the role
}

# Time estimates (hours per proficiency level to gain)
HOURS_PER_LEVEL = {
    "novice_to_beginner": 8,
    "beginner_to_intermediate": 20,
    "intermediate_to_advanced": 40,
    "advanced_to_expert": 60,
}
