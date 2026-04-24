// Auto-detect API base: if running on GitHub Pages, show a clear message
// If running locally, connect to local backend
const _isGitHubPages = window.location.hostname.includes("github.io");
const _isRailway = window.location.hostname.includes("railway.app") || window.location.hostname.includes("up.railway.app");
// On Railway the frontend is served by the same FastAPI process — use same origin
const API_BASE = window.__CAREER_OS_API__ ?? (_isRailway ? window.location.origin : _isGitHubPages ? null : "http://127.0.0.1:8000");

// If on GitHub Pages, patch submitAuth to show a helpful message
if (_isGitHubPages) {
  window.addEventListener("DOMContentLoaded", () => {
    const banner = document.createElement("div");
    banner.style.cssText = [
      "position:fixed;top:0;left:0;right:0;z-index:9999",
      "background:rgba(15,15,25,0.97);color:#fff;text-align:center",
      "font-family:'Plus Jakarta Sans',sans-serif;font-size:14px",
      "padding:12px 20px;border-bottom:1px solid rgba(99,102,241,0.5)"
    ].join(";");
    banner.innerHTML = `
      🌐 <strong>GitHub Pages Preview</strong> — UI only. 
      For full features run locally: 
      <code style="background:rgba(99,102,241,0.3);padding:2px 8px;border-radius:4px">
        cd Backend &amp;&amp; python -m uvicorn app.main:app --reload --port 8000
      </code>
      then open <a href="http://localhost:5500" style="color:#a5b4fc">http://localhost:5500</a>
    `;
    document.body.prepend(banner);
  });
}

const AppState = {
  view: "dashboard",
  analyticsSessionId: `web-${Date.now()}`,
  analytics: {
    firstJdUploaded: false,
    firstAnalysisCompleted: false,
    firstResumeUploaded: false,
  },
  resumeUploaded: false,
  scannerActive: false,
  heatmapActive: false,
  audioLevel: 0.5,
  resumeFile: null,
  feature1: {
    analysis: null,
    versions: []
  },
  feature2: {
    interview: null,
    trend: null,
    forecast: null,
    quickDebrief: null
  },
  feature3: {
    market: null,
    gap: null,
    sprint: null,
    future: null,
    roi: null,
    history: null,
    quiz: null,
    resumeInject: null
  },
  feature4: {
    session: null,
    lastTurn: null,
    turns: [],
    final: null,
    synthesis: null,
    share: null,
    history: [],
    compare: null,
    prompt: null
  },
  feature5: {
    session: null,
    history: [],
    exportBundle: null
  },
  dashboard: {
    loading: false,
    error: null,
    data: null,
    lastLoadedAt: null
  },
  ui: {
    mode: "beginner",
    feature1Loading: false,
    feature2Loading: false,
    feature3Loading: false,
    feature4Loading: false,
    feature5Loading: false,
    activity: []
  },
  listeners: new Set(),

  subscribe(fn) {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  },

  setState(patch) {
    Object.assign(this, patch);
    this.listeners.forEach((fn) => fn(this));
  }
};

let _authMode = "login";

function handleApiError(error, featureName) {
  const msg = String(error?.message ?? "");
  if (msg.includes("Failed to fetch") || msg.includes("NetworkError")) {
    return `${featureName}: Cannot reach the server. Make sure the backend is running.`;
  }
  if (msg.includes("401") || msg.includes("Unauthorized")) {
    return `${featureName}: Your session expired - please refresh the page.`;
  }
  if (msg.includes("422")) {
    return `${featureName}: Some required fields are missing or invalid.`;
  }
  if (msg.includes("429")) {
    return `${featureName}: Too many requests - please wait a moment and try again.`;
  }
  if (msg.includes("500")) {
    return `${featureName}: The server encountered an error. Please try again shortly.`;
  }
  return `${featureName}: Something went wrong. Please try again.`;
}

function switchAuthTab(mode) {
  _authMode = mode;
  document.getElementById("auth-fullname").style.display = mode === "register" ? "block" : "none";
  const loginTab = document.getElementById("tab-login");
  const regTab = document.getElementById("tab-register");
  if (loginTab) {
    loginTab.classList.toggle("active", mode === "login");
  }
  if (regTab) {
    regTab.classList.toggle("active", mode === "register");
  }
}

async function submitAuth() {
  const email = document.getElementById("auth-email").value.trim();
  const password = document.getElementById("auth-password").value;
  const fullName = document.getElementById("auth-fullname").value.trim();
  const errEl = document.getElementById("auth-error");
  errEl.style.display = "none";

  if (!email || !password) {
    errEl.textContent = "Email and password are required.";
    errEl.style.display = "block";
    return;
  }

  // GitHub Pages — no backend available, allow skip
  if (!API_BASE) {
    errEl.textContent = "No backend available on GitHub Pages. Use 'Continue without account' or run locally at http://localhost:5500.";
    errEl.style.display = "block";
    return;
  }
  const endpoint = _authMode === "login" ? "/api/auth/login" : "/api/auth/register";
  const body = _authMode === "login"
    ? { email, password }
    : { email, password, full_name: fullName, candidate_id: email.split("@")[0] };
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const data = await res.json();
    if (!res.ok) {
      errEl.textContent = data.detail ?? "Authentication failed.";
      errEl.style.display = "block";
      return;
    }
    sessionStorage.setItem("cos_token", data.session.access_token);
    sessionStorage.setItem("cos_candidate", data.user.candidate_id);
    // Hide modal and show app
    document.getElementById("auth-modal").style.display = "none";
    document.getElementById("landing-page").style.display = "none";
    document.getElementById("app-shell").style.display = "block";
    document.querySelectorAll("[id*='candidate']").forEach((el) => {
      if (el.tagName === "INPUT") el.value = data.user.candidate_id;
    });
    void loadDashboard();
  } catch {
    errEl.textContent = "Cannot connect to server. Make sure the backend is running on port 8000.";
    errEl.style.display = "block";
  }
}

async function apiFetch(url, options = {}) {
  const token = sessionStorage.getItem("cos_token");
  const headers = { ...(options.headers ?? {}) };
  const hasContentType = Object.keys(headers).some((k) => k.toLowerCase() === "content-type");
  if (!hasContentType && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  if (token) headers.Authorization = `Bearer ${token}`;
  return fetch(url, { ...options, headers });
}

function validateRequiredFields(fields) {
  const errors = [];
  fields.forEach(({ id, label }) => {
    const el = document.getElementById(id);
    if (!el) return;
    const val = el.value?.trim() ?? "";
    if (!val) {
      el.style.borderColor = "rgba(248,113,113,0.7)";
      errors.push(`${label} is required.`);
    } else {
      el.style.borderColor = "";
    }
  });
  return errors;
}

function showStepLoader(containerId, steps) {
  let current = 0;
  const el = document.getElementById(containerId);
  if (!el) return null;
  function render() {
    el.innerHTML = `
      <div style="display:flex;flex-direction:column;gap:8px;padding:12px 0;">
        ${steps.map((s, i) => `
          <div style="display:flex;align-items:center;gap:10px;opacity:${i <= current ? 1 : 0.35};
            transition:opacity 0.4s;">
            <div style="width:8px;height:8px;border-radius:50%;flex-shrink:0;
              background:${i < current ? "#34d399" : i === current ? "#818cf8" : "rgba(255,255,255,0.2)"};
              ${i === current ? "animation:pulse 1s ease-in-out infinite;" : ""}"></div>
            <span style="font-size:13px;color:rgba(255,255,255,${i <= current ? 0.85 : 0.4});">${s}</span>
          </div>`).join("")}
      </div>`;
  }
  render();
  const interval = setInterval(() => {
    if (current < steps.length - 1) {
      current += 1;
      render();
    }
  }, 2800);
  return { stop: () => clearInterval(interval) };
}

const SCORE_TOOLTIPS = {
  visual_hierarchy: "How well your resume guides the reader's eye - whitespace, font weight, and F-pattern layout.",
  ats_integrity: "Whether an applicant tracking system can correctly parse your sections, contact details, and fonts.",
  semantic_match: "How closely your resume vocabulary aligns with the job description - keywords, synonyms, and action verbs.",
  competitive_benchmark: "Your resume quality relative to other applicants in our database for this job category."
};

function renderScoreCard(key, value) {
  const label = key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  const tooltip = SCORE_TOOLTIPS[key] ?? "";
  const pct = Math.round((Number(value) || 0) * 100);
  const color = pct >= 75 ? "#34d399" : pct >= 50 ? "#fbbf24" : "#f87171";
  return `
    <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
      border-radius:12px;padding:14px;position:relative;">
      <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
        <span style="font-size:12px;color:rgba(255,255,255,0.6);">${label}</span>
        ${tooltip ? `<span title="${tooltip}" style="cursor:help;font-size:11px;
          color:rgba(255,255,255,0.35);border:1px solid rgba(255,255,255,0.2);
          border-radius:50%;width:14px;height:14px;display:inline-flex;
          align-items:center;justify-content:center;">?</span>` : ""}
      </div>
      <div style="font-size:22px;font-weight:700;color:${color};">${pct}%</div>
    </div>`;
}

function formatDashboardTimestamp(value) {
  if (!value) return "Not loaded";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Not loaded";
  return new Intl.DateTimeFormat([], {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

function dashboardStatusFromScore(score) {
  const pct = Math.max(0, Math.min(100, Number(score) || 0));
  if (pct >= 85) return { label: "Ready to Apply", tone: "#34d399" };
  if (pct >= 70) return { label: "Strong Candidate", tone: "#67e8f9" };
  if (pct >= 50) return { label: "Building Momentum", tone: "#fbbf24" };
  return { label: "Needs More Signal", tone: "#f87171" };
}

function renderDashboardBreakdown(components = []) {
  if (!nodes.dashboardScoreBreakdown) return;
  if (!components.length) {
    nodes.dashboardScoreBreakdown.innerHTML = `<div class="dashboard-empty-state">No breakdown available yet. Run Feature 1, Feature 2, or Feature 3 to populate the readiness score.</div>`;
    return;
  }

  nodes.dashboardScoreBreakdown.innerHTML = components
    .map((component) => {
      const pct = Math.max(0, Math.min(100, Number(component.score) || 0));
      const normalizedWeight = Math.round((Number(component.normalized_weight) || 0) * 100);
      const contribution = Number(component.contribution) || 0;
      return `
        <div class="dashboard-score-breakdown-card">
          <div class="dashboard-score-breakdown-label">
            <span>${component.label}</span>
            <span>${pct}% · ${normalizedWeight}% weight</span>
          </div>
          <div class="dashboard-score-breakdown-bar"><div class="dashboard-score-breakdown-fill" style="width:${pct}%;"></div></div>
          <div class="dashboard-score-breakdown-meta">${component.summary || "Not available yet"}<br/>Weighted contribution: ${contribution.toFixed(1)}</div>
        </div>`;
    })
    .join("");
}

function renderDashboardChart(chartData = []) {
  if (!nodes.dashboardChart) return;
  if (!chartData.length) {
    nodes.dashboardChart.innerHTML = `<div class="dashboard-empty-state">No analytics points yet. Complete a feature run and we’ll show real dashboard activity here.</div>`;
    return;
  }

  const maxValue = Math.max(...chartData.map((item) => Number(item.value) || 0), 1);
  nodes.dashboardChart.innerHTML = chartData
    .map((item) => {
      const value = Number(item.value) || 0;
      const width = Math.max(6, Math.min(100, (value / maxValue) * 100));
      const label = item.label || "Metric";
      const display = item.events != null ? item.events : Math.round(value);
      return `
        <div class="dashboard-chart-row">
          <div class="dashboard-chart-label">${label}</div>
          <div class="dashboard-chart-track"><div class="dashboard-chart-fill" style="width:${width}%;"></div></div>
          <div class="dashboard-chart-value">${display}</div>
        </div>`;
    })
    .join("");
}

function renderDashboardActivity(rows = []) {
  if (!nodes.dashboardActivity) return;
  if (!rows.length) {
    nodes.dashboardActivity.innerHTML = `<div class="activity-row">No dashboard activity yet. Run Feature 1 to generate the first real signal.</div>`;
    return;
  }

  nodes.dashboardActivity.innerHTML = rows
    .slice(0, 6)
    .map((row) => {
      const label = row.event_name || row.feature_area || "activity";
      const when = formatDashboardTimestamp(row.occurred_at_utc);
      const detail = row.application_id ? `Application ${row.application_id}` : (row.feature_area || "signal");
      return `<div class="activity-row"><div class="flex items-center justify-between gap-2"><span>${label}</span><span class="text-[11px]" style="color:var(--text-muted)">${when}</span></div><div class="text-[11px]" style="color:rgba(255,255,255,0.55)">${detail}</div></div>`;
    })
    .join("");
}

async function loadDashboard(options = {}) {
  const silent = Boolean(options.silent);
  if (!API_BASE) {
    AppState.setState({
      dashboard: {
        loading: false,
        error: "The backend is not available in this preview. Run the app locally to load the dashboard.",
        data: null,
        lastLoadedAt: null
      }
    });
    return;
  }

  if (!silent) {
    AppState.setState({
      dashboard: {
        ...AppState.dashboard,
        loading: true,
        error: null
      }
    });
  }

  try {
    const response = await apiFetch(`${API_BASE}/api/me/dashboard`);
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload?.detail || "Dashboard data unavailable.");
    }

    if (payload?.user?.candidate_id) {
      document.querySelectorAll("[id*='candidate']").forEach((el) => {
        if (el.tagName === "INPUT" && !el.matches(":focus")) {
          el.value = payload.user.candidate_id;
        }
      });
    }

    AppState.setState({
      dashboard: {
        loading: false,
        error: null,
        data: payload,
        lastLoadedAt: new Date().toISOString()
      }
    });
  } catch (error) {
    AppState.setState({
      dashboard: {
        loading: false,
        error: handleApiError(error, "Dashboard"),
        data: AppState.dashboard?.data ?? null,
        lastLoadedAt: AppState.dashboard?.lastLoadedAt ?? null
      }
    });
  }
}

function navigateTo(viewName) {
  startViewSwap(viewName);
}

window.addEventListener("DOMContentLoaded", () => {
  // Never auto-show auth modal — user must come through the landing page CTA
  // Only auto-skip to app if already authenticated
  if (sessionStorage.getItem("cos_token")) {
    const landing = document.getElementById("landing-page");
    const app = document.getElementById("app-shell");
    if (landing) landing.style.display = "none";
    if (app) app.style.display = "block";
    void loadDashboard();
  }
  lucide.createIcons();

  // Spotlight mouse tracking
  const spotlight = document.getElementById("spotlight");
  if (spotlight) {
    document.addEventListener("mousemove", (e) => {
      spotlight.style.left = e.clientX + "px";
      spotlight.style.top = e.clientY + "px";
    });
  }

  // Logout button
  document.getElementById("logout-btn")?.addEventListener("click", () => {
    const token = sessionStorage.getItem("cos_token");
    if (token) {
      fetch(`${API_BASE}/api/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ access_token: token })
      }).catch(() => {});
    }
    sessionStorage.removeItem("cos_token");
    sessionStorage.removeItem("cos_candidate");
    document.getElementById("app-shell").style.display = "none";
    document.getElementById("landing-page").style.display = "flex";
  });
});

const nodes = {
  viewRoot: document.getElementById("view-root"),
  dashboardView: document.getElementById("dashboard-view"),
  dashboardProgress: document.getElementById("dashboard-progress"),
  dashboardPlan: document.getElementById("dashboard-plan"),
  dashboardNextAction: document.getElementById("dashboard-next-action"),
  dashboardOpenWorkspace: document.getElementById("dashboard-open-workspace"),
  dashboardFeatureExplainer: document.getElementById("dashboard-feature-explainer"),
  dashboardActivity: document.getElementById("dashboard-activity"),
  dashboardSyncStatus: document.getElementById("dashboard-sync-status"),
  dashboardRefresh: document.getElementById("dashboard-refresh"),
  dashboardReadinessScore: document.getElementById("dashboard-readiness-score"),
  dashboardReadinessLabel: document.getElementById("dashboard-readiness-label"),
  dashboardReadinessSummary: document.getElementById("dashboard-readiness-summary"),
  dashboardScoreBreakdown: document.getElementById("dashboard-score-breakdown"),
  dashboardGeneratedAt: document.getElementById("dashboard-generated-at"),
  dashboardChart: document.getElementById("dashboard-chart"),
  dashboardChartNote: document.getElementById("dashboard-chart-note"),
  uiModeBeginner: document.getElementById("ui-mode-beginner"),
  uiModeExpert: document.getElementById("ui-mode-expert"),
  uiModeLabel: document.getElementById("ui-mode-label"),
  onboardingStatus: document.getElementById("onboarding-status"),
  onboardingCandidateId: document.getElementById("onboarding-candidate-id"),
  onboardingJobCategory: document.getElementById("onboarding-job-category"),
  onboardingJobDescription: document.getElementById("onboarding-job-description"),
  onboardingUploadResume: document.getElementById("onboarding-upload-resume"),
  onboardingResumeName: document.getElementById("onboarding-resume-name"),
  onboardingRunLens: document.getElementById("onboarding-run-lens"),
  onboardingRunRebound: document.getElementById("onboarding-run-rebound"),
  onboardingRunNarrative: document.getElementById("onboarding-run-narrative"),
  onboardingOpenWorkspace: document.getElementById("onboarding-open-workspace"),
  commandCenterView: document.getElementById("command-center-view"),
  lensWorkspace: document.getElementById("lens-workspace"),
  feature3Workspace: document.getElementById("feature3-workspace"),
  feature4Workspace: document.getElementById("feature4-workspace"),
  feature5Workspace: document.getElementById("feature5-workspace"),
  uploadZone: document.getElementById("upload-zone"),
  pdfInput: document.getElementById("pdf-input"),
  uploadStatus: document.getElementById("upload-status"),
  scannerLine: document.getElementById("scanner-line"),
  resumeCanvas: document.getElementById("resume-canvas"),
  reactiveCards: Array.from(document.querySelectorAll(".reactive-card")),
  navBtns: Array.from(document.querySelectorAll(".nav-btn")),
  simulateUpload: document.getElementById("simulate-upload"),
  rerenderHeatmap: document.getElementById("rerender-heatmap"),
  simulateVoice: document.getElementById("simulate-voice"),
  analyzeFeature1: document.getElementById("analyze-feature1"),
  runSmartAction: document.getElementById("run-smart-action"),
  runFeature2: document.getElementById("run-feature2"),
  runFeature4: document.getElementById("run-feature4"),
  runFeature3: document.getElementById("run-feature3"),
  runFeature5: document.getElementById("run-feature5"),
  fetchVersions: document.getElementById("fetch-versions"),
  candidateId: document.getElementById("candidate-id"),
  jobCategory: document.getElementById("job-category"),
  jobDescription: document.getElementById("job-description"),
  summaryCards: document.getElementById("analysis-summary-cards"),
  versionList: document.getElementById("version-list"),
  feature2Output: document.getElementById("feature2-output"),
  feature2Notes: document.getElementById("feature2-notes"),
  feature2Transcript: document.getElementById("feature2-transcript"),
  feature2AudioUrl: document.getElementById("feature2-audio-url"),
  feature2UseAssembly: document.getElementById("feature2-use-assembly"),
  feature2Company: document.getElementById("feature2-company"),
  feature2Role: document.getElementById("feature2-role"),
  feature2Round: document.getElementById("feature2-round"),
  feature2Vibe: document.getElementById("feature2-vibe"),
  feature2QuickDebrief: document.getElementById("feature2-quick-debrief"),
  feature2LoadTrend: document.getElementById("feature2-load-trend"),
  coreLoadPlan: document.getElementById("core-load-plan"),
  coreDailyPlan: document.getElementById("core-daily-plan"),
  feature4PersonaMode: document.getElementById("feature4-persona-mode"),
  feature4Language: document.getElementById("feature4-language"),
  feature4Finalize: document.getElementById("feature4-finalize"),
  feature4Share: document.getElementById("feature4-share"),
  feature4Output: document.getElementById("feature4-output"),
  feature4WorkspaceRun: document.getElementById("feature4-workspace-run"),
  feature4WorkspaceFinalize: document.getElementById("feature4-workspace-finalize"),
  // New per-workspace panel nodes
  lensRunFeature1Panel: document.getElementById("lens-run-feature1-panel"),
  lensCandidateId: document.getElementById("lens-candidate-id"),
  lensJobCategory: document.getElementById("lens-job-category"),
  lensJobDescription: document.getElementById("lens-job-description"),
  lensUploadBtn: document.getElementById("lens-upload-btn"),
  feature3WorkspaceRunPanel: document.getElementById("feature3-workspace-run-panel"),
  feature4WorkspaceRunPanel: document.getElementById("feature4-workspace-run-panel"),
  feature4WorkspacePersonaMode: document.getElementById("feature4-workspace-persona-mode"),
  feature4WorkspaceLanguage: document.getElementById("feature4-workspace-language"),
  feature4WorkspaceTopic: document.getElementById("feature4-workspace-topic"),
  feature4WorkspaceCandidateId: document.getElementById("feature4-workspace-candidate-id"),
  feature4WorkspaceShare: document.getElementById("feature4-workspace-share"),
  feature4WorkspaceHistory: document.getElementById("feature4-workspace-history"),
  feature4WorkspaceCompare: document.getElementById("feature4-workspace-compare"),
  feature4SessionBoard: document.getElementById("feature4-session-board"),
  feature4SignalChart: document.getElementById("feature4-signal-chart"),
  feature4LiveHints: document.getElementById("feature4-live-hints"),
  feature4CoachBoard: document.getElementById("feature4-coach-board"),
  feature4MediaBoard: document.getElementById("feature4-media-board"),
  feature4CompareBoard: document.getElementById("feature4-compare-board"),
  feature4InterviewerPrompt: document.getElementById("feature4-interviewer-prompt"),
  feature5TargetRole: document.getElementById("feature5-target-role"),
  feature5Tone: document.getElementById("feature5-tone"),
  feature5RepoSubpath: document.getElementById("feature5-repo-subpath"),
  feature5SelectedProjects: document.getElementById("feature5-selected-projects"),
  feature5GithubRepo: document.getElementById("feature5-github-repo"),
  feature5JdText: document.getElementById("feature5-jd-text"),
  // Workspace-specific inputs (dedicated per-feature pages)
  feature5WorkspaceGithubUrl: document.getElementById("feature5-workspace-github-url"),
  feature5WorkspaceTargetRole: document.getElementById("feature5-workspace-target-role"),
  feature5WorkspaceTone: document.getElementById("feature5-workspace-tone"),
  feature5WorkspaceJd: document.getElementById("feature5-workspace-jd"),
  feature5WorkspaceProjects: document.getElementById("feature5-workspace-projects"),
  feature5LoadHistory: document.getElementById("feature5-load-history"),
  feature5Export: document.getElementById("feature5-export"),
  feature5Download: document.getElementById("feature5-download"),
  feature5DownloadPdf: document.getElementById("feature5-download-pdf"),
  feature5DownloadSite: document.getElementById("feature5-download-site"),
  feature5Output: document.getElementById("feature5-output"),
  metricsApplicationId: document.getElementById("metrics-application-id"),
  metricsCompany: document.getElementById("metrics-company"),
  metricsRole: document.getElementById("metrics-role"),
  metricsChannel: document.getElementById("metrics-channel"),
  metricsStatus: document.getElementById("metrics-status"),
  metricsLogApplication: document.getElementById("metrics-log-application"),
  metricsUpdateStatus: document.getElementById("metrics-update-status"),
  metricsApplicationOutput: document.getElementById("metrics-application-output"),
  lensRunFeature1: document.getElementById("lens-run-feature1"),
  lensLoadVersions: document.getElementById("lens-load-versions"),
  lensSummaryBoard: document.getElementById("lens-summary-board"),
  lensVersionsBoard: document.getElementById("lens-versions-board"),
  lensHeatmapPreview: document.getElementById("lens-heatmap-preview"),
  feature5WorkspaceRun: document.getElementById("feature5-workspace-run"),
  feature5WorkspaceHistory: document.getElementById("feature5-workspace-history"),
  feature5WorkspaceExport: document.getElementById("feature5-workspace-export"),
  feature5WorkspaceDownload: document.getElementById("feature5-workspace-download"),
  feature5WorkspaceDownloadPdf: document.getElementById("feature5-workspace-download-pdf"),
  feature5WorkspaceDownloadSite: document.getElementById("feature5-workspace-download-site"),
  // Rebound workspace
  reboundWorkspaceRun: document.getElementById("rebound-workspace-run"),
  reboundWorkspaceQuickDebrief: document.getElementById("rebound-workspace-quick-debrief"),
  reboundWorkspaceLoadTrend: document.getElementById("rebound-workspace-load-trend"),
  reboundWorkspaceNotes: document.getElementById("rebound-workspace-notes"),
  reboundWorkspaceTranscript: document.getElementById("rebound-workspace-transcript"),
  reboundWorkspaceAudioUrl: document.getElementById("rebound-workspace-audio-url"),
  reboundWorkspaceCompany: document.getElementById("rebound-workspace-company"),
  reboundWorkspaceRole: document.getElementById("rebound-workspace-role"),
  reboundWorkspaceRound: document.getElementById("rebound-workspace-round"),
  reboundWorkspaceVibe: document.getElementById("rebound-workspace-vibe"),
  reboundWorkspaceUseAssembly: document.getElementById("rebound-workspace-use-assembly"),
  reboundOutputBoard: document.getElementById("rebound-output-board"),
  reboundTrendBoard: document.getElementById("rebound-trend-board"),
  reboundActionsBoard: document.getElementById("rebound-actions-board"),
  feature5AnalysisBoard: document.getElementById("feature5-analysis-board"),
  feature5NarrativeBoard: document.getElementById("feature5-narrative-board"),
  feature5TalkBoard: document.getElementById("feature5-talk-board"),
  feature5GapBoard: document.getElementById("feature5-gap-board"),
  feature5ExportBoard: document.getElementById("feature5-export-board"),
  feature3TargetRole: document.getElementById("feature3-target-role"),
  feature3Region: document.getElementById("feature3-region"),
  feature3CurrentSkills: document.getElementById("feature3-current-skills"),
  feature3RemoteOnly: document.getElementById("feature3-remote-only"),
  feature3Salary: document.getElementById("feature3-salary"),
  feature3YearsExp: document.getElementById("feature3-years-exp"),
  feature3Currency: document.getElementById("feature3-currency"),
  feature3Github: document.getElementById("feature3-github"),
  feature3LoadHistory: document.getElementById("feature3-load-history"),
  feature3RunQuiz: document.getElementById("feature3-run-quiz"),
  feature3ResumeInject: document.getElementById("feature3-resume-inject"),
  feature3Export: document.getElementById("feature3-export"),
  feature3Output: document.getElementById("feature3-output"),
  feature3Radar: document.getElementById("feature3-radar"),
  feature3RoiBars: document.getElementById("feature3-roi-bars"),
  feature3WorkspaceRun: document.getElementById("feature3-workspace-run"),
  feature3WorkspaceHistory: document.getElementById("feature3-workspace-history"),
  feature3WorkspaceExport: document.getElementById("feature3-workspace-export"),
  feature3WorkspaceQuiz: document.getElementById("feature3-workspace-quiz"),
  feature3WorkspaceResumeInject: document.getElementById("feature3-workspace-resume-inject"),
  feature3MarketTable: document.getElementById("feature3-market-table"),
  feature3RadarWorkspace: document.getElementById("feature3-radar-workspace"),
  feature3RoiBarsWorkspace: document.getElementById("feature3-roi-bars-workspace"),
  feature3RoadmapList: document.getElementById("feature3-roadmap-list"),
  feature3FutureList: document.getElementById("feature3-future-list"),
  feature3SprintList: document.getElementById("feature3-sprint-list"),
  spotlight: document.getElementById("spotlight"),
  wavePath: document.getElementById("wave-path")
};

