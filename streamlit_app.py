"""
SkillBridge — AI-Driven Adaptive Learning Engine
Streamlit Deployment: Pixel-perfect replica of the Flask UI.

Strategy:
- Page 1 (no results): Show the full original HTML with working upload form
  but intercept form submission - use Streamlit widgets above the iframe for upload
- Page 2 (with results): Re-render HTML with results pre-injected so renderResults() 
  runs on page load, showing the exact same results UI
"""
import streamlit as st
import streamlit.components.v1 as components
import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers.resume_parser import parse_resume
from parsers.jd_parser import parse_job_description
from engine.skill_extractor import extract_skills
from engine.gap_analyzer import analyze_gaps
from engine.pathway_generator import generate_pathway

# ─── Page Config ───
st.set_page_config(
    page_title="SkillBridge — AI-Powered Adaptive Learning Engine",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Hide Streamlit chrome, but keep widgets functional ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    #MainMenu, footer, header, .stDeployButton,
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"] { display: none !important; }
    
    .stApp {
        background: #0a0a0f;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Style the sidebar to match the dark theme */
    section[data-testid="stSidebar"] {
        background: #111118 !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #f1f0f5 !important;
    }
    section[data-testid="stSidebar"] .stTextArea textarea {
        background: rgba(0,0,0,0.3) !important;
        border-color: rgba(255,255,255,0.1) !important;
        color: #f1f0f5 !important;
    }
    section[data-testid="stSidebar"] .stTextArea textarea:focus {
        border-color: #a855f7 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stFileUploader"] section {
        background: rgba(0,0,0,0.3) !important;
        border-color: rgba(255,255,255,0.1) !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #6366f1, #a855f7) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
    }
    section[data-testid="stSidebar"] .stButton button:disabled {
        opacity: 0.4 !important;
    }
    section[data-testid="stSidebar"] .stButton button:hover:not(:disabled) {
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4) !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.06) !important;
    }
    
    /* Main content area */
    .block-container { padding: 0 !important; max-width: 100% !important; }
    div[data-testid="stVerticalBlock"] > div { gap: 0 !important; }
    iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)


def load_file(path):
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def run_analysis(uploaded_file, jd_text):
    """Full analysis pipeline."""
    suffix = "." + uploaded_file.name.rsplit(".", 1)[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name
    try:
        resume_data = parse_resume(tmp_path)
        jd_data = parse_job_description(jd_text)
        resume_skills = extract_skills(resume_data["text"])
        jd_skills = extract_skills(jd_text)
        gap_analysis = analyze_gaps(
            resume_skills, jd_skills,
            resume_data["text"], jd_text,
            resume_data["metadata"]
        )
        pathway = generate_pathway(gap_analysis, resume_data["metadata"])
        return {
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
                {"name": "O*NET Skills & Knowledge Database",
                 "url": "https://www.onetcenter.org/db_releases.html",
                 "usage": "Skill taxonomy and proficiency scale reference"},
                {"name": "Kaggle Resume Dataset",
                 "url": "https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset/data",
                 "usage": "Validation and testing of skill extraction accuracy"}
            ],
            "metrics": {
                "skill_extraction_accuracy": "Taxonomy-based matching with confidence scoring (0.6-1.0 range)",
                "gap_coverage_score": f"{gap_analysis['summary']['match_percentage']}% skills matched",
                "pathway_efficiency_index": pathway.get("metrics", {}).get("pathway_efficiency_index", "N/A"),
                "personalization_ratio": pathway.get("metrics", {}).get("personalization_ratio", "N/A"),
            }
        }
    finally:
        os.unlink(tmp_path)


