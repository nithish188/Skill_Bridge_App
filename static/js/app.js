/**
 * SkillBridge — AI-Driven Adaptive Learning Engine
 * Main Application JavaScript
 */

// ============================================================
// STATE
// ============================================================
const state = {
    resumeFile: null,
    jdText: "",
    analysisResult: null,
};

// ============================================================
// DOM ELEMENTS
// ============================================================
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const elements = {
    resumeInput: $("#resume-input"),
    resumeDropzone: $("#resume-dropzone"),
    resumeFileInfo: $("#resume-file-info"),
    resumeFilename: $("#resume-filename"),
    resumeRemove: $("#resume-remove"),
    jdTextarea: $("#jd-textarea"),
    jdCount: $("#jd-count"),
    analyzeBtn: $("#analyze-btn"),
    loadingOverlay: $("#loading-overlay"),
    loadingStep: $("#loading-step"),
    loadingBarFill: $("#loading-bar-fill"),
    resultsSection: $("#results"),
    summaryGrid: $("#summary-grid"),
    pathwayContainer: $("#pathway-container"),
    gapsList: $("#gaps-list"),
    radarCanvas: $("#radar-canvas"),
    skillsComparison: $("#skills-comparison"),
    metricsContainer: $("#metrics-container"),
};

// ============================================================
// FILE UPLOAD HANDLING
// ============================================================
function initUpload() {
    const dropzone = elements.resumeDropzone;
    const input = elements.resumeInput;

    // Click to browse
    dropzone.addEventListener("click", () => {
        if (!state.resumeFile) input.click();
    });

    // File selected
    input.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    // Drag and drop
    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("drag-over");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("drag-over");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("drag-over");
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    // Remove file
    elements.resumeRemove.addEventListener("click", (e) => {
        e.stopPropagation();
        state.resumeFile = null;
        input.value = "";
        $(".dropzone-content").style.display = "";
        elements.resumeFileInfo.style.display = "none";
        updateAnalyzeButton();
    });
}

function handleFileSelect(file) {
    const allowed = ["pdf", "docx", "txt"];
    const ext = file.name.split(".").pop().toLowerCase();
    if (!allowed.includes(ext)) {
        showToast("Please upload a PDF, DOCX, or TXT file.", "error");
        return;
    }
    if (file.size > 16 * 1024 * 1024) {
        showToast("File too large. Maximum size is 16MB.", "error");
        return;
    }

    state.resumeFile = file;
    elements.resumeFilename.textContent = file.name;
    $(".dropzone-content").style.display = "none";
    elements.resumeFileInfo.style.display = "flex";
    updateAnalyzeButton();
}

// ============================================================
// JD INPUT HANDLING
// ============================================================
function initJdInput() {
    elements.jdTextarea.addEventListener("input", () => {
        state.jdText = elements.jdTextarea.value;
        elements.jdCount.textContent = state.jdText.length;
        updateAnalyzeButton();
    });
}

// ============================================================
// ANALYZE BUTTON
// ============================================================
function updateAnalyzeButton() {
    const ready = state.resumeFile && state.jdText.trim().length > 20;
    elements.analyzeBtn.disabled = !ready;
}

function initAnalyzeButton() {
    elements.analyzeBtn.addEventListener("click", performAnalysis);
}

// ============================================================
// ANALYSIS PIPELINE
// ============================================================
async function performAnalysis() {
    if (!state.resumeFile || !state.jdText.trim()) return;

    showLoading();

    const formData = new FormData();
    formData.append("resume", state.resumeFile);
    formData.append("jd_text", state.jdText);

    try {
        updateLoadingStep("Parsing resume...", 10);
        await sleep(400);
        updateLoadingStep("Extracting skills from resume...", 25);
        await sleep(400);
        updateLoadingStep("Analyzing job description...", 40);
        await sleep(300);
        updateLoadingStep("Identifying skill gaps...", 55);

        const response = await fetch("/api/analyze", {
            method: "POST",
            body: formData,
        });

        updateLoadingStep("Generating adaptive pathway...", 75);
        await sleep(300);

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || "Analysis failed");
        }

        const data = await response.json();
        updateLoadingStep("Building your personalized roadmap...", 90);
        await sleep(400);

        state.analysisResult = data;
        updateLoadingStep("Done!", 100);
        await sleep(500);

        hideLoading();
        renderResults(data);
    } catch (err) {
        hideLoading();
        showToast(err.message || "Something went wrong. Please try again.", "error");
        console.error(err);
    }
}