const clamp = (n, min, max) => Math.min(max, Math.max(min, n));

function setStatus(text) {
  if (nodes.uploadStatus) nodes.uploadStatus.textContent = text;
  const stamp = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  const history = [`${stamp} - ${text}`, ...(AppState.ui?.activity || [])].slice(0, 8);
  AppState.setState({
    ui: {
      ...AppState.ui,   
      activity: history
    }
  });
}

function syncOnboardingToCoreInputs() {
  if (!nodes.onboardingCandidateId || !nodes.onboardingJobCategory || !nodes.onboardingJobDescription) return;
  nodes.candidateId.value = nodes.onboardingCandidateId.value.trim() || "candidate-001";
  nodes.jobCategory.value = nodes.onboardingJobCategory.value || "frontend";
  nodes.jobDescription.value = nodes.onboardingJobDescription.value || "";
}

function emitEvent(eventName, featureArea, metadata = {}, ids = {}) {
  const payload = [{
    event_name: eventName,
    event_version: "1.0",
    occurred_at_utc: new Date().toISOString(),
    user_id: nodes.candidateId.value.trim() || "candidate-001",
    session_id: AppState.analyticsSessionId,
    platform: "web",
    feature_area: featureArea,
    resume_id: ids.resumeId || null,
    jd_id: ids.jdId || null,
    application_id: ids.applicationId || null,
    interview_id: ids.interviewId || null,
    project_id: ids.projectId || null,
    metadata_json: metadata || {}
  }];

  fetch(`${API_BASE}/api/metrics/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }).catch(() => {
    // Telemetry is non-blocking and should never interrupt feature workflows.
  });
}

function setUiFlag(key, value) {
  AppState.setState({
    ui: {
      ...AppState.ui,
      [key]: value
    }
  });
}

function setUIMode(mode) {
  const nextMode = mode === "expert" ? "expert" : "beginner";
  AppState.setState({
    ui: {
      ...AppState.ui,
      mode: nextMode
    }
  });
}

function renderUIMode() {
  const mode = AppState.ui?.mode || "beginner";
  const isBeginner = mode === "beginner";

  document.querySelectorAll(".advanced-control").forEach((node) => {
    node.classList.toggle("hidden", isBeginner);
  });

  if (nodes.uiModeBeginner) nodes.uiModeBeginner.classList.toggle("active", isBeginner);
  if (nodes.uiModeExpert) nodes.uiModeExpert.classList.toggle("active", !isBeginner);
  if (nodes.uiModeLabel) nodes.uiModeLabel.textContent = `Mode: ${isBeginner ? "Beginner" : "Expert"}`;
}

function stateCard(message, tone = "idle") {
  return `<div class="state-card state-${tone}">${message}</div>`;
}

function stateStack(messages, tone = "idle") {
  return messages.map((message) => stateCard(message, tone)).join("");
}

function smartActionMeta() {
  if (!AppState.resumeFile) {
    return {
      label: "Next Best Action: Upload Resume",
      run: () => nodes.pdfInput.click(),
    };
  }
  if (!nodes.jobDescription.value.trim()) {
    return {
      label: "Next Best Action: Add JD",
      run: () => {
        nodes.jobDescription.focus();
        setStatus("Paste job description to continue the flow.");
      },
    };
  }
  if (!AppState.feature1.analysis) {
    return {
      label: "Next Best Action: Run Lens",
      run: runFeature1Analysis,
    };
  }
  if (!AppState.feature2.interview) {
    return {
      label: "Next Best Action: Run Rebound",
      run: runFeature2Autopsy,
    };
  }
  if (!AppState.feature5.session) {
    return {
      label: "Next Best Action: Run Narrative",
      run: runFeature5NarrativeArchitect,
    };
  }
  return {
    label: "Next Best Action: Export Narrative",
    run: exportFeature5Bundle,
  };
}

function renderSmartAction() {
  if (!nodes.runSmartAction) return;
  nodes.runSmartAction.textContent = smartActionMeta().label;
}

async function runSmartAction() {
  const action = smartActionMeta();
  await action.run();
}

function startViewSwap(nextView) {
  const run = () => {
    nodes.viewRoot.classList.remove("view-swap-active");
    nodes.viewRoot.classList.add("view-swap-enter");
    requestAnimationFrame(() => {
      nodes.viewRoot.classList.add("view-swap-active");
      nodes.viewRoot.classList.remove("view-swap-enter");
      AppState.setState({ view: nextView });
    });
  };

  if (document.startViewTransition) {
    document.startViewTransition(run);
  } else {
    run();
  }
}

function staggerCardWake() {
  nodes.reactiveCards.forEach((card, index) => {
    card.classList.remove("card-live");
    card.style.transitionDelay = `${index * 80}ms`;
    setTimeout(() => {
      card.classList.add("card-live");
    }, 40 + index * 80);
  });
}

function renderHeatmapOverlay() {
  const sourceSpots = AppState.feature1.analysis?.hot_zones || [
    { x: 0.24, y: 0.18, weight: 0.78 },
    { x: 0.72, y: 0.22, weight: 0.52 },
    { x: 0.43, y: 0.51, weight: 0.61 },
    { x: 0.64, y: 0.72, weight: 0.44 },
    { x: 0.3, y: 0.78, weight: 0.67 }
  ];

  const spots = sourceSpots.map((s) => ({
    x: s.x <= 1 ? s.x * 100 : s.x,
    y: s.y <= 1 ? s.y * 100 : s.y,
    r: clamp(12 + (s.weight || 0.5) * 14, 10, 24),
    o: clamp(s.weight || 0.5, 0.2, 0.8)
  }));

  const defs = spots
    .map(
      (s, i) => `
        <radialGradient id="hot${i}" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="rgba(236,72,153,${clamp(s.o + 0.12, 0.2, 0.8)})" />
          <stop offset="45%" stop-color="rgba(99,102,241,${s.o})" />
          <stop offset="100%" stop-color="rgba(168,85,247,0)" />
        </radialGradient>
      `
    )
    .join("");

  const circles = spots
    .map(
      (s, i) => `
        <circle cx="${s.x}%" cy="${s.y}%" r="${s.r}%" fill="url(#hot${i})" style="filter: blur(2px);"></circle>
      `
    )
    .join("");

  nodes.resumeCanvas.innerHTML = `
    <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none">
      <defs>${defs}</defs>
      ${circles}
    </svg>
  `;
  nodes.resumeCanvas.style.opacity = "1";
}

function resetHeatmapOverlay() {
  nodes.resumeCanvas.style.opacity = "0";
  nodes.resumeCanvas.innerHTML = "";
}

function drawSparkline(canvasId, color, fillColor, volatility = 0.3) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  const width = Math.max(200, rect.width || 200);
  const height = Math.max(56, rect.height || 56);

  canvas.width = width * ratio;
  canvas.height = height * ratio;

  const ctx = canvas.getContext("2d");
  ctx.scale(ratio, ratio);
  ctx.clearRect(0, 0, width, height);

  const points = 36;
  const step = width / (points - 1);
  const base = height * 0.58;

  const data = Array.from({ length: points }, (_, i) => {
    const wave = Math.sin(i * 0.32) * (height * 0.12);
    const noise = (Math.random() - 0.5) * height * volatility;
    return clamp(base + wave + noise, 10, height - 10);
  });

  ctx.beginPath();
  data.forEach((y, i) => {
    const x = i * step;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });

  const gradient = ctx.createLinearGradient(0, 0, width, 0);
  gradient.addColorStop(0, color);
  gradient.addColorStop(1, "rgba(255,255,255,0.85)");
  ctx.strokeStyle = gradient;
  ctx.lineWidth = 2;
  ctx.stroke();

  ctx.lineTo(width, height);
  ctx.lineTo(0, height);
  ctx.closePath();
  const fill = ctx.createLinearGradient(0, 10, 0, height);
  fill.addColorStop(0, fillColor);
  fill.addColorStop(1, "rgba(0,0,0,0)");
  ctx.fillStyle = fill;
  ctx.fill();
}

function drawAllSparklines() {
  drawSparkline("spark-1", "rgba(99, 102, 241, 0.95)", "rgba(99, 102, 241, 0.22)", 0.18);
  drawSparkline("spark-2", "rgba(245, 158, 11, 0.92)", "rgba(245, 158, 11, 0.2)", 0.14);
  drawSparkline("spark-3", "rgba(244, 63, 94, 0.92)", "rgba(244, 63, 94, 0.2)", 0.22);
}

function drawFeature3Radar() {
  const targets = [nodes.feature3Radar, nodes.feature3RadarWorkspace].filter(Boolean);
  if (!targets.length) return;

  const axes = AppState.feature3.gap?.radar_chart?.axes || [];
  targets.forEach((canvas) => {
    const ratio = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    const width = Math.max(260, rect.width || 260);
    const height = Math.max(150, rect.height || 150);

    canvas.width = width * ratio;
    canvas.height = height * ratio;
    const ctx = canvas.getContext("2d");
    ctx.scale(ratio, ratio);
    ctx.clearRect(0, 0, width, height);

    const cx = width / 2;
    const cy = height / 2;
    const radius = Math.min(width, height) * 0.33;
    const count = Math.max(axes.length, 5);

    ctx.strokeStyle = "rgba(255,255,255,0.14)";
    for (let ring = 1; ring <= 4; ring += 1) {
      ctx.beginPath();
      ctx.arc(cx, cy, (radius * ring) / 4, 0, Math.PI * 2);
      ctx.stroke();
    }

    for (let i = 0; i < count; i += 1) {
      const angle = -Math.PI / 2 + (i * Math.PI * 2) / count;
      const x = cx + Math.cos(angle) * radius;
      const y = cy + Math.sin(angle) * radius;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(x, y);
      ctx.stroke();
    }

    if (!axes.length) return;

    const drawPolygon = (key, color) => {
      ctx.beginPath();
      axes.forEach((axis, i) => {
        const angle = -Math.PI / 2 + (i * Math.PI * 2) / axes.length;
        const value = clamp((axis[key] || 0) / 100, 0, 1);
        const x = cx + Math.cos(angle) * radius * value;
        const y = cy + Math.sin(angle) * radius * value;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.closePath();
      ctx.fillStyle = color.fill;
      ctx.strokeStyle = color.stroke;
      ctx.lineWidth = 1.6;
      ctx.fill();
      ctx.stroke();
    };

    drawPolygon("market_target", {
      fill: "rgba(244, 63, 94, 0.14)",
      stroke: "rgba(244, 63, 94, 0.48)"
    });
    drawPolygon("user", {
      fill: "rgba(45, 212, 191, 0.18)",
      stroke: "rgba(45, 212, 191, 0.68)"
    });
  });
  
  // Update match score display
  updateFeature3MatchScoreDisplay();
}

function updateFeature3MatchScoreDisplay() {
  const gap = AppState.feature3?.gap;
  const display = document.getElementById('feature3-match-score-display');
  const matchScoreValue = document.getElementById('feature3-match-score-value');
  const gapScoreValue = document.getElementById('feature3-gap-score-value');
  const missingSkillsList = document.getElementById('feature3-missing-skills-list');
  
  if (!gap || !display) return;
  
  // Show the display
  display.style.display = 'flex';
  
  // Update match score
  if (matchScoreValue) {
    const score = Math.round(gap.match_score || 0);
    matchScoreValue.textContent = score + '%';
    // Color code: green if >80, yellow if >60, red otherwise
    matchScoreValue.style.color = score >= 80 ? '#34d399' : score >= 60 ? '#fbbf24' : '#f87171';
  }
  
  // Update gap to top 10%
  if (gapScoreValue) {
    const gapScore = Math.round(gap.gap_to_top10_score || 0);
    gapScoreValue.textContent = gapScore + '%';
  }
  
  // Update missing skills
  if (missingSkillsList && gap.niche_recommendations) {
    const missingSkills = gap.niche_recommendations
      .slice(0, 5)
      .map(rec => rec.skill)
      .join(', ');
    missingSkillsList.textContent = missingSkills || 'None identified';
  }
}

function renderFeature3RoiBars() {
  const targets = [nodes.feature3RoiBars, nodes.feature3RoiBarsWorkspace].filter(Boolean);
  if (!targets.length) return;
  const paths = AppState.feature3.roi?.path_comparison?.paths || [];
  if (!paths.length) {
    targets.forEach((target) => {
      target.innerHTML = "<p class='text-xs text-white/50'>Run Skill Arbitrage to populate ROI path comparison.</p>";
    });
    return;
  }

  const max = Math.max(...paths.map((p) => p.projected_salary_usd), 1);
  const html = paths
    .map((p) => {
      const pct = clamp((p.projected_salary_usd / max) * 100, 8, 100);
      return `
        <div>
          <div class="flex justify-between text-[11px] text-white/75 mb-1">
            <span>${p.path}</span>
            <span>$${Math.round(p.projected_salary_usd)}</span>
          </div>
          <div class="roi-bar-wrap"><div class="roi-bar-fill" style="width:${pct}%;"></div></div>
        </div>
      `;
    })
    .join("");
  targets.forEach((target) => {
    target.innerHTML = html;
  });
}

function renderFeature3Workspace() {
  const f3 = AppState.feature3;
  const loading = Boolean(AppState.ui?.feature3Loading);

  if (nodes.feature3MarketTable) {
    const jobs = f3.market?.jobs || [];
    nodes.feature3MarketTable.innerHTML = loading
      ? stateCard("Loading market rows and compensation bands...", "loading")
      : jobs.length
      ? jobs
          .slice(0, 8)
          .map(
            (job) =>
              `<div class="workspace-list-card"><div class="flex justify-between"><span class="text-white/90">${job.title}</span><span class="text-indigo-200">$${Math.round(job.salary_mid || 0)}</span></div><div class="text-white/60 text-xs">${job.company} � ${job.location} � ${job.remote ? "Remote" : "Onsite"}</div></div>`
          )
          .join("")
      : stateCard("Run full arbitrage to load market rows.");
  }

  if (nodes.feature3RoadmapList) {
    const phases = f3.gap?.roadmap_to_90?.phases || [];
    nodes.feature3RoadmapList.innerHTML = loading
      ? stateCard("Generating 30/60/90 roadmap phases...", "loading")
      : phases.length
      ? phases
          .map(
            (phase) =>
              `<div class="workspace-list-card"><div class="text-white/90 font-semibold">${phase.phase} � ${phase.goal}</div><div class="text-white/65 text-xs mt-1">${(phase.actions || []).slice(0, 2).join(" ")}</div></div>`
          )
          .join("")
      : stateCard("Roadmap appears after gap analysis.");
  }

  if (nodes.feature3FutureList) {
    const pivot = f3.future?.industry_pivot_advice?.recommended_pivot;
    const freeze = f3.future?.hiring_freeze_alert?.alert_level;
    const ob = (f3.future?.obsolescence_tracker || []).slice(0, 3);
    nodes.feature3FutureList.innerHTML = pivot
      ? `<div class="workspace-list-card">Pivot: ${pivot}</div><div class="workspace-list-card">Freeze alert: ${freeze || "n/a"}</div>${ob
          .map((x) => `<div class="workspace-list-card text-xs">${x.skill_or_pattern}: risk ${x.risk_score}</div>`)
          .join("")}`
      : stateCard("Future insights will appear after full run.");
  }

  if (nodes.feature3SprintList) {
    const sprint = f3.sprint;
    const quiz = f3.quiz;
    const bullet = f3.resumeInject?.star_bullets?.[0];
    nodes.feature3SprintList.innerHTML = sprint
      ? `<div class="workspace-list-card">Sprint: ${sprint.primary_skill} � ${sprint.sprint_status}</div>
         <div class="workspace-list-card">Quiz: ${quiz ? `${quiz.score} (${quiz.passed ? "pass" : "retry"})` : "not attempted"}</div>
         <div class="workspace-list-card text-xs">${bullet || "Run Resume Inject to generate STAR bullet."}</div>`
      : stateCard("Sprint module appears after full arbitrage run.");
  }
}

function renderDashboard() {
  if (!nodes.dashboardProgress || !nodes.dashboardPlan) return;

  const dashboard = AppState.dashboard || {};
  const data = dashboard.data || {};
  const readiness = data.readiness || {};
  const latestAnalysis = data.latest_analysis || {};
  const interviewAnalysis = data.interview_analysis || {};
  const marketAnalysis = data.market_analysis || {};
  const analytics = data.analytics || {};
  const nextActions = Array.isArray(data.next_actions) ? data.next_actions : [];
  const statusIndicators = data.status_indicators || {};
  const score = Number(readiness.score ?? data.readiness_score ?? 0);
  const scoreMeta = dashboardStatusFromScore(score);
  const lastLoaded = dashboard.lastLoadedAt || data.generated_at || null;
  const chartData = Array.isArray(analytics.chart_data) && analytics.chart_data.length
    ? analytics.chart_data
    : (Array.isArray(analytics.snapshot_chart_data) ? analytics.snapshot_chart_data : []);
  const activityRows = Array.isArray(analytics.recent_activity) && analytics.recent_activity.length
    ? analytics.recent_activity
    : (AppState.ui?.activity || []).map((line) => ({ event_name: line, feature_area: "activity", occurred_at_utc: new Date().toISOString() }));

  if (nodes.dashboardSyncStatus) {
    if (dashboard.loading) {
      nodes.dashboardSyncStatus.textContent = "Syncing dashboard...";
    } else if (dashboard.error && !data.readiness) {
      nodes.dashboardSyncStatus.textContent = "Dashboard offline";
    } else if (lastLoaded) {
      nodes.dashboardSyncStatus.textContent = `Live ${formatDashboardTimestamp(lastLoaded)}`;
    } else {
      nodes.dashboardSyncStatus.textContent = "Dashboard idle";
    }
  }

  if (nodes.dashboardReadinessScore) {
    nodes.dashboardReadinessScore.textContent = dashboard.loading ? "--" : `${Math.round(score)}%`;
  }
  if (nodes.dashboardReadinessLabel) {
    nodes.dashboardReadinessLabel.textContent = dashboard.loading
      ? "Loading live dashboard data"
      : readiness.label || scoreMeta.label;
    nodes.dashboardReadinessLabel.style.color = scoreMeta.tone;
  }
  if (nodes.dashboardReadinessSummary) {
    nodes.dashboardReadinessSummary.textContent = dashboard.loading
      ? "Pulling latest resume, interview, and market signals..."
      : readiness.formula || latestAnalysis.summary || "Connects your resume, interview, and market signals into one score.";
  }
  if (nodes.dashboardGeneratedAt) {
    nodes.dashboardGeneratedAt.textContent = lastLoaded ? `Updated ${formatDashboardTimestamp(lastLoaded)}` : "Not loaded";
  }

  if (dashboard.loading && !data.readiness) {
    nodes.dashboardProgress.innerHTML = stateStack([
      "Loading dashboard signals...",
      "Resolving resume, interview, and market data...",
      "Preparing analytics cards and status summary..."
    ], "loading");
    nodes.dashboardPlan.innerHTML = stateStack([
      "Loading your readiness signals...",
      "Syncing resume, interview, and market data..."
    ], "loading");
    renderDashboardBreakdown([]);
    renderDashboardChart([]);
    renderDashboardActivity([]);
  } else if (dashboard.error && !data.readiness) {
    nodes.dashboardProgress.innerHTML = `<div class="dashboard-empty-state">${dashboard.error}</div>`;
    nodes.dashboardPlan.innerHTML = `<div class="dashboard-empty-state">${dashboard.error}</div>`;
    renderDashboardBreakdown([]);
    renderDashboardChart([]);
    renderDashboardActivity([]);
  } else {
    const hasLens = Boolean(latestAnalysis.analysis_id || AppState.feature1.analysis);
    const hasRebound = Boolean(interviewAnalysis.interview_id || AppState.feature2.interview);
    const hasArbitrage = Boolean(marketAnalysis.gap_snapshot_id || AppState.feature3.gap);
    const hasNarrative = Boolean(AppState.feature5.session);

    const steps = [
      {
        done: hasLens,
        title: "Step 1: Resume intelligence",
        desc: latestAnalysis.summary || "Analyze your resume for ATS and semantic fit."
      },
      {
        done: hasRebound,
        title: "Step 2: Interview recovery",
        desc: interviewAnalysis.summary || "Debrief interviews and identify next steps."
      },
      {
        done: hasArbitrage,
        title: "Step 3: Skill gap + market fit",
        desc: marketAnalysis.summary || "Find high-ROI skills to accelerate your fit."
      },
      {
        done: hasNarrative,
        title: "Step 4: Narrative + portfolio",
        desc: "Build STAR stories and exportable portfolio."
      },
    ];

    nodes.dashboardProgress.innerHTML = [
      data.readiness_score != null
        ? `<div class="workspace-list-card"><div class="flex items-center justify-between"><span class="text-white/90">Overall readiness</span><span class="text-[11px]" style="color:${scoreMeta.tone}">${readiness.label || scoreMeta.label}</span></div><div class="text-xs text-white/65 mt-1">${readiness.formula || "Normalized weighted average of the available signals."}</div></div>`
        : `<div class="dashboard-empty-state">No readiness score yet. Start with Feature 1 to generate your first signal.</div>`,
      ...steps.map((step) => `<div class="workspace-list-card"><div class="flex items-center justify-between"><span class="text-white/90">${step.title}</span><span class="text-[11px] ${step.done ? "text-emerald-300" : "text-amber-300"}">${step.done ? "Done" : "Pending"}</span></div><div class="text-xs text-white/65 mt-1">${step.desc}</div></div>`)
    ].join("");

    const topAction = nextActions[0] || smartActionMeta();
    const pipeline = data.job_pipeline || {};
    const pipelineSummary = ["Wishlist", "Applied", "Interviewing", "Offered", "Rejected"]
      .map((status) => `${status}: ${pipeline[status] ?? 0}`)
      .join(" · ");

    nodes.dashboardPlan.innerHTML = `
      <div class="workspace-list-card"><div class="flex items-center justify-between gap-2"><span class="text-white/90">${topAction.label.replace(/^Next Best Action:\s*/, "")}</span><span class="text-[11px]" style="color:${scoreMeta.tone}">${statusIndicators.ready_to_apply ? "Ready to Apply" : scoreMeta.label}</span></div><div class="text-xs text-white/65 mt-1">${topAction.reason || "Recommended next step based on your readiness signals."}</div></div>
      <div class="workspace-list-card text-xs">Pipeline: ${pipelineSummary || "No jobs logged yet."}</div>
      <div class="workspace-list-card text-xs">Current mode: ${(AppState.ui?.mode || "beginner").toUpperCase()}</div>
    `;

    if (nodes.dashboardFeatureExplainer) {
      const explainer = [
        { view: "lens-engine", name: "Lens", desc: "Resume intelligence and ATS scoring.", done: hasLens },
        { view: "rebound", name: "Rebound", desc: "Interview recovery and follow-up analysis.", done: hasRebound },
        { view: "arbitrage", name: "Skill Arbitrage", desc: "Market-fit gap analysis and sprint planning.", done: hasArbitrage },
        { view: "narrative", name: "Narrative Architect", desc: "Portfolio and STAR-story generation.", done: hasNarrative },
        { view: "persona-play", name: "Persona Coach", desc: "Practice high-pressure mock interviews.", done: Boolean(AppState.feature4.session) },
      ];

      nodes.dashboardFeatureExplainer.innerHTML = explainer
        .map((item) => `
          <button class="feature-chip w-full" data-view="${item.view}">
            <span class="feature-chip-title">${item.name}</span>
            <span class="feature-chip-state ${item.done ? "done" : "pending"}">${item.done ? "Ready" : "Pending"}</span>
            <span class="feature-chip-desc">${item.desc}</span>
          </button>
        `)
        .join("");
    }

    renderDashboardBreakdown(readiness.components || []);
    renderDashboardChart(chartData);
    renderDashboardActivity(activityRows);

    if (nodes.dashboardNextAction) {
      nodes.dashboardNextAction.textContent = topAction.label || "Run Next Action";
    }
  }

  if (nodes.onboardingStatus) {
    const doneCount = [
      Boolean(latestAnalysis.analysis_id || AppState.feature1.analysis),
      Boolean(interviewAnalysis.interview_id || AppState.feature2.interview),
      Boolean(marketAnalysis.gap_snapshot_id || AppState.feature3.gap),
      Boolean(AppState.feature5.session)
    ].filter(Boolean).length;
    nodes.onboardingStatus.textContent = `Step ${Math.min(doneCount + 1, 4)} of 4`;
  }

  if (nodes.onboardingCandidateId && !nodes.onboardingCandidateId.matches(":focus")) {
    nodes.onboardingCandidateId.value = nodes.candidateId.value || "candidate-001";
  }
  if (nodes.onboardingJobCategory && !nodes.onboardingJobCategory.matches(":focus")) {
    nodes.onboardingJobCategory.value = nodes.jobCategory.value || "frontend";
  }
  if (nodes.onboardingJobDescription && !nodes.onboardingJobDescription.matches(":focus")) {
    nodes.onboardingJobDescription.value = nodes.jobDescription.value || "";
  }
}

function applyViewState(viewName) {
  const showDashboard = viewName === "dashboard";
  const showLens = viewName === "lens-engine";
  const showArbitrage = viewName === "arbitrage";
  const showPersona = viewName === "persona-play";
  const showNarrative = viewName === "narrative";
  const showJobTracker = viewName === "job-tracker";
  const showRebound = viewName === "rebound";
  nodes.dashboardView.classList.toggle("hidden", !showDashboard);
  nodes.commandCenterView.classList.toggle("hidden", showDashboard || showLens || showArbitrage || showPersona || showNarrative || showJobTracker || showRebound);
  nodes.lensWorkspace.classList.toggle("hidden", !showLens);
  nodes.feature3Workspace.classList.toggle("hidden", !showArbitrage);
  nodes.feature4Workspace.classList.toggle("hidden", !showPersona);
  nodes.feature5Workspace.classList.toggle("hidden", !showNarrative);
  if (nodes.feature5Workspace) {
    nodes.feature5Workspace.style.display = showNarrative ? "flex" : "none";
  }
  const jtView = document.getElementById("job-tracker-view");
  if (jtView) jtView.classList.toggle("hidden", !showJobTracker);
  const reboundView = document.getElementById("rebound-workspace");
  if (reboundView) reboundView.classList.toggle("hidden", !showRebound);

  // Update active nav button
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === viewName);
  });
}

function animateWavePath() {
  if (!nodes.wavePath) return; // wave SVG removed from simplified layout
  const t = performance.now() / 380;
  const level = AppState.audioLevel;
  const amplitude = 10 + level * 22;
  const path = [];
  path.push("M0,48");

  for (let x = 0; x <= 320; x += 32) {
    const y =
      48 +
      Math.sin(x / 30 + t) * amplitude * 0.42 +
      Math.cos(x / 42 - t * 0.8) * amplitude * 0.23;
    const cx = x + 16;
    const cy = 48 + Math.sin(x / 25 + t * 1.2) * amplitude * 0.3;
    path.push(`Q${cx},${cy} ${x + 32},${clamp(y, 12, 84)}`);
  }

  nodes.wavePath.setAttribute("d", path.join(" "));
  requestAnimationFrame(animateWavePath);
}

function renderFeature1Summary() {
  const analysis = AppState.feature1.analysis;
  const loading = Boolean(AppState.ui?.feature1Loading);
  if (loading) {
    nodes.summaryCards.innerHTML = stateStack([
      "Hiring Lens is scanning PDF layout and ATS structure...",
      "Scoring visual hierarchy, semantic match, and benchmark fit."
    ], "loading");
    return;
  }
  if (!analysis) {
    nodes.summaryCards.innerHTML = stateStack([
      "Hiring Lens API: Awaiting analysis run.",
      "Version tracker: Not loaded."
    ]);
    return;
  }

  const scores = analysis.score ?? {};
  const summaries = analysis.summaries;
  const recs = analysis.recommendations.slice(0, 2);

  nodes.summaryCards.innerHTML = `
    ${Object.entries(scores)
      .filter(([k]) => k !== "overall")
      .map(([k, v]) => renderScoreCard(k, v))
      .join("")}
    <div class="thin-glass rounded-lg p-2 text-xs text-white/70">${summaries.visual}</div>
    <div class="thin-glass rounded-lg p-2 text-xs text-white/70">${recs.join(" ")}</div>
  `;
}

function renderVersions() {
  const versions = AppState.feature1.versions;
  if (!versions.length) {
    nodes.versionList.innerHTML = stateCard("No versions yet.");
    return;
  }

  nodes.versionList.innerHTML = versions
    .map(
      (v) =>
        `<div class="rounded bg-white/5 px-2 py-1 flex justify-between"><span>v${v.version_number} ${v.job_category}</span><span class="text-indigo-200">${v.overall_score}</span></div>`
    )
    .join("");
}

function renderFeature2Output() {
  const feature2 = AppState.feature2;
  const loading = Boolean(AppState.ui?.feature2Loading);
  if (loading) {
    if (nodes.feature2Output) {
      nodes.feature2Output.innerHTML = stateStack([
        "Interview Autopsy autopsy is running...",
        "Extracting pattern breaks, trend deltas, and forecast trajectory."
      ], "loading");
    }
    return;
  }
  if (!feature2.interview && !feature2.quickDebrief && !feature2.trend) {
    if (nodes.feature2Output) nodes.feature2Output.innerHTML = stateCard("Interview Autopsy API: Awaiting autopsy run.");
    return;
  }

  const blocks = [];

  if (feature2.interview) {
    const s = feature2.interview.score;
    blocks.push(`<p><span class='text-white/90'>Autopsy #${feature2.interview.interview_id}</span> | Overall ${s.overall_autopsy_score}</p>`);
    blocks.push(`<p>Tech ${s.technical_accuracy} | Behavioral ${s.behavioral_quality} | Recovery ${s.strategic_recovery_readiness}</p>`);
    const recommendation = feature2.interview.strategic_actions?.resilience_prompt || "";
    if (recommendation) blocks.push(`<p class='text-white/60'>${recommendation}</p>`);
  }

  if (feature2.quickDebrief) {
    blocks.push(`<p><span class='text-white/90'>Quick Debrief:</span> ${feature2.quickDebrief.extracted_hardest_question}</p>`);
  }

  if (feature2.trend) {
    blocks.push(`<p><span class='text-white/90'>Trend:</span> overall delta ${feature2.trend.trend_summary.overall_delta}</p>`);
  }

  if (feature2.forecast) {
    blocks.push(`<p><span class='text-white/90'>Forecast:</span> ${feature2.forecast.forecast_label} (${feature2.forecast.expected_offer_window_weeks}w)</p>`);
  }

  const html = blocks.map((b) => `<div class='thin-glass rounded px-2 py-1'>${b}</div>`).join("");
  if (nodes.feature2Output) nodes.feature2Output.innerHTML = html;
}