def build_page(result_data=None):
    """Build the exact same HTML page as Flask serves, with inline CSS/JS."""
    css = load_file("static/css/styles.css")
    js = load_file("static/js/app.js")
    html = load_file("templates/index.html")

    # Inline the CSS
    html = html.replace(
        '<link rel="stylesheet" href="/static/css/styles.css">',
        f'<style>{css}</style>'
    )

    # Build auto-render script if results exist
    auto_render = ""
    if result_data:
        # Escape for safe JS injection
        data_json = json.dumps(result_data).replace("</", "<\\/").replace("'", "\\'")
        auto_render = f"""
<script>
document.addEventListener('DOMContentLoaded', function() {{
    // Auto-render results
    var data = JSON.parse('{data_json}');
    
    // Show a file in the dropzone
    var dropContent = document.querySelector('.dropzone-content');
    var fileInfo = document.getElementById('resume-file-info');
    var filename = document.getElementById('resume-filename');
    if (dropContent && fileInfo && filename) {{
        dropContent.style.display = 'none';
        fileInfo.style.display = 'flex';
        filename.textContent = 'Resume uploaded via sidebar';
    }}
    
    // Update JD textarea
    var jdEl = document.getElementById('jd-textarea');
    var jdCount = document.getElementById('jd-count');
    if (jdEl) {{
        jdEl.value = 'Job description provided via sidebar';
        if (jdCount) jdCount.textContent = jdEl.value.length;
    }}
    
    // Enable and update button
    var btn = document.getElementById('analyze-btn');
    if (btn) btn.disabled = false;
    
    // Render the results
    if (typeof renderResults === 'function') {{
        renderResults(data);
    }}
    
    // Scroll to results after a short delay
    setTimeout(function() {{
        var results = document.getElementById('results');
        if (results) results.scrollIntoView({{ behavior: 'smooth' }});
    }}, 300);
}});
</script>
"""

    # Override the analyze button to show a message about using the sidebar
    sidebar_override = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    var btn = document.getElementById('analyze-btn');
    var dropzone = document.getElementById('resume-dropzone');
    var hint = document.querySelector('.analyze-hint');
    
    // Update hint text
    if (hint) {
        hint.innerHTML = '↖ Use the sidebar (click <b>></b> arrow at top-left) to upload resume & paste JD';
    }
    
    // Show message on dropzone click  
    if (dropzone) {
        dropzone.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            alert('Please use the sidebar (click the > arrow at the top-left) to upload your resume file.');
        });
    }
    
    if (btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            alert('Please use the sidebar (click the > arrow at the top-left) to upload files and analyze.');
        });
        btn.disabled = false;
        btn.textContent = '↖ Use Sidebar to Upload & Analyze';
    }
});
</script>
"""

    # If no results yet, add sidebar override
    if not result_data:
        extra_scripts = sidebar_override
    else:
        extra_scripts = auto_render

    # Inline the JS + extras
    html = html.replace(
        '<script src="/static/js/app.js"></script>',
        f'<script>{js}</script>\n{extra_scripts}'
    )

    return html


def main():
    # ─── Sidebar for uploads ───
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:16px 0 8px;">
            <span style="font-size:1.3rem;font-weight:700;background:linear-gradient(135deg,#6366f1,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                🌉 SkillBridge
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("##### 📄 Upload Resume")
        resume_file = st.file_uploader(
            "Resume file",
            type=["pdf", "docx", "txt"],
            label_visibility="collapsed"
        )
        
        st.markdown("##### 📋 Job Description")
        jd_text = st.text_area(
            "Paste here",
            height=250,
            placeholder="Paste the full job description here...\n\nExample:\nSenior Software Engineer\n\nRequirements:\n- 5+ years Python\n- React, Node.js\n- AWS, Docker",
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        can_analyze = resume_file is not None and jd_text and len(jd_text.strip()) > 20
        analyze = st.button(
            "🚀 Generate Learning Pathway",
            use_container_width=True,
            disabled=not can_analyze
        )
        
        if not can_analyze:
            st.caption("Upload a resume and paste a JD to begin")

    # ─── Run analysis ───
    if analyze and resume_file and jd_text:
        with st.spinner("🔍 Analyzing..."):
            try:
                result = run_analysis(resume_file, jd_text)
                st.session_state["result"] = result
            except Exception as e:
                st.error(f"❌ {str(e)}")

    # ─── Render page ───
    result = st.session_state.get("result", None)
    page_html = build_page(result)
    
    height = 5500 if result else 3800
    components.html(page_html, height=height, scrolling=True)


if __name__ == "__main__":
    main()
