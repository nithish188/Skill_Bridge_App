"""
Job Description Parser Module
Extracts required skills, experience level, and role information from JDs.
"""
import re


def parse_job_description(text):
    """
    Parse a job description text and extract structured information.
    
    Args:
        text: Raw text of the job description
    
    Returns:
        dict with 'title', 'required_skills', 'preferred_skills',
        'experience_required', 'sections'
    """
    if not text or not text.strip():
        raise ValueError("Job description text is empty.")
    
    result = {
        "title": extract_job_title(text),
        "required_skills_text": "",
        "preferred_skills_text": "",
        "experience_required": extract_experience_requirement(text),
        "sections": extract_jd_sections(text),
        "seniority_level": detect_seniority(text),
        "full_text": text.strip()
    }
    
    return result


def extract_job_title(text):
    """Extract job title from the beginning of the JD."""
    lines = text.strip().split("\n")
    for line in lines[:5]:
        line = line.strip()
        if line and len(line) < 100 and not re.match(r"(?i)(about|company|location|department)", line):
            return line
    return "Unknown Role"


def extract_experience_requirement(text):
    """Extract required years of experience from JD."""
    patterns = [
        r"(\d+)\+?\s*years?\s*(?:of\s+)?(?:relevant\s+)?experience",
        r"experience\s*(?:of\s+)?(\d+)\+?\s*years?",
        r"minimum\s+(\d+)\s*years?",
        r"at\s+least\s+(\d+)\s*years?",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    return 0


def detect_seniority(text):
    """Detect the seniority level from JD text."""
    text_lower = text.lower()
    
    if any(kw in text_lower for kw in ["principal", "staff", "distinguished", "fellow", "vp ", "vice president"]):
        return "principal"
    elif any(kw in text_lower for kw in ["senior", "sr.", "sr ", "lead", "tech lead"]):
        return "senior"
    elif any(kw in text_lower for kw in ["mid-level", "mid level", "intermediate", "regular"]):
        return "mid"
    elif any(kw in text_lower for kw in ["junior", "jr.", "jr ", "entry-level", "entry level", "associate", "intern", "trainee", "graduate"]):
        return "junior"
    else:
        return "mid"


def extract_jd_sections(text):
    """Extract sections from the job description."""
    sections = {}
    
    section_patterns = [
        r"(?i)(responsibilities|duties|what\s+you.ll\s+do|role\s+description|key\s+responsibilities)",
        r"(?i)(requirements?|qualifications?|must\s+have|what\s+we.re\s+looking\s+for|what\s+you.ll\s+need)",
        r"(?i)(preferred|nice\s+to\s+have|bonus|desired|good\s+to\s+have|plus)",
        r"(?i)(benefits?|perks|what\s+we\s+offer|compensation)",
        r"(?i)(about\s+us|company|who\s+we\s+are|our\s+team)",
        r"(?i)(skills?|technical\s+skills?|required\s+skills?)",
    ]
    
    lines = text.split("\n")
    current_section = "overview"
    current_content = []
    
    for line in lines:
        matched = False
        for pattern in section_patterns:
            if re.search(pattern, line) and len(line.strip()) < 80:
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = line.strip().lower()
                current_content = []
                matched = True
                break
        if not matched:
            current_content.append(line)
    
    if current_content:
        sections[current_section] = "\n".join(current_content).strip()
    
    return sections