function renderReboundWorkspace() {
  const f2 = AppState.feature2;
  const loading = Boolean(AppState.ui?.feature2Loading);

  // Output board
  if (nodes.reboundOutputBoard) {
    if (loading) {
      nodes.reboundOutputBoard.innerHTML = stateStack([
        "Running interview autopsy...",
        "Analyzing technical accuracy, behavioral patterns, and recovery signals..."
      ], "loading");
    } else if (!f2.interview && !f2.quickDebrief) {
      nodes.reboundOutputBoard.innerHTML = stateCard("Run Full Autopsy or Quick Debrief to see results here.");
    } else {
      const blocks = [];
      if (f2.interview) {
        const s = f2.interview.score || {};
        blocks.push(`<div class="workspace-list-card"><span style="color:rgba(255,255,255,0.9);font-weight:600">Autopsy #${f2.interview.interview_id}</span></div>`);
        blocks.push(`<div class="workspace-list-card">Overall Score: <strong style="color:#34d399">${s.overall_autopsy_score ?? "n/a"}</strong></div>`);
        blocks.push(`<div class="workspace-list-card text-xs">Technical Accuracy: ${s.technical_accuracy ?? "n/a"} &nbsp;|&nbsp; Behavioral: ${s.behavioral_quality ?? "n/a"} &nbsp;|&nbsp; Recovery: ${s.strategic_recovery_readiness ?? "n/a"}</div>`);
        const tech = f2.interview.technical || {};
        if (tech.false_confidence_zones?.length) {
          blocks.push(`<div class="workspace-list-card text-xs" style="border-color:rgba(248,113,113,0.3)">⚠ False confidence: ${tech.false_confidence_zones.slice(0,2).join(", ")}</div>`);
        }
        const behav = f2.interview.behavioral || {};
        if (behav.filler_word_count) {
          blocks.push(`<div class="workspace-list-card text-xs">Filler words: ${behav.filler_word_count} &nbsp;|&nbsp; STAR compliance: ${behav.star_compliance_score ?? "n/a"}</div>`);
        }
        const resilience = f2.interview.strategic_actions?.resilience_prompt;
        if (resilience) blocks.push(`<div class="workspace-list-card text-xs" style="color:rgba(165,180,252,0.9)">${resilience}</div>`);
      }
      if (f2.quickDebrief) {
        blocks.push(`<div class="workspace-list-card"><span style="color:rgba(255,255,255,0.9);font-weight:600">Quick Debrief</span></div>`);
        if (f2.quickDebrief.extracted_hardest_question) {
          blocks.push(`<div class="workspace-list-card text-xs">Hardest Q: ${f2.quickDebrief.extracted_hardest_question}</div>`);
        }
        if (f2.quickDebrief.immediate_action) {
          blocks.push(`<div class="workspace-list-card text-xs">Action: ${f2.quickDebrief.immediate_action}</div>`);
        }
      }
      nodes.reboundOutputBoard.innerHTML = blocks.join("");
    }
  }

  // Trend board
  if (nodes.reboundTrendBoard) {
    if (!f2.trend && !f2.forecast) {
      nodes.reboundTrendBoard.innerHTML = stateCard("Load Trend to see your interview performance over time.");
    } else {
      const blocks = [];
      if (f2.trend) {
        const ts = f2.trend.trend_summary || {};
        blocks.push(`<div class="workspace-list-card">Overall delta: <strong style="color:${ts.overall_delta >= 0 ? "#34d399" : "#f87171"}">${ts.overall_delta >= 0 ? "+" : ""}${ts.overall_delta ?? "n/a"}</strong></div>`);
        blocks.push(`<div class="workspace-list-card text-xs">Interviews tracked: ${f2.trend.interview_count ?? "n/a"}</div>`);
        const signals = f2.trend.rejection_category_signals || [];
        if (signals.length) {
          blocks.push(`<div class="workspace-list-card text-xs">Top rejection signal: ${signals[0].category} (${signals[0].frequency}x)</div>`);
        }
      }
      if (f2.forecast) {
        blocks.push(`<div class="workspace-list-card">Forecast: <strong style="color:#a5b4fc">${f2.forecast.forecast_label ?? "n/a"}</strong></div>`);
        if (f2.forecast.expected_offer_window_weeks) {
          blocks.push(`<div class="workspace-list-card text-xs">Expected offer window: ${f2.forecast.expected_offer_window_weeks} weeks</div>`);
        }
        if (f2.forecast.readiness_score) {
          blocks.push(`<div class="workspace-list-card text-xs">Readiness score: ${f2.forecast.readiness_score}</div>`);
        }
      }
      nodes.reboundTrendBoard.innerHTML = blocks.join("");
    }
  }

  // Recovery actions board
  if (nodes.reboundActionsBoard) {
    const interview = f2.interview;
    if (!interview) {
      nodes.reboundActionsBoard.innerHTML = stateCard("Recovery actions appear after running Full Autopsy.");
    } else {
      const actions = interview.strategic_actions || {};
      const blocks = [];
      if (actions.clarification_email_draft) {
        blocks.push(`<div class="workspace-list-card"><span style="color:rgba(255,255,255,0.9);font-weight:600">📧 Clarification Email</span><p class="text-xs mt-1" style="color:rgba(255,255,255,0.6)">${String(actions.clarification_email_draft).slice(0, 200)}...</p></div>`);
      }
      if (actions.follow_up_cadence?.length) {
        blocks.push(`<div class="workspace-list-card text-xs"><span style="color:rgba(255,255,255,0.9)">📅 Follow-up:</span> ${actions.follow_up_cadence[0]}</div>`);
      }
      if (actions.negotiation_script) {
        blocks.push(`<div class="workspace-list-card text-xs"><span style="color:rgba(255,255,255,0.9)">💰 Negotiation:</span> ${String(actions.negotiation_script).slice(0, 150)}...</div>`);
      }
      if (actions.code_patch_suggestions?.length) {
        blocks.push(`<div class="workspace-list-card text-xs"><span style="color:rgba(255,255,255,0.9)">🔧 Code Patch:</span> ${actions.code_patch_suggestions[0]}</div>`);
      }
      if (!blocks.length) {
        blocks.push(stateCard("No recovery actions generated. Try running Full Autopsy with more interview details."));
      }
      nodes.reboundActionsBoard.innerHTML = blocks.join("");
    }
  }
}

async function runFeature4PersonaPlay() {
  // Read from dedicated workspace panel inputs first, fall back to legacy IDs
  const candidateId = (nodes.feature4WorkspaceCandidateId?.value?.trim()
    || nodes.candidateId?.value?.trim()
    || "candidate-001");

  const personaMode = (nodes.feature4WorkspacePersonaMode?.value
    || nodes.feature4PersonaMode?.value
    || "blind");

  const language = (nodes.feature4WorkspaceLanguage?.value
    || nodes.feature4Language?.value
    || "english");

  const topic = nodes.feature4WorkspaceTopic?.value?.trim() || "Software Engineering";
  const roleName = topic || nodes.feature2Role?.value?.trim() || "Software Engineer";

  // For persona coach, we don't need pre-existing notes — the AI generates questions
  // Use topic as the seed utterance if no notes exist
  const rawText = nodes.feature2Notes?.value?.trim()
    || nodes.feature2Transcript?.value?.trim()
    || `I want to practice a mock interview for ${roleName}. Topic: ${topic}.`;

  const utterances = rawText
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean)
    .slice(0, 5);

  if (!utterances.length) {
    utterances.push(rawText.slice(0, 400));
  }

  let loader = null;
  try {
    // Show loading in the session board (visible on the workspace)
    if (nodes.feature4SessionBoard) {
      nodes.feature4SessionBoard.innerHTML = `<div class="state-card state-loading" style="display:flex;align-items:center;gap:10px"><div style="width:8px;height:8px;border-radius:50%;background:#818cf8;animation:pulse 1s ease-in-out infinite;flex-shrink:0"></div>Starting persona session...</div>`;
    }
    setUiFlag("feature4Loading", true);
    if (nodes.feature4WorkspaceRun) nodes.feature4WorkspaceRun.disabled = true;
    if (nodes.feature4WorkspaceRunPanel) nodes.feature4WorkspaceRunPanel.disabled = true;
    setStatus("Persona Coach: starting persona session...");
    const sessionResp = await apiFetch(`${API_BASE}/api/feature4/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        candidate_id: candidateId,
        role_name: roleName,
        persona_mode: personaMode,
        language,
        include_video: true,
        environment_theme: "zoom"
      })
    });
    if (!sessionResp.ok) throw new Error(await sessionResp.text());
    const sessionData = await sessionResp.json();

    let lastTurn = null;
    const turns = [];
    for (let i = 0; i < utterances.length; i += 1) {
      const utterance = utterances[i];
      setStatus(`Persona Coach: analyzing turn ${i + 1}/${utterances.length}...`);
      const turnResp = await apiFetch(`${API_BASE}/api/feature4/sessions/${sessionData.session_id}/turn`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          utterance,
          response_latency_ms: Math.round(1300 + i * 260 + Math.random() * 220),
          audio_pitch_variance: clamp(0.48 + i * 0.03 + Math.random() * 0.12, 0.35, 0.92),
          silent_seconds: clamp(0.6 + Math.random() * 1.2, 0.2, 2.4),
          gaze_focus_ratio: clamp(0.55 + Math.random() * 0.35, 0.2, 0.98)
        })
      });
      if (!turnResp.ok) throw new Error(await turnResp.text());
      lastTurn = await turnResp.json();
      turns.push(lastTurn);
      AppState.setState({
        feature4: {
          ...AppState.feature4,
          session: sessionData,
          lastTurn,
          turns,
          prompt: lastTurn.next_question?.question || null,
          final: null,
          synthesis: null,
          share: null,
          compare: null
        }
      });
    }

    setStatus("Persona Coach: finalizing coach report...");
    const finalResp = await apiFetch(`${API_BASE}/api/feature4/sessions/${sessionData.session_id}/finalize`, { method: "POST" });
    if (!finalResp.ok) throw new Error(await finalResp.text());
    const finalData = await finalResp.json();

    setStatus("Persona Coach: preparing voice/video synthesis...");
    const synthResp = await apiFetch(`${API_BASE}/api/feature4/sessions/${sessionData.session_id}/synthesis`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        voice_style: "calm",
        avatar_style: "mentor",
        language,
        environment_theme: "zoom"
      })
    });
    if (!synthResp.ok) throw new Error(await synthResp.text());
    const synthesis = await synthResp.json();

    AppState.setState({
      feature4: {
        session: sessionData,
        lastTurn,
        turns,
        final: finalData,
        synthesis,
        share: null,
        compare: null,
        prompt: lastTurn?.next_question?.question || null,
        history: AppState.feature4.history || []
      }
    });
    await loadFeature4History();
    setStatus(`Persona Coach complete - overall ${finalData.scorecard.overall}`);
  } catch (error) {
    setStatus(handleApiError(error, "Persona Coach"));
    if (nodes.feature4SessionBoard) {
      nodes.feature4SessionBoard.innerHTML = `<div class="state-card" style="color:#f87171">Error: ${handleApiError(error, "Persona Coach")}</div>`;
    }
  } finally {
    loader?.stop();
    if (nodes.runFeature4) nodes.runFeature4.disabled = false;
    if (nodes.feature4WorkspaceRun) nodes.feature4WorkspaceRun.disabled = false;
    if (nodes.feature4WorkspaceRunPanel) nodes.feature4WorkspaceRunPanel.disabled = false;
    setUiFlag("feature4Loading", false);
  }
}

async function finalizeFeature4Again() {
  const sid = AppState.feature4.session?.session_id;
  if (!sid) {
    setStatus("Run Persona Coach first.");
    return;
  }
  try {
    const finalResp = await apiFetch(`${API_BASE}/api/feature4/sessions/${sid}/finalize`, { method: "POST" });
    if (!finalResp.ok) throw new Error(await finalResp.text());
    const finalData = await finalResp.json();
    AppState.setState({ feature4: { ...AppState.feature4, final: finalData } });
    setStatus("Persona Coach coach report refreshed.");
  } catch (error) {
    setStatus(`Persona Coach finalize error: ${String(error.message).slice(0, 120)}`);
  }
}

async function shareFeature4Session() {
  const sid = AppState.feature4.session?.session_id;
  if (!sid) {
    setStatus("Run Persona Coach first.");
    return;
  }
  try {
    const response = await apiFetch(`${API_BASE}/api/feature4/sessions/${sid}/share`, { method: "POST" });
    if (!response.ok) throw new Error(await response.text());
    const share = await response.json();
    AppState.setState({ feature4: { ...AppState.feature4, share } });
    setStatus("Persona Coach share link generated.");
  } catch (error) {
    setStatus(`Persona Coach share error: ${String(error.message).slice(0, 120)}`);
  }
}

async function loadFeature4History() {
  const candidateId = nodes.candidateId.value.trim() || "candidate-001";
  try {
    const response = await apiFetch(`${API_BASE}/api/feature4/candidate/${encodeURIComponent(candidateId)}/sessions`);
    if (!response.ok) throw new Error(await response.text());
    const payload = await response.json();
    AppState.setState({
      feature4: {
        ...AppState.feature4,
        history: payload.sessions || []
      }
    });
    setStatus(`Persona Coach history loaded (${(payload.sessions || []).length} sessions).`);
  } catch (error) {
    setStatus(`Persona Coach history error: ${String(error.message).slice(0, 120)}`);
  }
}

async function compareLatestFeature4Sessions() {
  const candidateId = nodes.candidateId.value.trim() || "candidate-001";
  const history = AppState.feature4.history || [];
  if (history.length < 2) {
    setStatus("Load history with at least 2 sessions to compare.");
    return;
  }

  const left = history[1]?.session_id;
  const right = history[0]?.session_id;
  if (!left || !right) {
    setStatus("Could not resolve sessions for compare.");
    return;
  }

  try {
    const url = `${API_BASE}/api/feature4/candidate/${encodeURIComponent(candidateId)}/heatmap-compare?left_session=${left}&right_session=${right}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(await response.text());
    const compare = await response.json();
    AppState.setState({
      feature4: {
        ...AppState.feature4,
        compare
      }
    });
    setStatus(`Persona Coach compare ready: sessions ${left} vs ${right}.`);
  } catch (error) {
    setStatus(`Persona Coach compare error: ${String(error.message).slice(0, 120)}`);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// FEATURE 4: INTERACTIVE TURN-BY-TURN MOCK INTERVIEW FUNCTIONS
// Member 2 implementation - simplified browser-friendly flow
// ═══════════════════════════════════════════════════════════════════════════

let currentMockSessionId = null;
let currentQuestionIndex = 0;
let conversationLog = [];
let interactiveMode = false; // Toggle between batch mode and interactive mode

/**
 * Start a new mock interview session (interactive mode)
 * Uses the simplified /turn-text endpoint for browser-friendly interaction
 * This is called when user wants turn-by-turn interaction
 */
async function startMockInterview() {
  const candidateId = getCurrentCandidateId();
  const roleName = nodes.feature4WorkspaceTopic?.value?.trim() || "Software Engineer";
  const personaMode = nodes.feature4WorkspacePersonaMode?.value || "blind";
  const language = nodes.feature4WorkspaceLanguage?.value || "english";
  const targetCompany = "";

  if (!roleName) {
    alert('Please enter target role or interview topic');
    return;
  }

  try {
    setStatus("Starting mock interview session...");
    setUiFlag("feature4Loading", true);
    if (nodes.feature4WorkspaceRun) nodes.feature4WorkspaceRun.disabled = true;
    if (nodes.feature4WorkspaceRunPanel) nodes.feature4WorkspaceRunPanel.disabled = true;

    // Create session
    const response = await apiFetch(`${API_BASE}/api/feature4/sessions`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        candidate_id: candidateId,
        role_name: roleName,
        persona_mode: personaMode,
        selected_persona: personaMode === 'blind' ? null : personaMode,
        target_company: targetCompany,
        language: language,
        include_video: false
      })
    });

    if (!response.ok) throw new Error('Failed to start session');

    const data = await response.json();
    currentMockSessionId = data.session_id;
    currentQuestionIndex = 0;
    conversationLog = [];
    interactiveMode = true;

    // Update AppState
    AppState.setState({
      feature4: {
        ...AppState.feature4,
        session: data,
        turns: [],
        lastTurn: null,
        final: null
      }
    });

    // Display first question
    const firstQuestion = data.opening_questions?.[0]?.question_text || "Tell me about yourself.";
    addToConversationLog('interviewer', firstQuestion);

    setStatus(`Mock interview started - ${data.persona.label}. Type your answer in the Topic field and click Submit Answer.`);
    setUiFlag("feature4Loading", false);
    if (nodes.feature4WorkspaceRun) nodes.feature4WorkspaceRun.disabled = false;
    if (nodes.feature4WorkspaceRunPanel) nodes.feature4WorkspaceRunPanel.disabled = false;

  } catch (error) {
    console.error('Session start error:', error);
    setStatus(handleApiError(error, "Mock Interview"));
    setUiFlag("feature4Loading", false);
    if (nodes.feature4WorkspaceRun) nodes.feature4WorkspaceRun.disabled = false;
    if (nodes.feature4WorkspaceRunPanel) nodes.feature4WorkspaceRunPanel.disabled = false;
  }
}

/**
 * Submit a single answer turn (interactive mode)
 * Uses the simplified /turn-text endpoint
 */
async function submitAnswer() {
  if (!currentMockSessionId) {
    alert('Please start a mock interview first');
    return;
  }

  // Get answer from workspace topic input (reused as answer input during session)
  const answerText = nodes.feature4WorkspaceTopic?.value?.trim() || "";

  if (!answerText) {
    alert('Please enter your answer in the Interview Topic field');
    return;
  }

  try {
    setStatus("Analyzing your answer...");
    setUiFlag("feature4Loading", true);

    // Use simplified turn-text endpoint (browser-friendly, no signal params needed)
    const response = await apiFetch(`${API_BASE}/api/feature4/sessions/${currentMockSessionId}/turn-text`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        utterance: answerText
      })
    });

    if (!response.ok) throw new Error('Failed to submit answer');

    const data = await response.json();

    // Add answer to conversation
    addToConversationLog('candidate', answerText);

    // Update AppState with turn data
    const updatedTurns = [...(AppState.feature4.turns || []), data];
    AppState.setState({
      feature4: {
        ...AppState.feature4,
        lastTurn: data,
        turns: updatedTurns
      }
    });

    // Show real-time feedback
    if (nodes.feature4LiveHints) {
      // Calculate depth score from available signals
      const fillerScore = data.realtime_signals?.filler_tracker?.score || 0;
      const confidenceScore = data.realtime_signals?.pitch_analysis?.confidence_score || 0;
      const silenceScore = data.realtime_signals?.silence_detection?.score || 0;
      const gazeScore = data.realtime_signals?.gaze_tracking?.eye_contact_score || 0;
      
      // Average of all signal scores as depth indicator
      const depthScore = Math.round((fillerScore + confidenceScore + silenceScore + gazeScore) / 4);
      
      const whisperHint = data.whisper_hint || "Keep going...";
      const tradeoffDepth = data.deep_logic?.analysis?.tradeoff_depth || "needs_depth";
      const hedgeDetected = data.deep_logic?.analysis?.hedge_detected || false;
      
      nodes.feature4LiveHints.innerHTML = `
        <div class="workspace-list-card text-xs" style="border-left:3px solid rgba(99,102,241,0.9)">💡 <strong>Whisper Hint:</strong> ${whisperHint}</div>
        <div class="workspace-list-card text-xs">Depth Score: <strong style="color:${depthScore >= 70 ? '#34d399' : depthScore >= 50 ? '#fbbf24' : '#f87171'}">${depthScore}/100</strong></div>
        <div class="workspace-list-card text-xs">Filler: ${Math.round(fillerScore)} | Confidence: ${Math.round(confidenceScore)} | Silence: ${Math.round(silenceScore)} | Gaze: ${Math.round(gazeScore)}</div>
        ${tradeoffDepth === 'needs_depth' ? `<div class="workspace-list-card text-xs" style="color:rgba(248,113,113,0.9)">⚠️ Add explicit tradeoffs and downsides</div>` : ''}
        ${hedgeDetected ? `<div class="workspace-list-card text-xs" style="color:rgba(251,191,36,0.9)">⚠️ Reduce hedging language</div>` : ''}
        <div class="workspace-list-card text-xs">Turn: ${updatedTurns.length}</div>
      `;
    }

    // Add next question after a brief delay
    if (data.next_question) {
      setTimeout(() => {
        addToConversationLog('interviewer', data.next_question.question_text);
        // Clear answer input
        if (nodes.feature4WorkspaceTopic) {
          nodes.feature4WorkspaceTopic.value = '';
          nodes.feature4WorkspaceTopic.placeholder = 'Type your answer here...';
        }
        currentQuestionIndex++;
      }, 1500);
    } else {
      // No more questions - suggest ending session
      setStatus(`Turn ${updatedTurns.length} complete. Click "End Session" to get your final report.`);
    }

    setStatus(`Turn ${updatedTurns.length} analyzed - depth score: ${Math.round((data.realtime_signals?.filler_tracker?.score || 0 + data.realtime_signals?.pitch_analysis?.confidence_score || 0 + data.realtime_signals?.silence_detection?.score || 0 + data.realtime_signals?.gaze_tracking?.eye_contact_score || 0) / 4)}`);
    setUiFlag("feature4Loading", false);

  } catch (error) {
    console.error('Answer submission error:', error);
    setStatus(handleApiError(error, "Mock Interview"));
    setUiFlag("feature4Loading", false);
  }
}

