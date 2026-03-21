"""
Resume Parser Module
Extracts text from PDF, DOCX, and TXT files for skill analysis.
"""
import os
import re


def extract_text_from_pdf(filepath):
    """Extract text from a PDF file using pdfplumber."""
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")


def extract_text_from_docx(filepath):
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document
        doc = Document(filepath)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to parse DOCX: {str(e)}")


def extract_text_from_txt(filepath):
    """Extract text from a plain text file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except Exception as e:
        raise ValueError(f"Failed to read TXT file: {str(e)}")


def parse_resume(filepath):
    """
    Parse a resume file and extract its text content.
    
    Args:
        filepath: Path to the resume file (PDF, DOCX, or TXT)
    
    Returns:
        dict with 'text', 'sections', and 'metadata'
    """
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == ".pdf":
        text = extract_text_from_pdf(filepath)
    elif ext == ".docx":
        text = extract_text_from_docx(filepath)
    elif ext == ".txt":
        text = extract_text_from_txt(filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
    
    if not text:
        raise ValueError("No text could be extracted from the file.")
    
    # Extract sections
    sections = extract_sections(text)
    
    # Extract metadata
    metadata = extract_metadata(text)
    
    return {
        "text": text,
        "sections": sections,
        "metadata": metadata
    }


def extract_sections(text):
    """
    Identify common resume sections from the text.
    Returns a dictionary of section_name -> section_content.
    """
    # Common resume section headers
    section_patterns = [
        r"(?i)(education|academic|qualification)",
        r"(?i)(experience|employment|work\s*history|professional\s*experience)",
        r"(?i)(skills|technical\s*skills|core\s*competenc|proficienc)",
        r"(?i)(projects|portfolio|key\s*projects)",
        r"(?i)(certifications?|licenses?|credentials?)",
        r"(?i)(summary|objective|profile|about\s*me|professional\s*summary)",
        r"(?i)(awards?|honors?|achievements?)",
        r"(?i)(publications?|research)",
        r"(?i)(languages?)",
        r"(?i)(interests?|hobbies?|extracurricular)",
    ]
    
    sections = {}
    lines = text.split("\n")
    current_section = "header"
    current_content = []
    
    for line in lines:
        matched = False
        for pattern in section_patterns:
            if re.search(pattern, line) and len(line.strip()) < 60:
                # Save previous section
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                # Start new section
                current_section = line.strip().lower()
                current_content = []
                matched = True
                break
        if not matched:
            current_content.append(line)
    
    # Save last section
    if current_content:
        sections[current_section] = "\n".join(current_content).strip()
    
    return sections


def extract_metadata(text):
    """
    Extract metadata like years of experience from resume text.
    """
    metadata = {
        "estimated_years": 0,
        "education_level": "unknown",
        "has_certifications": False
    }
    
    # Estimate years of experience
    year_patterns = [
        r"(\d+)\+?\s*years?\s*(?:of\s+)?experience",
        r"experience\s*(?:of\s+)?(\d+)\+?\s*years?",
        r"(\d{4})\s*[-–]\s*(?:present|current|now|\d{4})",
    ]
    
    years_found = []
    for pattern in year_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                val = int(match)
                if val > 1900:  # It's a year, not a count
                    years_found.append(2025 - val)
                elif val < 50:
                    years_found.append(val)
            except ValueError:
                pass
    
    if years_found:
        metadata["estimated_years"] = max(years_found)
    
    # Detect education level
    edu_patterns = {
        "phd": r"(?i)(ph\.?d|doctorate|doctoral)",
        "masters": r"(?i)(master|m\.?s\.?|m\.?tech|mba|m\.?eng)",
        "bachelors": r"(?i)(bachelor|b\.?s\.?|b\.?tech|b\.?eng|b\.?a\.?|undergraduate)",
        "associate": r"(?i)(associate|diploma)",
    }
    
    for level, pattern in edu_patterns.items():
        if re.search(pattern, text):
            metadata["education_level"] = level
            break
    
    # Check for certifications
    cert_patterns = r"(?i)(certified|certification|certificate|aws\s+certified|google\s+certified|microsoft\s+certified|pmp|scrum\s+master|cisco)"
    if re.search(cert_patterns, text):
        metadata["has_certifications"] = True
    
    return metadata
