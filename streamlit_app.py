"""
SkillBridge — AI-Driven Adaptive Learning Engine
Streamlit App — Identical dashboard to the Flask version.
Renders the exact same HTML/CSS/JS results as the Flask app.
"""
import streamlit as st
import streamlit.components.v1 as components
import os
import json
import tempfile

# Fix imports for deployed env
import sys
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

# ─── Inject Custom CSS to Match the Flask Dark Theme ───
st.markdown("""
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    div[data-testid="stToolbar"] {display: none;}
    div[data-testid="stDecoration"] {display: none;}

    /* Dark background matching Flask */
    .stApp {
        background: #0a0a0f;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Style all text */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div {
        color: #f1f0f5;
    }

    /* Style file uploader */
    div[data-testid="stFileUploader"] {
        background: rgba(22, 22, 35, 0.7);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 20px;
    }
    div[data-testid="stFileUploader"] label {
        color: #a09cb0 !important;
    }
    div[data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #6366f1, #a855f7) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
    }
    div[data-testid="stFileUploader"] section {
        background: rgba(0,0,0,0.3);
        border: 2px dashed rgba(255,255,255,0.1);
        border-radius: 12px;
    }

    /* Style text area */
    div[data-testid="stTextArea"] textarea {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        color: #f1f0f5 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #a855f7 !important;
        box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.1) !important;
    }
    div[data-testid="stTextArea"] label {
        color: #a09cb0 !important;
    }

    /* Style button */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #a855f7) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 40px !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        width: 100%;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        box-shadow: 0 6px 30px rgba(99, 102, 241, 0.5) !important;
        transform: translateY(-1px);
    }
    .stButton > button:disabled {
        opacity: 0.4 !important;
    }

    /* Style columns gaps */
    div[data-testid="stHorizontalBlock"] {
        gap: 24px;
    }

    /* Style spinners */
    .stSpinner > div {
        border-top-color: #6366f1 !important;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(22, 22, 35, 0.7);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #a09cb0;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #a855f7) !important;
        color: #fff !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 24px;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(22, 22, 35, 0.7) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 12px !important;
        color: #f1f0f5 !important;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: rgba(22, 22, 35, 0.7);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 20px;
    }
    div[data-testid="stMetric"] label {
        color: #a09cb0 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #f1f0f5 !important;
        font-weight: 800 !important;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #111118; }
    ::-webkit-scrollbar-thumb { background: #6366f1; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


def render_hero():
    """Render the hero section matching Flask UI."""
    st.markdown("""
    <div style="text-align:center; padding: 40px 0 20px;">
        <div style="display:inline-flex;align-items:center;gap:8px;padding:8px 20px;background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.15);border-radius:100px;font-size:0.85rem;font-weight:500;color:#c4b5fd;margin-bottom:28px;">
            <span style="width:8px;height:8px;border-radius:50%;background:#10b981;display:inline-block;"></span>
            AI-Powered Learning Pathways
        </div>
        <h1 style="font-size:3.2rem;font-weight:900;line-height:1.1;margin-bottom:20px;letter-spacing:-0.03em;font-family:'Inter',sans-serif;">
            Bridge the <span style="background:linear-gradient(135deg,#6366f1 0%,#a855f7 50%,#ec4899 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Skill Gap</span><br>
            with Adaptive Learning
        </h1>
        <p style="font-size:1.15rem;color:#a09cb0;line-height:1.7;max-width:700px;margin:0 auto 30px;">
            Upload a resume and job description — our AI engine extracts skills,
            identifies gaps, and generates a personalized, time-optimized training roadmap.
        </p>
        <div style="display:flex;justify-content:center;gap:48px;margin-top:30px;">
            <div style="text-align:center;">
                <span style="font-size:2rem;font-weight:800;background:linear-gradient(135deg,#6366f1,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">270+</span><br>
                <span style="font-size:0.85rem;color:#6b6680;font-weight:500;">Skills Tracked</span>
            </div>
            <div style="text-align:center;">
                <span style="font-size:2rem;font-weight:800;background:linear-gradient(135deg,#6366f1,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">40+</span><br>
                <span style="font-size:0.85rem;color:#6b6680;font-weight:500;">Learning Modules</span>
            </div>
            <div style="text-align:center;">
                <span style="font-size:2rem;font-weight:800;background:linear-gradient(135deg,#6366f1,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">14</span><br>
                <span style="font-size:0.85rem;color:#6b6680;font-weight:500;">Skill Categories</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_summary_cards(gap_summary, pathway):
    """Render summary metric cards."""
    c1, c2, c3, c4 = st.columns(4)

    def card(col, icon, value, label, color):
        col.markdown(f"""
        <div style="background:rgba(22,22,35,0.7);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:24px;text-align:center;border-top:3px solid {color};">
            <div style="font-size:1.5rem;margin-bottom:8px;">{icon}</div>
            <div style="font-size:2rem;font-weight:800;margin-bottom:4px;color:#f1f0f5;">{value}</div>
            <div style="font-size:0.8rem;color:#6b6680;text-transform:uppercase;letter-spacing:1px;font-weight:600;">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    card(c1, "✅", f"{gap_summary['match_percentage']}%", "Skills Match", "#10b981")
    card(c2, "⚠️", str(gap_summary['skills_with_gaps']), "Skill Gaps Found", "#f59e0b")
    card(c3, "⏱️", f"{pathway.get('total_hours', 0)}h", "Training Hours", "#6366f1")
    card(c4, "🚀", f"{pathway.get('efficiency_score', 0)}%", "Efficiency vs Generic", "#a855f7")


def render_pathway_html(pathway):
    """Generate the exact same pathway HTML as the Flask app."""
    if not pathway.get("phases"):
        return f'<div style="text-align:center;padding:48px;background:rgba(22,22,35,0.7);border:1px solid rgba(255,255,255,0.06);border-radius:16px;"><h3 style="color:#f1f0f5;">🎉 No Training Needed!</h3><p style="color:#a09cb0;">{pathway.get("message", "Candidate meets all requirements.")}</p></div>'

    html = f"""
    <div style="background:rgba(22,22,35,0.7);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:24px;margin-bottom:24px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
            <div>
                <h3 style="color:#f1f0f5;margin:0;font-family:'Inter',sans-serif;">📋 Personalized Pathway Summary</h3>
                <p style="color:#a09cb0;margin:4px 0 0;font-size:0.9rem;">{pathway['total_modules']} modules across {len(pathway['phases'])} phases</p>
            </div>
            <div style="text-align:right;">
                <div style="font-size:1.6rem;font-weight:800;color:#6366f1;">{pathway['total_hours']}h</div>
                <div style="font-size:0.75rem;color:#10b981;font-weight:600;">
                    {"%.1fh saved vs generic" % pathway['total_hours_saved'] if pathway.get('total_hours_saved', 0) > 0 else "Optimized pathway"}
                </div>
            </div>
        </div>
        <div style="height:10px;background:#1a1a24;border-radius:5px;overflow:hidden;margin-bottom:8px;">
            <div style="height:100%;width:{min((pathway['total_hours']/max(pathway.get('generic_curriculum_hours',1),1))*100, 100):.1f}%;background:linear-gradient(135deg,#6366f1,#a855f7);border-radius:5px;"></div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#6b6680;">
            <span>Your pathway: {pathway['total_hours']}h</span>
            <span>Generic curriculum: {pathway.get('generic_curriculum_hours', 0)}h</span>
        </div>
    </div>
    """

    for phase in pathway["phases"]:
        html += f"""
        <div style="margin-bottom:24px;">
            <div style="display:flex;align-items:center;gap:16px;padding:20px 24px;background:rgba(22,22,35,0.7);border:1px solid rgba(255,255,255,0.06);border-radius:16px 16px 0 0;">
                <div style="font-size:2rem;">{phase['icon']}</div>
                <div style="flex:1;">
                    <h3 style="margin:0;font-size:1.2rem;font-weight:700;color:#f1f0f5;font-family:'Inter',sans-serif;">Phase {phase['id']}: {phase['name']}</h3>
                    <p style="margin:2px 0 0;font-size:0.85rem;color:#a09cb0;">{phase['description']}</p>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.4rem;font-weight:800;color:#6366f1;">{phase['total_hours']}h</div>
                    <div style="font-size:0.75rem;color:#6b6680;text-transform:uppercase;">Total</div>
                </div>
            </div>
            <div style="border:1px solid rgba(255,255,255,0.06);border-top:none;border-radius:0 0 16px 16px;overflow:hidden;">
        """
        for mod in phase["modules"]:
            tags = ""
            for s in mod["skills_covered"]:
                tags += f'<span style="padding:3px 10px;border-radius:100px;font-size:0.7rem;font-weight:600;background:rgba(6,182,212,0.1);color:#06b6d4;border:1px solid rgba(6,182,212,0.2);margin-right:4px;">{s}</span>'
            tags += f'<span style="padding:3px 10px;border-radius:100px;font-size:0.7rem;font-weight:600;background:rgba(168,85,247,0.1);color:#a855f7;border:1px solid rgba(168,85,247,0.2);margin-right:4px;">{mod["format"]}</span>'
            if mod.get("is_prerequisite"):
                tags += '<span style="padding:3px 10px;border-radius:100px;font-size:0.7rem;font-weight:600;background:rgba(245,158,11,0.1);color:#f59e0b;border:1px solid rgba(245,158,11,0.2);margin-right:4px;">Prerequisite</span>'
            if mod.get("transfer_applied"):
                tags += f'<span style="padding:3px 10px;border-radius:100px;font-size:0.7rem;font-weight:600;background:rgba(16,185,129,0.1);color:#10b981;border:1px solid rgba(16,185,129,0.2);">⚡ {mod["time_saved"]}h saved</span>'

            saved_html = f'<div style="font-size:0.75rem;color:#10b981;font-weight:600;">was {mod["original_duration"]}h</div>' if mod.get("transfer_applied") else ""

            html += f"""
                <div style="display:flex;align-items:flex-start;gap:16px;padding:20px 24px;background:rgba(255,255,255,0.03);border-bottom:1px solid rgba(255,255,255,0.06);">
                    <div style="padding:4px 10px;background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.2);border-radius:6px;font-size:0.7rem;font-weight:700;color:#6366f1;font-family:'JetBrains Mono',monospace;white-space:nowrap;margin-top:2px;">{mod["module_id"]}</div>
                    <div style="flex:1;">
                        <div style="font-size:1rem;font-weight:600;color:#f1f0f5;margin-bottom:4px;">{mod["title"]}</div>
                        <div style="font-size:0.85rem;color:#a09cb0;margin-bottom:8px;line-height:1.5;">{mod["description"]}</div>
                        <div style="display:flex;flex-wrap:wrap;gap:4px;">{tags}</div>
                    </div>
                    <div style="text-align:right;white-space:nowrap;">
                        <div style="font-size:1.1rem;font-weight:700;color:#f1f0f5;">{mod["adjusted_duration"]}h</div>
                        <div style="font-size:0.7rem;color:#6b6680;text-transform:uppercase;">Hours</div>
                        {saved_html}
                    </div>
                </div>
            """
        html += "</div></div>"

    return html


def render_gaps_html(gap_analysis):
    """Generate the exact same gaps HTML as the Flask app."""
    gaps = gap_analysis["gaps"]
    if not gaps:
        return '<div style="text-align:center;padding:32px;background:rgba(22,22,35,0.7);border-radius:12px;"><p style="color:#10b981;">No skill gaps detected! 🎉</p></div>'

    html = ""
    for gap in gaps:
        bar_color = "#f43f5e" if gap["severity"] == "critical" else "#f59e0b" if gap["severity"] == "important" else "#06b6d4"
        sev_bg = "rgba(244,63,94,0.1)" if gap["severity"] == "critical" else "rgba(245,158,11,0.1)" if gap["severity"] == "important" else "rgba(6,182,212,0.1)"
        sev_border = "rgba(244,63,94,0.2)" if gap["severity"] == "critical" else "rgba(245,158,11,0.2)" if gap["severity"] == "important" else "rgba(6,182,212,0.2)"
        current_w = max(gap["current_proficiency"], 2)

        transfer_html = ""
        if gap.get("has_transferable"):
            transfer_html = f'<div style="font-size:0.8rem;color:#10b981;margin-top:8px;">⚡ Transferable from: {", ".join(gap["transferable_from"])}</div>'

        html += f"""
        <div style="background:rgba(22,22,35,0.7);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:20px;margin-bottom:12px;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                <span style="font-size:1rem;font-weight:600;color:#f1f0f5;">{gap["skill"]}</span>
                <span style="padding:4px 12px;border-radius:100px;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;background:{sev_bg};color:{bar_color};border:1px solid {sev_border};">{gap["severity"].replace("_"," ")}</span>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#6b6680;margin-bottom:6px;">
                <span>Current: {gap["current_proficiency"]}%</span>
                <span>Required: {gap["required_proficiency"]}%</span>
            </div>
            <div style="height:8px;background:#1a1a24;border-radius:4px;overflow:hidden;position:relative;">
                <div style="height:100%;width:{current_w}%;background:{bar_color};border-radius:4px;"></div>
                <div style="position:absolute;top:-2px;left:{gap["required_proficiency"]}%;width:3px;height:12px;background:#f1f0f5;border-radius:2px;"></div>
            </div>
            {transfer_html}
        </div>
        """
    return html


def render_skills_html(data):
    """Generate skills comparison HTML."""
    resume_cats = data["resume_analysis"]["skill_categories"]
    jd_skills = data["jd_analysis"]["skills"]
    matched = [m["skill"] for m in data["gap_analysis"]["matched_skills"]]
    gap_skills = [g["skill"] for g in data["gap_analysis"]["gaps"]]

    html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">'

    # Resume panel
    html += '<div style="background:rgba(22,22,35,0.7);border:1px solid rgba(255,255,255,0.06);border-radius:16px;overflow:hidden;">'
    html += f'<div style="padding:20px 24px;border-bottom:1px solid rgba(255,255,255,0.06);display:flex;align-items:center;gap:12px;"><span style="font-size:1.3rem;">📄</span><h3 style="margin:0;font-size:1.1rem;font-weight:700;color:#f1f0f5;font-family:Inter,sans-serif;">Resume Skills</h3><span style="margin-left:auto;padding:4px 12px;background:rgba(99,102,241,0.1);border-radius:100px;font-size:0.8rem;font-weight:700;color:#6366f1;">{data["resume_analysis"]["skills_found"]}</span></div>'
    for cat, skills in resume_cats.items():
        chips = "".join([f'<span style="padding:5px 14px;border-radius:100px;font-size:0.8rem;font-weight:500;background:{"rgba(16,185,129,0.08)" if s in matched else "rgba(99,102,241,0.08)"};color:{"#10b981" if s in matched else "#c4b5fd"};border:1px solid {"rgba(16,185,129,0.15)" if s in matched else "rgba(99,102,241,0.15)"};margin:3px;">{s}</span>' for s in skills])
        html += f'<div style="padding:16px 24px;border-bottom:1px solid rgba(255,255,255,0.06);"><div style="font-size:0.75rem;font-weight:700;color:#6b6680;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">{cat}</div><div style="display:flex;flex-wrap:wrap;gap:4px;">{chips}</div></div>'
    html += '</div>'

    # JD panel
    jd_cats = {}
    for s in jd_skills:
        jd_cats.setdefault(s["category"], []).append(s["skill"])

    html += '<div style="background:rgba(22,22,35,0.7);border:1px solid rgba(255,255,255,0.06);border-radius:16px;overflow:hidden;">'
    html += f'<div style="padding:20px 24px;border-bottom:1px solid rgba(255,255,255,0.06);display:flex;align-items:center;gap:12px;"><span style="font-size:1.3rem;">📋</span><h3 style="margin:0;font-size:1.1rem;font-weight:700;color:#f1f0f5;font-family:Inter,sans-serif;">Required Skills (JD)</h3><span style="margin-left:auto;padding:4px 12px;background:rgba(99,102,241,0.1);border-radius:100px;font-size:0.8rem;font-weight:700;color:#6366f1;">{data["jd_analysis"]["skills_found"]}</span></div>'
    for cat, skills in jd_cats.items():
        chips = ""
        for s in skills:
            if s in matched:
                chips += f'<span style="padding:5px 14px;border-radius:100px;font-size:0.8rem;font-weight:500;background:rgba(16,185,129,0.08);color:#10b981;border:1px solid rgba(16,185,129,0.15);margin:3px;">{s}</span>'
            elif s in gap_skills:
                chips += f'<span style="padding:5px 14px;border-radius:100px;font-size:0.8rem;font-weight:500;background:rgba(244,63,94,0.08);color:#f43f5e;border:1px solid rgba(244,63,94,0.15);margin:3px;">{s}</span>'
            else:
                chips += f'<span style="padding:5px 14px;border-radius:100px;font-size:0.8rem;font-weight:500;background:rgba(99,102,241,0.08);color:#c4b5fd;border:1px solid rgba(99,102,241,0.15);margin:3px;">{s}</span>'
        html += f'<div style="padding:16px 24px;border-bottom:1px solid rgba(255,255,255,0.06);"><div style="font-size:0.75rem;font-weight:700;color:#6b6680;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">{cat}</div><div style="display:flex;flex-wrap:wrap;gap:4px;">{chips}</div></div>'
    html += '</div></div>'

    return html


def render_metrics_html(data):
    """Generate metrics HTML."""
    pw = data["pathway"]
    gap = data["gap_analysis"]["summary"]
    metrics = pw.get("metrics", {})

    html = f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">
        <div style="background:rgba(22,22,35,0.7);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:32px;">
            <h3 style="font-size:1rem;font-weight:700;color:#f1f0f5;margin:0 0 8px;font-family:'Inter',sans-serif;">📊 Pathway Efficiency Index</h3>
            <p style="font-size:0.85rem;color:#a09cb0;margin:0 0 16px;">Ratio of personalized pathway time to full generic curriculum. Lower is better.</p>
            <div style="font-size:2.8rem;font-weight:900;background:linear-gradient(135deg,#6366f1,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1;">{(metrics.get('pathway_efficiency_index',0)*100):.1f}%</div>
            <div style="margin-top:16px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:0.85rem;color:#a09cb0;"><span>Your pathway</span><span>{pw.get('total_hours',0)}h / {pw.get('generic_curriculum_hours',0)}h</span></div>
                <div style="height:10px;background:#1a1a24;border-radius:5px;overflow:hidden;"><div style="height:100%;width:{metrics.get('pathway_efficiency_index',0)*100:.1f}%;background:linear-gradient(135deg,#6366f1,#a855f7);border-radius:5px;"></div></div>
            </div>
        </div>
        <div style="background:rgba(22,22,35,0.7);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:32px;">
            <h3 style="font-size:1rem;font-weight:700;color:#f1f0f5;margin:0 0 8px;font-family:'Inter',sans-serif;">🎯 Personalization Ratio</h3>
            <p style="font-size:0.85rem;color:#a09cb0;margin:0 0 16px;">Fraction of total catalog modules selected for your pathway.</p>
            <div style="font-size:2.8rem;font-weight:900;background:linear-gradient(135deg,#6366f1,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1;">{(metrics.get('personalization_ratio',0)*100):.1f}%</div>
            <div style="margin-top:16px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:0.85rem;color:#a09cb0;"><span>Selected modules</span><span>{pw.get('total_modules',0)} of {round(pw.get('total_modules',1)/max(metrics.get('personalization_ratio',1),0.001))}</span></div>
                <div style="height:10px;background:#1a1a24;border-radius:5px;overflow:hidden;"><div style="height:100%;width:{metrics.get('personalization_ratio',0)*100:.1f}%;background:linear-gradient(135deg,#6366f1,#a855f7);border-radius:5px;"></div></div>
            </div>
        </div>
        <div style="background:rgba(22,22,35,0.7);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:32px;">
            <h3 style="font-size:1rem;font-weight:700;color:#f1f0f5;margin:0 0 8px;font-family:'Inter',sans-serif;">⚡ Gap Coverage</h3>
            <p style="font-size:0.85rem;color:#a09cb0;margin:0 0 16px;">Breakdown of skill gaps by severity level.</p>
            <div style="margin-top:8px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:0.85rem;"><span style="color:#f43f5e;">Critical</span><span style="color:#a09cb0;">{gap['critical_gaps']} gaps</span></div>
                <div style="height:10px;background:#1a1a24;border-radius:5px;overflow:hidden;margin-bottom:16px;"><div style="height:100%;width:{gap['critical_gaps']/max(gap['skills_with_gaps'],1)*100:.0f}%;background:#f43f5e;border-radius:5px;"></div></div>
                <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:0.85rem;"><span style="color:#f59e0b;">Important</span><span style="color:#a09cb0;">{gap['important_gaps']} gaps</span></div>
                <div style="height:10px;background:#1a1a24;border-radius:5px;overflow:hidden;margin-bottom:16px;"><div style="height:100%;width:{gap['important_gaps']/max(gap['skills_with_gaps'],1)*100:.0f}%;background:#f59e0b;border-radius:5px;"></div></div>
                <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:0.85rem;"><span style="color:#06b6d4;">Nice to Have</span><span style="color:#a09cb0;">{gap['nice_to_have_gaps']} gaps</span></div>
                <div style="height:10px;background:#1a1a24;border-radius:5px;overflow:hidden;"><div style="height:100%;width:{gap['nice_to_have_gaps']/max(gap['skills_with_gaps'],1)*100:.0f}%;background:#06b6d4;border-radius:5px;"></div></div>
            </div>
        </div>
        <div style="background:rgba(22,22,35,0.7);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:32px;">
            <h3 style="font-size:1rem;font-weight:700;color:#f1f0f5;margin:0 0 8px;font-family:'Inter',sans-serif;">📈 Skill Extraction Stats</h3>
            <p style="font-size:0.85rem;color:#a09cb0;margin:0 0 16px;">Summary of NLP-based skill extraction results.</p>
            <div style="display:grid;gap:4px;">
                <div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.06);"><span style="color:#a09cb0;">Resume Skills</span><span style="font-weight:700;color:#f1f0f5;">{data['resume_analysis']['skills_found']}</span></div>
                <div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.06);"><span style="color:#a09cb0;">JD Skills</span><span style="font-weight:700;color:#f1f0f5;">{data['jd_analysis']['skills_found']}</span></div>
                <div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.06);"><span style="color:#a09cb0;">Skills Matched</span><span style="font-weight:700;color:#10b981;">{gap['skills_matched']}</span></div>
                <div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.06);"><span style="color:#a09cb0;">Match Rate</span><span style="font-weight:700;color:#6366f1;">{gap['match_percentage']}%</span></div>
                <div style="display:flex;justify-content:space-between;padding:10px 0;"><span style="color:#a09cb0;">Avg Module Time</span><span style="font-weight:700;color:#f1f0f5;">{metrics.get('avg_time_per_module',0)}h</span></div>
            </div>
        </div>
    </div>
    """
    return html


def render_datasets_html():
    """Render datasets section."""
    return """
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:40px;">
        <div style="background:rgba(22,22,35,0.7);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:32px;">
            <div style="font-size:2rem;margin-bottom:16px;">🏛️</div>
            <h3 style="font-size:1.1rem;font-weight:700;color:#f1f0f5;margin:0 0 8px;font-family:'Inter',sans-serif;">O*NET Skills & Knowledge</h3>
            <p style="font-size:0.9rem;color:#a09cb0;line-height:1.6;margin-bottom:16px;">Industry-standard occupational taxonomy from the U.S. Department of Labor. Used as the foundation for our 270+ skill taxonomy.</p>
            <a href="https://www.onetcenter.org/db_releases.html" target="_blank" style="font-size:0.9rem;font-weight:600;color:#6366f1;text-decoration:none;">onetcenter.org →</a>
        </div>
        <div style="background:rgba(22,22,35,0.7);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:32px;">
            <div style="font-size:2rem;margin-bottom:16px;">📊</div>
            <h3 style="font-size:1.1rem;font-weight:700;color:#f1f0f5;margin:0 0 8px;font-family:'Inter',sans-serif;">Kaggle Resume Dataset</h3>
            <p style="font-size:0.9rem;color:#a09cb0;line-height:1.6;margin-bottom:16px;">Collection of 2,400+ resumes across various fields. Used for validation and testing of skill extraction accuracy.</p>
            <a href="https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset/data" target="_blank" style="font-size:0.9rem;font-weight:600;color:#6366f1;text-decoration:none;">kaggle.com →</a>
        </div>
        <div style="background:rgba(22,22,35,0.7);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:32px;">
            <div style="font-size:2rem;margin-bottom:16px;">🤖</div>
            <h3 style="font-size:1.1rem;font-weight:700;color:#f1f0f5;margin:0 0 8px;font-family:'Inter',sans-serif;">Custom NLP Pipeline</h3>
            <p style="font-size:0.9rem;color:#a09cb0;line-height:1.6;margin-bottom:16px;">Taxonomy-based skill extraction using regex pattern matching with confidence scoring against 270+ skills across 14 categories.</p>
            <span style="font-size:0.9rem;font-weight:600;color:#6366f1;">Custom Implementation</span>
        </div>
        <div style="background:rgba(22,22,35,0.7);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:32px;">
            <div style="font-size:2rem;margin-bottom:16px;">⚙️</div>
            <h3 style="font-size:1.1rem;font-weight:700;color:#f1f0f5;margin:0 0 8px;font-family:'Inter',sans-serif;">Original Adaptive Logic</h3>
            <p style="font-size:0.9rem;color:#a09cb0;line-height:1.6;margin-bottom:16px;">Custom weighted scoring algorithm considers gap severity, prerequisite depth, transferable skills, and role priority.</p>
            <span style="font-size:0.9rem;font-weight:600;color:#6366f1;">Custom Implementation</span>
        </div>
    </div>
    """


# ─── Main App ───
def main():
    render_hero()

    st.markdown("---")

    # Upload section header
    st.markdown("""
    <div style="text-align:center;margin-bottom:30px;">
        <span style="display:inline-block;padding:6px 16px;background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.2);border-radius:100px;font-size:0.8rem;font-weight:600;color:#6366f1;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:16px;">Analyze</span>
        <h2 style="font-size:2.2rem;font-weight:800;margin:0 0 12px;letter-spacing:-0.02em;color:#f1f0f5;font-family:'Inter',sans-serif;">Upload & Analyze</h2>
        <p style="font-size:1.05rem;color:#a09cb0;">Provide a resume and job description to generate your personalized pathway</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p style="font-size:1.1rem;font-weight:700;color:#f1f0f5;margin-bottom:4px;">📄 Resume</p>', unsafe_allow_html=True)
        resume_file = st.file_uploader("Upload candidate's resume", type=["pdf", "docx", "txt"], label_visibility="collapsed")

    with col2:
        st.markdown('<p style="font-size:1.1rem;font-weight:700;color:#f1f0f5;margin-bottom:4px;">📋 Job Description</p>', unsafe_allow_html=True)
        jd_text = st.text_area("Paste target role requirements", height=200, placeholder="Paste the full job description here...\n\nExample:\nSenior Software Engineer\n\nRequirements:\n- 5+ years of experience with Python\n- Strong knowledge of React and Node.js", label_visibility="collapsed")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    analyze_clicked = st.button("🚀 Generate Learning Pathway", disabled=(not resume_file or not jd_text or len(jd_text.strip()) < 20), use_container_width=True)

    if analyze_clicked and resume_file and jd_text:
        with st.spinner("🔍 Analyzing resume and generating pathway..."):
            try:
                # Save uploaded file temporarily
                suffix = "." + resume_file.name.split(".")[-1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(resume_file.getbuffer())
                    tmp_path = tmp.name

                # Run pipeline
                resume_data = parse_resume(tmp_path)
                jd_data = parse_job_description(jd_text)
                resume_skills = extract_skills(resume_data["text"])
                jd_skills = extract_skills(jd_text)
                gap_analysis = analyze_gaps(resume_skills, jd_skills, resume_data["text"], jd_text, resume_data["metadata"])
                pathway = generate_pathway(gap_analysis, resume_data["metadata"])

                # Clean up
                os.unlink(tmp_path)

                # Store results
                st.session_state["results"] = {
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
                }

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                return

    # Render results if available
    if "results" in st.session_state:
        data = st.session_state["results"]

        st.markdown("---")
        st.markdown("""
        <div style="text-align:center;margin-bottom:30px;">
            <span style="display:inline-block;padding:6px 16px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.2);border-radius:100px;font-size:0.8rem;font-weight:600;color:#10b981;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:16px;">Analysis Complete</span>
            <h2 style="font-size:2.2rem;font-weight:800;margin:0;letter-spacing:-0.02em;color:#f1f0f5;font-family:'Inter',sans-serif;">Your Personalized Pathway</h2>
        </div>
        """, unsafe_allow_html=True)

        render_summary_cards(data["gap_analysis"]["summary"], data["pathway"])
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Learning Pathway", "📊 Skill Gaps", "🎯 Skills Overview", "📈 Metrics"])

        with tab1:
            components.html(render_pathway_html(data["pathway"]), height=max(len(data["pathway"].get("phases", [])) * 400 + 200, 600), scrolling=True)

        with tab2:
            components.html(render_gaps_html(data["gap_analysis"]), height=max(len(data["gap_analysis"]["gaps"]) * 140 + 100, 400), scrolling=True)

        with tab3:
            components.html(render_skills_html(data), height=600, scrolling=True)

        with tab4:
            components.html(render_metrics_html(data), height=700, scrolling=True)

    # Datasets section
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center;margin-bottom:30px;">
        <span style="display:inline-block;padding:6px 16px;background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.2);border-radius:100px;font-size:0.8rem;font-weight:600;color:#6366f1;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:16px;">Transparency</span>
        <h2 style="font-size:2.2rem;font-weight:800;margin:0 0 12px;letter-spacing:-0.02em;color:#f1f0f5;font-family:'Inter',sans-serif;">Datasets & Models</h2>
        <p style="font-size:1.05rem;color:#a09cb0;">Full disclosure of all data sources and models used</p>
    </div>
    """, unsafe_allow_html=True)
    components.html(render_datasets_html(), height=450, scrolling=True)

    # Footer
    st.markdown("""
    <div style="text-align:center;padding:40px 0 20px;border-top:1px solid rgba(255,255,255,0.06);margin-top:40px;">
        <p style="font-size:1.1rem;font-weight:700;background:linear-gradient(135deg,#6366f1,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🌉 SkillBridge</p>
        <p style="font-size:0.85rem;color:#a09cb0;">AI-Driven Adaptive Learning Engine for Corporate Onboarding</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