/**
 * End the mock interview session and get final report
 */
async function endSession() {
  if (!currentMockSessionId) {
    alert('No active session to end');
    return;
  }

  if (!confirm('Are you sure you want to end the interview and get your final report?')) return;

  try {
    setStatus("Finalizing interview session...");
    setUiFlag("feature4Loading", true);

    const response = await apiFetch(`${API_BASE}/api/feature4/sessions/${currentMockSessionId}/finalize`, {
      method: 'POST'
    });

    if (!response.ok) throw new Error('Failed to finalize session');

    const data = await response.json();

    // Update AppState with final report
    AppState.setState({
      feature4: {
        ...AppState.feature4,
        final: data
      }
    });

    // Display final report in coach board
    if (nodes.feature4CoachBoard) {
      const scorecard = data.scorecard || {};
      const strengths = data.synthesis?.strengths || [];
      const weaknesses = data.synthesis?.weaknesses || [];
      const badges = data.badges?.earned || [];
      
      nodes.feature4CoachBoard.innerHTML = `
        <div class="workspace-list-card"><span style="color:rgba(255,255,255,0.9);font-weight:600">📊 Final Interview Report</span></div>
        <div class="workspace-list-card">Overall Score: <strong style="color:#34d399">${scorecard.overall || 'N/A'}</strong></div>
        <div class="workspace-list-card text-xs">Logic Depth: ${scorecard.logic_depth || 'N/A'} | Behavioral: ${scorecard.behavioral_control || 'N/A'} | Confidence: ${scorecard.confidence_delivery || 'N/A'}</div>
        ${badges.length ? `<div class="workspace-list-card text-xs"><strong>🏆 Badges Earned:</strong> ${badges.join(', ')}</div>` : ''}
        ${strengths.length ? `<div class="workspace-list-card text-xs"><strong style="color:#34d399">✅ Strengths:</strong><br>${strengths.slice(0, 3).join('<br>')}</div>` : ''}
        ${weaknesses.length ? `<div class="workspace-list-card text-xs"><strong style="color:#fbbf24">⚠️ Areas to Improve:</strong><br>${weaknesses.slice(0, 3).join('<br>')}</div>` : ''}
        <div class="workspace-list-card text-xs" style="color:rgba(165,180,252,0.9)">Session #${currentMockSessionId} completed with ${(AppState.feature4.turns || []).length} turns</div>
      `;
    }

    // Show AI coaching insights if available
    if (data.ai_coaching_report && nodes.feature4LiveHints) {
      const coaching = data.ai_coaching_report;
      nodes.feature4LiveHints.innerHTML = `
        <div class="workspace-list-card text-xs"><strong>🎯 AI Coaching Summary:</strong></div>
        <div class="workspace-list-card text-xs" style="color:rgba(255,255,255,0.8)">${coaching.summary || 'Great job! Keep practicing.'}</div>
      `;
    }

    // Reset session state
    currentMockSessionId = null;
    currentQuestionIndex = 0;
    conversationLog = [];
    interactiveMode = false;

    // Reset topic input placeholder
    if (nodes.feature4WorkspaceTopic) {
      nodes.feature4WorkspaceTopic.value = '';
      nodes.feature4WorkspaceTopic.placeholder = 'e.g. System Design, React, Behavioral';
    }

    setStatus("Interview session completed! Check the Coach Board for your final report.");
    setUiFlag("feature4Loading", false);

    // Load history to show this session
    await loadFeature4History();

  } catch (error) {
    console.error('Session end error:', error);
    setStatus(handleApiError(error, "Mock Interview"));
    setUiFlag("feature4Loading", false);
  }
}

/**
 * Helper function to add messages to conversation log
 * Displays in the session board
 */
function addToConversationLog(speaker, text) {
  conversationLog.push({ speaker, text, timestamp: new Date() });

  if (nodes.feature4SessionBoard) {
    const messages = conversationLog.map((msg, idx) => {
      const isInterviewer = msg.speaker === 'interviewer';
      const color = isInterviewer ? 'rgba(99,102,241,0.9)' : 'rgba(34,197,94,0.9)';
      const label = isInterviewer ? '🎤 Interviewer' : '💬 You';
      const turnNum = Math.floor(idx / 2) + 1;
      return `
        <div class="workspace-list-card text-xs" style="border-left:3px solid ${color}">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
            <strong style="color:${color}">${label}</strong>
            <span style="color:rgba(255,255,255,0.4);font-size:10px">Turn ${turnNum}</span>
          </div>
          <p style="color:rgba(255,255,255,0.85);line-height:1.4">${text}</p>
        </div>
      `;
    }).join('');

    const header = `
      <div class="workspace-list-card" style="background:rgba(99,102,241,0.1);border-color:rgba(99,102,241,0.3)">
        <strong style="color:rgba(99,102,241,0.9)">💬 Interview Conversation</strong>
        <span style="color:rgba(255,255,255,0.6);font-size:11px;margin-left:8px">${conversationLog.length} messages</span>
      </div>
    `;

    nodes.feature4SessionBoard.innerHTML = header + messages;
    // Auto-scroll to bottom
    nodes.feature4SessionBoard.scrollTop = nodes.feature4SessionBoard.scrollHeight;
  }
}

/**
 * Helper function to get current candidate ID from various sources
 */
function getCurrentCandidateId() {
  return nodes.feature4WorkspaceCandidateId?.value?.trim() 
    || nodes.candidateId?.value?.trim() 
    || sessionStorage.getItem("cos_candidate")
    || "candidate-001";
}

function renderFeature4Output() {
  if (!nodes.feature4Output) return;
  const f4 = AppState.feature4;
  const loading = Boolean(AppState.ui?.feature4Loading);
  if (loading) {
    nodes.feature4Output.innerHTML = stateStack([
      "Persona Coach persona simulation is active...",
      "Running multi-turn coaching signals and interviewer probes."
    ], "loading");
    return;
  }
  if (!f4.session && !f4.final) {
    nodes.feature4Output.innerHTML = stateCard("Persona Coach API: Awaiting persona run.");
    return;
  }

  const blocks = [];
  if (f4.session) {
    blocks.push(`<p><span class='text-white/90'>Session:</span> #${f4.session.session_id} � ${f4.session.persona?.label || "persona"}</p>`);
  }
  if (f4.lastTurn) {
    blocks.push(`<p><span class='text-white/90'>Realtime:</span> hint '${f4.lastTurn.whisper_hint}'</p>`);
  }
  if (f4.final) {
    blocks.push(`<p><span class='text-white/90'>Coach Score:</span> overall ${f4.final.scorecard?.overall} | logic ${f4.final.scorecard?.logic_depth}</p>`);
    blocks.push(`<p><span class='text-white/90'>Badges:</span> ${(f4.final.badges?.earned || []).join(", ") || "none yet"}</p>`);
  }
  if (f4.synthesis) {
    blocks.push(`<p><span class='text-white/90'>Synthesis:</span> ${f4.synthesis.low_latency_audio?.estimated_latency_ms}ms audio � ${f4.synthesis.multilingual_pack?.primary}</p>`);
  }
  if (f4.share) {
    blocks.push(`<p><span class='text-white/90'>Share:</span> ${f4.share.review_url}</p>`);
  }

  nodes.feature4Output.innerHTML = blocks.map((b) => `<div class='thin-glass rounded px-2 py-1'>${b}</div>`).join("");
}

function renderFeature4Workspace() {
  const f4 = AppState.feature4;
  const loading = Boolean(AppState.ui?.feature4Loading);

  if (nodes.feature4InterviewerPrompt) {
    const prompt = f4.prompt || f4.lastTurn?.next_question?.question;
    nodes.feature4InterviewerPrompt.textContent = prompt || "Interviewer prompt will appear here during multi-turn run.";
    nodes.feature4InterviewerPrompt.classList.toggle("animate-pulse", Boolean(prompt));
  }

  if (nodes.feature4SessionBoard) {
    if (loading) {
      nodes.feature4SessionBoard.innerHTML = stateCard("Creating persona session and generating turn-by-turn signals...", "loading");
    } else if (!f4.session) {
      nodes.feature4SessionBoard.innerHTML = stateCard("Run Persona Session to start.");
    } else {
      const persona = f4.session.persona || {};
      nodes.feature4SessionBoard.innerHTML = `
        <div class="workspace-list-card">Session #${f4.session.session_id}</div>
        <div class="workspace-list-card">Persona: ${persona.label || "unknown"}</div>
        <div class="workspace-list-card text-xs">Style: ${persona.style || "n/a"}</div>
        <div class="workspace-list-card text-xs">Turns: ${(f4.turns || []).length}</div>
        <div class="workspace-list-card text-xs">Status: ${f4.final ? "completed" : "in-progress"}</div>
      `;
    }
  }

  if (nodes.feature4LiveHints) {
    const hint = f4.lastTurn?.whisper_hint;
    const nextQ = f4.lastTurn?.next_question?.question;
    nodes.feature4LiveHints.innerHTML = hint
      ? `<div class="workspace-list-card text-xs">Whisper hint: ${hint}</div><div class="workspace-list-card text-xs">Next probe: ${nextQ || "n/a"}</div><div class="workspace-list-card text-xs">Turn count: ${(f4.turns || []).length}</div>`
      : stateCard("Realtime hints appear after first turn.");
  }

  if (nodes.feature4CoachBoard) {
    if (!f4.final) {
      nodes.feature4CoachBoard.innerHTML = stateCard("Finalize coach to see scorecard and badges.");
    } else {
      const s = f4.final.scorecard || {};
      const badges = (f4.final.badges?.earned || []).join(", ") || "none";
      const heat = f4.final.improvement_heatmap?.delta || {};
      nodes.feature4CoachBoard.innerHTML = `
        <div class="workspace-list-card">Overall: ${s.overall} | Logic: ${s.logic_depth}</div>
        <div class="workspace-list-card">Behavioral: ${s.behavioral_control} | Delivery: ${s.confidence_delivery}</div>
        <div class="workspace-list-card text-xs">Badges: ${badges}</div>
        <div class="workspace-list-card text-xs">Heatmap delta: filler ${heat.filler_control ?? "n/a"}, confidence ${heat.confidence ?? "n/a"}, freeze ${heat.freeze_control ?? "n/a"}</div>
      `;
    }
  }

  if (nodes.feature4MediaBoard) {
    const synth = f4.synthesis;
    const share = f4.share;
    nodes.feature4MediaBoard.innerHTML = synth
      ? `<div class="workspace-list-card">Audio latency: ${synth.low_latency_audio?.estimated_latency_ms}ms</div>
         <div class="workspace-list-card">Avatar: ${synth.lip_sync_avatar?.avatar_style} | Env: ${synth.environment_simulation?.selected}</div>
         <div class="workspace-list-card text-xs">Language pack: ${synth.multilingual_pack?.primary}</div>
         <div class="workspace-list-card text-xs">Share URL: ${share?.review_url || "Generate with Share button."}</div>`
      : stateCard("Synthesis details appear after persona run.");
  }

  if (nodes.feature4CompareBoard) {
    const historyRows = (f4.history || []).slice(0, 4).map((item) => {
      const score = item.overall_score == null ? "n/a" : Math.round(item.overall_score);
      return `<div class="workspace-list-card text-[11px]">#${item.session_id} � ${item.persona_key} � ${item.status} � score ${score}</div>`;
    });

    const compare = f4.compare;
    const compareRow = compare
      ? `<div class="workspace-list-card text-[11px]">Compare ${compare.left_session} -> ${compare.right_session}: filler ${compare.delta?.filler_control ?? "n/a"}, confidence ${compare.delta?.confidence ?? "n/a"}, freeze ${compare.delta?.freeze_control ?? "n/a"}</div>`
      : "";

    const fallback = historyRows.length
      ? historyRows.join("")
      : stateCard("Load history to view recent sessions.");

    nodes.feature4CompareBoard.innerHTML = `${compareRow}${fallback}`;
  }
}

function drawFeature4SignalChart() {
  const canvas = nodes.feature4SignalChart;
  if (!canvas) return;

  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  const width = Math.max(260, rect.width || 260);
  const height = Math.max(150, rect.height || 150);
  canvas.width = width * ratio;
  canvas.height = height * ratio;

  const ctx = canvas.getContext("2d");
  ctx.scale(ratio, ratio);
  ctx.clearRect(0, 0, width, height);

  const turns = AppState.feature4.turns || [];
  const turn = AppState.feature4.lastTurn;
  if (!turn) {
    ctx.fillStyle = "rgba(255,255,255,0.5)";
    ctx.font = "12px sans-serif";
    ctx.fillText("Run Persona Session to populate realtime signal chart.", 12, height / 2);
    return;
  }

  if (turns.length > 1) {
    const metrics = [
      {
        label: "Filler",
        color: "rgba(244,63,94,0.9)",
        values: turns.map((t) => t.realtime_signals?.filler_tracker?.score ?? 0)
      },
      {
        label: "Confidence",
        color: "rgba(99,102,241,0.9)",
        values: turns.map((t) => t.realtime_signals?.pitch_analysis?.confidence_score ?? 0)
      },
      {
        label: "Freeze",
        color: "rgba(245,158,11,0.9)",
        values: turns.map((t) => t.realtime_signals?.silence_detection?.score ?? 0)
      },
      {
        label: "Gaze",
        color: "rgba(45,212,191,0.9)",
        values: turns.map((t) => t.realtime_signals?.gaze_tracking?.eye_contact_score ?? 0)
      }
    ];

    const left = 26;
    const right = width - 16;
    const top = 16;
    const bottom = height - 24;
    const spanX = Math.max(1, right - left);
    const spanY = Math.max(1, bottom - top);

    ctx.strokeStyle = "rgba(255,255,255,0.16)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i += 1) {
      const y = top + (spanY * i) / 4;
      ctx.beginPath();
      ctx.moveTo(left, y);
      ctx.lineTo(right, y);
      ctx.stroke();
    }

    metrics.forEach((metric) => {
      ctx.strokeStyle = metric.color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      metric.values.forEach((v, i) => {
        const x = left + (spanX * i) / Math.max(1, metric.values.length - 1);
        const y = bottom - (clamp(v, 0, 100) / 100) * spanY;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
    });

    ctx.fillStyle = "rgba(255,255,255,0.7)";
    ctx.font = "11px sans-serif";
    ctx.fillText(`Turns: ${turns.length}`, left, height - 8);
    return;
  }

  const points = [
    { label: "Filler", value: turn.realtime_signals?.filler_tracker?.score ?? 0, color: "rgba(244,63,94,0.9)" },
    { label: "Confidence", value: turn.realtime_signals?.pitch_analysis?.confidence_score ?? 0, color: "rgba(99,102,241,0.9)" },
    { label: "Freeze", value: turn.realtime_signals?.silence_detection?.score ?? 0, color: "rgba(245,158,11,0.9)" },
    { label: "Gaze", value: turn.realtime_signals?.gaze_tracking?.eye_contact_score ?? 0, color: "rgba(45,212,191,0.9)" },
  ];

  const barW = Math.floor((width - 40) / points.length);
  const baseY = height - 24;
  const maxH = height - 50;

  points.forEach((p, i) => {
    const h = Math.max(6, (p.value / 100) * maxH);
    const x = 20 + i * barW + 8;
    const y = baseY - h;
    ctx.fillStyle = p.color;
    ctx.fillRect(x, y, barW - 16, h);
    ctx.fillStyle = "rgba(255,255,255,0.85)";
    ctx.font = "11px sans-serif";
    ctx.fillText(p.label, x, baseY + 14);
    ctx.fillText(String(Math.round(p.value)), x, y - 6);
  });
}

async function runFeature5NarrativeArchitect() {
  // Read from dedicated workspace inputs first, fall back to command-center inputs
  const githubUrlEl = nodes.feature5WorkspaceGithubUrl || nodes.feature5GithubRepo;
  const targetRoleEl = nodes.feature5WorkspaceTargetRole || nodes.feature5TargetRole;
  const toneEl = nodes.feature5WorkspaceTone || nodes.feature5Tone;
  const jdEl = nodes.feature5WorkspaceJd || nodes.feature5JdText;
  const projectsEl = nodes.feature5WorkspaceProjects || nodes.feature5SelectedProjects;

  const githubRepo = githubUrlEl?.value?.trim() || "";
  const targetRole = targetRoleEl?.value?.trim() || "Software Engineer";
  const tone = toneEl?.value || "balanced";
  const jdText = jdEl?.value?.trim() || "";
  const selectedProjects = (projectsEl?.value || "Backend, Frontend")
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean)
    .slice(0, 8);

  const candidateId = nodes.candidateId.value.trim() || "candidate-001";
  const repoSubpath = nodes.feature5RepoSubpath?.value?.trim() || ".";

  // Validate GitHub URL — must be https://github.com/user/repo format
  if (githubRepo) {
    const githubRegex = /^https:\/\/github\.com\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_.-]+\/?$/;
    if (!githubRegex.test(githubRepo)) {
      setStatus("Narrative: Invalid GitHub URL. Use format: https://github.com/username/repo");
      if (githubUrlEl) githubUrlEl.style.borderColor = "rgba(248,113,113,0.7)";
      return;
    }
  }
  if (githubUrlEl) githubUrlEl.style.borderColor = "";

  let loader = null;
  try {
    loader = showStepLoader("feature5-output", [
      "Scanning repository structure and ownership signals...",
      "Building STAR narratives from implementation evidence...",
      "Running consistency and credibility checks...",
      "Preparing export-ready portfolio artifacts..."
    ]);
    setUiFlag("feature5Loading", true);
    if (nodes.runFeature5) nodes.runFeature5.disabled = true;
    if (nodes.feature5WorkspaceRun) nodes.feature5WorkspaceRun.disabled = true;
    if (githubRepo) {
      emitEvent("github_repo_connected", "feature5", { github_repo: githubRepo });
    }
    selectedProjects.forEach((projectName) => {
      emitEvent("project_selected_for_narrative", "feature5", {}, { projectId: projectName });
    });

    setStatus("Portfolio Narrator: running deep codebase analysis and narrative generation...");
    const response = await apiFetch(`${API_BASE}/api/feature5/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        candidate_id: candidateId,
        repo_subpath: repoSubpath,
        target_role: targetRole,
        tone,
        jd_text: jdText,
        resume_text: nodes.feature2Notes?.value?.trim() || "",
        linkedin_text: nodes.feature2Transcript?.value?.trim() || "",
        github_repo: githubRepo,
        selected_projects: selectedProjects.length ? selectedProjects : ["Backend", "Frontend", "Requirements"]
      })
    });
    if (!response.ok) throw new Error(await response.text());

    const session = await response.json();
    AppState.setState({
      feature5: {
        ...AppState.feature5,
        session,
        exportBundle: null
      }
    });

    const warningCount = (session.consistency_check?.claim_evidence_soft_warnings || []).length;
    emitEvent("star_bullets_generated", "feature5", {
      narrative_tone: tone,
      warning_count: warningCount,
      evidence_link_count: session.deep_analysis?.epic_5_1?.logic_identification?.custom_logic_ratio || null
    }, { projectId: selectedProjects[0] || null });
    if (warningCount > 0) {
      emitEvent("claim_warning_shown", "feature5", { warning_count: warningCount });
    }

    await loadFeature5History();
    setStatus("Portfolio Narrator complete - narrative artifacts ready.");
  } catch (error) {
    setStatus(handleApiError(error, "Portfolio Narrator"));
  } finally {
    loader?.stop();
    if (nodes.runFeature5) nodes.runFeature5.disabled = false;
    if (nodes.feature5WorkspaceRun) nodes.feature5WorkspaceRun.disabled = false;
    setUiFlag("feature5Loading", false);
  }
}

async function loadFeature5History() {
  const candidateId = nodes.candidateId.value.trim() || "candidate-001";
  try {
    const response = await apiFetch(`${API_BASE}/api/feature5/candidate/${encodeURIComponent(candidateId)}/sessions`);
    if (!response.ok) throw new Error(await response.text());
    const payload = await response.json();
    AppState.setState({
      feature5: {
        ...AppState.feature5,
        history: payload.sessions || []
      }
    });
    setStatus(`Portfolio Narrator history loaded (${(payload.sessions || []).length} sessions).`);
  } catch (error) {
    setStatus(`Portfolio Narrator history error: ${String(error.message).slice(0, 120)}`);
  }
}

async function exportFeature5Bundle() {
  const sid = AppState.feature5.session?.session_id;
  if (!sid) {
    setStatus("Run Portfolio Narrator first.");
    return;
  }

  try {
    const response = await apiFetch(`${API_BASE}/api/feature5/sessions/${sid}/export`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        include_sections: ["linkedin_sync", "resume_optimizer", "case_study_pdf", "consistency_check"]
      })
    });
    if (!response.ok) throw new Error(await response.text());
    const bundle = await response.json();

    AppState.setState({
      feature5: {
        ...AppState.feature5,
        exportBundle: bundle
      }
    });
    emitEvent("narrative_exported", "feature5", {
      exported_sections: bundle.exported_sections || []
    });
    setStatus("Portfolio Narrator export bundle generated.");
    return bundle;
  } catch (error) {
    setStatus(`Portfolio Narrator export error: ${String(error.message).slice(0, 120)}`);
    return null;
  }
}

async function downloadFeature5Bundle() {
  const session = AppState.feature5.session;
  if (!session) {
    setStatus("Run Portfolio Narrator first.");
    return;
  }

  let bundle = AppState.feature5.exportBundle;
  if (!bundle?.markdown_bundle) {
    bundle = await exportFeature5Bundle();
  }
  if (!bundle?.markdown_bundle) return;

  const safeCandidate = (session.candidate_id || "candidate").replace(/[^a-zA-Z0-9_-]/g, "-");
  const filename = `feature5_narrative_${safeCandidate}_s${session.session_id}.md`;
  const blob = new Blob([bundle.markdown_bundle], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  emitEvent("narrative_exported", "feature5", { format: "markdown" });
  setStatus(`Portfolio Narrator markdown downloaded: ${filename}`);
}

async function downloadFeature5CaseStudyPdf() {
  const sid = AppState.feature5.session?.session_id;
  if (!sid) {
    setStatus("Run Portfolio Narrator first.");
    return;
  }

  try {
    const response = await apiFetch(`${API_BASE}/api/feature5/sessions/${sid}/case-study.pdf`);
    if (!response.ok) throw new Error(await response.text());
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `feature5_case_study_s${sid}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    emitEvent("narrative_exported", "feature5", { format: "pdf" });
    setStatus("Portfolio Narrator case study PDF downloaded.");
  } catch (error) {
    setStatus(`Portfolio Narrator PDF download error: ${String(error.message).slice(0, 120)}`);
  }
}

async function downloadFeature5PortfolioSite() {
  const sid = AppState.feature5.session?.session_id;
  if (!sid) {
    setStatus("Run Portfolio Narrator first.");
    return;
  }

  try {
    const response = await apiFetch(`${API_BASE}/api/feature5/sessions/${sid}/portfolio-site`);
    if (!response.ok) throw new Error(await response.text());
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `feature5_portfolio_site_s${sid}.zip`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    emitEvent("narrative_exported", "feature5", { format: "zip" });
    setStatus("Portfolio Narrator portfolio site package downloaded.");
  } catch (error) {
    setStatus(`Portfolio Narrator site download error: ${String(error.message).slice(0, 120)}`);
  }
}

function renderLensWorkspace() {
  const analysis = AppState.feature1.analysis;
  const versions = AppState.feature1.versions || [];
  const loading = Boolean(AppState.ui?.feature1Loading);

  if (nodes.lensSummaryBoard) {
    if (loading) {
      nodes.lensSummaryBoard.innerHTML = stateCard("Lens is scoring the resume against job intent...", "loading");
    } else if (!analysis) {
      nodes.lensSummaryBoard.innerHTML = stateCard("Run Lens analysis after uploading resume and JD in Command view.");
    } else {
      const s = analysis.score || {};
      const recs = (analysis.recommendations || []).slice(0, 3);
      nodes.lensSummaryBoard.innerHTML = `
        <div class="workspace-list-card">Overall: ${s.overall} | Visual: ${s.visual_hierarchy}</div>
        <div class="workspace-list-card">ATS: ${s.ats_integrity} | Semantic: ${s.semantic_match} | Benchmark: ${s.competitive_benchmark}</div>
        ${recs.map((r) => `<div class="workspace-list-card text-xs">${r}</div>`).join("")}
      `;
    }
  }

  if (nodes.lensVersionsBoard) {
    nodes.lensVersionsBoard.innerHTML = versions.length
      ? versions
          .slice(0, 16)
          .map((v) => `<div class="workspace-list-card text-xs">v${v.version_number} � ${v.job_category} � score ${v.overall_score}</div>`)
          .join("")
      : stateCard("Load versions to view timeline.");
  }

  if (nodes.lensHeatmapPreview) {
    nodes.lensHeatmapPreview.textContent = analysis
      ? "Heatmap overlay has been computed. Switch to Command > Zone A canvas to inspect visual hotspots."
      : "Run Lens analysis to refresh heatmap signal overlay in command canvas.";
  }
}

