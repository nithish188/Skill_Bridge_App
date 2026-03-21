"""
SkillBridge — AI-Driven Adaptive Learning Engine
Streamlit Application

Datasets Used:
- O*NET Skills & Knowledge (https://www.onetcenter.org/db_releases.html)
- Kaggle Resume Dataset (https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset/data)

All adaptive logic is original implementation.
"""
import os
import sys
import tempfile
import streamlit as st
import plotly.graph_objects as go
import math

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers.resume_parser import parse_resume
from parsers.jd_parser import parse_job_description
from engine.skill_extractor import extract_skills
from engine.gap_analyzer import analyze_gaps
from engine.pathway_generator import generate_pathway

# ──────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="SkillBridge — Adaptive Learning Engine",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# Custom CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* Global */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Hero */
    .hero-container {
        text-align: center;
        padding: 2rem 0 3rem;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 18px;
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 100px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #818cf8;
        letter-spacing: 1px;
        margin-bottom: 1rem;
    }
    .hero-badge .dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #10b981;
        animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 900;
        line-height: 1.1;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
    }
    .gradient-text {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-sub {
        font-size: 1.1rem;
        color: #9ca3af;
        max-width: 650px;
        margin: 0 auto 2rem;
        line-height: 1.7;
    }

    /* Stats Row */
    .stats-row {
        display: flex;
        justify-content: center;
        gap: 48px;
        margin-top: 1.5rem;
    }
    .stat-item { text-align: center; }
    .stat-val {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-lbl { font-size: 0.8rem; color: #6b7280; font-weight: 500; }

    /* Summary Cards */
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin: 1.5rem 0;
    }
    .summary-card {
        background: rgba(30, 30, 50, 0.5);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .summary-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
    }
    .card-match::after { background: #10b981; }
    .card-gaps::after  { background: #f59e0b; }
    .card-hours::after { background: #6366f1; }
    .card-eff::after   { background: #a855f7; }
    .card-icon { font-size: 1.4rem; margin-bottom: 4px; }
    .card-val  { font-size: 1.8rem; font-weight: 800; }
    .card-lbl  { font-size: 0.7rem; color: #6b7280; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }

    /* Phase cards */
    .phase-header {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 18px 22px;
        background: rgba(30, 30, 50, 0.6);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px 14px 0 0;
        margin-top: 20px;
    }
    .phase-icon { font-size: 1.8rem; }
    .phase-name { font-size: 1.1rem; font-weight: 700; }
    .phase-desc { font-size: 0.8rem; color: #9ca3af; }
    .phase-hrs  { margin-left: auto; text-align: right; }
    .phase-hrs-val { font-size: 1.3rem; font-weight: 800; color: #818cf8; }
    .phase-hrs-lbl { font-size: 0.65rem; color: #6b7280; text-transform: uppercase; }

    .module-row {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        padding: 16px 22px;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
        border-top: none;
        transition: background 0.2s;
    }
    .module-row:last-child { border-radius: 0 0 14px 14px; }
    .module-row:hover { background: rgba(255,255,255,0.04); }
    .mod-id {
        padding: 3px 10px;
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 6px;
        font-size: 0.65rem;
        font-weight: 700;
        color: #818cf8;
        font-family: monospace;
        white-space: nowrap;
        margin-top: 2px;
    }
    .mod-info { flex: 1; }
    .mod-title { font-weight: 600; font-size: 0.95rem; margin-bottom: 3px; }
    .mod-desc  { font-size: 0.8rem; color: #9ca3af; margin-bottom: 6px; }
    .mod-tags  { display: flex; flex-wrap: wrap; gap: 5px; }
    .tag {
        padding: 2px 10px;
        border-radius: 100px;
        font-size: 0.65rem;
        font-weight: 600;
    }
    .tag-skill  { background: rgba(6,182,212,0.1);  color: #06b6d4; border: 1px solid rgba(6,182,212,0.2); }
    .tag-format { background: rgba(168,85,247,0.1); color: #a855f7; border: 1px solid rgba(168,85,247,0.2); }
    .tag-prereq { background: rgba(245,158,11,0.1); color: #f59e0b; border: 1px solid rgba(245,158,11,0.2); }
    .tag-saved  { background: rgba(16,185,129,0.1); color: #10b981; border: 1px solid rgba(16,185,129,0.2); }
    .mod-dur { text-align: right; white-space: nowrap; }
    .dur-val { font-size: 1.05rem; font-weight: 700; }
    .dur-lbl { font-size: 0.65rem; color: #6b7280; text-transform: uppercase; }
    .dur-saved { font-size: 0.7rem; color: #10b981; font-weight: 600; }

    /* Gap item */
    .gap-item {
        background: rgba(30,30,50,0.5);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 10px;
    }
    .gap-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
    .gap-name   { font-weight: 600; }
    .severity-badge {
        padding: 3px 12px;
        border-radius: 100px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .sev-critical  { background: rgba(244,63,94,0.1);  color: #f43f5e; border: 1px solid rgba(244,63,94,0.2); }
    .sev-important { background: rgba(245,158,11,0.1); color: #f59e0b; border: 1px solid rgba(245,158,11,0.2); }
    .sev-nice      { background: rgba(6,182,212,0.1);  color: #06b6d4; border: 1px solid rgba(6,182,212,0.2); }
    .gap-bar-wrap { margin-bottom: 6px; }
    .gap-labels { display: flex; justify-content: space-between; font-size: 0.7rem; color: #6b7280; margin-bottom: 4px; }
    .gap-bar { height: 7px; background: rgba(255,255,255,0.06); border-radius: 4px; overflow: hidden; position: relative; }
    .gap-fill { height: 100%; border-radius: 4px; }
    .gap-marker { position: absolute; top: -2px; width: 3px; height: 11px; background: white; border-radius: 2px; }
    .gap-transfer { font-size: 0.75rem; color: #10b981; }

    /* Skill chips */
    .chip {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 100px;
        font-size: 0.78rem;
        font-weight: 500;
        margin: 3px;
    }
    .chip-default  { background: rgba(99,102,241,0.08); color: #c4b5fd; border: 1px solid rgba(99,102,241,0.15); }
    .chip-matched  { background: rgba(16,185,129,0.08); color: #10b981; border: 1px solid rgba(16,185,129,0.15); }
    .chip-missing  { background: rgba(244,63,94,0.08);  color: #f43f5e; border: 1px solid rgba(244,63,94,0.15); }

    /* Dataset card */
    .ds-card {
        background: rgba(30,30,50,0.5);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 24px;
        height: 100%;
    }
    .ds-icon { font-size: 1.8rem; margin-bottom: 12px; }
    .ds-card h4 { margin-bottom: 6px; }
    .ds-card p  { font-size: 0.85rem; color: #9ca3af; line-height: 1.5; }
    .ds-link    { font-size: 0.85rem; color: #818cf8; font-weight: 600; text-decoration: none; }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem;
        border-top: 1px solid rgba(255,255,255,0.06);
        margin-top: 3rem;
    }
    .footer p { color: #6b7280; font-size: 0.85rem; }

    /* Responsive */
    @media (max-width: 768px) {
        .hero-title { font-size: 2rem; }
        .summary-grid { grid-template-columns: repeat(2, 1fr); }
        .stats-row { flex-direction: column; gap: 16px; }
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Hero Section
# ──────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-badge"><span class="dot"></span> AI-Powered Learning Pathways</div>
    <div class="hero-title">Bridge the <span class="gradient-text">Skill Gap</span><br>with Adaptive Learning</div>
    <p class="hero-sub">Upload a resume and job description — our AI engine extracts skills,
    identifies gaps, and generates a personalized, time-optimized training roadmap.</p>
    <div class="stats-row">
        <div class="stat-item"><div class="stat-val">270+</div><div class="stat-lbl">Skills Tracked</div></div>
        <div class="stat-item"><div class="stat-val">40+</div><div class="stat-lbl">Learning Modules</div></div>
        <div class="stat-item"><div class="stat-val">14</div><div class="stat-lbl">Skill Categories</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Upload Section
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📤 Upload & Analyze")
st.caption("Provide a resume and job description to generate your personalized pathway")

col_resume, col_jd = st.columns(2)

with col_resume:
    st.markdown("**📄 Resume**")
    uploaded_file = st.file_uploader(
        "Upload candidate's resume",
        type=["pdf", "docx", "txt"],
        help="PDF, DOCX or TXT — max 16 MB"
    )

with col_jd:
    st.markdown("**📋 Job Description**")
    jd_text = st.text_area(
        "Paste target role requirements",
        height=200,
        placeholder="Paste the full job description here...\n\nExample:\nSenior Software Engineer\n\nRequirements:\n- 5+ years of experience with Python\n- Strong knowledge of React and Node.js\n- Experience with AWS and Docker",
    )

# ──────────────────────────────────────────────
# Analysis
# ──────────────────────────────────────────────
ready = uploaded_file is not None and len(jd_text.strip()) > 20
analyze_btn = st.button(
    "🚀 Generate Learning Pathway",
    disabled=not ready,
    use_container_width=True,
    type="primary",
)

if analyze_btn and ready:
    with st.spinner("Analyzing..."):
        # Save uploaded file to temp
        suffix = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        try:
            progress = st.progress(0, text="Parsing resume...")
            resume_data = parse_resume(tmp_path)
            progress.progress(15, text="Extracting skills from resume...")

            jd_data = parse_job_description(jd_text)
            progress.progress(30, text="Analyzing job description...")

            resume_skills = extract_skills(resume_data["text"])
            jd_skills = extract_skills(jd_text)
            progress.progress(50, text="Identifying skill gaps...")

            gap_analysis = analyze_gaps(
                resume_skills, jd_skills,
                resume_data["text"], jd_text,
                resume_data["metadata"]
            )
            progress.progress(70, text="Generating adaptive pathway...")

            pathway = generate_pathway(gap_analysis, resume_data["metadata"])
            progress.progress(100, text="Done!")

            # Store results in session
            st.session_state["results"] = {
                "resume_skills": resume_skills,
                "jd_skills": jd_skills,
                "jd_data": jd_data,
                "gap_analysis": gap_analysis,
                "pathway": pathway,
                "metadata": resume_data["metadata"],
            }

        except Exception as e:
            st.error(f"❌ Error: {e}")
        finally:
            os.unlink(tmp_path)

# ──────────────────────────────────────────────
# Results
# ──────────────────────────────────────────────
if "results" in st.session_state:
    r = st.session_state["results"]
    gap = r["gap_analysis"]["summary"]
    pw = r["pathway"]
    metrics = pw.get("metrics", {})

    st.markdown("---")
    st.markdown("### ✅ Analysis Complete — Your Personalized Pathway")

    # Summary cards
    st.markdown(f"""
    <div class="summary-grid">
        <div class="summary-card card-match">
            <div class="card-icon">✅</div>
            <div class="card-val">{gap['match_percentage']}%</div>
            <div class="card-lbl">Skills Match</div>
        </div>
        <div class="summary-card card-gaps">
            <div class="card-icon">⚠️</div>
            <div class="card-val">{gap['skills_with_gaps']}</div>
            <div class="card-lbl">Skill Gaps</div>
        </div>
        <div class="summary-card card-hours">
            <div class="card-icon">⏱️</div>
            <div class="card-val">{pw.get('total_hours', 0)}h</div>
            <div class="card-lbl">Training Hours</div>
        </div>
        <div class="summary-card card-eff">
            <div class="card-icon">🚀</div>
            <div class="card-val">{pw.get('efficiency_score', 0)}%</div>
            <div class="card-lbl">Efficiency vs Generic</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tab_pathway, tab_gaps, tab_skills, tab_metrics = st.tabs([
        "🗺️ Learning Pathway", "📊 Skill Gaps", "🎯 Skills Overview", "📈 Metrics"
    ])

    # ── TAB: Pathway ──
    with tab_pathway:
        phases = pw.get("phases", [])
        if not phases:
            st.success("🎉 No training needed! The candidate meets all requirements.")
        else:
            # Summary bar
            st.markdown(f"""
            **📋 Personalized Pathway Summary** — {pw['total_modules']} modules across {len(phases)} phases
            """)
            cols = st.columns([3, 1])
            with cols[0]:
                st.progress(
                    min(pw["total_hours"] / max(pw.get("generic_curriculum_hours", 1), 1), 1.0),
                    text=f"Your pathway: **{pw['total_hours']}h** (generic: {pw.get('generic_curriculum_hours', 0)}h)"
                )
            with cols[1]:
                saved = pw.get("total_hours_saved", 0)
                if saved > 0:
                    st.metric("Time Saved", f"{saved}h")

            # Phases
            for phase in phases:
                # Phase header
                st.markdown(f"""
                <div class="phase-header">
                    <div class="phase-icon">{phase['icon']}</div>
                    <div>
                        <div class="phase-name">Phase {phase['id']}: {phase['name']}</div>
                        <div class="phase-desc">{phase['description']}</div>
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
                    for s in mod["skills_covered"]:
                        tags_html += f'<span class="tag tag-skill">{s}</span>'
                    tags_html += f'<span class="tag tag-format">{mod["format"]}</span>'
                    if mod.get("is_prerequisite"):
                        tags_html += '<span class="tag tag-prereq">Prerequisite</span>'
                    if mod.get("transfer_applied"):
                        tags_html += f'<span class="tag tag-saved">⚡ {mod["time_saved"]}h saved</span>'

                    saved_html = f'<div class="dur-saved">was {mod["original_duration"]}h</div>' if mod.get("transfer_applied") else ""

                    st.markdown(f"""
                    <div class="module-row">
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

    # ── TAB: Gaps ──
    with tab_gaps:
        gaps_list = r["gap_analysis"]["gaps"]
        if not gaps_list:
            st.success("No skill gaps detected! 🎉")
        else:
            col_chart, col_list = st.columns([1, 1])

            with col_chart:
                # Radar chart with Plotly
                cat_gaps = r["gap_analysis"]["category_gaps"]
                if cat_gaps:
                    categories = list(cat_gaps.keys())
                    values = [min(cat_gaps[c]["total_gap"] / cat_gaps[c]["count"] / 100, 1) for c in categories]
                    values.append(values[0])  # close the polygon
                    categories.append(categories[0])

                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        fillcolor='rgba(244, 63, 94, 0.15)',
                        line=dict(color='#f43f5e', width=2),
                        marker=dict(size=6, color='#f43f5e'),
                        name='Skill Gaps'
                    ))
                    fig.update_layout(
                        polar=dict(
                            bgcolor='rgba(0,0,0,0)',
                            radialaxis=dict(visible=True, range=[0, 1], showticklabels=False, gridcolor='rgba(255,255,255,0.06)'),
                            angularaxis=dict(gridcolor='rgba(255,255,255,0.06)')
                        ),
                        showlegend=False,
                        title=dict(text="Skill Gap Distribution", font=dict(size=14)),
                        margin=dict(t=60, b=40, l=60, r=60),
                        height=400,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#9ca3af'),
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with col_list:
                for g in gaps_list:
                    sev_cls = "sev-critical" if g["severity"] == "critical" else "sev-important" if g["severity"] == "important" else "sev-nice"
                    bar_color = "#f43f5e" if g["severity"] == "critical" else "#f59e0b" if g["severity"] == "important" else "#06b6d4"
                    cur = max(g["current_proficiency"], 2)
                    transfer_html = f'<div class="gap-transfer">⚡ Transferable from: {", ".join(g["transferable_from"])}</div>' if g.get("has_transferable") else ""

                    st.markdown(f"""
                    <div class="gap-item">
                        <div class="gap-header">
                            <span class="gap-name">{g['skill']}</span>
                            <span class="severity-badge {sev_cls}">{g['severity'].replace('_', ' ')}</span>
                        </div>
                        <div class="gap-bar-wrap">
                            <div class="gap-labels">
                                <span>Current: {g['current_proficiency']}%</span>
                                <span>Required: {g['required_proficiency']}%</span>
                            </div>
                            <div class="gap-bar">
                                <div class="gap-fill" style="width:{cur}%;background:{bar_color};"></div>
                                <div class="gap-marker" style="left:{g['required_proficiency']}%"></div>
                            </div>
                        </div>
                        {transfer_html}
                    </div>
                    """, unsafe_allow_html=True)

    # ── TAB: Skills ──
    with tab_skills:
        col_r, col_j = st.columns(2)

        with col_r:
            st.markdown(f"**📄 Resume Skills** ({r['resume_skills']['total_skills_found']})")
            matched_names = [m["skill"] for m in r["gap_analysis"]["matched_skills"]]
            for cat, skills in r["resume_skills"]["skill_categories"].items():
                st.caption(cat.upper())
                chips = ""
                for s in skills:
                    cls = "chip-matched" if s in matched_names else "chip-default"
                    chips += f'<span class="chip {cls}">{s}</span>'
                st.markdown(chips, unsafe_allow_html=True)

        with col_j:
            st.markdown(f"**📋 Required Skills — JD** ({r['jd_skills']['total_skills_found']})")
            gap_names = [g["skill"] for g in r["gap_analysis"]["gaps"]]
            jd_cats = {}
            for s in r["jd_skills"]["found_skills"]:
                jd_cats.setdefault(s["category"], []).append(s["skill"])
            for cat, skills in jd_cats.items():
                st.caption(cat.upper())
                chips = ""
                for s in skills:
                    cls = "chip-matched" if s in matched_names else "chip-missing" if s in gap_names else "chip-default"
                    chips += f'<span class="chip {cls}">{s}</span>'
                st.markdown(chips, unsafe_allow_html=True)

    # ── TAB: Metrics ──
    with tab_metrics:
        mc1, mc2 = st.columns(2)
        with mc1:
            pei = metrics.get("pathway_efficiency_index", 0)
            st.markdown("**📊 Pathway Efficiency Index**")
            st.caption("Ratio of personalized pathway to generic curriculum. Lower = better.")
            st.metric("", f"{(pei * 100):.1f}%")
            st.progress(min(pei, 1.0), text=f"{pw.get('total_hours', 0)}h / {pw.get('generic_curriculum_hours', 0)}h")

        with mc2:
            pr = metrics.get("personalization_ratio", 0)
            st.markdown("**🎯 Personalization Ratio**")
            st.caption("Fraction of catalog selected. More selective = more personalized.")
            st.metric("", f"{(pr * 100):.1f}%")
            total_catalog = round(pw.get("total_modules", 1) / max(pr, 0.01))
            st.progress(min(pr, 1.0), text=f"{pw.get('total_modules', 0)} of {total_catalog} modules")

        mc3, mc4 = st.columns(2)
        with mc3:
            st.markdown("**⚡ Gap Coverage**")
            st.caption("Breakdown by severity level.")
            for sev, color, count in [
                ("Critical", "#f43f5e", gap["critical_gaps"]),
                ("Important", "#f59e0b", gap["important_gaps"]),
                ("Nice to Have", "#06b6d4", gap["nice_to_have_gaps"]),
            ]:
                st.markdown(f"<span style='color:{color};font-weight:600'>{sev}</span>: {count} gaps", unsafe_allow_html=True)
                st.progress(count / max(gap["skills_with_gaps"], 1))

        with mc4:
            st.markdown("**📈 Extraction Stats**")
            st.caption("NLP-based skill extraction results.")
            data_rows = {
                "Resume Skills": r["resume_skills"]["total_skills_found"],
                "JD Skills": r["jd_skills"]["total_skills_found"],
                "Skills Matched": gap["skills_matched"],
                "Match Rate": f"{gap['match_percentage']}%",
                "Avg Module Time": f"{metrics.get('avg_time_per_module', 0)}h",
            }
            for label, val in data_rows.items():
                st.markdown(f"**{label}:** {val}")

# ──────────────────────────────────────────────
# Datasets & Models Section
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📚 Datasets & Models")
st.caption("Full disclosure of all data sources and models used")

ds1, ds2, ds3, ds4 = st.columns(4)
with ds1:
    st.markdown("""
    <div class="ds-card">
        <div class="ds-icon">🏛️</div>
        <h4>O*NET Skills</h4>
        <p>Industry-standard taxonomy from the U.S. Dept of Labor. 270+ skills.</p>
        <a class="ds-link" href="https://www.onetcenter.org/db_releases.html" target="_blank">onetcenter.org →</a>
    </div>
    """, unsafe_allow_html=True)
with ds2:
    st.markdown("""
    <div class="ds-card">
        <div class="ds-icon">📊</div>
        <h4>Kaggle Resumes</h4>
        <p>2,400+ resumes for validation and testing of extraction accuracy.</p>
        <a class="ds-link" href="https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset/data" target="_blank">kaggle.com →</a>
    </div>
    """, unsafe_allow_html=True)
with ds3:
    st.markdown("""
    <div class="ds-card">
        <div class="ds-icon">🤖</div>
        <h4>Custom NLP</h4>
        <p>Taxonomy-based matching with confidence scoring. No external models needed.</p>
        <span class="ds-link">Original Pipeline</span>
    </div>
    """, unsafe_allow_html=True)
with ds4:
    st.markdown("""
    <div class="ds-card">
        <div class="ds-icon">⚙️</div>
        <h4>Adaptive Logic</h4>
        <p>Weighted scoring: gap severity, prerequisites, transferable skills, role priority.</p>
        <span class="ds-link">Original Algorithm</span>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>🌉 <strong>SkillBridge</strong> — AI-Driven Adaptive Learning Engine for Corporate Onboarding</p>
</div>
""", unsafe_allow_html=True)
