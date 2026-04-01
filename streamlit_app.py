"""
SkillBridge — AI-Driven Adaptive Learning Engine
Pure Streamlit exact UI replication (No Sidebar)
"""
import streamlit as st
import os
import sys
import tempfile
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers.resume_parser import parse_resume
from parsers.jd_parser import parse_job_description
from engine.skill_extractor import extract_skills
from engine.gap_analyzer import analyze_gaps
from engine.pathway_generator import generate_pathway

st.set_page_config(
    page_title="SkillBridge — AI-Powered Adaptive Learning Engine",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# Load original CSS to guarantee identical colors
css_path = os.path.join(os.path.dirname(__file__), "static", "css", "styles.css")
with open(css_path, "r", encoding="utf-8") as f:
    original_css = f.read()

# ─── INJECT EXACT CSS MATCHING FLASK APP ───
st.markdown(f"""
<style>
    {original_css}
    
    /* Hide Streamlit UI Chrome */
    #MainMenu, footer, header, .stDeployButton, section[data-testid="stSidebar"], [data-testid="stSidebarNav"] {{ display: none !important; visibility: hidden !important; }}
    
    /* Force body to use correct background variable */
    .stApp {{ background-color: var(--bg-primary) !important; font-family: 'Inter', sans-serif !important; color: var(--text-primary) !important; }}
    .block-container {{ max-width: 1200px !important; padding-top: 0 !important; padding-bottom: 50px !important; z-index: 10; position: relative; }}
    
    /* Override Streamlit's aggressive default typography colors */
    .stMarkdown p, .stMarkdown span {{ color: var(--text-secondary) !important; }}
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{ color: var(--text-primary) !important; }}
    .sec-title {{ color: var(--text-primary) !important; }}
    .hero-title {{ color: var(--text-primary) !important; }}
    
    /* Title color override */
    .gradient-text, .brand-text {{
        background: linear-gradient(135deg, #2596be, #c54fcc) !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        color: transparent !important;
        display: inline-block !important;
    }}
    
    /* Revert Streamlit's default blue link styling */
    a.nav-link {{ color: var(--text-secondary) !important; font-weight: 500 !important; font-size: 0.95rem !important; text-decoration: none !important; transition: all 0.3s !important; }}
    a.nav-link:hover {{ color: var(--text-primary) !important; }}
    a.dataset-link {{ color: var(--accent-primary) !important; font-weight: 600 !important; font-size: 0.9rem !important; text-decoration: none !important; }}
    a.dataset-link:hover {{ color: var(--accent-secondary) !important; }}
    
    /* Hide Streamlit's automatic chain-link anchor icons next to headers */
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, .stMarkdown h4 a, .stMarkdown h5 a, .stMarkdown h6 a {{
        display: none !important;
    }}
    
    /* Fix anchor scrolling behind fixed navbar */
    #upload-analyze, #how-it-works, #datasets-models {{
        scroll-margin-top: 120px;
    }}
    
    /* Spacer for fixed navbar */
    .nav-spacer {{ height: 120px; }}

    /* Hero Section additions */
    .hero-container {{ text-align: center; margin-bottom: 60px; }}
    .hero-badge {{
        display: inline-flex; align-items: center; gap: 8px;
        padding: 8px 20px; background: rgba(99, 102, 241, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.15); border-radius: 100px;
        font-size: 0.85rem; font-weight: 500; color: #c4b5fd; margin-bottom: 24px;
    }}
    .hero-badge .dot {{ width: 8px; height: 8px; background: #10b981; border-radius: 50%; display: inline-block; }}
    .stats-row {{ display: flex; justify-content: center; gap: 48px; margin-top: 40px; }}
    .stat-val {{ font-size: 2rem; font-weight: 800; background: linear-gradient(135deg, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .stat-lbl {{ font-size: 0.85rem; color: #6b6680; font-weight: 500; }}

    /* Make the whole Streamlit column look like .upload-card */
    div[data-testid="column"]:has(div.upload-card-header) {{
        background: rgba(18, 18, 30, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 32px !important;
        padding: 48px 40px !important;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3) !important;
        min-height: 520px !important;
    }}
    div[data-testid="column"]:has(div.upload-card-header):hover {{
        border-color: rgba(255, 255, 255, 0.15) !important;
        background: rgba(20, 20, 35, 0.9) !important;
        transform: translateY(-2px) !important;
    }}
    
    div[data-testid="stFileUploader"] {{ 
        background: transparent !important;
        border: 2px dashed rgba(255, 255, 255, 0.2) !important;
        border-radius: 24px !important;
        padding: 30px !important;
        text-align: center !important;
    }}
    div[data-testid="stFileUploader"]:hover {{ border-color: #6366f1 !important; background: rgba(99, 102, 241, 0.05) !important; }}
    div[data-testid="stFileUploader"] section {{ background: transparent !important; color: #a09cb0 !important; }}
    div[data-testid="stFileUploader"] small {{ color: #6b6680 !important; }}
    div[data-testid="stFileUploader"] button {{
        background: transparent !important; border: none !important; color: #6366f1 !important;
        font-weight: 600 !important; font-size: 1rem !important; box-shadow: none !important; padding: 0 !important;
    }}
    div[data-testid="stFileUploader"] button:hover {{ color: #a855f7 !important; background: transparent !important; }}

    div[data-baseweb="textarea"], div[data-baseweb="textarea"] > textarea {{
        background-color: rgba(0, 0, 0, 0.4) !important;
        border: none !important;
        color: #f1f0f5 !important;
        padding: 20px !important;
        font-size: 0.95rem !important;
    }}
    div[data-testid="stTextArea"] {{ 
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        border-radius: 20px !important; 
        background: transparent !important;
        overflow: hidden !important;
    }}
    div[data-testid="stTextArea"]:focus-within {{ 
        border-color: rgba(99, 102, 241, 0.5) !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }}
    
    .stButton button {{
        background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        padding: 16px 60px !important;
        border-radius: 20px !important;
        border: none !important;
        width: auto !important;
        min-width: 450px !important;
        margin: 0 auto !important;
        display: block !important;
        box-shadow: 0 10px 30px rgba(124, 58, 237, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }}
    .stButton button:hover {{
        transform: scale(1.02) translateY(-2px) !important;
        box-shadow: 0 15px 40px rgba(124, 58, 237, 0.5) !important;
    }}
    .stButton button:hover:not(:disabled) {{
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.3) !important;
    }}
</style>

<!-- Background exact match -->
<div class="bg-grid"></div>
<div class="bg-gradient-orb bg-orb-1"></div>
<div class="bg-gradient-orb bg-orb-2"></div>
<div class="bg-gradient-orb bg-orb-3"></div>

<!-- Top Navbar -->
<nav class="navbar" id="navbar" style="position: fixed; top: 0; left: 0; width: 100%; z-index: 1000;">
    <div class="nav-content">
        <div class="nav-brand">
            <div class="brand-icon">
        <svg width="24" height="24" viewBox="0 0 32 32" fill="none">
            <path d="M16 2L4 8V24L16 30L28 24V8L16 2Z" stroke="url(#brand-gradient)" stroke-width="2"/>
            <path d="M16 10L10 13V19L16 22L22 19V13L16 10Z" fill="url(#brand-gradient)"/>
            <defs>
                <linearGradient id="brand-gradient" x1="4" y1="2" x2="28" y2="30">
                    <stop stop-color="#6366f1"/><stop offset="1" stop-color="#a855f7"/>
                </linearGradient>
            </div>
            <span class="brand-text">SkillBridge</span>
        </div>
        <div class="nav-links">
            <a href="#upload-analyze" class="nav-link">Analyze</a>
            <a href="#how-it-works" class="nav-link">How It Works</a>
            <a href="#datasets-models" class="nav-link">Datasets</a>
        </div>
    </div>
</nav>
<div class="nav-spacer"></div>
""", unsafe_allow_html=True)

# ─── Hero ───
st.markdown("""
<div class="hero-container">
    <div class="hero-badge"><span class="dot"></span> AI-Powered Learning Pathways</div>
    <h1 class="hero-title"><span class="gradient-text">Bridge the Skill Gap<br>with Adaptive Learning</span></h1>
    <p class="hero-subtitle">Upload a resume and job description — our AI engine extracts skills, identifies gaps, and generates a personalized, time-optimized training roadmap.</p>
    <div class="stats-row">
        <div><div class="stat-val">270+</div><div class="stat-lbl">Skills Tracked</div></div>
        <div><div class="stat-val">40+</div><div class="stat-lbl">Learning Modules</div></div>
        <div><div class="stat-val">14</div><div class="stat-lbl">Skill Categories</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── How it Works ───
st.markdown("""
<div class="section-title-wrapper" id="how-it-works">
    <span class="sec-badge">Process</span>
    <h2 class="sec-title"><span class="gradient-text">How It Works</span></h2>
    <p class="sec-subtitle">Four intelligent steps from document to personalized pathway</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="steps-grid">
    <div class="step-card" style="--delay: 0">
        <div class="step-number">01</div>
        <div class="step-icon">📄</div>
        <h3>Upload Documents</h3>
        <p>Upload a resume (PDF/DOCX/TXT) and paste the target job description.</p>
    </div>
    <div class="step-card" style="--delay: 1">
        <div class="step-number">02</div>
        <div class="step-icon">🔍</div>
        <h3>Skill Extraction</h3>
        <p>Our NLP engine parses both documents against a 270+ skill taxonomy (O*NET-based).</p>
    </div>
    <div class="step-card" style="--delay: 2">
        <div class="step-number">03</div>
        <div class="step-icon">📊</div>
        <h3>Gap Analysis</h3>
        <p>Smart comparison identifies gaps, considering proficiency levels and transferable skills.</p>
    </div>
    <div class="step-card" style="--delay: 3">
        <div class="step-number">04</div>
        <div class="step-icon">🗺️</div>
        <h3>Adaptive Pathway</h3>
        <p>A personalized, phased learning roadmap is generated with time-optimized modules.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Upload Area ───
st.markdown("""
<div class="section-title-wrapper" id="upload-analyze">
    <span class="sec-badge">Demo</span>
    <h2 class="sec-title"><span class="gradient-text">Upload & Analyze</span></h2>
    <p class="sec-subtitle">Experience the engine in real-time</p>
</div>
""", unsafe_allow_html=True)

upload_col1, upload_col2 = st.columns(2)

with upload_col1:
    st.markdown("""
    <div class="upload-card" style="border: none; background: transparent; padding: 0 0 10px;">
        <div class="upload-card-header">
            <div class="upload-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                    <polyline points="10 9 9 9 8 9"/>
                </svg>
            </div>
            <h3>Resume</h3>
            <p>Upload candidate's resume</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    resume_file = st.file_uploader("", type=["pdf", "docx", "txt"])

with upload_col2:
    st.markdown("""
    <div class="upload-card" style="border: none; background: transparent; padding: 0 0 10px;">
        <div class="upload-card-header">
            <div class="upload-icon jd-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="2" y="3" width="20" height="18" rx="2" ry="2"/>
                    <line x1="8" y1="7" x2="16" y2="7"/>
                    <line x1="8" y1="11" x2="16" y2="11"/>
                    <line x1="8" y1="15" x2="12" y2="15"/>
                </svg>
            </div>
            <h3>Job Description</h3>
            <p>Paste target role requirements</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    jd_text = st.text_area("", height=220, placeholder="Paste the full job description here...\n\nExample:\nSenior Software Engineer\n\nRequirements:\n- 5+ years of experience with Python\n- Strong knowledge of React and Node.js")

st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([1,2,1])
with btn_col:
    can_analyze = resume_file is not None and jd_text and len(jd_text.strip()) > 20
    analyze = st.button("🚀 Generate Learning Pathway", disabled=not can_analyze)
    if not can_analyze:
        st.markdown("<p style='text-align: center; color: #6b6680; font-size: 0.85rem; margin-top: 8px;'>Both resume and job description are required</p>", unsafe_allow_html=True)

# ─── Logic ───
if analyze and resume_file and jd_text:
    with st.spinner("Analyzing... Extracting skills and calculating gaps..."):
        try:
            suffix = "." + resume_file.name.rsplit(".", 1)[-1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(resume_file.getbuffer())
                tmp_path = tmp.name
                
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
            os.unlink(tmp_path)
            
            st.session_state["result"] = {
                "success": True,
                "resume_analysis": {
                    "skills_found": resume_skills["total_skills_found"],
                    "skill_categories": resume_skills["skill_categories"],
                    "skills": resume_skills["found_skills"],
                    "metadata": resume_data.get("metadata", {}),
                },
                "jd_analysis": {
                    "title": jd_data.get("title", ""),
                    "seniority": jd_data.get("seniority_level", ""),
                    "experience_required": jd_data.get("experience_required", ""),
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
                    "skill_extraction_accuracy": "Taxonomy-based (0.6-1.0 confidence score)",
                    "gap_coverage_score": f"{gap_analysis['summary']['match_percentage']}% skills matched",
                    "pathway_efficiency_index": pathway.get("metrics", {}).get("pathway_efficiency_index", "N/A"),
                    "personalization_ratio": pathway.get("metrics", {}).get("personalization_ratio", "N/A"),
                }
            }
        except Exception as e:
            st.error(f"Error during analysis: {e}")

# Render results entirely via a specialized iframe if they exist
if "result" in st.session_state:
    st.markdown("""
    <div class="section-title-wrapper" style="margin-top: 100px; margin-bottom: 0;">
        <span class="sec-badge success-badge">Analysis Complete</span>
        <h2 class="sec-title">Your Personalized Pathway</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # We use a custom components embed but pass the JSON data purely so the frontend renders it beautifully.
    # This prevents UI bugs and keeps the absolute perfect original Results CSS!
    
    result_data = st.session_state["result"]
    import json
    import streamlit.components.v1 as components
    
    json_str = json.dumps(result_data).replace("</", "<\\/").replace("'", "\\'")
    
    css_path = os.path.join(os.path.dirname(__file__), "static", "css", "styles.css")
    js_path = os.path.join(os.path.dirname(__file__), "static", "js", "app.js")
    with open(css_path, "r", encoding="utf-8") as f: css = f.read()
    with open(js_path, "r", encoding="utf-8") as f: 
        js = f.read()
        js = js.split('document.addEventListener("DOMContentLoaded"')[0]
    
    html = f"""
    <!DOCTYPE html><html><head>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        {css}
        html,body {{ background: transparent !important; margin: 0; padding: 0; min-height: 100vh; overflow:hidden; }}
        #results {{ display: block !important; padding: 0 !important; }}
        .results-header {{ display:none; /* hid this because we show it above the iframe */ }}
    </style></head><body>
    
    <section class="section" id="results">
        <div class="container" style="max-width:1200px; padding:0;">
            <div class="summary-grid" id="summary-grid"></div>
            <div class="results-tabs">
                <button class="tab-btn active" data-tab="pathway" id="tab-pathway">🗺️ Learning Pathway</button>
                <button class="tab-btn" data-tab="gaps" id="tab-gaps">📊 Skill Gaps</button>
                <button class="tab-btn" data-tab="skills" id="tab-skills">🎯 Skills Overview</button>
                <button class="tab-btn" data-tab="metrics" id="tab-metrics">📈 Metrics</button>
            </div>
            <div class="tab-content active" id="content-pathway"><div id="pathway-container"></div></div>
            <div class="tab-content" id="content-gaps"><div class="gaps-layout"><div class="radar-chart-container" id="radar-chart-container"><canvas id="radar-canvas" width="450" height="450"></canvas></div><div class="gaps-list" id="gaps-list"></div></div></div>
            <div class="tab-content" id="content-skills"><div class="skills-comparison" id="skills-comparison"></div></div>
            <div class="tab-content" id="content-metrics"><div id="metrics-container"></div></div>
        </div>
    </section>
    
    <script>{js}</script>
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        try {{ initTabs(); }} catch(e) {{ console.error("Tab init error:", e); }}
        
        var fullData = JSON.parse('{json_str}');
        try {{ renderResults(fullData); }} catch(e) {{ console.error("Render error:", e); }}
    }});
    </script>
    </body></html>
    """
    components.html(html, height=1800, scrolling=True)


# ─── Datasets & Footer ───
st.markdown("""
<br><br>
<div class="section-title-wrapper" id="datasets-models">
    <span class="sec-badge">Information</span>
    <h2 class="sec-title"><span class="gradient-text">Datasets & Models</span></h2>
    <p class="sec-subtitle">Background on the data and models powering SkillBridge.</p>
</div>
<div class="datasets-grid">
    <div class="dataset-card">
        <div class="dataset-icon">🏛️</div>
        <h3>O*NET Skills & Knowledge</h3>
        <p>Industry-standard occupational taxonomy from the U.S. Department of Labor. Used as the foundation for our 270+ skill taxonomy and proficiency scales.</p>
        <a href="#" class="dataset-link">onetcenter.org →</a>
    </div>
    <div class="dataset-card">
        <div class="dataset-icon">🤖</div>
        <h3>spaCy NLP (Open Source)</h3>
        <p>Industrial-strength NLP library used for text processing. Our skill extraction uses custom taxonomy-based matching with confidence scoring.</p>
        <a href="#" class="dataset-link">spacy.io →</a>
    </div>
    <div class="dataset-card">
        <div class="dataset-icon">📊</div>
        <h3>Kaggle Resume Dataset</h3>
        <p>Collection of 2,400+ resumes across various fields. Used for validation and testing of skill extraction accuracy.</p>
        <a href="#" class="dataset-link">kaggle.com →</a>
    </div>
    <div class="dataset-card">
        <div class="dataset-icon">⚙️</div>
        <h3>Original Adaptive Logic</h3>
        <p>Our custom weighted scoring algorithm considers gap severity, prerequisite depth, transferable skills, and role priority to optimize learning pathways.</p>
        <span class="dataset-link" style="text-decoration: none;">Custom Implementation</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding: 60px 0 40px; border-top: 1px solid rgba(255,255,255,0.06); margin-top: 60px;">
    <div style="font-size: 1.2rem; font-weight: 700; margin-bottom: 8px; color: #f1f0f5;">SkillBridge</div>
    <div style="color:#6b6680; font-size: 0.9rem;">AI-Driven Adaptive Learning Engine for Corporate Onboarding</div>
</div>
""", unsafe_allow_html=True)