function renderFeature5Output() {
  if (!nodes.feature5Output) return;

  const f5 = AppState.feature5;
  const loading = Boolean(AppState.ui?.feature5Loading);
  if (loading) {
    nodes.feature5Output.innerHTML = stateStack([
      "Portfolio Narrator is building architecture narrative artifacts...",
      "Preparing STAR stories, talk-track, and export sync."
    ], "loading");
    return;
  }
  if (!f5.session) {
    nodes.feature5Output.innerHTML = stateCard("Portfolio Narrator API: Awaiting narrative run.");
    return;
  }

  const deep = f5.session.deep_analysis?.epic_5_1 || {};
  const gap = f5.session.gap_analysis?.epic_5_4 || {};
  const consistency = f5.session.consistency_check || {};

  const blocks = [
    `<p><span class='text-white/90'>Session:</span> #${f5.session.session_id} � ${f5.session.tone}</p>`,
    `<p><span class='text-white/90'>Architecture:</span> ${deep.architecture_mapping?.identified_style || "unknown"}</p>`,
    `<p><span class='text-white/90'>Sophistication:</span> ${deep.sophistication_scoring?.score || "n/a"}</p>`,
    `<p><span class='text-white/90'>Doc Score:</span> ${gap.documentation_score?.score || "n/a"}</p>`,
    `<p><span class='text-white/90'>Consistency:</span> ${consistency.consistency_score || "n/a"}</p>`
  ];

  nodes.feature5Output.innerHTML = blocks.map((b) => `<div class='thin-glass rounded px-2 py-1'>${b}</div>`).join("");
}

function renderFeature5Workspace() {
  const f5 = AppState.feature5;
  const session = f5.session;
  const loading = Boolean(AppState.ui?.feature5Loading);

  const loadingCard = (msg) => `<div class="state-card state-loading" style="display:flex;align-items:center;gap:10px"><div style="width:8px;height:8px;border-radius:50%;background:#818cf8;animation:pulse 1s ease-in-out infinite;flex-shrink:0"></div>${msg}</div>`;
  const emptyCard = (msg) => `<div class="state-card" style="text-align:center;padding:24px 16px;color:rgba(255,255,255,0.4)">${msg}</div>`;
  const pill = (label, value, color) => `<div style="display:inline-flex;align-items:center;gap:6px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:6px 12px;font-size:13px"><span style="color:rgba(255,255,255,0.5);font-size:11px;text-transform:uppercase;letter-spacing:0.05em">${label}</span><span style="color:${color || "#818cf8"};font-weight:600">${value}</span></div>`;
  const row = (icon, text, sub) => `<div style="display:flex;align-items:flex-start;gap:10px;padding:10px 12px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:10px;margin-bottom:6px"><span style="font-size:16px;flex-shrink:0;margin-top:1px">${icon}</span><div><div style="font-size:13px;color:rgba(255,255,255,0.9);line-height:1.5">${text}</div>${sub ? `<div style="font-size:11px;color:rgba(255,255,255,0.45);margin-top:2px">${sub}</div>` : ""}</div></div>`;

  if (loading) {
    if (nodes.feature5AnalysisBoard) nodes.feature5AnalysisBoard.innerHTML = loadingCard("Analyzing architecture and code sophistication...");
    if (nodes.feature5NarrativeBoard) nodes.feature5NarrativeBoard.innerHTML = loadingCard("Drafting STAR narratives from implementation evidence...");
    if (nodes.feature5TalkBoard) nodes.feature5TalkBoard.innerHTML = loadingCard("Building confident talk-track script...");
    if (nodes.feature5GapBoard) nodes.feature5GapBoard.innerHTML = loadingCard("Computing portfolio and documentation gaps...");
    if (nodes.feature5ExportBoard) nodes.feature5ExportBoard.innerHTML = loadingCard("Preparing export and consistency bundles...");
    return;
  }

  if (!session) {
    if (nodes.feature5AnalysisBoard) nodes.feature5AnalysisBoard.innerHTML = emptyCard("Enter a GitHub URL and click Run to analyze your codebase.");
    if (nodes.feature5NarrativeBoard) nodes.feature5NarrativeBoard.innerHTML = emptyCard("STAR narratives will appear here after analysis.");
    if (nodes.feature5TalkBoard) nodes.feature5TalkBoard.innerHTML = emptyCard("Interview talk-track scripts will appear here.");
    if (nodes.feature5GapBoard) nodes.feature5GapBoard.innerHTML = emptyCard("Skill gaps and documentation issues will appear here.");
    if (nodes.feature5ExportBoard) nodes.feature5ExportBoard.innerHTML = emptyCard("Export options and session history will appear here.");
    return;
  }

  const deep = session.deep_analysis?.epic_5_1 || {};
  const nar = session.narrative?.epic_5_2 || {};
  const talk = session.talk_track?.epic_5_3 || {};
  const gap = session.gap_analysis?.epic_5_4 || {};
  const exp = session.export_sync?.epic_5_5 || {};

  if (nodes.feature5AnalysisBoard) {
    const arch = deep.architecture_mapping?.identified_style || "unknown";
    const score = deep.sophistication_scoring?.score;
    const tier = deep.sophistication_scoring?.tier || "";
    const clr = score >= 80 ? "#34d399" : score >= 60 ? "#fbbf24" : "#f87171";
    const cloneRisk = deep.tutorial_detector?.clone_risk_score ?? 0;
    const missingReadme = deep.readme_polisher?.missing_sections || [];
    const customLogic = deep.logic_identification?.custom_logic_ratio;
    nodes.feature5AnalysisBoard.innerHTML =
      `<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px">` +
      pill("Architecture", arch, "#a5b4fc") +
      (score != null ? pill("Sophistication", score + " " + tier, clr) : "") +
      (customLogic != null ? pill("Custom Logic", customLogic + "%", "#34d399") : "") +
      pill("Clone Risk", cloneRisk === 0 ? "None" : cloneRisk, cloneRisk === 0 ? "#34d399" : "#f87171") +
      `</div>` +
      (missingReadme.length ? row("📄", "README missing sections", missingReadme.join(", ")) : row("✅", "README is complete", "")) +
      (deep.ownership_signals?.key_contributors || []).slice(0, 2).map((c) => row("👤", c.name || c, "Key contributor")).join("");
  }

  if (nodes.feature5NarrativeBoard) {
    const lines = nar.problem_solution_narrative || [];
    const stars = nar.star_summaries || [];
    const metrics = nar.impact_metrics || [];
    const tone = nar.narrative_personalization?.selected_tone || "balanced";
    nodes.feature5NarrativeBoard.innerHTML =
      `<div style="margin-bottom:10px"><span style="font-size:11px;background:rgba(99,102,241,0.2);color:#a5b4fc;padding:3px 10px;border-radius:999px;font-weight:600;text-transform:uppercase;letter-spacing:0.05em">Tone: ${tone}</span></div>` +
      lines.map((l) => row("💡", l, "")).join("") +
      stars.slice(0, 3).map((s) => row("⭐", "<strong>" + s.project + "</strong>: " + s.action, s.result || "")).join("") +
      metrics.slice(0, 3).map((m) => row("📈", m, "")).join("");
  }

  if (nodes.feature5TalkBoard) {
    const steps = talk.code_walkthrough_script || [];
    const qs = talk.edge_case_anticipator || [];
    nodes.feature5TalkBoard.innerHTML =
      (steps.length ? `<p style="font-size:11px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px">Walkthrough Script</p>` : "") +
      steps.slice(0, 5).map((s, i) => row((i + 1) + ".", s, "")).join("") +
      (qs.length ? `<p style="font-size:11px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:0.06em;margin:12px 0 8px">Likely Interview Questions</p>` : "") +
      qs.slice(0, 4).map((q) => row("❓", q, "")).join("");
  }

  if (nodes.feature5GapBoard) {
    const docScore = gap.documentation_score?.score;
    const staleRisk = gap.stale_date_alert?.stale_risk || "n/a";
    const seniorAddOn = gap.feature_suggestion?.title;
    const missing = gap.coverage_report?.missing_coverage || [];
    const docClr = docScore >= 80 ? "#34d399" : docScore >= 60 ? "#fbbf24" : "#f87171";
    nodes.feature5GapBoard.innerHTML =
      `<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px">` +
      (docScore != null ? pill("Doc Score", docScore.toFixed(1), docClr) : "") +
      pill("Stale Risk", staleRisk, staleRisk === "low" ? "#34d399" : "#f87171") +
      `</div>` +
      (seniorAddOn ? row("🚀", "Senior add-on: " + seniorAddOn, gap.feature_suggestion?.description || "") : "") +
      missing.slice(0, 4).map((m) => row("⚠️", "Missing: " + m, "")).join("") +
      (!missing.length && !seniorAddOn ? row("✅", "No critical gaps found", "") : "");
  }

  if (nodes.feature5ExportBoard) {
    const top3 = exp.resume_optimizer?.top_3_projects || [];
    const warnings = exp.consistency_check?.claim_evidence_soft_warnings || [];
    const history = (f5.history || []).slice(0, 3);
    const bundleReady = Boolean(f5.exportBundle);
    nodes.feature5ExportBoard.innerHTML =
      (bundleReady ? row("✅", "Export bundle ready", (f5.exportBundle.exported_sections || []).join(", ")) : "") +
      top3.map((p) => row("🏆", "Top project: " + p.project, "JD relevance: " + p.jd_relevance_score)).join("") +
      warnings.slice(0, 2).map((w) => row("⚠️", w.warning || w, "Consistency warning")).join("") +
      (history.length ? `<p style="font-size:11px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:0.06em;margin:12px 0 8px">Past Sessions</p>` : "") +
      history.map((h) => row("🕐", "Session #" + h.session_id + " · " + (h.architecture_style || "unknown"), "Sophistication: " + Math.round(h.sophistication_score || 0))).join("");
  }
}

async function generateLinkedInPost() {
  const sid = AppState.feature5.session?.session_id;
  const board = document.getElementById("feature5-linkedin-board");
  const copyBtn = document.getElementById("feature5-copy-linkedin");
  const genBtn = document.getElementById("feature5-generate-linkedin");

  if (!sid) {
    if (board) board.innerHTML = `<div class="state-card" style="color:#f87171;padding:16px">⚠️ Run Narrative Architect first, then generate your LinkedIn post.</div>`;
    return;
  }

  if (board) board.innerHTML = `<div class="state-card state-loading" style="display:flex;align-items:center;gap:10px;padding:16px"><div style="width:8px;height:8px;border-radius:50%;background:#818cf8;animation:pulse 1s ease-in-out infinite;flex-shrink:0"></div>Crafting your LinkedIn post — analyzing architecture, STAR stories, and impact metrics...</div>`;
  if (genBtn) { genBtn.disabled = true; genBtn.innerHTML = `<i data-lucide="loader" class="w-3 h-3"></i> Generating...`; lucide.createIcons(); }

  try {
    const res = await apiFetch(`${API_BASE}/api/feature5/sessions/${sid}/linkedin-post`);
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    const post = data.post_text || "";
    const charCount = data.character_count || post.length;
    const charColor = charCount > 1300 ? "#f87171" : charCount > 1000 ? "#fbbf24" : "#34d399";
    const charLabel = charCount > 1300 ? "Over limit — trim before posting" : charCount > 1000 ? "Good length" : "Concise";

    if (board) {
      board.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
          <span style="font-size:12px;color:rgba(255,255,255,0.5)">Ready to paste on LinkedIn</span>
          <span style="font-size:11px;color:${charColor};background:rgba(255,255,255,0.06);padding:3px 10px;border-radius:999px;font-weight:600">${charCount} chars · ${charLabel}</span>
        </div>
        <div id="linkedin-post-text" style="
          background:rgba(255,255,255,0.04);
          border:1px solid rgba(255,255,255,0.1);
          border-radius:12px;
          padding:20px;
          font-size:14px;
          line-height:1.8;
          color:rgba(255,255,255,0.92);
          white-space:pre-wrap;
          word-break:break-word;
          font-family:'Plus Jakarta Sans',sans-serif;
        ">${post.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")}</div>
        <p style="font-size:11px;color:rgba(255,255,255,0.3);margin-top:10px">💡 Tip: Add real metrics (e.g. "reduced load time by 40%") to make this post stand out even more.</p>
      `;
    }
    if (copyBtn) copyBtn.style.display = "inline-flex";
    setStatus("LinkedIn post generated.");
  } catch (err) {
    if (board) board.innerHTML = `<div class="state-card" style="color:#f87171;padding:16px">Failed to generate: ${String(err.message).slice(0, 120)}</div>`;
  } finally {
    if (genBtn) { genBtn.disabled = false; genBtn.innerHTML = `<i data-lucide="refresh-cw" class="w-3 h-3"></i> Regenerate`; lucide.createIcons(); }
  }
}

function copyLinkedInPost() {
  const el = document.getElementById("linkedin-post-text");
  if (!el) return;
  const text = el.innerText || el.textContent;
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.getElementById("feature5-copy-linkedin");
    if (btn) {
      btn.innerHTML = `<i data-lucide="check" class="w-3 h-3"></i> Copied!`;
      btn.style.borderColor = "#34d399";
      btn.style.color = "#34d399";
      setTimeout(() => {
        btn.innerHTML = `<i data-lucide="copy" class="w-3 h-3"></i> Copy`;
        btn.style.borderColor = "";
        btn.style.color = "";
        lucide.createIcons();
      }, 2000);
      lucide.createIcons();
    }
    setStatus("LinkedIn post copied to clipboard.");
  }).catch(() => setStatus("Copy failed — please select and copy manually."));
}

function parseCommaSkills(text) {
  return text
    .split(",")
    .map((x) => x.trim().toLowerCase())
    .filter(Boolean)
    .filter((v, i, arr) => arr.indexOf(v) === i);
}

function extractSearchTerms() {
  const text = nodes.jobDescription.value.toLowerCase();
  const words = text.match(/[a-z][a-z0-9\-\+\.]{2,}/g) || [];
  const ignore = new Set(["with", "that", "this", "from", "have", "will", "your", "role", "team", "years", "experience"]);
  const counts = new Map();
  words.forEach((w) => {
    if (ignore.has(w)) return;
    counts.set(w, (counts.get(w) || 0) + 1);
  });
  return Array.from(counts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map((x) => x[0]);
}

function roleFromCategory(category) {
  const map = {
    frontend: "Frontend Engineer",
    backend: "Backend Engineer",
    fullstack: "Fullstack Engineer",
    data: "Data Engineer"
  };
  return map[category] || "Software Engineer";
}

async function loadFeature3History() {
  // Bug 11 fix: always fetch from API and show modal, don't rely on AppState (resets on page reload)
  const candidateId = nodes.candidateId.value.trim() || "candidate-001";
  try {
    setStatus("Loading Skill Arbitrage history...");
    const response = await apiFetch(`${API_BASE}/api/feature3/candidate/${encodeURIComponent(candidateId)}/historical-gaps`);
    if (!response.ok) throw new Error("History unavailable");
    const history = await response.json();
    // Always update AppState with fresh data
    AppState.setState({ feature3: { ...AppState.feature3, history } });
    setStatus("Skill Arbitrage historical gaps loaded.");
    // Always show modal — data is now in AppState
    showHistoryModal();
  } catch (error) {
    AppState.setState({ feature3: { ...AppState.feature3, history: null } });
    setStatus(`Skill Arbitrage history error: ${String(error.message).slice(0, 120)}`);
    alert('Could not load history. Run Full Arbitrage first to generate data.');
  }
}

async function runFeature3SprintQuiz() {
  const sprint = AppState.feature3?.sprint;
  if (!sprint || !sprint.sprint_id) {
    setStatus("Run Skill Arbitrage first to create a sprint.");
    return;
  }
  
  // Show sprint modal with full plan
  showSprintModal();
}

async function runFeature3ResumeInjector() {
  const sprintId = AppState.feature3.sprint?.sprint_id;
  const primarySkill = AppState.feature3.sprint?.primary_skill || "skill";
  if (!sprintId) {
    setStatus("Run Skill Arbitrage arbitrage first to create a sprint.");
    return;
  }

  try {
    setStatus("Skill Arbitrage: generating resume injection bullets...");
    const response = await apiFetch(`${API_BASE}/api/feature3/sprint/${sprintId}/resume-inject`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project_name: `${primarySkill} Skill Sprint Project`,
        baseline_context: "a market-aligned sprint project with quality gates",
        impact_metric_hint: "p95 latency and deployment reliability"
      })
    });

    if (!response.ok) throw new Error(await response.text());
    const resumeInject = await response.json();
    AppState.setState({ feature3: { ...AppState.feature3, resumeInject } });
    emitEvent("recommendation_accepted", "feature3", {
      accepted_recommendation: "resume_inject",
      projected_fit_delta: AppState.feature3.gap?.match_score || null
    });
    setStatus("Skill Arbitrage resume injector complete.");
  } catch (error) {
    setStatus(`Skill Arbitrage resume injector error: ${String(error.message).slice(0, 120)}`);
  }
}

function exportFeature3Snapshot() {
  // Open export modal for format selection
  showExportModal();
}

async function runFeature3Arbitrage() {
  const errs = validateRequiredFields([
    { id: "candidate-id", label: "Candidate ID" },
    { id: "feature3-target-role", label: "Target Role" },
    { id: "feature3-region", label: "Region" },
    { id: "feature3-current-skills", label: "Current Skills" }
  ]);
  const candidateId = nodes.candidateId.value.trim() || "candidate-001";
  const targetRole = (nodes.feature3TargetRole.value || "").trim() || roleFromCategory(nodes.jobCategory.value);
  const region = (nodes.feature3Region.value || "").trim() || "gb";
  const currentSkills = parseCommaSkills(nodes.feature3CurrentSkills.value || "");
  const salary = Number(nodes.feature3Salary.value || 10000);
  const remoteOnly = Boolean(nodes.feature3RemoteOnly.checked);
  const yearsExp = parseFloat(nodes.feature3YearsExp?.value || "2") || 2.0;
  const currency = nodes.feature3Currency?.value || "USD";
  const githubUsername = (nodes.feature3Github?.value || "").trim();
  const searchTerms = extractSearchTerms();

  if (!currentSkills.length) errs.push("Current Skills is required.");
  if (errs.length) {
    setStatus(errs[0]);
    return;
  }

  let loader = null;
  try {
    loader = showStepLoader("feature3-output", [
      "Collecting live market demand and salary signals...",
      "Computing your skill-gap map against target role...",
      "Generating 7-day sprint and future trend forecasts...",
      "Building ROI and callback probability projections..."
    ]);
    setUiFlag("feature3Loading", true);
    if (nodes.runFeature3) nodes.runFeature3.disabled = true;
    if (nodes.feature3WorkspaceRun) nodes.feature3WorkspaceRun.disabled = true;
    setStatus("Skill Arbitrage: building market snapshot...");
    const marketResponse = await apiFetch(`${API_BASE}/api/feature3/market-snapshot`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        candidate_id: candidateId,
        target_role: targetRole,
        region,
        remote_only: remoteOnly,
        search_terms: searchTerms,
        salary_currency: currency
      })
    });
    if (!marketResponse.ok) throw new Error(await marketResponse.text());
    const market = await marketResponse.json();
    emitEvent("market_snapshot_loaded", "feature3", {
      region,
      target_role: targetRole,
      data_sources_used: market.source_meta?.source_health || market.source_meta || null
    });

    setStatus("Skill Arbitrage: computing personalized gap map...");
    const gapResponse = await apiFetch(`${API_BASE}/api/feature3/gap-analysis`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        candidate_id: candidateId,
        market_snapshot_id: market.snapshot_id,
        current_skills: currentSkills,
        years_experience: yearsExp,
        github_username: githubUsername
      })
    });
    if (!gapResponse.ok) throw new Error(await gapResponse.text());
    const gap = await gapResponse.json();
    emitEvent("skill_gap_viewed", "feature3", {
      target_role: targetRole,
      projected_fit_delta: gap.gap_to_top10_score
    });

    const primarySkill = gap.niche_recommendations?.[0]?.skill || "kubernetes";
    setStatus("Skill Arbitrage: generating 7-day sprint...");
    const sprintResponse = await apiFetch(`${API_BASE}/api/feature3/sprint`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        candidate_id: candidateId,
        gap_snapshot_id: gap.gap_snapshot_id,
        target_role: targetRole,
        primary_skill: primarySkill
      })
    });
    if (!sprintResponse.ok) throw new Error(await sprintResponse.text());
    const sprint = await sprintResponse.json();

    setStatus("Skill Arbitrage: forecasting future trends...");
    const futureResponse = await apiFetch(`${API_BASE}/api/feature3/future-insights`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        candidate_id: candidateId,
        market_snapshot_id: market.snapshot_id,
        current_skills: currentSkills
      })
    });
    if (!futureResponse.ok) throw new Error(await futureResponse.text());
    const future = await futureResponse.json();

    setStatus("Skill Arbitrage: computing ROI projections...");
    const roiResponse = await apiFetch(`${API_BASE}/api/feature3/roi-report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        candidate_id: candidateId,
        market_snapshot_id: market.snapshot_id,
        gap_snapshot_id: gap.gap_snapshot_id,
        // Normalize to USD for backend — PKR and GBP users enter local amounts
        current_salary_usd: currency === "PKR"
          ? Math.round((Number.isFinite(salary) ? salary : 10000) / 278.5)
          : currency === "GBP"
            ? Math.round((Number.isFinite(salary) ? salary : 10000) / 0.79)
            : (Number.isFinite(salary) ? salary : 10000),
        target_path: nodes.jobCategory.value
      })
    });
    if (!roiResponse.ok) throw new Error(await roiResponse.text());
    const roi = await roiResponse.json();
    emitEvent("recommendation_generated", "feature3", {
      target_role: targetRole,
      projected_fit_delta: gap.match_score,
      region
    });

    let history = null;
    try {
      const historyResponse = await apiFetch(`${API_BASE}/api/feature3/candidate/${encodeURIComponent(candidateId)}/historical-gaps`);
      if (historyResponse.ok) history = await historyResponse.json();
    } catch {
      history = null;
    }

    AppState.setState({
      feature3: {
        market,
        gap,
        sprint,
        future,
        roi,
        history
      }
    });
    
    // Update match score display
    updateFeature3MatchScoreDisplay();
    
    // Update enhanced ROI display
    updateEnhancedRoiDisplay();

    setStatus(`Skill Arbitrage complete - match ${gap.match_score}, callback ${roi.callback_probability.probability}%`);
    
    // Refresh dashboard readiness score — backend uses feature3.match_score in calculation
    void loadDashboard({ silent: true });

    // Auto-show sprint modal after successful arbitrage
    setTimeout(() => {
      showSprintModal();
    }, 500);
    
  } catch (error) {
    setStatus(handleApiError(error, "Skill Arbitrage"));
  } finally {
    loader?.stop();
    if (nodes.runFeature3) nodes.runFeature3.disabled = false;
    if (nodes.feature3WorkspaceRun) nodes.feature3WorkspaceRun.disabled = false;
    setUiFlag("feature3Loading", false);
  }
}

function renderFeature3Output() {
  if (!nodes.feature3Output) return;

  const feature3 = AppState.feature3;
  const loading = Boolean(AppState.ui?.feature3Loading);
  if (loading) {
    nodes.feature3Output.innerHTML = stateStack([
      "Skill Arbitrage is ingesting market data and scoring skill gaps...",
      "Generating sprint plan, future signals, and ROI projection."
    ], "loading");
    return;
  }
  if (!feature3.market && !feature3.gap && !feature3.roi && !feature3.history) {
    nodes.feature3Output.innerHTML = stateCard("Skill Arbitrage API: Awaiting arbitrage run.");
    return;
  }

  const blocks = [];

  if (feature3.market) {
    const meta = feature3.market.source_meta || {};
    const refreshAt = meta.refreshed_at_utc || meta.generated_at_utc || meta.fetched_at_utc || "n/a";
    const sourceNames = meta.sources ? Object.keys(meta.sources).join(", ") : "configured providers";
    blocks.push(`<p><span class='text-white/90'>Market Snapshot:</span> ${meta.total_jobs || 0} jobs, ${feature3.market.region}</p>`);
    blocks.push(`<p><span class='text-white/90'>Sources:</span> ${sourceNames} | refresh ${refreshAt}</p>`);
  }

  if (feature3.gap) {
    blocks.push(`<p><span class='text-white/90'>Gap Map:</span> match ${feature3.gap.match_score}, top-10 gap ${feature3.gap.gap_to_top10_score}</p>`);
    const niche = feature3.gap.niche_recommendations?.[0]?.skill;
    if (niche) blocks.push(`<p><span class='text-white/90'>Niche Skill:</span> ${niche}</p>`);
  }

  if (feature3.sprint) {
    blocks.push(`<p><span class='text-white/90'>Skill Sprint:</span> ${feature3.sprint.primary_skill} (${feature3.sprint.sprint_status})</p>`);
  }

  if (feature3.future) {
    const agentic = feature3.future.agentic_ai_score?.score ?? 0;
    const pivot = feature3.future.industry_pivot_advice?.recommended_pivot || "n/a";
    blocks.push(`<p><span class='text-white/90'>Future:</span> Agentic ${agentic}, pivot ${pivot}</p>`);
  }

  if (feature3.roi) {
    const cb = feature3.roi.callback_probability?.probability ?? 0;
    const ltv = feature3.roi.lifetime_value?.five_year_value_delta_usd ?? 0;
    blocks.push(`<p><span class='text-white/90'>ROI:</span> callback ${cb}% | 5y delta $${Math.round(ltv)}</p>`);
  }

  if (feature3.quiz) {
    blocks.push(`<p><span class='text-white/90'>Sprint Quiz:</span> score ${feature3.quiz.score} (${feature3.quiz.passed ? "pass" : "retry"})</p>`);
  }

  if (feature3.resumeInject?.star_bullets?.length) {
    blocks.push(`<p><span class='text-white/90'>Resume Inject:</span> ${feature3.resumeInject.star_bullets[0]}</p>`);
  }

  if (feature3.history?.trend) {
    blocks.push(`<p><span class='text-white/90'>History:</span> monthly delta ${feature3.history.trend.monthly_delta}</p>`);
  }

  nodes.feature3Output.innerHTML = blocks.map((b) => `<div class='thin-glass rounded px-2 py-1'>${b}</div>`).join("");
}