// ============================================================
// LOADING UI
// ============================================================
function showLoading() {
    elements.loadingOverlay.style.display = "flex";
    document.body.style.overflow = "hidden";
}

function hideLoading() {
    elements.loadingOverlay.style.display = "none";
    document.body.style.overflow = "";
}

function updateLoadingStep(text, progress) {
    elements.loadingStep.textContent = text;
    elements.loadingBarFill.style.width = progress + "%";
}

function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
}

// ============================================================
// RENDER RESULTS
// ============================================================
function renderResults(data) {
    elements.resultsSection.style.display = "block";

    renderSummary(data);
    renderPathway(data.pathway);
    renderGaps(data.gap_analysis);
    renderSkillsOverview(data);
    renderMetrics(data);

    // Scroll to results
    setTimeout(() => {
        elements.resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 200);
}

// --- Summary Cards ---
function renderSummary(data) {
    const gap = data.gap_analysis.summary;
    const pw = data.pathway;

    elements.summaryGrid.innerHTML = `
        <div class="summary-card card-match animate-in">
            <div class="summary-card-icon">✅</div>
            <div class="summary-card-value">${gap.match_percentage}%</div>
            <div class="summary-card-label">Skills Match</div>
        </div>
        <div class="summary-card card-gaps animate-in animate-in-delay-1">
            <div class="summary-card-icon">⚠️</div>
            <div class="summary-card-value">${gap.skills_with_gaps}</div>
            <div class="summary-card-label">Skill Gaps Found</div>
        </div>
        <div class="summary-card card-hours animate-in animate-in-delay-2">
            <div class="summary-card-icon">⏱️</div>
            <div class="summary-card-value">${pw.total_hours || 0}h</div>
            <div class="summary-card-label">Training Hours</div>
        </div>
        <div class="summary-card card-efficiency animate-in animate-in-delay-3">
            <div class="summary-card-icon">🚀</div>
            <div class="summary-card-value">${pw.efficiency_score || 0}%</div>
            <div class="summary-card-label">Efficiency vs Generic</div>
        </div>
    `;
}

// --- Pathway ---
function renderPathway(pathway) {
    if (!pathway.phases || pathway.phases.length === 0) {
        elements.pathwayContainer.innerHTML = `
            <div class="metric-card" style="text-align:center; padding:48px;">
                <h3>🎉 No Training Needed!</h3>
                <p>${pathway.message || "The candidate meets all requirements."}</p>
            </div>
        `;
        return;
    }

    let html = "";

    // Total summary bar
    html += `
        <div class="metric-card" style="margin-bottom:24px;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                <div>
                    <h3>📋 Personalized Pathway Summary</h3>
                    <p>${pathway.total_modules} modules across ${pathway.phases.length} phases</p>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.6rem;font-weight:800;color:var(--accent-primary);">${pathway.total_hours}h</div>
                    <div style="font-size:0.75rem;color:var(--accent-emerald);font-weight:600;">
                        ${pathway.total_hours_saved > 0 ? `${pathway.total_hours_saved}h saved vs generic` : "Optimized pathway"}
                    </div>
                </div>
            </div>
            <div class="metric-bar">
                <div class="metric-bar-fill" style="width:${Math.min((pathway.total_hours / pathway.generic_curriculum_hours) * 100, 100)}%"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:var(--text-muted);">
                <span>Your pathway: ${pathway.total_hours}h</span>
                <span>Generic curriculum: ${pathway.generic_curriculum_hours}h</span>
            </div>
        </div>
    `;

    pathway.phases.forEach((phase, i) => {
        html += `
            <div class="pathway-phase animate-in" style="animation-delay:${i * 0.1}s">
                <div class="phase-header">
                    <div class="phase-icon">${phase.icon}</div>
                    <div class="phase-info">
                        <h3>Phase ${phase.id}: ${phase.name}</h3>
                        <p>${phase.description}</p>
                    </div>
                    <div class="phase-hours">
                        <div class="phase-hours-value">${phase.total_hours}h</div>
                        <div class="phase-hours-label">Total</div>
                    </div>
                </div>
                <div class="phase-modules">
                    ${phase.modules.map((mod) => renderModuleCard(mod)).join("")}
                </div>
            </div>
        `;
    });

    elements.pathwayContainer.innerHTML = html;

    // Animate metric bars after render
    setTimeout(() => {
        $$(".metric-bar-fill").forEach((el) => {
            el.style.width = el.style.width; // force reflow
        });
    }, 100);
}

function renderModuleCard(mod) {
    const tags = [];
    mod.skills_covered.forEach((s) => {
        tags.push(`<span class="module-tag tag-skill">${s}</span>`);
    });
    tags.push(`<span class="module-tag tag-format">${mod.format}</span>`);
    if (mod.is_prerequisite) {
        tags.push(`<span class="module-tag tag-prereq">Prerequisite</span>`);
    }
    if (mod.transfer_applied) {
        tags.push(`<span class="module-tag tag-saved">⚡ ${mod.time_saved}h saved</span>`);
    }

    return `
        <div class="module-card">
            <div class="module-id">${mod.module_id}</div>
            <div class="module-info">
                <div class="module-title">${mod.title}</div>
                <div class="module-desc">${mod.description}</div>
                <div class="module-tags">${tags.join("")}</div>
            </div>
            <div class="module-duration">
                <div class="duration-value">${mod.adjusted_duration}h</div>
                <div class="duration-label">Hours</div>
                ${mod.transfer_applied ? `<div class="duration-saved">was ${mod.original_duration}h</div>` : ""}
            </div>
        </div>
    `;
}

// --- Gaps ---
function renderGaps(gapData) {
    const gaps = gapData.gaps;

    // Render gap list
    let gapsHtml = "";
    gaps.forEach((gap) => {
        const barColor = gap.severity === "critical" ? "#f43f5e" :
            gap.severity === "important" ? "#f59e0b" : "#06b6d4";
        const currentWidth = Math.max(gap.current_proficiency, 2);

        gapsHtml += `
            <div class="gap-item">
                <div class="gap-item-header">
                    <span class="gap-skill-name">${gap.skill}</span>
                    <span class="gap-severity severity-${gap.severity}">${gap.severity.replace('_', ' ')}</span>
                </div>
                <div class="gap-bar-container">
                    <div class="gap-bar-labels">
                        <span>Current: ${gap.current_proficiency}%</span>
                        <span>Required: ${gap.required_proficiency}%</span>
                    </div>
                    <div class="gap-bar">
                        <div class="gap-bar-current" style="width:${currentWidth}%;background:${barColor};"></div>
                        <div class="gap-bar-required" style="left:${gap.required_proficiency}%"></div>
                    </div>
                </div>
                ${gap.has_transferable ? `
                    <div class="gap-transferable">
                        ⚡ Transferable from: ${gap.transferable_from.join(", ")}
                    </div>
                ` : ""}
            </div>
        `;
    });

    elements.gapsList.innerHTML = gapsHtml || `
        <div class="metric-card" style="text-align:center;padding:32px;">
            <p style="color:var(--accent-emerald);">No skill gaps detected! 🎉</p>
        </div>
    `;

    // Render radar chart
    renderRadarChart(gapData);
}

// --- Radar Chart ---
function renderRadarChart(gapData) {
    const canvas = elements.radarCanvas;
    const ctx = canvas.getContext("2d");
    
    // High DPI support
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect ? { width: 450, height: 450 } : canvas;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
    ctx.scale(dpr, dpr);

    const W = rect.width;
    const H = rect.height;
    const cx = W / 2;
    const cy = H / 2;
    const maxR = Math.min(cx, cy) - 60;

    // Prepare data from category gaps
    const categories = Object.keys(gapData.category_gaps);
    if (categories.length < 3) {
        // Need at least 3 points for radar
        // Add matched skill categories
        const matched = gapData.matched_skills || [];
        const matchedCats = new Set(matched.map(m => m.category));
        matchedCats.forEach(c => {
            if (!categories.includes(c)) categories.push(c);
        });
    }
    
    if (categories.length < 3) {
        ctx.fillStyle = "#a09cb0";
        ctx.font = "14px Inter";
        ctx.textAlign = "center";
        ctx.fillText("Not enough skill categories for radar chart", cx, cy);
        return;
    }

    const n = categories.length;
    const angleStep = (2 * Math.PI) / n;

    ctx.clearRect(0, 0, W, H);

    // Draw grid rings
    for (let ring = 1; ring <= 5; ring++) {
        const r = (ring / 5) * maxR;
        ctx.beginPath();
        for (let i = 0; i <= n; i++) {
            const angle = i * angleStep - Math.PI / 2;
            const x = cx + r * Math.cos(angle);
            const y = cy + r * Math.sin(angle);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.strokeStyle = "rgba(255,255,255,0.06)";
        ctx.lineWidth = 1;
        ctx.stroke();
    }

    // Draw axes
    for (let i = 0; i < n; i++) {
        const angle = i * angleStep - Math.PI / 2;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(cx + maxR * Math.cos(angle), cy + maxR * Math.sin(angle));
        ctx.strokeStyle = "rgba(255,255,255,0.06)";
        ctx.lineWidth = 1;
        ctx.stroke();
    }

    // Calculate gap data
    const gapValues = categories.map((cat) => {
        const catData = gapData.category_gaps[cat];
        if (catData) {
            return Math.min(catData.total_gap / catData.count / 100, 1);
        }
        return 0;
    });

    // Draw gap area
    ctx.beginPath();
    gapValues.forEach((val, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const r = val * maxR;
        const x = cx + r * Math.cos(angle);
        const y = cy + r * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.fillStyle = "rgba(244, 63, 94, 0.15)";
    ctx.fill();
    ctx.strokeStyle = "rgba(244, 63, 94, 0.6)";
    ctx.lineWidth = 2;
    ctx.stroke();

    // Draw data points
    gapValues.forEach((val, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const r = val * maxR;
        const x = cx + r * Math.cos(angle);
        const y = cy + r * Math.sin(angle);
        
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = "#f43f5e";
        ctx.fill();
        ctx.strokeStyle = "rgba(244, 63, 94, 0.3)";
        ctx.lineWidth = 6;
        ctx.stroke();
    });

    // Draw labels
    ctx.font = "600 11px Inter";
    ctx.fillStyle = "#a09cb0";
    ctx.textAlign = "center";

    categories.forEach((cat, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const labelR = maxR + 30;
        let x = cx + labelR * Math.cos(angle);
        let y = cy + labelR * Math.sin(angle);

        // Truncate long names
        let label = cat.length > 18 ? cat.substring(0, 16) + "…" : cat;

        ctx.fillText(label, x, y + 4);
    });

    // Title
    ctx.font = "700 13px Inter";
    ctx.fillStyle = "#f1f0f5";
    ctx.fillText("Skill Gap Distribution", cx, 20);
}

// --- Skills Overview ---
function renderSkillsOverview(data) {
    const resumeSkills = data.resume_analysis.skill_categories;
    const jdSkills = data.jd_analysis.skills;
    const matched = data.gap_analysis.matched_skills.map(m => m.skill);
    const gaps = data.gap_analysis.gaps.map(g => g.skill);

    let html = "";

    // Resume skills panel
    html += `
        <div class="skills-panel animate-in">
            <div class="skills-panel-header">
                <span style="font-size:1.3rem;">📄</span>
                <h3>Resume Skills</h3>
                <span class="skills-panel-count">${data.resume_analysis.skills_found}</span>
            </div>
    `;
    for (const [category, skills] of Object.entries(resumeSkills)) {
        html += `
            <div class="skills-category">
                <div class="skills-category-name">${category}</div>
                <div class="skill-chips">
                    ${skills.map((s) => `<span class="skill-chip ${matched.includes(s) ? 'matched' : ''}">${s}</span>`).join("")}
                </div>
            </div>
        `;
    }
    html += `</div>`;

    // JD skills panel
    const jdCategories = {};
    jdSkills.forEach((s) => {
        if (!jdCategories[s.category]) jdCategories[s.category] = [];
        jdCategories[s.category].push(s.skill);
    });

    html += `
        <div class="skills-panel animate-in animate-in-delay-1">
            <div class="skills-panel-header">
                <span style="font-size:1.3rem;">📋</span>
                <h3>Required Skills (JD)</h3>
                <span class="skills-panel-count">${data.jd_analysis.skills_found}</span>
            </div>
    `;
    for (const [category, skills] of Object.entries(jdCategories)) {
        html += `
            <div class="skills-category">
                <div class="skills-category-name">${category}</div>
                <div class="skill-chips">
                    ${skills.map((s) => {
                        const cls = matched.includes(s) ? 'matched' : gaps.includes(s) ? 'missing' : '';
                        return `<span class="skill-chip ${cls}">${s}</span>`;
                    }).join("")}
                </div>
            </div>
        `;
    }
    html += `</div>`;

    elements.skillsComparison.innerHTML = html;
}

// --- Metrics ---
function renderMetrics(data) {
    const pw = data.pathway;
    const gap = data.gap_analysis.summary;
    const metrics = pw.metrics || {};

    elements.metricsContainer.innerHTML = `
        <div class="metrics-grid">
            <div class="metric-card animate-in">
                <h3>📊 Pathway Efficiency Index</h3>
                <p>Ratio of personalized pathway time to full generic curriculum. Lower is better.</p>
                <div class="metric-value-large">${((metrics.pathway_efficiency_index || 0) * 100).toFixed(1)}%</div>
                <div style="margin-top:16px">
                    <div class="metric-bar-label">
                        <span>Your pathway</span>
                        <span>${pw.total_hours || 0}h / ${pw.generic_curriculum_hours || 0}h</span>
                    </div>
                    <div class="metric-bar">
                        <div class="metric-bar-fill" style="width:${(metrics.pathway_efficiency_index || 0) * 100}%"></div>
                    </div>
                </div>
            </div>
            <div class="metric-card animate-in animate-in-delay-1">
                <h3>🎯 Personalization Ratio</h3>
                <p>Fraction of total catalog modules selected for your pathway. More selective = more personalized.</p>
                <div class="metric-value-large">${((metrics.personalization_ratio || 0) * 100).toFixed(1)}%</div>
                <div style="margin-top:16px">
                    <div class="metric-bar-label">
                        <span>Selected modules</span>
                        <span>${pw.total_modules || 0} of ${Math.round((pw.total_modules || 1) / (metrics.personalization_ratio || 1))}</span>
                    </div>
                    <div class="metric-bar">
                        <div class="metric-bar-fill" style="width:${(metrics.personalization_ratio || 0) * 100}%"></div>
                    </div>
                </div>
            </div>
            <div class="metric-card animate-in animate-in-delay-2">
                <h3>⚡ Gap Coverage</h3>
                <p>Breakdown of skill gaps by severity level.</p>
                <div style="margin-top:16px;">
                    <div class="metric-bar-label">
                        <span style="color:#f43f5e">Critical</span>
                        <span>${gap.critical_gaps} gaps</span>
                    </div>
                    <div class="metric-bar" style="margin-bottom:16px">
                        <div class="metric-bar-fill" style="background:#f43f5e;width:${(gap.critical_gaps / Math.max(gap.skills_with_gaps, 1)) * 100}%"></div>
                    </div>
                    <div class="metric-bar-label">
                        <span style="color:#f59e0b">Important</span>
                        <span>${gap.important_gaps} gaps</span>
                    </div>
                    <div class="metric-bar" style="margin-bottom:16px">
                        <div class="metric-bar-fill" style="background:#f59e0b;width:${(gap.important_gaps / Math.max(gap.skills_with_gaps, 1)) * 100}%"></div>
                    </div>
                    <div class="metric-bar-label">
                        <span style="color:#06b6d4">Nice to Have</span>
                        <span>${gap.nice_to_have_gaps} gaps</span>
                    </div>
                    <div class="metric-bar">
                        <div class="metric-bar-fill" style="background:#06b6d4;width:${(gap.nice_to_have_gaps / Math.max(gap.skills_with_gaps, 1)) * 100}%"></div>
                    </div>
                </div>
            </div>
            <div class="metric-card animate-in animate-in-delay-3">
                <h3>📈 Skill Extraction Stats</h3>
                <p>Summary of the NLP-based skill extraction results.</p>
                <div style="margin-top:16px; display:grid; gap:12px;">
                    <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border-subtle);">
                        <span style="color:var(--text-secondary)">Resume Skills</span>
                        <span style="font-weight:700">${data.resume_analysis.skills_found}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border-subtle);">
                        <span style="color:var(--text-secondary)">JD Skills</span>
                        <span style="font-weight:700">${data.jd_analysis.skills_found}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border-subtle);">
                        <span style="color:var(--text-secondary)">Skills Matched</span>
                        <span style="font-weight:700;color:var(--accent-emerald)">${gap.skills_matched}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border-subtle);">
                        <span style="color:var(--text-secondary)">Match Rate</span>
                        <span style="font-weight:700;color:var(--accent-primary)">${gap.match_percentage}%</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:8px 0;">
                        <span style="color:var(--text-secondary)">Avg Module Time</span>
                        <span style="font-weight:700">${metrics.avg_time_per_module || 0}h</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="metric-card animate-in" style="margin-top:24px;">
            <h3>📚 Datasets & Citations</h3>
            <p>All public datasets and open-source tools used in this analysis.</p>
            <div style="margin-top:16px; display:grid; gap:12px;">
                ${data.datasets_used.map(d => `
                    <div style="display:flex;align-items:start;gap:12px;padding:12px;background:var(--bg-glass);border-radius:var(--radius-sm);border:1px solid var(--border-subtle);">
                        <span style="color:var(--accent-primary);font-weight:700;white-space:nowrap;">📎</span>
                        <div>
                            <div style="font-weight:600;margin-bottom:2px;">${d.name}</div>
                            <div style="font-size:0.8rem;color:var(--text-secondary);">${d.usage}</div>
                            <a href="${d.url}" target="_blank" style="font-size:0.8rem;color:var(--accent-primary);text-decoration:none;">${d.url} →</a>
                        </div>
                    </div>
                `).join("")}
            </div>
        </div>
    `;
}

// ============================================================
// TABS
// ============================================================
function initTabs() {
    $$(".tab-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const tab = btn.dataset.tab;

            // Update active tab
            $$(".tab-btn").forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");

            // Show content
            $$(".tab-content").forEach((c) => c.classList.remove("active"));
            $(`#content-${tab}`).classList.add("active");
        });
    });
}

// ============================================================
// TOAST NOTIFICATIONS
// ============================================================
function showToast(message, type = "info") {
    // Remove existing toasts
    $$(".toast").forEach((t) => t.remove());

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" style="background:none;border:none;color:inherit;font-size:1.2rem;cursor:pointer;padding:0 4px;">&times;</button>
    `;

    // Style
    Object.assign(toast.style, {
        position: "fixed",
        bottom: "24px",
        right: "24px",
        padding: "14px 20px",
        borderRadius: "12px",
        background: type === "error" ? "rgba(244, 63, 94, 0.9)" : "rgba(99, 102, 241, 0.9)",
        color: "#fff",
        fontFamily: "var(--font-primary)",
        fontSize: "0.9rem",
        fontWeight: "500",
        display: "flex",
        alignItems: "center",
        gap: "12px",
        backdropFilter: "blur(20px)",
        boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
        zIndex: "3000",
        animation: "fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
        maxWidth: "400px",
    });

    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

// ============================================================
// SMOOTH SCROLL NAVBAR
// ============================================================
function initNavbar() {
    window.addEventListener("scroll", () => {
        const nav = $("#navbar");
        if (window.scrollY > 50) {
            nav.style.padding = "10px 0";
            nav.style.background = "rgba(10, 10, 15, 0.95)";
        } else {
            nav.style.padding = "16px 0";
            nav.style.background = "rgba(10, 10, 15, 0.8)";
        }
    });
}

// ============================================================
// INIT
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
    initUpload();
    initJdInput();
    initAnalyzeButton();
    initTabs();
    initNavbar();
});
