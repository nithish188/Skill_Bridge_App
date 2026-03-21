"""
SkillBridge - AI-Driven Adaptive Learning Engine
Flask Application Entry Point

Datasets Used:
- O*NET Skills & Knowledge (https://www.onetcenter.org/db_releases.html)
  Used for skill taxonomy and proficiency scales.
- Kaggle Resume Dataset (https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset/data)
  Referenced for validation and testing of skill extraction accuracy.

Models & Libraries:
- spaCy (https://spacy.io/) - Open-source NLP library for text processing
- Custom NLP pipeline for skill extraction using regex + taxonomy matching

All adaptive logic is original implementation by the SkillBridge team.
"""
import os
import json
import traceback
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import UPLOAD_DIR, ALLOWED_EXTENSIONS
from parsers.resume_parser import parse_resume
from parsers.jd_parser import parse_job_description
from engine.skill_extractor import extract_skills
from engine.gap_analyzer import analyze_gaps
from engine.pathway_generator import generate_pathway

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Main analysis endpoint.
    Accepts resume file + JD text, returns full analysis with pathway.
    """
    import sys
    filepath = None
    try:
        print("[API] /api/analyze called", flush=True)
        
        # Get resume file
        if "resume" not in request.files:
            return jsonify({"error": "No resume file provided"}), 400
        
        resume_file = request.files["resume"]
        if resume_file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(resume_file.filename):
            return jsonify({"error": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
        
        # Get JD text
        jd_text = request.form.get("jd_text", "").strip()
        if not jd_text:
            return jsonify({"error": "No job description provided"}), 400
        
        # Save and parse resume
        filename = secure_filename(resume_file.filename)
        filepath = os.path.join(UPLOAD_DIR, filename)
        resume_file.save(filepath)
        print(f"[API] File saved: {filepath} ({os.path.getsize(filepath)} bytes)", flush=True)
        
        # Step 1: Parse resume
        print("[API] Step 1: Parsing resume...", flush=True)
        resume_data = parse_resume(filepath)
        print(f"[API] Resume parsed. Text length: {len(resume_data['text'])}", flush=True)
        
        # Step 2: Parse JD
        print("[API] Step 2: Parsing JD...", flush=True)
        jd_data = parse_job_description(jd_text)
        print(f"[API] JD parsed. Title: {jd_data['title']}", flush=True)
        
        # Step 3: Extract skills from both
        print("[API] Step 3: Extracting skills...", flush=True)
        resume_skills = extract_skills(resume_data["text"])
        jd_skills = extract_skills(jd_text)
        print(f"[API] Resume skills: {resume_skills['total_skills_found']}, JD skills: {jd_skills['total_skills_found']}", flush=True)
        
        # Step 4: Analyze gaps
        print("[API] Step 4: Analyzing gaps...", flush=True)
        gap_analysis = analyze_gaps(
            resume_skills, jd_skills,
            resume_data["text"], jd_text,
            resume_data["metadata"]
        )
        print(f"[API] Gaps found: {gap_analysis['summary']['skills_with_gaps']}", flush=True)
        
        # Step 5: Generate adaptive pathway
        print("[API] Step 5: Generating pathway...", flush=True)
        pathway = generate_pathway(gap_analysis, resume_data["metadata"])
        print(f"[API] Pathway generated: {pathway.get('total_modules', 0)} modules, {pathway.get('total_hours', 0)}h", flush=True)
        
        # Build response
        response = {
            "success": True,
            "resume_analysis": {
                "skills_found": resume_skills["total_skills_found"],
                "skill_categories": resume_skills["skill_categories"],
                "skills": resume_skills["found_skills"],
                "metadata": resume_data["metadata"],
            },
            "jd_analysis": {
                "title": jd_data["title"],
                "seniority": jd_data["seniority_level"],
                "experience_required": jd_data["experience_required"],
                "skills_found": jd_skills["total_skills_found"],
                "skills": jd_skills["found_skills"],
            },
            "gap_analysis": {
                "summary": gap_analysis["summary"],
                "gaps": gap_analysis["gaps"],
                "matched_skills": gap_analysis["matched_skills"],
                "category_gaps": gap_analysis["category_gaps"],
            },
            "pathway": pathway,
            "datasets_used": [
                {
                    "name": "O*NET Skills & Knowledge Database",
                    "url": "https://www.onetcenter.org/db_releases.html",
                    "usage": "Skill taxonomy and proficiency scale reference"
                },
                {
                    "name": "Kaggle Resume Dataset",
                    "url": "https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset/data",
                    "usage": "Validation and testing of skill extraction accuracy"
                }
            ],
            "metrics": {
                "skill_extraction_accuracy": "Taxonomy-based matching with confidence scoring (0.6-1.0 range)",
                "gap_coverage_score": f"{gap_analysis['summary']['match_percentage']}% skills matched",
                "pathway_efficiency_index": pathway.get("metrics", {}).get("pathway_efficiency_index", "N/A"),
                "personalization_ratio": pathway.get("metrics", {}).get("personalization_ratio", "N/A"),
            }
        }
        
        print("[API] ✅ Analysis complete, sending response", flush=True)
        return jsonify(response)
    
    except Exception as e:
        print(f"[API] ❌ ERROR: {e}", flush=True)
        traceback.print_exc()
        sys.stdout.flush()
        return jsonify({"error": str(e)}), 500
    
    finally:
        # Clean up uploaded file
        if filepath and os.path.exists(filepath):
            os.remove(filepath)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "SkillBridge API"})


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=debug, host="0.0.0.0", port=port)