// ─── Sprint Plan Modal Functions ──────────────────────────────────────────────

function showSprintModal() {
  const sprint = AppState.feature3?.sprint;
  if (!sprint) {
    alert('No sprint data available. Please run Full Arbitrage first.');
    return;
  }
  
  const modal = document.getElementById('sprint-modal');
  if (!modal) return;
  
  // Populate modal content
  document.getElementById('sprint-modal-skill').textContent = `Primary Skill: ${sprint.primary_skill}`;
  document.getElementById('sprint-status-text').textContent = sprint.sprint_status || 'Active';
  document.getElementById('sprint-target-role').textContent = sprint.target_role || '--';
  
  // Render day-by-day plan
  const dayPlanContainer = document.getElementById('sprint-day-plan');
  if (sprint.curated_day_plan && Array.isArray(sprint.curated_day_plan)) {
    dayPlanContainer.innerHTML = sprint.curated_day_plan.map((day, index) => `
      <div class="p-3" style="background:rgba(255,255,255,0.05);border-radius:10px;border:1px solid rgba(255,255,255,0.1)">
        <div class="flex items-center justify-between mb-2">
          <h4 style="font-size:0.9rem;font-weight:600;color:#818cf8">Day ${day.day || index + 1}: ${day.objective || day.title || day.topic || 'Learning'}</h4>
          <span style="font-size:0.75rem;color:rgba(255,255,255,0.5)">${day.duration || '2-3 hours'}</span>
        </div>
        <p style="font-size:0.85rem;color:rgba(255,255,255,0.7);line-height:1.5;margin-bottom:8px">${day.deliverable || day.description || day.goal || ''}</p>
        ${day.resource ? `
          <div class="flex flex-wrap gap-2 mt-2">
            <a href="${day.resource.url || '#'}" target="_blank" class="text-xs px-2 py-1 rounded" style="background:rgba(59,130,246,0.2);color:#60a5fa;text-decoration:none;border:1px solid rgba(59,130,246,0.3)">
              ${day.resource.title || 'Resource'}
            </a>
          </div>
        ` : (day.resources && day.resources.length > 0 ? `
          <div class="flex flex-wrap gap-2 mt-2">
            ${day.resources.map(resource => `
              <a href="${resource.url || '#'}" target="_blank" class="text-xs px-2 py-1 rounded" style="background:rgba(59,130,246,0.2);color:#60a5fa;text-decoration:none;border:1px solid rgba(59,130,246,0.3)">
                ${resource.title || resource.name || 'Resource'}
              </a>
            `).join('')}
          </div>
        ` : '')}
      </div>
    `).join('');
  } else {
    dayPlanContainer.innerHTML = '<p style="color:rgba(255,255,255,0.5)">No day plan available</p>';
  }
  
  // Render MVP prompt — Bug 3 fix: backend returns .brief not .prompt/.description
  const mvpPromptContainer = document.getElementById('sprint-mvp-prompt');
  if (sprint.mvp_prompt) {
    const promptText = typeof sprint.mvp_prompt === 'string'
      ? sprint.mvp_prompt
      : sprint.mvp_prompt.brief || sprint.mvp_prompt.prompt || sprint.mvp_prompt.description || 'Build a project to demonstrate your skills';
    mvpPromptContainer.textContent = promptText;
  } else {
    mvpPromptContainer.textContent = 'Build a project to demonstrate your skills with ' + sprint.primary_skill;
  }
  
  // Render peer group tags
  const peerTagsContainer = document.getElementById('sprint-peer-tags');
  if (sprint.peer_group_tags && Array.isArray(sprint.peer_group_tags)) {
    peerTagsContainer.innerHTML = sprint.peer_group_tags.map(tag => `
      <span class="px-3 py-1 rounded-full text-xs" style="background:rgba(168,85,247,0.2);color:#c084fc;border:1px solid rgba(168,85,247,0.3)">
        ${tag}
      </span>
    `).join('');
  } else {
    peerTagsContainer.innerHTML = '<p style="color:rgba(255,255,255,0.5);font-size:0.85rem">No peer group data</p>';
  }
  
  // Show modal
  modal.style.display = 'flex';
  
  // Store sprint_id for quiz and resume inject
  window.currentSprintId = sprint.sprint_id;
}

function closeSprintModal() {
  const modal = document.getElementById('sprint-modal');
  if (modal) modal.style.display = 'none';
}

// Sprint modal event listeners
document.addEventListener('DOMContentLoaded', function() {
  const sprintModalClose = document.getElementById('sprint-modal-close');
  const sprintModalCloseBtn = document.getElementById('sprint-modal-close-btn');
  const sprintModalQuiz = document.getElementById('sprint-modal-quiz');
  const sprintModalResume = document.getElementById('sprint-modal-resume');
  
  if (sprintModalClose) {
    sprintModalClose.addEventListener('click', closeSprintModal);
  }
  if (sprintModalCloseBtn) {
    sprintModalCloseBtn.addEventListener('click', closeSprintModal);
  }
  if (sprintModalQuiz) {
    sprintModalQuiz.addEventListener('click', function() {
      closeSprintModal();
      showQuizModal();
    });
  }
  if (sprintModalResume) {
    sprintModalResume.addEventListener('click', function() {
      closeSprintModal();
      showResumeModal();
    });
  }
  
  // Close modal on backdrop click
  const sprintModal = document.getElementById('sprint-modal');
  if (sprintModal) {
    sprintModal.addEventListener('click', function(e) {
      if (e.target === sprintModal) {
        closeSprintModal();
      }
    });
  }
});

// ─── Quiz Modal Functions ─────────────────────────────────────────────────────

function showQuizModal() {
  const sprint = AppState.feature3?.sprint;
  if (!sprint || !sprint.quick_quiz) {
    alert('No quiz data available. Please run Full Arbitrage first.');
    return;
  }
  
  const quiz = sprint.quick_quiz;
  const modal = document.getElementById('quiz-modal');
  if (!modal) return;
  
  // Populate modal content
  document.getElementById('quiz-modal-skill').textContent = `Day ${quiz.day || 3} Checkpoint - ${sprint.primary_skill}`;
  document.getElementById('quiz-pass-mark').textContent = `${quiz.pass_mark || 70}%`;
  
  // Render quiz questions
  const questionsContainer = document.getElementById('quiz-questions-container');
  if (quiz.questions && Array.isArray(quiz.questions)) {
    questionsContainer.innerHTML = quiz.questions.map((question, index) => `
      <div class="p-4" style="background:rgba(255,255,255,0.05);border-radius:12px;border:1px solid rgba(255,255,255,0.1)">
        <label style="font-size:0.9rem;font-weight:600;color:#fff;margin-bottom:8px;display:block">
          Question ${index + 1}:
        </label>
        <p style="font-size:0.85rem;color:rgba(255,255,255,0.7);margin-bottom:12px;line-height:1.5">${question}</p>
        <textarea 
          id="quiz-answer-${index}" 
          class="jt-input jt-textarea" 
          placeholder="Your answer... (Focus on trade-offs, constraints, and measurable impact)"
          rows="4"
          style="width:100%;resize:vertical"
        ></textarea>
      </div>
    `).join('');
  } else {
    questionsContainer.innerHTML = '<p style="color:rgba(255,255,255,0.5)">No questions available</p>';
  }
  
  // Reset results section
  document.getElementById('quiz-results').style.display = 'none';
  document.getElementById('quiz-submit-btn').style.display = 'block';
  document.getElementById('quiz-retry-btn').style.display = 'none';
  
  // Show modal
  modal.style.display = 'flex';
  
  // Store quiz data for submission
  window.currentQuizData = quiz;
}

function closeQuizModal() {
  const modal = document.getElementById('quiz-modal');
  if (modal) modal.style.display = 'none';
}

async function submitQuiz() {
  const sprint = AppState.feature3?.sprint;
  const quiz = window.currentQuizData;

  if (!sprint || !quiz) {
    alert('Quiz data not available. Please run Full Arbitrage first.');
    return;
  }

  // Collect answers
  const answers = [];
  for (let i = 0; i < quiz.questions.length; i++) {
    const answerElement = document.getElementById(`quiz-answer-${i}`);
    answers.push(answerElement ? answerElement.value.trim() : '');
  }

  // Validate BEFORE disabling the button so it never gets stuck
  if (answers.some(a => !a)) {
    alert('Please answer all questions before submitting.');
    return;
  }

  // Validate sprint_id exists and is a real number
  const sprintId = sprint.sprint_id;
  if (!sprintId || typeof sprintId !== 'number') {
    alert('Sprint ID missing. Please run Full Arbitrage again.');
    return;
  }

  const submitBtn = document.getElementById('quiz-submit-btn');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = 'Evaluating...';
  }

  try {
    setStatus("Evaluating quiz answers...");

    const response = await apiFetch(`${API_BASE}/api/feature3/sprint/${sprintId}/quiz`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers })
    });

    if (!response.ok) throw new Error(await response.text());

    const result = await response.json();

    AppState.setState({
      feature3: {
        ...AppState.feature3,
        quizResult: result
      }
    });

    displayQuizResults(result);
    setStatus(`Quiz complete - Score: ${Math.round(result.score)}%`);

  } catch (error) {
    setStatus(`Quiz submission error: ${String(error.message).slice(0, 120)}`);
    alert('Failed to submit quiz. Please try again.');
  } finally {
    // Always re-enable the button — prevents permanent "Evaluating..." stuck state
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Submit Answers';
    }
  }
}

function displayQuizResults(result) {
  const resultsContainer = document.getElementById('quiz-results');
  const scoreValue = document.getElementById('quiz-score-value');
  const statusBadge = document.getElementById('quiz-status-badge');
  const feedbackList = document.getElementById('quiz-feedback-list');
  
  if (!resultsContainer) return;
  
  // Show results section
  resultsContainer.style.display = 'block';
  
  // Display score
  const score = Math.round(result.score || 0);
  scoreValue.textContent = `${score}%`;
  scoreValue.style.color = result.passed ? '#34d399' : '#f87171';
  
  // Display pass/fail badge
  if (result.passed) {
    statusBadge.style.background = 'rgba(34,197,94,0.2)';
    statusBadge.style.border = '1px solid rgba(34,197,94,0.4)';
    statusBadge.style.color = '#34d399';
    statusBadge.textContent = '✅ PASSED - Checkpoint Complete!';
  } else {
    statusBadge.style.background = 'rgba(239,68,68,0.2)';
    statusBadge.style.border = '1px solid rgba(239,68,68,0.4)';
    statusBadge.style.color = '#f87171';
    statusBadge.textContent = '❌ Not Passed - Review and Retry';
  }
  
  // Display feedback
  if (result.feedback && Array.isArray(result.feedback)) {
    feedbackList.innerHTML = result.feedback.map(fb => `
      <div class="p-3" style="background:rgba(59,130,246,0.1);border-radius:8px;border:1px solid rgba(59,130,246,0.3)">
        <p style="font-size:0.85rem;color:rgba(255,255,255,0.8);line-height:1.5">${fb}</p>
      </div>
    `).join('');
  } else {
    feedbackList.innerHTML = '<p style="color:rgba(255,255,255,0.5);font-size:0.85rem">No feedback available</p>';
  }
  
  // Hide submit button, show retry button
  document.getElementById('quiz-submit-btn').style.display = 'none';
  document.getElementById('quiz-retry-btn').style.display = 'block';
}

function retryQuiz() {
  // Reset quiz
  showQuizModal();
}

// Quiz modal event listeners
document.addEventListener('DOMContentLoaded', function() {
  const quizModalClose = document.getElementById('quiz-modal-close');
  const quizModalCloseBtn = document.getElementById('quiz-modal-close-btn');
  const quizSubmitBtn = document.getElementById('quiz-submit-btn');
  const quizRetryBtn = document.getElementById('quiz-retry-btn');
  
  if (quizModalClose) {
    quizModalClose.addEventListener('click', closeQuizModal);
  }
  if (quizModalCloseBtn) {
    quizModalCloseBtn.addEventListener('click', closeQuizModal);
  }
  if (quizSubmitBtn) {
    quizSubmitBtn.addEventListener('click', submitQuiz);
  }
  if (quizRetryBtn) {
    quizRetryBtn.addEventListener('click', retryQuiz);
  }
  
  // Close modal on backdrop click
  const quizModal = document.getElementById('quiz-modal');
  if (quizModal) {
    quizModal.addEventListener('click', function(e) {
      if (e.target === quizModal) {
        closeQuizModal();
      }
    });
  }
});

// ─── Resume Inject Modal Functions ────────────────────────────────────────────

function showResumeModal() {
  const sprint = AppState.feature3?.sprint;
  if (!sprint || !sprint.sprint_id) {
    alert('No sprint data available. Please run Full Arbitrage first.');
    return;
  }
  
  const modal = document.getElementById('resume-modal');
  if (!modal) return;
  
  // Populate modal content
  document.getElementById('resume-modal-skill').textContent = `Skill: ${sprint.primary_skill}`;
  
  // Reset form
  document.getElementById('resume-project-name').value = '';
  document.getElementById('resume-baseline-context').value = '';
  document.getElementById('resume-impact-metric').value = '';
  
  // Hide results
  document.getElementById('resume-results').style.display = 'none';
  document.getElementById('resume-input-form').style.display = 'block';
  document.getElementById('resume-generate-btn').style.display = 'block';
  
  // Show modal
  modal.style.display = 'flex';
}

function closeResumeModal() {
  const modal = document.getElementById('resume-modal');
  if (modal) modal.style.display = 'none';
}

async function generateResumeBullets() {
  const sprint = AppState.feature3?.sprint;
  if (!sprint || !sprint.sprint_id) {
    alert('Sprint data not available. Please run Full Arbitrage first.');
    return;
  }

  const projectName = document.getElementById('resume-project-name').value.trim();
  const baselineContext = document.getElementById('resume-baseline-context').value.trim();
  const impactMetric = document.getElementById('resume-impact-metric').value.trim();

  // Validate BEFORE disabling button
  if (!projectName || !baselineContext || !impactMetric) {
    alert('Please fill in all required fields.');
    return;
  }

  const generateBtn = document.getElementById('resume-generate-btn');
  if (generateBtn) {
    generateBtn.disabled = true;
    generateBtn.textContent = 'Generating...';
  }

  try {
    setStatus("Generating resume bullets...");

    const response = await apiFetch(`${API_BASE}/api/feature3/sprint/${sprint.sprint_id}/resume-inject`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project_name: projectName,
        baseline_context: baselineContext,
        impact_metric_hint: impactMetric
      })
    });

    if (!response.ok) throw new Error(await response.text());

    const result = await response.json();

    AppState.setState({
      feature3: {
        ...AppState.feature3,
        resumeInject: result
      }
    });

    displayResumeBullets(result);
    setStatus("Resume bullets generated successfully");

  } catch (error) {
    setStatus(`Resume generation error: ${String(error.message).slice(0, 120)}`);
    alert('Failed to generate resume bullets. Please try again.');
  } finally {
    // Always re-enable — prevents permanent "Generating..." stuck state
    if (generateBtn) {
      generateBtn.disabled = false;
      generateBtn.textContent = 'Generate Bullets';
    }
  }
}

function displayResumeBullets(result) {
  const resultsContainer = document.getElementById('resume-results');
  const bulletsList = document.getElementById('resume-bullets-list');
  const linkedinSnippet = document.getElementById('resume-linkedin-snippet');
  
  if (!resultsContainer) return;
  
  // Show results section
  resultsContainer.style.display = 'block';
  
  // Hide input form
  document.getElementById('resume-input-form').style.display = 'none';
  document.getElementById('resume-generate-btn').style.display = 'none';
  
  // Display bullets
  if (result.star_bullets && Array.isArray(result.star_bullets)) {
    bulletsList.innerHTML = result.star_bullets.map((bullet, index) => `
      <div class="p-3" style="background:rgba(34,197,94,0.1);border-radius:8px;border:1px solid rgba(34,197,94,0.3)">
        <div class="flex items-start gap-2">
          <span style="color:#34d399;font-weight:600;font-size:0.85rem;flex-shrink:0">${index + 1}.</span>
          <p style="font-size:0.85rem;color:rgba(255,255,255,0.85);line-height:1.6">${bullet}</p>
        </div>
      </div>
    `).join('');
  } else {
    bulletsList.innerHTML = '<p style="color:rgba(255,255,255,0.5)">No bullets generated</p>';
  }
  
  // Display LinkedIn snippet
  if (result.linkedin_snippet) {
    linkedinSnippet.textContent = result.linkedin_snippet;
  } else {
    linkedinSnippet.textContent = 'No LinkedIn snippet available';
  }
}

function copyResumeBullets() {
  const result = AppState.feature3?.resumeInject;
  if (!result || !result.star_bullets) {
    alert('No bullets to copy');
    return;
  }
  
  const text = result.star_bullets.map((bullet, index) => `• ${bullet}`).join('\n\n');
  
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.getElementById('copy-bullets-btn');
    if (btn) {
      const originalText = btn.textContent;
      btn.textContent = '✓ Copied!';
      btn.style.color = '#34d399';
      setTimeout(() => {
        btn.textContent = originalText;
        btn.style.color = '';
      }, 2000);
    }
    setStatus('Resume bullets copied to clipboard');
  }).catch(() => {
    alert('Failed to copy to clipboard');
  });
}

function copyLinkedInSnippet() {
  const result = AppState.feature3?.resumeInject;
  if (!result || !result.linkedin_snippet) {
    alert('No LinkedIn snippet to copy');
    return;
  }
  
  navigator.clipboard.writeText(result.linkedin_snippet).then(() => {
    const btn = document.getElementById('copy-linkedin-btn');
    if (btn) {
      const originalText = btn.textContent;
      btn.textContent = '✓ Copied!';
      btn.style.color = '#34d399';
      setTimeout(() => {
        btn.textContent = originalText;
        btn.style.color = '';
      }, 2000);
    }
    setStatus('LinkedIn snippet copied to clipboard');
  }).catch(() => {
    alert('Failed to copy to clipboard');
  });
}

// Resume modal event listeners
document.addEventListener('DOMContentLoaded', function() {
  const resumeModalClose = document.getElementById('resume-modal-close');
  const resumeModalCloseBtn = document.getElementById('resume-modal-close-btn');
  const resumeGenerateBtn = document.getElementById('resume-generate-btn');
  const copyBulletsBtn = document.getElementById('copy-bullets-btn');
  const copyLinkedInBtn = document.getElementById('copy-linkedin-btn');
  
  if (resumeModalClose) {
    resumeModalClose.addEventListener('click', closeResumeModal);
  }
  if (resumeModalCloseBtn) {
    resumeModalCloseBtn.addEventListener('click', closeResumeModal);
  }
  if (resumeGenerateBtn) {
    resumeGenerateBtn.addEventListener('click', generateResumeBullets);
  }
  if (copyBulletsBtn) {
    copyBulletsBtn.addEventListener('click', copyResumeBullets);
  }
  if (copyLinkedInBtn) {
    copyLinkedInBtn.addEventListener('click', copyLinkedInSnippet);
  }
  
  // Close modal on backdrop click
  const resumeModal = document.getElementById('resume-modal');
  if (resumeModal) {
    resumeModal.addEventListener('click', function(e) {
      if (e.target === resumeModal) {
        closeResumeModal();
      }
    });
  }
});

// ─── Enhanced ROI Display Functions ───────────────────────────────────────────

function updateEnhancedRoiDisplay() {
  const roi = AppState.feature3?.roi;
  const enhancedSection = document.getElementById('feature3-roi-enhanced');
  
  if (!roi || !enhancedSection) return;
  
  // Show enhanced ROI section
  enhancedSection.style.display = 'block';
  
  // Update callback probability
  const callbackProb = roi.callback_probability || {};
  const callbackValue = document.getElementById('roi-callback-value');
  const callbackDelta = document.getElementById('roi-callback-delta');
  
  if (callbackValue) {
    callbackValue.textContent = `${Math.round(callbackProb.probability || 0)}%`;
  }
  if (callbackDelta) {
    const increase = callbackProb.increase_percentage || 0;
    callbackDelta.textContent = `+${Math.round(increase)}%`;
  }
  
  // Update lifetime value
  const ltv = roi.lifetime_value || {};
  const ltvValue = document.getElementById('roi-lifetime-value');
  const annualValue = document.getElementById('roi-annual-value');
  
  if (ltvValue) {
    const delta = ltv.five_year_value_delta_usd || 0;
    ltvValue.textContent = `$${Math.round(delta).toLocaleString()}`;
  }
  if (annualValue) {
    const delta = ltv.five_year_value_delta_usd || 0;
    const annual = delta / 5;
    annualValue.textContent = `$${Math.round(annual).toLocaleString()}`;
  }
}

function showRoiModal() {
  const roi = AppState.feature3?.roi;
  if (!roi) {
    alert('No ROI data available. Please run Full Arbitrage first.');
    return;
  }
  
  const modal = document.getElementById('roi-modal');
  if (!modal) return;
  
  // Populate callback probability
  const callback = roi.callback_probability || {};
  document.getElementById('roi-modal-callback-current').textContent = `${Math.round(callback.baseline_probability || 0)}%`;
  document.getElementById('roi-modal-callback-after').textContent = `${Math.round(callback.probability || 0)}%`;
  document.getElementById('roi-modal-callback-increase').textContent = `+${Math.round(callback.increase_percentage || 0)}%`;
  document.getElementById('roi-modal-callback-reasoning').textContent = callback.reasoning || 'Closing skill gaps increases interview callback rates.';
  
  // Populate lifetime value
  const ltv = roi.lifetime_value || {};
  const fiveYearDelta = ltv.five_year_value_delta_usd || 0;
  const annualIncrease = fiveYearDelta / 5;
  const roiMultiple = ltv.roi_multiple || 0;
  
  document.getElementById('roi-modal-ltv-5year').textContent = `$${Math.round(fiveYearDelta).toLocaleString()}`;
  document.getElementById('roi-modal-ltv-annual').textContent = `$${Math.round(annualIncrease).toLocaleString()}`;
  document.getElementById('roi-modal-ltv-multiple').textContent = `${roiMultiple.toFixed(1)}x`;
  document.getElementById('roi-modal-ltv-explanation').textContent = ltv.explanation || 'Projected earnings increase over 5 years based on market data and skill gap closure.';
  
  // Populate skill impact — Bug 12 fix: backend returns {baseline_match_rate, projected_match_rate, delta_points}
  const skillImpact = roi.skill_impact || {};
  const skillImpactContainer = document.getElementById('roi-modal-skill-impact');
  if (skillImpact.delta_points !== undefined) {
    const gap = AppState.feature3?.gap;
    const niche = gap?.niche_recommendations || [];
    const nicheRows = niche.slice(0, 5).map(rec => [
      '<div class="p-3" style="background:rgba(168,85,247,0.1);border-radius:8px;border:1px solid rgba(168,85,247,0.3)">',
      '<div class="flex items-center justify-between">',
      '<span style="font-size:0.9rem;font-weight:600;color:#fff">' + (rec.skill || 'Skill') + '</span>',
      '<span style="font-size:0.85rem;color:#c084fc">Score: ' + Math.round(rec.opportunity_score || 0) + '</span>',
      '</div>',
      '<p style="font-size:0.8rem;color:rgba(255,255,255,0.6);margin-top:4px">' + (rec.why || 'High-demand skill with strong market value') + '</p>',
      '</div>'
    ].join('')).join('');
    const summaryRow = [
      '<div class="p-3 mb-2" style="background:rgba(59,130,246,0.1);border-radius:8px;border:1px solid rgba(59,130,246,0.3)">',
      '<div class="flex items-center justify-between"><span style="font-size:0.85rem;color:rgba(255,255,255,0.7)">Match Rate Baseline</span><span style="font-size:0.9rem;font-weight:600;color:#60a5fa">' + (skillImpact.baseline_match_rate || 0) + '%</span></div>',
      '<div class="flex items-center justify-between mt-1"><span style="font-size:0.85rem;color:rgba(255,255,255,0.7)">After Upskilling</span><span style="font-size:0.9rem;font-weight:600;color:#34d399">' + (skillImpact.projected_match_rate || 0) + '%</span></div>',
      '<div class="flex items-center justify-between mt-1"><span style="font-size:0.85rem;color:rgba(255,255,255,0.7)">Delta</span><span style="font-size:0.9rem;font-weight:700;color:#34d399">+' + (skillImpact.delta_points || 0) + '%</span></div>',
      '</div>'
    ].join('');
    skillImpactContainer.innerHTML = summaryRow + (nicheRows || '<p style="color:rgba(255,255,255,0.5);font-size:0.85rem">Run analysis to see skill breakdown</p>');
  } else {
    skillImpactContainer.innerHTML = '<p style="color:rgba(255,255,255,0.5);font-size:0.85rem">No skill impact data available</p>';
  }
  
  // Populate path comparison
  const pathComparison = roi.path_comparison || {};
  const pathContainer = document.getElementById('roi-modal-path-comparison');
  if (pathComparison.paths && Array.isArray(pathComparison.paths)) {
    const maxSalary = Math.max(...pathComparison.paths.map(p => p.projected_salary_usd || 0), 1);
    pathContainer.innerHTML = pathComparison.paths.map(path => {
      const pct = ((path.projected_salary_usd || 0) / maxSalary) * 100;
      return `
        <div class="p-3" style="background:rgba(255,255,255,0.05);border-radius:8px;border:1px solid rgba(255,255,255,0.1)">
          <div class="flex items-center justify-between mb-2">
            <span style="font-size:0.9rem;font-weight:600;color:#fff">${path.path || 'Career Path'}</span>
            <span style="font-size:0.9rem;font-weight:700;color:#60a5fa">$${Math.round(path.projected_salary_usd || 0).toLocaleString()}</span>
          </div>
          <div style="width:100%;height:8px;background:rgba(255,255,255,0.1);border-radius:4px;overflow:hidden">
            <div style="width:${pct}%;height:100%;background:linear-gradient(90deg, #3b82f6, #8b5cf6);border-radius:4px"></div>
          </div>
        </div>
      `;
    }).join('');
  } else {
    pathContainer.innerHTML = '<p style="color:rgba(255,255,255,0.5);font-size:0.85rem">No path comparison data available</p>';
  }
  
  // Populate success stories
  const successStories = roi.success_stories || [];
  const storiesContainer = document.getElementById('roi-modal-success-stories');
  if (successStories.length > 0) {
    storiesContainer.innerHTML = successStories.map(story => `
      <div class="p-3" style="background:rgba(34,197,94,0.1);border-radius:8px;border:1px solid rgba(34,197,94,0.3)">
        <div class="flex items-start gap-2">
          <span style="font-size:1.2rem">✨</span>
          <div style="flex:1">
            <p style="font-size:0.9rem;font-weight:600;color:#fff;margin-bottom:4px">${story.persona || 'Career Changer'}</p>
            <p style="font-size:0.85rem;color:rgba(255,255,255,0.85);line-height:1.6;margin-bottom:4px">${story.result || story.story || story.description || ''}</p>
            <div class="flex items-center gap-3 mt-1">
              ${story.timeline_weeks ? `<span style="font-size:0.75rem;color:rgba(255,255,255,0.5)">⏱ ${story.timeline_weeks} weeks</span>` : ''}
              ${story.match_rate_lift_points ? `<span style="font-size:0.75rem;color:#34d399">+${story.match_rate_lift_points} match pts</span>` : ''}
              ${story.bucket ? `<span style="font-size:0.7rem;padding:2px 6px;border-radius:4px;background:rgba(34,197,94,0.2);color:#34d399">${story.bucket.replace('_', ' ')}</span>` : ''}
            </div>
          </div>
        </div>
      </div>
    `).join('');
  } else {
    storiesContainer.innerHTML = '<p style="color:rgba(255,255,255,0.5);font-size:0.85rem">No success stories available</p>';
  }
  
  // Show modal
  modal.style.display = 'flex';
}

