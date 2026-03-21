"""
SkillBridge — AI-Driven Adaptive Learning Engine
Streamlit Application for Streamlit Cloud Deployment

Datasets Used:
- O*NET Skills & Knowledge (https://www.onetcenter.org/db_releases.html)
- Kaggle Resume Dataset (https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset/data)

All adaptive logic is original implementation by the SkillBridge team.
"""
import streamlit as st
import os
import tempfile
import json

from parsers.resume_parser import parse_resume
from parsers.jd_parser import parse_job_description
from engine.skill_extractor import extract_skills
from engine.gap_analyzer import analyze_gaps
from engine.pathway_generator import generate_pathway

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SkillBridge — AI Adaptive Learning Engine",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* Global */
    .stApp {
        background: #0a0a0f;
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit Defaults */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 2rem; max-width: 1200px;}

    /* Hero */
    .hero-container {
        text-align: center;
        padding: 40px 20px 30px;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 18px;
        background: rgba(99,102,241,0.08);
        border: 1px solid rgba(99,102,241,0.18);
        border-radius: 100px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #a78bfa;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 18px;
    }
    .hero-badge .dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #10b981;
        display: inline-block;
        animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
        0%,100% {opacity:1;transform:scale(1);}
        50% {opacity:.5;transform:scale(.8);}
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 900;
        color: #f1f0f5;
        line-height: 1.1;
        margin-bottom: 14px;
        letter-spacing: -0.03em;
    }
    .gradient-text {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-sub {
        font-size: 1.1rem;
        color: #a09cb0;
        max-width: 650px;
        margin: 0 auto 30px;
        line-height: 1.7;
    }
    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 48px;
        margin-top: 20px;
    }
    .stat-item {text-align:center;}
    .stat-val {
        display: block;
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg,#6366f1,#a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-lbl {font-size:.8rem;color:#6b6680;font-weight:500;}

    /* Cards */
    .glass-card {
        background: rgba(22,22,35,0.7);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 16px;
        backdrop-filter: blur(10px);
    }
    .glass-card:hover {
        border-color: rgba(99,102,241,0.3);
    }
    .card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 6px;
    }
    .card-header h3 {
        font-size: 1.15rem;
        font-weight: 700;
        color: #f1f0f5;
        margin: 0;
    }
    .card-sub {
        font-size: 0.85rem;
        color: #6b6680;
        margin-bottom: 0;
    }

    /* Summary metric cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .metric-card {
        background: rgba(22,22,35,0.7);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 20px;
        position: relative;
        overflow: hidden;
    }
    .metric-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
    }
    .metric-card.mc-match::after {background:#10b981}
    .metric-card.mc-gaps::after {background:#f59e0b}
    .metric-card.mc-hours::after {background:#6366f1}
    .metric-card.mc-eff::after {background:#a855f7}
    .metric-icon {font-size:1.4rem;margin-bottom:6px;}
    .metric-val {font-size:1.8rem;font-weight:800;color:#f1f0f5;line-height:1;}
    .metric-lbl {font-size:.7rem;color:#6b6680;text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-top:4px;}

    /* Phase header */
    .phase-hdr {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 18px 22px;
        background: rgba(22,22,35,0.7);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px 14px 0 0;
        margin-top: 18px;
    }
    .phase-icon {font-size:1.8rem;}
    .phase-info h4 {margin:0;font-size:1.1rem;font-weight:700;color:#f1f0f5;}
    .phase-info p {margin:0;font-size:.8rem;color:#a09cb0;}
    .phase-hrs {
        margin-left: auto;
        text-align: right;
    }
    .phase-hrs-val {font-size:1.3rem;font-weight:800;color:#6366f1;}
    .phase-hrs-lbl {font-size:.65rem;color:#6b6680;text-transform:uppercase;}

    /* Module row */
    .mod-row {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        padding: 16px 22px;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
        border-top: none;
        transition: background .2s;
    }
    .mod-row:last-child {border-radius: 0 0 14px 14px;}
    .mod-row:hover {background: rgba(255,255,255,0.04);}
    .mod-id {
        padding: 3px 9px;
        background: rgba(99,102,241,0.1);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 6px;
        font-size: .65rem;
        font-weight: 700;
        color: #818cf8;
        font-family: monospace;
        white-space: nowrap;
        margin-top: 2px;
    }
    .mod-info {flex:1;}
    .mod-title {font-size:.95rem;font-weight:600;color:#f1f0f5;margin-bottom:3px;}
    .mod-desc {font-size:.8rem;color:#a09cb0;margin-bottom:6px;line-height:1.5;}
    .mod-tags {display:flex;flex-wrap:wrap;gap:5px;}
    .tag {
        padding: 2px 9px;
        border-radius: 100px;
        font-size: .65rem;
        font-weight: 600;
    }
    .tag-skill {background:rgba(6,182,212,.1);color:#22d3ee;border:1px solid rgba(6,182,212,.2);}
    .tag-fmt {background:rgba(168,85,247,.1);color:#c084fc;border:1px solid rgba(168,85,247,.2);}
    .tag-saved {background:rgba(16,185,129,.1);color:#34d399;border:1px solid rgba(16,185,129,.2);}
    .tag-prereq {background:rgba(245,158,11,.1);color:#fbbf24;border:1px solid rgba(245,158,11,.2);}
    .mod-dur {text-align:right;white-space:nowrap;}
    .dur-val {font-size:1rem;font-weight:700;color:#f1f0f5;}
    .dur-lbl {font-size:.6rem;color:#6b6680;text-transform:uppercase;}
    .dur-saved {font-size:.7rem;color:#34d399;font-weight:600;}

    /* Gap item */
    .gap-item {
        background: rgba(22,22,35,0.7);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 10px;
    }
    .gap-hdr {display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;}
    .gap-skill {font-size:.95rem;font-weight:600;color:#f1f0f5;}
    .gap-sev {
        padding: 3px 10px;
        border-radius: 100px;
        font-size: .65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .5px;
    }
    .sev-critical {background:rgba(244,63,94,.1);color:#fb7185;border:1px solid rgba(244,63,94,.2);}
    .sev-important {background:rgba(245,158,11,.1);color:#fbbf24;border:1px solid rgba(245,158,11,.2);}
    .sev-nice_to_have {background:rgba(6,182,212,.1);color:#22d3ee;border:1px solid rgba(6,182,212,.2);}
    .gap-bar-wrap {margin-bottom:6px;}
    .gap-labels {display:flex;justify-content:space-between;font-size:.7rem;color:#6b6680;margin-bottom:4px;}
    .gap-bar {height:7px;background:#1a1a24;border-radius:4px;overflow:hidden;position:relative;}
    .gap-fill {height:100%;border-radius:4px;}
    .gap-mark {position:absolute;top:-2px;width:2px;height:11px;background:#f1f0f5;border-radius:1px;}
    .gap-transfer {font-size:.78rem;color:#34d399;margin-top:4px;}

    /* Skill chips */
    .chip {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 100px;
        font-size: .78rem;
        font-weight: 500;
        margin: 3px 3px;
    }
    .chip-default {background:rgba(99,102,241,.08);color:#c4b5fd;border:1px solid rgba(99,102,241,.15);}
    .chip-match {background:rgba(16,185,129,.08);color:#34d399;border:1px solid rgba(16,185,129,.15);}
    .chip-miss {background:rgba(244,63,94,.08);color:#fb7185;border:1px solid rgba(244,63,94,.15);}

    /* Section headers */
    .sec-badge {
        display: inline-block;
        padding: 5px 14px;
        background: rgba(99,102,241,0.1);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 100px;
        font-size: .72rem;
        font-weight: 600;
        color: #818cf8;
        text-transform: uppercase;
        letter-spacing: 1.3px;
        margin-bottom: 10px;
    }
    .sec-badge-green {
        background: rgba(16,185,129,0.1);
        border-color: rgba(16,185,129,0.2);
        color: #34d399;
    }
    .sec-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #f1f0f5;
        margin-bottom: 6px;
        letter-spacing: -0.02em;
    }
    .sec-sub {font-size:1rem;color:#a09cb0;margin-bottom:24px;}

    /* Dataset cards */
    .ds-grid {display:grid;grid-template-columns:1fr 1fr;gap:16px;}
    .ds-card {
        background: rgba(22,22,35,0.7);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 24px;
    }
    .ds-icon {font-size:1.8rem;margin-bottom:12px;}
    .ds-card h4 {font-size:1rem;font-weight:700;color:#f1f0f5;margin:0 0 6px;}
    .ds-card p {font-size:.85rem;color:#a09cb0;line-height:1.5;margin-bottom:12px;}
    .ds-link {font-size:.85rem;font-weight:600;color:#818cf8;text-decoration:none;}

    /* Footer */
    .footer {
        text-align: center;
        padding: 30px 0 20px;
        border-top: 1px solid rgba(255,255,255,0.06);
        margin-top: 40px;
    }
    .footer-brand {
        font-size: 1.1rem;
        font-weight: 700;
        background: linear-gradient(135deg,#6366f1,#a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .footer-txt {font-size:.8rem;color:#6b6680;}

    /* Streamlit overrides */
    .stTextArea textarea {
        background: rgba(0,0,0,0.3) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #f1f0f5 !important;
        border-radius: 12px !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextArea textarea:focus {
        border-color: #a855f7 !important;
        box-shadow: 0 0 0 3px rgba(168,85,247,0.1) !important;
    }
    .stFileUploader {
        background: rgba(22,22,35,0.7) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 14px !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(22,22,35,0.7);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #a09cb0;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg,#6366f1,#a855f7) !important;
        color: white !important;
    }
    div[data-testid="stMetric"] {
        background: rgba(22,22,35,0.7);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 16px;
    }
    div[data-testid="stMetric"] label {color: #6b6680 !important;}
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {color: #f1f0f5 !important;}

    @media (max-width:768px) {
        .hero-title {font-size:2rem;}
        .hero-stats {flex-direction:column;gap:16px;}
        .metric-grid {grid-template-columns:1fr 1fr;}
        .ds-grid {grid-template-columns:1fr;}
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HERO SECTION
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-badge"><span class="dot"></span> AI-Powered Learning Pathways</div>
    <div class="hero-title">Bridge the <span class="gradient-text">Skill Gap</span><br>with Adaptive Learning</div>
    <p class="hero-sub">Upload a resume and job description — our AI engine extracts skills, identifies gaps, and generates a personalized, time-optimized training roadmap.</p>
    <div class="hero-stats">
        <div class="stat-item"><span class="stat-val">270+</span><span class="stat-lbl">Skills Tracked</span></div>
        <div class="stat-item"><span class="stat-val">40+</span><span class="stat-lbl">Learning Modules</span></div>
        <div class="stat-item"><span class="stat-val">14</span><span class="stat-lbl">Skill Categories</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# UPLOAD SECTION
# ─────────────────────────────────────────────
st.markdown('<div class="sec-badge">ANALYZE</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-title">Upload & Analyze</div>', unsafe_allow_html=True)
st.markdown('<p class="sec-sub">Provide a resume and job description to generate your personalized pathway</p>', unsafe_allow_html=True)

col_resume, col_jd = st.columns(2)

with col_resume:
    st.markdown("""
    <div class="card-header"><span style="font-size:1.5rem;">📄</span><h3>Resume</h3></div>
    <p class="card-sub">Upload candidate's resume (PDF, DOCX, or TXT)</p>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["pdf", "docx", "txt"], label_visibility="collapsed")

with col_jd:
    st.markdown("""
    <div class="card-header"><span style="font-size:1.5rem;">📋</span><h3>Job Description</h3></div>
    <p class="card-sub">Paste target role requirements</p>
    """, unsafe_allow_html=True)
    jd_text = st.text_area(
        "",
        height=200,
        placeholder="Paste the full job description here...\n\nExample:\nSenior Software Engineer\n\nRequirements:\n- 5+ years of experience with Python\n- Strong knowledge of React and Node.js\n- Experience with AWS and Docker",
        label_visibility="collapsed",
    )

st.markdown("")

# ─────────────────────────────────────────────
# ANALYZE BUTTON
# ─────────────────────────────────────────────
col_l, col_btn, col_r = st.columns([1, 2, 1])
with col_btn:
    analyze_clicked = st.button(
        "🚀 Generate Learning Pathway",
        use_container_width=True,
        type="primary",
        disabled=not (uploaded_file and jd_text and len(jd_text.strip()) > 20),
    )

if analyze_clicked and uploaded_file and jd_text.strip():
    with st.spinner("🔍 Analyzing skills and generating your personalized pathway..."):
        try:
            # Save uploaded file to temp
            suffix = "." + uploaded_file.name.split(".")[-1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            # Pipeline
            resume_data = parse_resume(tmp_path)
            jd_data = parse_job_description(jd_text)
            resume_skills = extract_skills(resume_data["text"])
            jd_skills = extract_skills(jd_text)
            gap_analysis = analyze_gaps(
                resume_skills, jd_skills,
                resume_data["text"], jd_text,
                resume_data["metadata"],
            )
            pathway = generate_pathway(gap_analysis, resume_data["metadata"])

            # Cleanup
            os.unlink(tmp_path)

            # Store in session
            st.session_state["result"] = {
                "resume_skills": resume_skills,
                "jd_skills": jd_skills,
                "jd_data": jd_data,
                "gap_analysis": gap_analysis,
                "pathway": pathway,
                "metadata": resume_data["metadata"],
            }

        except Exception as e:
            os.unlink(tmp_path) if os.path.exists(tmp_path) else None
            st.error(f"❌ Error: {str(e)}")

# ─────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────
if "result" in st.session_state:
    r = st.session_state["result"]
    gap = r["gap_analysis"]["summary"]
    pw = r["pathway"]
    metrics = pw.get("metrics", {})

    st.markdown("---")
    st.markdown('<div class="sec-badge sec-badge-green">ANALYSIS COMPLETE</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">Your Personalized Pathway</div>', unsafe_allow_html=True)

    # ── Summary Cards ──
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card mc-match">
            <div class="metric-icon">✅</div>
            <div class="metric-val">{gap['match_percentage']}%</div>
            <div class="metric-lbl">Skills Match</div>
        </div>
        <div class="metric-card mc-gaps">
            <div class="metric-icon">⚠️</div>
            <div class="metric-val">{gap['skills_with_gaps']}</div>
            <div class="metric-lbl">Skill Gaps Found</div>
        </div>
        <div class="metric-card mc-hours">
            <div class="metric-icon">⏱️</div>
            <div class="metric-val">{pw.get('total_hours', 0)}h</div>
            <div class="metric-lbl">Training Hours</div>
        </div>
        <div class="metric-card mc-eff">
            <div class="metric-icon">🚀</div>
            <div class="metric-val">{pw.get('efficiency_score', 0)}%</div>
            <div class="metric-lbl">Efficiency vs Generic</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ──
    tab_pathway, tab_gaps, tab_skills, tab_metrics = st.tabs(
        ["🗺️ Learning Pathway", "📊 Skill Gaps", "🎯 Skills Overview", "📈 Metrics & Citations"]
    )

    # ── TAB: PATHWAY ──
    with tab_pathway:
        phases = pw.get("phases", [])
        if not phases:
            st.success("🎉 No training needed! The candidate meets all requirements.")
        else:
            # Summary bar
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
                    <div>
                        <strong style="color:#f1f0f5;">📋 Personalized Pathway Summary</strong><br>
                        <span style="font-size:.85rem;color:#a09cb0;">{pw['total_modules']} modules across {len(phases)} phases</span>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:1.4rem;font-weight:800;color:#818cf8;">{pw['total_hours']}h</div>
                        <div style="font-size:.7rem;color:#34d399;font-weight:600;">
                            {"%.1f" % pw['total_hours_saved']}h saved vs generic
                        </div>
                    </div>
                </div>
                <div class="gap-bar" style="margin-bottom:6px;">
                    <div class="gap-fill" style="width:{min(pw['total_hours']/max(pw.get('generic_curriculum_hours',1),1)*100,100):.1f}%;background:linear-gradient(90deg,#6366f1,#a855f7);border-radius:4px;"></div>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:.7rem;color:#6b6680;">
                    <span>Your pathway: {pw['total_hours']}h</span>
                    <span>Generic curriculum: {pw.get('generic_curriculum_hours',0)}h</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            for phase in phases:
                # Phase header
                st.markdown(f"""
                <div class="phase-hdr">
                    <div class="phase-icon">{phase['icon']}</div>
                    <div class="phase-info">
                        <h4>Phase {phase['id']}: {phase['name']}</h4>
                        <p>{phase['description']}</p>
                    </div>
                    <div class="phase-hrs">
                        <div class="phase-hrs-val">{phase['total_hours']}h</div>
                        <div class="phase-hrs-lbl">Total</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Modules
                for mod in phase["modules"]:
                    tags_html = ""
                    for sk in mod["skills_covered"]:
                        tags_html += f'<span class="tag tag-skill">{sk}</span>'
                    tags_html += f'<span class="tag tag-fmt">{mod["format"]}</span>'
                    if mod.get("is_prerequisite"):
                        tags_html += '<span class="tag tag-prereq">Prerequisite</span>'
                    if mod.get("transfer_applied"):
                        tags_html += f'<span class="tag tag-saved">⚡ {mod["time_saved"]}h saved</span>'

                    saved_html = f'<div class="dur-saved">was {mod["original_duration"]}h</div>' if mod.get("transfer_applied") else ""

                    st.markdown(f"""
                    <div class="mod-row">
                        <div class="mod-id">{mod['module_id']}</div>
                        <div class="mod-info">
                            <div class="mod-title">{mod['title']}</div>
                            <div class="mod-desc">{mod['description']}</div>
                            <div class="mod-tags">{tags_html}</div>
                        </div>
                        <div class="mod-dur">
                            <div class="dur-val">{mod['adjusted_duration']}h</div>
                            <div class="dur-lbl">Hours</div>
                            {saved_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # ── TAB: GAPS ──
    with tab_gaps:
        all_gaps = r["gap_analysis"]["gaps"]
        if not all_gaps:
            st.success("🎉 No skill gaps detected!")
        else:
            for g in all_gaps:
                sev_cls = f"sev-{g['severity']}"
                bar_color = "#fb7185" if g["severity"] == "critical" else "#fbbf24" if g["severity"] == "important" else "#22d3ee"
                cur_w = max(g["current_proficiency"], 2)
                transfer_html = f'<div class="gap-transfer">⚡ Transferable from: {", ".join(g["transferable_from"])}</div>' if g.get("has_transferable") else ""

                st.markdown(f"""
                <div class="gap-item">
                    <div class="gap-hdr">
                        <span class="gap-skill">{g['skill']}</span>
                        <span class="gap-sev {sev_cls}">{g['severity'].replace('_',' ')}</span>
                    </div>
                    <div class="gap-bar-wrap">
                        <div class="gap-labels">
                            <span>Current: {g['current_proficiency']}%</span>
                            <span>Required: {g['required_proficiency']}%</span>
                        </div>
                        <div class="gap-bar">
                            <div class="gap-fill" style="width:{cur_w}%;background:{bar_color};"></div>
                            <div class="gap-mark" style="left:{g['required_proficiency']}%"></div>
                        </div>
                    </div>
                    {transfer_html}
                </div>
                """, unsafe_allow_html=True)

    # ── TAB: SKILLS ──
    with tab_skills:
        col_res, col_jd2 = st.columns(2)
        matched_names = [m["skill"] for m in r["gap_analysis"]["matched_skills"]]
        gap_names = [g["skill"] for g in r["gap_analysis"]["gaps"]]

        with col_res:
            st.markdown(f"""
            <div class="glass-card">
                <div class="card-header"><span style="font-size:1.2rem;">📄</span><h3>Resume Skills</h3>
                <span style="margin-left:auto;padding:3px 10px;background:rgba(99,102,241,.1);border-radius:100px;font-size:.75rem;font-weight:700;color:#818cf8;">{r['resume_skills']['total_skills_found']}</span></div>
            """, unsafe_allow_html=True)
            for cat, skills in r["resume_skills"]["skill_categories"].items():
                chips = ""
                for s in skills:
                    cls = "chip-match" if s in matched_names else "chip-default"
                    chips += f'<span class="chip {cls}">{s}</span>'
                st.markdown(f"""
                <div style="margin-top:12px;">
                    <div style="font-size:.7rem;font-weight:700;color:#6b6680;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">{cat}</div>
                    <div>{chips}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_jd2:
            jd_cats = {}
            for s in r["jd_skills"]["found_skills"]:
                jd_cats.setdefault(s["category"], []).append(s["skill"])

            st.markdown(f"""
            <div class="glass-card">
                <div class="card-header"><span style="font-size:1.2rem;">📋</span><h3>Required Skills (JD)</h3>
                <span style="margin-left:auto;padding:3px 10px;background:rgba(99,102,241,.1);border-radius:100px;font-size:.75rem;font-weight:700;color:#818cf8;">{r['jd_skills']['total_skills_found']}</span></div>
            """, unsafe_allow_html=True)
            for cat, skills in jd_cats.items():
                chips = ""
                for s in skills:
                    cls = "chip-match" if s in matched_names else "chip-miss" if s in gap_names else "chip-default"
                    chips += f'<span class="chip {cls}">{s}</span>'
                st.markdown(f"""
                <div style="margin-top:12px;">
                    <div style="font-size:.7rem;font-weight:700;color:#6b6680;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">{cat}</div>
                    <div>{chips}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB: METRICS ──
    with tab_metrics:
        mc1, mc2 = st.columns(2)
        with mc1:
            pei = (metrics.get("pathway_efficiency_index", 0) * 100)
            st.markdown(f"""
            <div class="glass-card">
                <strong style="color:#f1f0f5;">📊 Pathway Efficiency Index</strong>
                <p style="font-size:.8rem;color:#a09cb0;margin:4px 0 12px;">Ratio of personalized pathway time to full generic curriculum. Lower is better.</p>
                <div style="font-size:2.5rem;font-weight:900;background:linear-gradient(135deg,#6366f1,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1;">{pei:.1f}%</div>
                <div style="margin-top:14px;">
                    <div style="display:flex;justify-content:space-between;font-size:.8rem;color:#a09cb0;margin-bottom:6px;">
                        <span>Your pathway</span><span>{pw.get('total_hours',0)}h / {pw.get('generic_curriculum_hours',0)}h</span>
                    </div>
                    <div class="gap-bar"><div class="gap-fill" style="width:{pei:.1f}%;background:linear-gradient(90deg,#6366f1,#a855f7);border-radius:4px;"></div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with mc2:
            pr = (metrics.get("personalization_ratio", 0) * 100)
            st.markdown(f"""
            <div class="glass-card">
                <strong style="color:#f1f0f5;">🎯 Personalization Ratio</strong>
                <p style="font-size:.8rem;color:#a09cb0;margin:4px 0 12px;">Fraction of total catalog modules selected. More selective = more personalized.</p>
                <div style="font-size:2.5rem;font-weight:900;background:linear-gradient(135deg,#6366f1,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1;">{pr:.1f}%</div>
                <div style="margin-top:14px;">
                    <div style="display:flex;justify-content:space-between;font-size:.8rem;color:#a09cb0;margin-bottom:6px;">
                        <span>Selected modules</span><span>{pw.get('total_modules',0)} of {round(pw.get('total_modules',1)/max(metrics.get('personalization_ratio',0.01),0.01))}</span>
                    </div>
                    <div class="gap-bar"><div class="gap-fill" style="width:{pr:.1f}%;background:linear-gradient(90deg,#6366f1,#a855f7);border-radius:4px;"></div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        mc3, mc4 = st.columns(2)
        with mc3:
            st.markdown(f"""
            <div class="glass-card">
                <strong style="color:#f1f0f5;">⚡ Gap Coverage</strong>
                <p style="font-size:.8rem;color:#a09cb0;margin:4px 0 12px;">Breakdown of skill gaps by severity level.</p>
                <div style="margin-top:10px;">
                    <div style="display:flex;justify-content:space-between;font-size:.8rem;margin-bottom:4px;"><span style="color:#fb7185;">Critical</span><span style="color:#a09cb0;">{gap['critical_gaps']} gaps</span></div>
                    <div class="gap-bar" style="margin-bottom:12px;"><div class="gap-fill" style="width:{gap['critical_gaps']/max(gap['skills_with_gaps'],1)*100:.0f}%;background:#fb7185;border-radius:4px;"></div></div>
                    <div style="display:flex;justify-content:space-between;font-size:.8rem;margin-bottom:4px;"><span style="color:#fbbf24;">Important</span><span style="color:#a09cb0;">{gap['important_gaps']} gaps</span></div>
                    <div class="gap-bar" style="margin-bottom:12px;"><div class="gap-fill" style="width:{gap['important_gaps']/max(gap['skills_with_gaps'],1)*100:.0f}%;background:#fbbf24;border-radius:4px;"></div></div>
                    <div style="display:flex;justify-content:space-between;font-size:.8rem;margin-bottom:4px;"><span style="color:#22d3ee;">Nice to Have</span><span style="color:#a09cb0;">{gap['nice_to_have_gaps']} gaps</span></div>
                    <div class="gap-bar"><div class="gap-fill" style="width:{gap['nice_to_have_gaps']/max(gap['skills_with_gaps'],1)*100:.0f}%;background:#22d3ee;border-radius:4px;"></div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with mc4:
            st.markdown(f"""
            <div class="glass-card">
                <strong style="color:#f1f0f5;">📈 Skill Extraction Stats</strong>
                <p style="font-size:.8rem;color:#a09cb0;margin:4px 0 12px;">NLP-based skill extraction summary.</p>
                <div style="margin-top:10px;">
                    <div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid rgba(255,255,255,.06);font-size:.85rem;">
                        <span style="color:#a09cb0;">Resume Skills</span><span style="font-weight:700;color:#f1f0f5;">{r['resume_skills']['total_skills_found']}</span></div>
                    <div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid rgba(255,255,255,.06);font-size:.85rem;">
                        <span style="color:#a09cb0;">JD Skills</span><span style="font-weight:700;color:#f1f0f5;">{r['jd_skills']['total_skills_found']}</span></div>
                    <div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid rgba(255,255,255,.06);font-size:.85rem;">
                        <span style="color:#a09cb0;">Skills Matched</span><span style="font-weight:700;color:#34d399;">{gap['skills_matched']}</span></div>
                    <div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid rgba(255,255,255,.06);font-size:.85rem;">
                        <span style="color:#a09cb0;">Match Rate</span><span style="font-weight:700;color:#818cf8;">{gap['match_percentage']}%</span></div>
                    <div style="display:flex;justify-content:space-between;padding:7px 0;font-size:.85rem;">
                        <span style="color:#a09cb0;">Avg Module Time</span><span style="font-weight:700;color:#f1f0f5;">{metrics.get('avg_time_per_module',0)}h</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Datasets
        st.markdown("")
        st.markdown(f"""
        <div class="glass-card">
            <strong style="color:#f1f0f5;">📚 Datasets & Citations</strong>
            <p style="font-size:.8rem;color:#a09cb0;margin:4px 0 14px;">All public datasets and open-source tools used.</p>
            <div class="ds-grid">
                <div class="ds-card">
                    <div class="ds-icon">🏛️</div>
                    <h4>O*NET Skills & Knowledge</h4>
                    <p>Industry-standard skill taxonomy from the U.S. Department of Labor.</p>
                    <a class="ds-link" href="https://www.onetcenter.org/db_releases.html" target="_blank">onetcenter.org →</a>
                </div>
                <div class="ds-card">
                    <div class="ds-icon">📊</div>
                    <h4>Kaggle Resume Dataset</h4>
                    <p>2,400+ resumes for validation of skill extraction accuracy.</p>
                    <a class="ds-link" href="https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset/data" target="_blank">kaggle.com →</a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <div class="footer-brand">🌉 SkillBridge</div>
    <div class="footer-txt">AI-Driven Adaptive Learning Engine for Corporate Onboarding</div>
</div>
""", unsafe_allow_html=True)