function closeRoiModal() {
  const modal = document.getElementById('roi-modal');
  if (modal) modal.style.display = 'none';
}

// ROI modal event listeners
document.addEventListener('DOMContentLoaded', function() {
  const roiDetailsBtn = document.getElementById('feature3-roi-details-btn');
  const roiModalClose = document.getElementById('roi-modal-close');
  const roiModalCloseBtn = document.getElementById('roi-modal-close-btn');
  
  if (roiDetailsBtn) {
    roiDetailsBtn.addEventListener('click', showRoiModal);
  }
  if (roiModalClose) {
    roiModalClose.addEventListener('click', closeRoiModal);
  }
  if (roiModalCloseBtn) {
    roiModalCloseBtn.addEventListener('click', closeRoiModal);
  }
  
  // Close modal on backdrop click
  const roiModal = document.getElementById('roi-modal');
  if (roiModal) {
    roiModal.addEventListener('click', function(e) {
      if (e.target === roiModal) {
        closeRoiModal();
      }
    });
  }
});

// ─── History Modal Functions ──────────────────────────────────────────────────

function showHistoryModal() {
  const history = AppState.feature3?.history;
  if (!history || !history.monthly_snapshots || history.monthly_snapshots.length === 0) {
    alert('No historical data available. Run Skill Arbitrage multiple times to build history.');
    return;
  }
  
  const modal = document.getElementById('history-modal');
  if (!modal) return;
  
  // Populate trend summary
  const trend = history.trend || { monthly_delta: 0, confidence: 0 };
  const delta = trend.monthly_delta || 0;
  const confidence = Math.round((trend.confidence || 0) * 100);
  
  document.getElementById('history-trend-delta').textContent = delta > 0 ? `+${delta}%` : `${delta}%`;
  document.getElementById('history-trend-confidence').textContent = `${confidence}%`;
  
  // Set trend message
  let trendMessage = '';
  if (delta > 5) {
    trendMessage = '🚀 Your skills are improving! Keep up the momentum.';
  } else if (delta < -5) {
    trendMessage = '⚠️ Market requirements are shifting. Time to upskill.';
  } else {
    trendMessage = '📊 Your skill match is stable. Consider targeting high-ROI skills.';
  }
  document.getElementById('history-trend-message').textContent = trendMessage;
  
  // Draw timeline chart
  drawHistoryChart(history.monthly_snapshots);
  
  // Populate monthly snapshots list
  const snapshotsList = document.getElementById('history-snapshots-list');
  if (snapshotsList) {
    snapshotsList.innerHTML = history.monthly_snapshots.map(snapshot => {
      const month = snapshot.month || 'Unknown';
      const score = snapshot.avg_match_score || 0;
      const samples = snapshot.samples || 0;
      
      return `
        <div class="p-3" style="background:rgba(255,255,255,0.03);border-radius:8px;border:1px solid rgba(255,255,255,0.1);display:flex;justify-content:space-between;align-items:center">
          <div>
            <p style="font-size:0.9rem;font-weight:600;color:#fff">${month}</p>
            <p style="font-size:0.75rem;color:rgba(255,255,255,0.5);margin-top:2px">${samples} sample${samples !== 1 ? 's' : ''}</p>
          </div>
          <div class="text-right">
            <p style="font-size:1.2rem;font-weight:700;color:#818cf8">${score}%</p>
          </div>
        </div>
      `;
    }).join('');
  }
  
  // Show modal
  modal.style.display = 'flex';
}

function closeHistoryModal() {
  const modal = document.getElementById('history-modal');
  if (modal) modal.style.display = 'none';
}

function drawHistoryChart(snapshots) {
  const canvas = document.getElementById('history-chart-canvas');
  if (!canvas || !snapshots || snapshots.length === 0) return;
  
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  
  // Set canvas size
  const width = canvas.offsetWidth || 700;
  const height = 180;
  canvas.width = width;
  canvas.height = height;
  
  // Clear canvas
  ctx.clearRect(0, 0, width, height);
  
  // Chart dimensions
  const padding = { top: 20, right: 20, bottom: 40, left: 50 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  
  // Extract data
  const scores = snapshots.map(s => s.avg_match_score || 0);
  const labels = snapshots.map(s => s.month || '');
  
  // Calculate scales
  const minScore = Math.max(0, Math.min(...scores) - 10);
  const maxScore = Math.min(100, Math.max(...scores) + 10);
  const scoreRange = maxScore - minScore;
  
  // Draw grid lines
  ctx.strokeStyle = 'rgba(255,255,255,0.1)';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = padding.top + (chartHeight / 4) * i;
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(padding.left + chartWidth, y);
    ctx.stroke();
    
    // Y-axis labels
    const scoreValue = maxScore - (scoreRange / 4) * i;
    ctx.fillStyle = 'rgba(255,255,255,0.5)';
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(`${Math.round(scoreValue)}%`, padding.left - 10, y + 4);
  }
  
  // Draw line chart
  if (scores.length > 0) {
    ctx.strokeStyle = '#818cf8';
    ctx.lineWidth = 3;
    ctx.beginPath();
    
    // Bug 15 fix: compute divisor once — handles single data point correctly
    const divisor = scores.length > 1 ? scores.length - 1 : 1;
    
    scores.forEach((score, index) => {
      const x = scores.length === 1 ? padding.left + chartWidth / 2 : padding.left + (chartWidth / divisor) * index;
      const y = padding.top + chartHeight - ((score - minScore) / scoreRange) * chartHeight;
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    
    ctx.stroke();
    
    // Draw data points
    scores.forEach((score, index) => {
      const x = scores.length === 1 ? padding.left + chartWidth / 2 : padding.left + (chartWidth / divisor) * index;
      const y = padding.top + chartHeight - ((score - minScore) / scoreRange) * chartHeight;
      
      // Point circle
      ctx.fillStyle = '#818cf8';
      ctx.beginPath();
      ctx.arc(x, y, 5, 0, 2 * Math.PI);
      ctx.fill();
      
      // Point border
      ctx.strokeStyle = '#1e1b4b';
      ctx.lineWidth = 2;
      ctx.stroke();
    });
  }
  
  // Draw X-axis labels — Bug 15 fix: use same divisor logic
  ctx.fillStyle = 'rgba(255,255,255,0.5)';
  ctx.font = '10px Inter, sans-serif';
  ctx.textAlign = 'center';
  const labelDivisor = labels.length > 1 ? labels.length - 1 : 1;
  labels.forEach((label, index) => {
    const x = labels.length === 1 ? padding.left + chartWidth / 2 : padding.left + (chartWidth / labelDivisor) * index;
    const y = height - padding.bottom + 20;
    ctx.fillText(label, x, y);
  });
}

// History modal event listeners
document.addEventListener('DOMContentLoaded', function() {
  const historyModalClose = document.getElementById('history-modal-close');
  const historyModalCloseBtn = document.getElementById('history-modal-close-btn');
  
  if (historyModalClose) {
    historyModalClose.addEventListener('click', closeHistoryModal);
  }
  if (historyModalCloseBtn) {
    historyModalCloseBtn.addEventListener('click', closeHistoryModal);
  }
  
  // Close modal on backdrop click
  const historyModal = document.getElementById('history-modal');
  if (historyModal) {
    historyModal.addEventListener('click', function(e) {
      if (e.target === historyModal) {
        closeHistoryModal();
      }
    });
  }
});

// ─── Export Modal Functions ───────────────────────────────────────────────────

function showExportModal() {
  const candidateId = nodes.candidateId.value.trim() || "candidate-001";
  
  // Check if there's any data to export
  const hasData = AppState.feature3?.marketSnapshot || 
                  AppState.feature3?.gapAnalysis || 
                  AppState.feature3?.sprint || 
                  AppState.feature3?.roiReport;
  
  if (!hasData) {
    alert('No analysis data available. Please run Full Arbitrage first.');
    return;
  }
  
  const modal = document.getElementById('export-modal');
  if (!modal) return;
  
  // Reset status
  const statusDiv = document.getElementById('export-status');
  if (statusDiv) statusDiv.style.display = 'none';
  
  // Show modal
  modal.style.display = 'flex';
}

function closeExportModal() {
  const modal = document.getElementById('export-modal');
  if (modal) modal.style.display = 'none';
}

async function selectExportFormat(format) {
  const candidateId = nodes.candidateId.value.trim() || "candidate-001";
  const statusDiv = document.getElementById('export-status');
  const statusText = document.getElementById('export-status-text');
  
  if (!statusDiv || !statusText) return;
  
  // Show loading status
  statusDiv.style.display = 'block';
  statusText.textContent = `Preparing ${format.toUpperCase()} export...`;
  
  try {
    setStatus(`Exporting analysis as ${format.toUpperCase()}...`);
    
    const response = await apiFetch(
      `${API_BASE}/api/feature3/candidate/${encodeURIComponent(candidateId)}/export?format=${format}`,
      { method: "GET" }
    );
    
    if (!response.ok) throw new Error("Export failed");
    
    // Get filename from Content-Disposition header or use default
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = `career_os_analysis_${candidateId}.${format}`;
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
      if (filenameMatch) filename = filenameMatch[1];
    }
    
    // Get the blob
    const blob = await response.blob();
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    
    // Cleanup
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    // Show success status
    statusText.textContent = `✅ ${format.toUpperCase()} export downloaded successfully!`;
    setStatus(`Analysis exported as ${format.toUpperCase()}`);
    
    // Close modal after 2 seconds
    setTimeout(() => {
      closeExportModal();
    }, 2000);
    
  } catch (error) {
    statusText.textContent = `❌ Export failed: ${error.message}`;
    setStatus(`Export error: ${String(error.message).slice(0, 120)}`);
  }
}

// Export modal event listeners
document.addEventListener('DOMContentLoaded', function() {
  const exportModalClose = document.getElementById('export-modal-close');
  const exportModalCloseBtn = document.getElementById('export-modal-close-btn');
  
  if (exportModalClose) {
    exportModalClose.addEventListener('click', closeExportModal);
  }
  if (exportModalCloseBtn) {
    exportModalCloseBtn.addEventListener('click', closeExportModal);
  }
  
  // Close modal on backdrop click
  const exportModal = document.getElementById('export-modal');
  if (exportModal) {
    exportModal.addEventListener('click', function(e) {
      if (e.target === exportModal) {
        closeExportModal();
      }
    });
  }
});

function processResume(fileName = "Resume.pdf", fileObject = null) {
  AppState.setState({
    resumeUploaded: true,
    scannerActive: false,
    heatmapActive: false,
    resumeFile: fileObject || AppState.resumeFile
  });
  setStatus(`Loaded ${fileName}`);
  // Update all resume name indicators
  if (nodes.onboardingResumeName) {
    nodes.onboardingResumeName.textContent = `Selected resume: ${fileName}`;
  }
  const lensResumeName = document.getElementById("lens-resume-name");
  if (lensResumeName) lensResumeName.textContent = `Selected: ${fileName}`;

  if (!AppState.analytics.firstResumeUploaded) {
    AppState.analytics.firstResumeUploaded = true;
    emitEvent("first_resume_uploaded", "onboarding", { filename: fileName });
  }
}

async function runFeature1Analysis() {
  const errs = validateRequiredFields([
    { id: "candidate-id", label: "Candidate ID" },
    { id: "job-description", label: "Job Description" }
  ]);
  if (!AppState.resumeFile) errs.push("Please upload a resume PDF.");
  if (errs.length) {
    setStatus(errs[0]);
    return;
  }

  if (!AppState.analytics.firstJdUploaded) {
    AppState.analytics.firstJdUploaded = true;
    emitEvent("first_jd_uploaded", "onboarding", { job_category: nodes.jobCategory.value });
  }

  const t0 = performance.now();
  emitEvent("resume_analysis_requested", "feature1", {
    analysis_mode: "hybrid",
    job_category: nodes.jobCategory.value
  });

  AppState.setState({ scannerActive: true, heatmapActive: false });
  setUiFlag("feature1Loading", true);
  if (nodes.analyzeFeature1) nodes.analyzeFeature1.disabled = true;
  if (nodes.lensRunFeature1) nodes.lensRunFeature1.disabled = true;
  setStatus("Scanning and scoring resume...");
  const loader = showStepLoader("analysis-summary-cards", [
    "Uploading and parsing your resume PDF...",
    "Running visual hierarchy analysis...",
    "Checking ATS compatibility...",
    "Scoring keyword match against job description...",
    "Benchmarking against market percentile..."
  ]);

  const form = new FormData();
  form.append("candidate_id", nodes.candidateId.value.trim() || "candidate-001");
  form.append("job_category", nodes.jobCategory.value);
  form.append("job_description", nodes.jobDescription.value.trim());
  form.append("resume_pdf", AppState.resumeFile, AppState.resumeFile.name || "resume.pdf");

  try {
    const response = await apiFetch(`${API_BASE}/api/feature1/analyze`, {
      method: "POST",
      body: form
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || "Hiring Lens analysis failed.");
    }

    const data = await response.json();
    AppState.setState({
      feature1: { ...AppState.feature1, analysis: data },
      scannerActive: false,
      heatmapActive: true,
      resumeUploaded: true
    });
    const latencyMs = Math.round(performance.now() - t0);
    emitEvent("resume_analysis_completed", "feature1", {
      analysis_mode: "hybrid",
      score_total: data.score.overall,
      top_issue_category: data.recommendations?.[0] || "unknown",
      processing_latency_ms: latencyMs,
      confidence_distribution: data.metrics?.confidence_tier_distribution || null
    }, { resumeId: String(data.analysis_id) });
    emitEvent("resume_version_saved", "feature1", {
      version_number: data.version_number,
      score_total: data.score.overall
    }, { resumeId: String(data.analysis_id) });
    emitEvent("recommendation_viewed", "feature1", {
      recommendation_count: (data.recommendations || []).length
    }, { resumeId: String(data.analysis_id) });

    if (!AppState.analytics.firstAnalysisCompleted) {
      AppState.analytics.firstAnalysisCompleted = true;
      emitEvent("first_analysis_completed", "onboarding", {
        score_total: data.score.overall
      }, { resumeId: String(data.analysis_id) });
    }

    setStatus(`Hiring Lens complete - score ${data.score.overall}`);
    await loadVersions();
    void loadDashboard({ silent: true });
  } catch (error) {
    AppState.setState({ scannerActive: false, heatmapActive: false });
    setStatus(handleApiError(error, "Hiring Lens"));
  } finally {
    loader?.stop();
    if (nodes.analyzeFeature1) nodes.analyzeFeature1.disabled = false;
    if (nodes.lensRunFeature1) nodes.lensRunFeature1.disabled = false;
    setUiFlag("feature1Loading", false);
  }
}

async function loadVersions() {
  const candidateId = nodes.candidateId.value.trim() || "candidate-001";
  try {
    const response = await apiFetch(`${API_BASE}/api/feature1/versions/${encodeURIComponent(candidateId)}`);
    if (!response.ok) throw new Error("Could not load versions");
    const versions = await response.json();
    AppState.setState({ feature1: { ...AppState.feature1, versions } });
  } catch {
    AppState.setState({ feature1: { ...AppState.feature1, versions: [] } });
  }
}

function buildFeature2Payload() {
  // Read from dedicated rebound workspace inputs first, fall back to command-center inputs
  const notesEl = nodes.reboundWorkspaceNotes || nodes.feature2Notes;
  const transcriptEl = nodes.reboundWorkspaceTranscript || nodes.feature2Transcript;
  const audioUrlEl = nodes.reboundWorkspaceAudioUrl || nodes.feature2AudioUrl;
  const useAssemblyEl = nodes.reboundWorkspaceUseAssembly || nodes.feature2UseAssembly;
  const companyEl = nodes.reboundWorkspaceCompany || nodes.feature2Company;
  const roleEl = nodes.reboundWorkspaceRole || nodes.feature2Role;
  const roundEl = nodes.reboundWorkspaceRound || nodes.feature2Round;
  const vibeEl = nodes.reboundWorkspaceVibe || nodes.feature2Vibe;

  // Prefer whichever has content
  const notes = (notesEl?.value?.trim() && notesEl.value.trim()) ||
                (nodes.feature2Notes?.value?.trim()) || "";
  const transcript = (transcriptEl?.value?.trim() && transcriptEl.value.trim()) ||
                     (nodes.feature2Transcript?.value?.trim()) || "";
  const isVtt = transcript.includes("WEBVTT") || transcript.includes("-->");

  return {
    candidate_id: nodes.candidateId.value.trim() || "candidate-001",
    interview_round: roundEl?.value || "tech",
    company_name: companyEl?.value?.trim() || "Unknown",
    role_name: roleEl?.value?.trim() || "Software Engineer",
    interview_notes: notes,
    transcript_text: isVtt ? "" : transcript,
    transcript_vtt: isVtt ? transcript : "",
    assembly_audio_url: audioUrlEl?.value?.trim() || "",
    use_assemblyai: Boolean(useAssemblyEl?.checked),
    culture_vibe: vibeEl?.value || "neutral",
    interviewer_friendliness: 6,
    hardest_question_hint: "",
    lifecycle_stage: roundEl?.value || "tech",
    technical_expectations: ["api", "sql", "testing"],
    interview_outcome: "rejected",
    rejection_reason_hint: "",
    advanced_round_reached: false
  };
}

async function runFeature2Autopsy() {
  const errs = validateRequiredFields([
    { id: "candidate-id", label: "Candidate ID" },
    { id: "feature2-company", label: "Company" },
    { id: "feature2-role", label: "Role" }
  ]);
  const payload = buildFeature2Payload();
  if (!payload.interview_notes && !payload.transcript_text && !payload.transcript_vtt) {
    errs.push("Notes or transcript is required.");
  }
  if (errs.length) {
    setStatus(errs[0]);
    return;
  }

  let loader = null;
  setStatus("Running Interview Autopsy autopsy...");
  setUiFlag("feature2Loading", true);
  if (nodes.runFeature2) nodes.runFeature2.disabled = true;
  emitEvent("interview_debrief_started", "feature2", {
    interview_round: payload.interview_round
  });
  if (payload.transcript_text || payload.transcript_vtt || payload.assembly_audio_url) {
    emitEvent("transcript_uploaded", "feature2", {
      interview_round: payload.interview_round,
      source: payload.transcript_vtt ? "vtt" : payload.transcript_text ? "text" : "assembly_audio_url"
    });
  }
  try {
    loader = showStepLoader("feature2-output", [
      "Ingesting interview notes and transcript...",
      "Detecting weak spots and pattern breaks...",
      "Generating recovery plan and confidence signals...",
      "Computing trend and forecast outlook..."
    ]);
    const response = await apiFetch(`${API_BASE}/api/feature2/interviews`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || "Interview Autopsy analysis failed");
    }

    const interview = await response.json();
    AppState.setState({
      feature2: { ...AppState.feature2, interview }
    });

    emitEvent("feedback_generated", "feature2", {
      interview_round: interview.interview_round,
      confidence_score: interview.score?.overall_autopsy_score || null
    }, { interviewId: String(interview.interview_id) });
    emitEvent("action_plan_created", "feature2", {
      failure_theme: interview.analytics_snapshot?.rejection_category_likelihood?.[0]?.category || "unknown"
    }, { interviewId: String(interview.interview_id) });

    await Promise.all([loadFeature2Trend(), loadFeature2Forecast()]);
    setStatus(`Interview Autopsy complete - autopsy #${interview.interview_id}`);
    void loadDashboard({ silent: true });
  } catch (error) {
    setStatus(handleApiError(error, "Interview Autopsy"));
  } finally {
    loader?.stop();
    if (nodes.runFeature2) nodes.runFeature2.disabled = false;
    setUiFlag("feature2Loading", false);
  }
}

async function runQuickDebrief() {
  const debriefText =
    nodes.reboundWorkspaceNotes?.value?.trim() ||
    nodes.reboundWorkspaceTranscript?.value?.trim() ||
    nodes.feature2Notes?.value?.trim() ||
    nodes.feature2Transcript?.value?.trim() || "";
  if (!debriefText) {
    setStatus("Add notes/transcript before quick debrief.");
    return;
  }

  try {
    const response = await apiFetch(`${API_BASE}/api/feature2/quick-debrief`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ debrief_text: debriefText })
    });
    if (!response.ok) throw new Error("Quick debrief failed");

    const quickDebrief = await response.json();
    AppState.setState({ feature2: { ...AppState.feature2, quickDebrief } });
    setStatus("Quick debrief generated.");
  } catch (error) {
    setStatus(`Quick debrief error: ${String(error.message).slice(0, 120)}`);
  }
}

async function loadFeature2Trend() {
  const candidateId = nodes.candidateId.value.trim() || "candidate-001";
  try {
    const response = await apiFetch(`${API_BASE}/api/feature2/candidate/${encodeURIComponent(candidateId)}/trend`);
    if (!response.ok) throw new Error("Trend unavailable");
    const trend = await response.json();
    AppState.setState({ feature2: { ...AppState.feature2, trend } });
  } catch {
    AppState.setState({ feature2: { ...AppState.feature2, trend: null } });
  }
}

async function loadFeature2Forecast() {
  const candidateId = nodes.candidateId.value.trim() || "candidate-001";
  try {
    const response = await apiFetch(`${API_BASE}/api/feature2/candidate/${encodeURIComponent(candidateId)}/forecast`);
    if (!response.ok) throw new Error("Forecast unavailable");
    const forecast = await response.json();
    AppState.setState({ feature2: { ...AppState.feature2, forecast } });
  } catch {
    AppState.setState({ feature2: { ...AppState.feature2, forecast: null } });
  }
}

async function loadCoreDailyPlan() {
  if (!nodes.coreDailyPlan) return;
  const candidateId = nodes.candidateId.value.trim() || "candidate-001";
  try {
    nodes.coreDailyPlan.innerHTML = stateCard("Loading daily battle plan...", "loading");
    const response = await fetch(`${API_BASE}/api/core/daily-plan/${encodeURIComponent(candidateId)}`);
    if (!response.ok) throw new Error(await response.text());
    const plan = await response.json();

    const actions = (plan.next_actions || [])
      .slice(0, 3)
      .map((a) => `<div class="workspace-list-card text-[11px]">P${a.priority}: ${a.title}</div>`)
      .join("");

    nodes.coreDailyPlan.innerHTML = `
      <div class="workspace-list-card text-[11px]">Readiness: ${plan.readiness_score} (${plan.confidence_label})</div>
      <div class="workspace-list-card text-[11px]">IIR: ${Math.round((plan.metrics_snapshot?.interview_invitation_rate || 0) * 100)}% � Apps: ${plan.metrics_snapshot?.applications_logged || 0}</div>
      ${actions || stateCard("No actions yet. Run a feature to generate plan context.")}
    `;
  } catch (error) {
    nodes.coreDailyPlan.innerHTML = stateCard(`Core plan error: ${String(error.message).slice(0, 90)}`);
  }
}

async function refreshApplicationLogs() {
  if (!nodes.metricsApplicationOutput) return;
  const userId = nodes.candidateId.value.trim() || "candidate-001";
  try {
    const response = await fetch(`${API_BASE}/api/metrics/applications/${encodeURIComponent(userId)}`);
    if (!response.ok) throw new Error(await response.text());
    const rows = await response.json();
    if (!rows.length) {
      nodes.metricsApplicationOutput.innerHTML = stateCard("No application logs yet.");
      return;
    }
    nodes.metricsApplicationOutput.innerHTML = rows
      .slice(0, 6)
      .map((row) => `<div class="workspace-list-card text-[11px]">${row.application_id} � ${row.company_name_normalized} � ${row.status}</div>`)
      .join("");
  } catch (error) {
    nodes.metricsApplicationOutput.innerHTML = stateCard(`Application log load error: ${String(error.message).slice(0, 80)}`);
  }
}

async function logApplication() {
  const userId = nodes.candidateId.value.trim() || "candidate-001";
  const applicationId = (nodes.metricsApplicationId.value || "").trim();
  const company = (nodes.metricsCompany.value || "").trim();
  const role = (nodes.metricsRole.value || "").trim();
  const channel = nodes.metricsChannel.value || "job_board";

  if (!applicationId || !company || !role) {
    setStatus("Application tracker: add application ID, company, and role.");
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/api/metrics/applications`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        application_id: applicationId,
        company_name_normalized: company,
        role_name_normalized: role,
        channel
      })
    });
    if (!response.ok) throw new Error(await response.text());
    setStatus(`Application logged: ${applicationId}`);
    await refreshApplicationLogs();
  } catch (error) {
    setStatus(`Application log error: ${String(error.message).slice(0, 120)}`);
  }
}

async function updateApplicationStatus() {
  const userId = nodes.candidateId.value.trim() || "candidate-001";
  const applicationId = (nodes.metricsApplicationId.value || "").trim();
  const status = nodes.metricsStatus.value || "submitted";

  if (!applicationId) {
    setStatus("Application tracker: add application ID first.");
    return;
  }

  try {
    const response = await fetch(
      `${API_BASE}/api/metrics/applications/${encodeURIComponent(applicationId)}?user_id=${encodeURIComponent(userId)}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          status,
          status_reason: "manual_update"
        })
      }
    );
    if (!response.ok) throw new Error(await response.text());
    setStatus(`Application status updated: ${applicationId} -> ${status}`);
    await refreshApplicationLogs();
  } catch (error) {
    setStatus(`Application status error: ${String(error.message).slice(0, 120)}`);
  }
}

function attachUploadHandlers() {
  const triggerUpload = () => nodes.pdfInput.click();
  nodes.uploadZone.addEventListener("click", triggerUpload);

  nodes.uploadZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    nodes.uploadZone.classList.add("border-indigo-300/60", "bg-indigo-500/10");
  });

  nodes.uploadZone.addEventListener("dragleave", () => {
    nodes.uploadZone.classList.remove("border-indigo-300/60", "bg-indigo-500/10");
  });

  nodes.uploadZone.addEventListener("drop", (e) => {
    e.preventDefault();
    nodes.uploadZone.classList.remove("border-indigo-300/60", "bg-indigo-500/10");
    const file = e.dataTransfer.files?.[0];
    if (file) processResume(file.name, file);
  });

  nodes.pdfInput.addEventListener("change", (e) => {
    const file = e.target.files?.[0];
    if (file) processResume(file.name, file);
  });
}

function setupCursorGlow() {
  let tx = window.innerWidth * 0.45;
  let ty = window.innerHeight * 0.3;
  let x = tx;
  let y = ty;

  window.addEventListener("mousemove", (e) => {
    tx = e.clientX;
    ty = e.clientY;
  });

  const tick = () => {
    x += (tx - x) * 0.12;
    y += (ty - y) * 0.12;
    nodes.spotlight.style.left = `${x}px`;
    nodes.spotlight.style.top = `${y}px`;
    requestAnimationFrame(tick);
  };
  tick();
}

function setupNavigation() {
  nodes.navBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const nextView = btn.dataset.view;
      startViewSwap(nextView);
    });
  });

  nodes.simulateUpload.addEventListener("click", () => {
    processResume("Resume.pdf", new File(["demo"], "Resume.pdf", { type: "application/pdf" }));
    AppState.setState({ heatmapActive: true });
  });

  nodes.rerenderHeatmap.addEventListener("click", () => {
    if (AppState.resumeUploaded) AppState.setState({ heatmapActive: true });
  });

  nodes.simulateVoice?.addEventListener("click", () => {
    const randomLevel = 0.2 + Math.random() * 0.95;
    AppState.setState({ audioLevel: randomLevel });
  });

  nodes.analyzeFeature1?.addEventListener("click", runFeature1Analysis);
  nodes.runSmartAction?.addEventListener("click", runSmartAction);
  nodes.uiModeBeginner?.addEventListener("click", () => setUIMode("beginner"));
  nodes.uiModeExpert?.addEventListener("click", () => setUIMode("expert"));
  nodes.onboardingUploadResume?.addEventListener("click", () => nodes.pdfInput.click());
  nodes.onboardingRunLens?.addEventListener("click", async () => {
    syncOnboardingToCoreInputs();
    await runFeature1Analysis();
  });
  nodes.onboardingRunRebound?.addEventListener("click", async () => {
    syncOnboardingToCoreInputs();
    await runFeature2Autopsy();
  });
  nodes.onboardingRunNarrative?.addEventListener("click", async () => {
    syncOnboardingToCoreInputs();
    await runFeature5NarrativeArchitect();
  });
  nodes.onboardingOpenWorkspace?.addEventListener("click", () => startViewSwap("command-center"));
  nodes.onboardingCandidateId?.addEventListener("input", syncOnboardingToCoreInputs);
  nodes.onboardingJobCategory?.addEventListener("change", syncOnboardingToCoreInputs);
  nodes.onboardingJobDescription?.addEventListener("input", syncOnboardingToCoreInputs);
  nodes.lensRunFeature1.addEventListener("click", runFeature1Analysis);
  nodes.fetchVersions.addEventListener("click", loadVersions);
  nodes.lensLoadVersions.addEventListener("click", loadVersions);
  document.getElementById("fetch-versions-output")?.addEventListener("click", loadVersions);

  nodes.lensRunFeature1Panel?.addEventListener("click", () => {
    // Sync lens panel inputs → global inputs before running
    if (nodes.lensCandidateId?.value) nodes.candidateId.value = nodes.lensCandidateId.value;
    if (nodes.lensJobCategory?.value) nodes.jobCategory.value = nodes.lensJobCategory.value;
    if (nodes.lensJobDescription?.value) nodes.jobDescription.value = nodes.lensJobDescription.value;
    runFeature1Analysis();
  });
  nodes.lensUploadBtn?.addEventListener("click", () => nodes.pdfInput.click());

  // Sync lens panel inputs live
  nodes.lensCandidateId?.addEventListener("input", () => { nodes.candidateId.value = nodes.lensCandidateId.value; });
  nodes.lensJobCategory?.addEventListener("change", () => { nodes.jobCategory.value = nodes.lensJobCategory.value; });
  nodes.lensJobDescription?.addEventListener("input", () => { nodes.jobDescription.value = nodes.lensJobDescription.value; });

  nodes.feature3WorkspaceRunPanel?.addEventListener("click", runFeature3Arbitrage);
  nodes.feature4WorkspaceRunPanel?.addEventListener("click", runFeature4PersonaPlay);

  nodes.runFeature2?.addEventListener("click", runFeature2Autopsy);
  nodes.runFeature4?.addEventListener("click", runFeature4PersonaPlay);
  nodes.runFeature3?.addEventListener("click", runFeature3Arbitrage);
  nodes.runFeature5?.addEventListener("click", runFeature5NarrativeArchitect);
  nodes.dashboardNextAction?.addEventListener("click", runSmartAction);
  nodes.dashboardOpenWorkspace?.addEventListener("click", () => startViewSwap("command-center"));
  nodes.dashboardRefresh?.addEventListener("click", () => loadDashboard());
  nodes.dashboardFeatureExplainer?.addEventListener("click", (event) => {
    const target = event.target.closest("button[data-view]");
    if (!target) return;
    startViewSwap(target.dataset.view);
  });
  nodes.feature2QuickDebrief?.addEventListener("click", runQuickDebrief);
  nodes.feature2LoadTrend?.addEventListener("click", async () => {
    await Promise.all([loadFeature2Trend(), loadFeature2Forecast()]);
    setStatus("Interview Autopsy trend/forecast loaded.");
  });
  // Rebound workspace buttons
  nodes.reboundWorkspaceRun?.addEventListener("click", runFeature2Autopsy);
  nodes.reboundWorkspaceQuickDebrief?.addEventListener("click", runQuickDebrief);
  nodes.reboundWorkspaceLoadTrend?.addEventListener("click", async () => {
    await Promise.all([loadFeature2Trend(), loadFeature2Forecast()]);
    setStatus("Interview Autopsy trend/forecast loaded.");
  });
  nodes.feature3LoadHistory?.addEventListener("click", loadFeature3History);
  nodes.feature3RunQuiz?.addEventListener("click", runFeature3SprintQuiz);
  nodes.feature3ResumeInject?.addEventListener("click", runFeature3ResumeInjector);
  nodes.feature3Export?.addEventListener("click", exportFeature3Snapshot);
  nodes.feature4Finalize?.addEventListener("click", finalizeFeature4Again);
  nodes.feature4Share?.addEventListener("click", shareFeature4Session);
  nodes.feature4WorkspaceRun?.addEventListener("click", runFeature4PersonaPlay);
  nodes.feature4WorkspaceFinalize?.addEventListener("click", finalizeFeature4Again);
  nodes.feature4WorkspaceShare?.addEventListener("click", shareFeature4Session);
  nodes.feature4WorkspaceHistory?.addEventListener("click", loadFeature4History);
  nodes.feature4WorkspaceCompare?.addEventListener("click", compareLatestFeature4Sessions);
  // Feature 4 Interactive Mode buttons (Member 2 implementation)
  document.getElementById("feature4-start-interactive")?.addEventListener("click", startMockInterview);
  document.getElementById("feature4-submit-answer")?.addEventListener("click", submitAnswer);
  document.getElementById("feature4-end-session")?.addEventListener("click", endSession);
  nodes.feature5LoadHistory?.addEventListener("click", loadFeature5History);
  nodes.feature5Export?.addEventListener("click", exportFeature5Bundle);
  nodes.feature5Download?.addEventListener("click", downloadFeature5Bundle);
  nodes.feature5DownloadPdf?.addEventListener("click", downloadFeature5CaseStudyPdf);
  nodes.feature5DownloadSite?.addEventListener("click", downloadFeature5PortfolioSite);
  nodes.feature5WorkspaceRun?.addEventListener("click", runFeature5NarrativeArchitect);
  nodes.feature5WorkspaceHistory?.addEventListener("click", loadFeature5History);
  nodes.feature5WorkspaceExport?.addEventListener("click", exportFeature5Bundle);
  nodes.feature5WorkspaceDownload?.addEventListener("click", downloadFeature5Bundle);
  nodes.feature5WorkspaceDownloadPdf?.addEventListener("click", downloadFeature5CaseStudyPdf);
  nodes.feature5WorkspaceDownloadSite?.addEventListener("click", downloadFeature5PortfolioSite);
  // Duplicate buttons inside the results panel
  document.getElementById("feature5-workspace-run-2")?.addEventListener("click", runFeature5NarrativeArchitect);
  document.getElementById("feature5-workspace-export-2")?.addEventListener("click", exportFeature5Bundle);
  document.getElementById("feature5-workspace-download-2")?.addEventListener("click", downloadFeature5Bundle);
  document.getElementById("feature5-workspace-download-pdf-2")?.addEventListener("click", downloadFeature5CaseStudyPdf);
  document.getElementById("feature5-workspace-download-site-2")?.addEventListener("click", downloadFeature5PortfolioSite);

  // LinkedIn post
  document.getElementById("feature5-generate-linkedin")?.addEventListener("click", generateLinkedInPost);
  document.getElementById("feature5-copy-linkedin")?.addEventListener("click", copyLinkedInPost);
  nodes.feature3WorkspaceRun?.addEventListener("click", runFeature3Arbitrage);
  nodes.feature3WorkspaceHistory?.addEventListener("click", loadFeature3History);
  nodes.feature3WorkspaceExport?.addEventListener("click", exportFeature3Snapshot);
  nodes.feature3WorkspaceQuiz?.addEventListener("click", runFeature3SprintQuiz);

  // Fix 2: Auto-fill skills from Feature 1 resume
  document.getElementById("feature3-autofill-skills")?.addEventListener("click", async function() {
    const candidateId = nodes.candidateId.value.trim() || "candidate-001";
    this.textContent = "...";
    this.disabled = true;
    try {
      const res = await apiFetch(`${API_BASE}/api/feature1/candidate/${encodeURIComponent(candidateId)}/skills`);
      if (!res.ok) throw new Error("No resume analysis found");
      const data = await res.json();
      if (data.skills && data.skills.length > 0) {
        nodes.feature3CurrentSkills.value = data.skills.join(", ");
        setStatus(`Auto-filled ${data.skills.length} skills from your resume.`);
      } else {
        setStatus("No skills found in resume. Run Lens analysis first.");
      }
    } catch {
      setStatus("Run Lens (Feature 1) first to enable skill auto-fill.");
    } finally {
      this.textContent = "↑ Resume";
      this.disabled = false;
    }
  });
  nodes.feature3WorkspaceResumeInject?.addEventListener("click", runFeature3ResumeInjector);
  nodes.coreLoadPlan?.addEventListener("click", loadCoreDailyPlan);
  nodes.metricsLogApplication?.addEventListener("click", logApplication);
  nodes.metricsUpdateStatus?.addEventListener("click", updateApplicationStatus);

  window.addEventListener("resize", drawAllSparklines);
  window.addEventListener("resize", drawFeature3Radar);
  window.addEventListener("resize", drawFeature4SignalChart);
}

AppState.subscribe((state) => {
  nodes.scannerLine.classList.toggle("scanning", state.scannerActive);

  if (state.heatmapActive) renderHeatmapOverlay();
  else resetHeatmapOverlay();

  if (state.resumeUploaded) {
    staggerCardWake();
    nodes.reactiveCards.forEach((card, i) => {
      card.classList.add("card-glow");
      setTimeout(() => card.classList.remove("card-glow"), 900 + i * 80);
    });
  }

  renderFeature1Summary();
  renderUIMode();
  renderDashboard();
  renderSmartAction();
  renderLensWorkspace();
  renderVersions();
  renderFeature2Output();
  renderReboundWorkspace();
  renderFeature4Output();
  renderFeature4Workspace();
  renderFeature5Output();
  renderFeature5Workspace();
  renderFeature3Output();
  renderFeature3Workspace();
  drawFeature3Radar();
  drawFeature4SignalChart();
  renderFeature3RoiBars();
  applyViewState(state.view);
});

function init() {
  lucide.createIcons();
  setupNavigation();
  attachUploadHandlers();
  setupCursorGlow();
  drawAllSparklines();
  animateWavePath();
  applyViewState(AppState.view);
  loadCoreDailyPlan();
  refreshApplicationLogs();
  setTimeout(staggerCardWake, 140);
}

init();


// ═══════════════════════════════════════════════════════════════════════════
// JOB TRACKER MODULE
// Kanban board backed by /api/jobs — JWT auth via existing apiFetch helper.
// ═══════════════════════════════════════════════════════════════════════════

const JT = (() => {
  // ── State ────────────────────────────────────────────────────────────────
  const state = {
    jobs: [],          // JobRead[]
    loading: false,
  };

  const STATUSES = ["Wishlist", "Applied", "Interviewing", "Offered", "Rejected"];

  // ── DOM refs (resolved lazily so the module is safe to load before DOM) ──
  const el = (id) => document.getElementById(id);

  // ── API helpers ──────────────────────────────────────────────────────────

  /**
   * Thin wrapper around the existing apiFetch that handles 401 by showing
   * the auth modal instead of crashing the board.
   */
  async function jtFetch(path, options = {}) {
    const res = await apiFetch(`${API_BASE}${path}`, options);
    if (res.status === 401) {
      const modal = el("auth-modal");
      if (modal) modal.style.display = "flex";
      throw new Error("401 Unauthorized");
    }
    return res;
  }

  async function fetchJobs() {
    state.loading = true;
    renderBoard();
    try {
      const res = await jtFetch("/api/jobs");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      state.jobs = await res.json();
    } catch (err) {
      console.error("[JT] fetchJobs:", err);
    } finally {
      state.loading = false;
      renderBoard();
    }
  }

  async function createJob(payload) {
    const res = await jtFetch("/api/jobs", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail ?? `HTTP ${res.status}`);
    }
    const job = await res.json();
    state.jobs = [...state.jobs, job];
    renderBoard();
    return job;
  }

  async function updateJob(id, patch) {
    const res = await jtFetch(`/api/jobs/${id}`, {
      method: "PATCH",
      body: JSON.stringify(patch),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail ?? `HTTP ${res.status}`);
    }
    const updated = await res.json();
    state.jobs = state.jobs.map((j) => (j.id === id ? updated : j));
    renderBoard();
    return updated;
  }

  async function deleteJob(id) {
    const res = await jtFetch(`/api/jobs/${id}`, { method: "DELETE" });
    if (!res.ok && res.status !== 204) {
      throw new Error(`HTTP ${res.status}`);
    }
    state.jobs = state.jobs.filter((j) => j.id !== id);
    renderBoard();
  }

  // ── Rendering ────────────────────────────────────────────────────────────

  const STATUS_COLORS = {
    Wishlist:     { dot: "#6366f1", badge: "rgba(99,102,241,0.18)",  text: "#a5b4fc" },
    Applied:      { dot: "#f59e0b", badge: "rgba(245,158,11,0.18)",  text: "#fcd34d" },
    Interviewing: { dot: "#06b6d4", badge: "rgba(6,182,212,0.18)",   text: "#67e8f9" },
    Offered:      { dot: "#10b981", badge: "rgba(16,185,129,0.18)",  text: "#6ee7b7" },
    Rejected:     { dot: "#ef4444", badge: "rgba(239,68,68,0.18)",   text: "#fca5a5" },
  };

  function buildCard(job) {
    const col = STATUS_COLORS[job.status] ?? STATUS_COLORS.Wishlist;
    const dateStr = job.date_applied
      ? new Date(job.date_applied + "T00:00:00").toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })
      : null;

    const card = document.createElement("article");
    card.className = "jt-card";
    card.dataset.id = job.id;
    card.draggable = true;
    card.innerHTML = `
      <div class="jt-card-header">
        <div class="jt-card-company">${escHtml(job.company)}</div>
        <button class="jt-card-delete" data-action="delete" data-id="${job.id}" aria-label="Delete job" title="Delete">
          <i data-lucide="trash-2" class="w-3.5 h-3.5 pointer-events-none"></i>
        </button>
      </div>
      <div class="jt-card-position">${escHtml(job.position)}</div>
      <div class="jt-card-meta">
        ${dateStr ? `<span class="jt-meta-chip"><i data-lucide="calendar" class="w-3 h-3"></i>${dateStr}</span>` : ""}
        ${job.salary ? `<span class="jt-meta-chip"><i data-lucide="banknote" class="w-3 h-3"></i>${escHtml(job.salary)}</span>` : ""}
      </div>
      ${job.notes ? `<p class="jt-card-notes">${escHtml(job.notes.slice(0, 90))}${job.notes.length > 90 ? "…" : ""}</p>` : ""}
      <div class="jt-card-footer">
        <select class="jt-status-select" data-action="status" data-id="${job.id}" aria-label="Change status">
          ${STATUSES.map((s) => `<option value="${s}"${s === job.status ? " selected" : ""}>${s}</option>`).join("")}
        </select>
        <button class="jt-card-edit" data-action="edit" data-id="${job.id}" aria-label="Edit job">
          <i data-lucide="pencil" class="w-3.5 h-3.5 pointer-events-none"></i> Edit
        </button>
      </div>
    `;
    return card;
  }

  function renderBoard() {
    if (state.loading) {
      STATUSES.forEach((s) => {
        const col = el(`jt-col-${s}`);
        if (col) col.innerHTML = `<div class="jt-skeleton"></div><div class="jt-skeleton"></div>`;
      });
      return;
    }

    // Group by status
    const grouped = {};
    STATUSES.forEach((s) => { grouped[s] = []; });
    state.jobs.forEach((j) => {
      if (grouped[j.status]) grouped[j.status].push(j);
    });

    STATUSES.forEach((status) => {
      const col = el(`jt-col-${status}`);
      const countEl = el(`jt-count-${status}`);
      if (!col) return;

      const jobs = grouped[status];
      if (countEl) countEl.textContent = jobs.length;

      col.innerHTML = "";
      if (!jobs.length) {
        col.innerHTML = `<p class="jt-empty">No jobs here yet.</p>`;
        return;
      }
      const frag = document.createDocumentFragment();
      jobs.forEach((job) => {
        const card = buildCard(job);
        frag.appendChild(card);
      });
      col.appendChild(frag);
    });

    // Re-init lucide icons for newly created elements
    if (window.lucide) lucide.createIcons();
  }

  // ── Modal ────────────────────────────────────────────────────────────────

  function openModal(job = null) {
    const modal = el("jt-modal");
    const title = el("jt-modal-title");
    const errEl = el("jt-modal-error");

    el("jt-edit-id").value = job ? job.id : "";
    el("jt-company").value = job ? job.company : "";
    el("jt-position").value = job ? job.position : "";
    el("jt-status").value = job ? job.status : "Wishlist";
    el("jt-date").value = job?.date_applied ?? "";
    el("jt-salary").value = job?.salary ?? "";
    el("jt-notes").value = job?.notes ?? "";

    if (title) title.textContent = job ? "Edit Job" : "Add Job";
    if (errEl) errEl.style.display = "none";

    modal.style.display = "flex";
    el("jt-company").focus();
  }

  function closeModal() {
    el("jt-modal").style.display = "none";
  }

  async function saveModal() {
    const errEl = el("jt-modal-error");
    const company = el("jt-company").value.trim();
    const position = el("jt-position").value.trim();

    if (!company || !position) {
      errEl.textContent = "Company and Position are required.";
      errEl.style.display = "block";
      return;
    }

    const payload = {
      company,
      position,
      status: el("jt-status").value,
      date_applied: el("jt-date").value || null,
      salary: el("jt-salary").value.trim() || null,
      notes: el("jt-notes").value.trim() || null,
    };

    const editId = el("jt-edit-id").value;
    try {
      if (editId) {
        await updateJob(Number(editId), payload);
      } else {
        await createJob(payload);
      }
      closeModal();
    } catch (err) {
      errEl.textContent = err.message ?? "Failed to save job.";
      errEl.style.display = "block";
    }
  }

  // ── Event delegation ─────────────────────────────────────────────────────

  function onBoardClick(e) {
    const action = e.target.closest("[data-action]")?.dataset?.action;
    const id = Number(e.target.closest("[data-action]")?.dataset?.id);
    if (!action || !id) return;

    if (action === "delete") {
      if (confirm("Delete this job?")) deleteJob(id);
    }
    if (action === "edit") {
      const job = state.jobs.find((j) => j.id === id);
      if (job) openModal(job);
    }
  }

  function onBoardChange(e) {
    if (e.target.dataset.action !== "status") return;
    const id = Number(e.target.dataset.id);
    const status = e.target.value;
    updateJob(id, { status }).catch((err) => {
      console.error("[JT] status update failed:", err);
    });
  }

  // ── Init ─────────────────────────────────────────────────────────────────

  function init() {
    const board = el("jt-board");
    const rejectedStrip = document.querySelector(".jt-rejected-strip .jt-cards");

    if (board) {
      board.addEventListener("click", onBoardClick);
      board.addEventListener("change", onBoardChange);
    }
    if (rejectedStrip) {
      rejectedStrip.addEventListener("click", onBoardClick);
      rejectedStrip.addEventListener("change", onBoardChange);
    }

    el("jt-add-btn")?.addEventListener("click", () => openModal());
    el("jt-refresh-btn")?.addEventListener("click", fetchJobs);
    el("jt-modal-save")?.addEventListener("click", saveModal);
    el("jt-modal-cancel")?.addEventListener("click", closeModal);
    el("jt-modal-close")?.addEventListener("click", closeModal);

    // Close modal on backdrop click
    el("jt-modal")?.addEventListener("click", (e) => {
      if (e.target === el("jt-modal")) closeModal();
    });

    // Close modal on Escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && el("jt-modal")?.style.display !== "none") closeModal();
    });

    // Load jobs when the view becomes active
    AppState.subscribe((s) => {
      if (s.view === "job-tracker" && !state.loading) fetchJobs();
    });

    // ── Drag & Drop Support ──────────────────────────────────────────────
    let draggedCard = null;

    document.addEventListener("dragstart", (e) => {
      const card = e.target.closest(".jt-card");
      if (!card) return;
      draggedCard = card;
      card.style.opacity = "0.5";
      e.dataTransfer.effectAllowed = "move";
    });

    document.addEventListener("dragend", (e) => {
      if (draggedCard) {
        draggedCard.style.opacity = "1";
        draggedCard = null;
      }
      // Clear drag-over state from all columns
      document.querySelectorAll(".jt-cards").forEach((col) => {
        col.classList.remove("drag-over");
      });
    });

    document.addEventListener("dragover", (e) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = "move";
      
      // Add visual feedback to the target column
      const col = e.target.closest(".jt-cards");
      if (col) {
        document.querySelectorAll(".jt-cards").forEach((c) => {
          c.classList.toggle("drag-over", c === col);
        });
      }
    });

    document.addEventListener("drop", (e) => {
      e.preventDefault();
      if (!draggedCard) return;

      const col = e.target.closest(".jt-cards");
      if (!col) return;

      const status = col.closest(".jt-column")?.dataset?.status ||
                     (col.classList.contains("jt-cards-row") ? "Rejected" : null);
      if (!status) return;

      const jobId = Number(draggedCard.dataset.id);
      if (jobId) {
        updateJob(jobId, { status }).catch((err) => {
          console.error("[JT] drag-drop status update failed:", err);
        });
      }
      
      // Clear drag-over state
      document.querySelectorAll(".jt-cards").forEach((c) => {
        c.classList.remove("drag-over");
      });
    });
  }

  return { init, fetchJobs };
})();

// ── Utility: HTML escape ──────────────────────────────────────────────────
function escHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ── Bootstrap ─────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  JT.init();
});
