/* =====================================================
   Jira Executive Dashboard - app.js
   Jira REST API v3 + Claude (Lilly LLM Gateway)
   Projects: EAA, ASO, KILO
   ===================================================== */
/* global Chart */

"use strict";

// ── Config keys in localStorage ──────────────────────────────────────────────
const LS = {
  BASE_URL:    "jiraDash_baseUrl",
  EMAIL:       "jiraDash_email",
  TOKEN:       "jiraDash_token",
  PROJECTS:    "jiraDash_projects",
  CLAUDE_URL:  "jiraDash_claudeUrl",
  CLAUDE_KEY:  "jiraDash_claudeKey",
  CLAUDE_MODEL:"jiraDash_claudeModel",
};

// ── Constants ─────────────────────────────────────────────────────────────────
const JIRA_PAGE_SIZE      = 100;   // issues per Jira API request
const MAX_ISSUES_PER_PROJ = 2000;  // safety cap per project
const DEFAULT_PAGE_SIZE   = 25;    // table rows per page

// ── Runtime state ─────────────────────────────────────────────────────────────
let allIssues   = [];   // raw normalized issues
let filtered    = [];   // after applying filters
let sortCol     = "updated";
let sortDir     = "desc";
let currentPage = 1;
let charts      = {};   // Chart.js instances keyed by id

// ── Jira field → issue type icon map ─────────────────────────────────────────
const TYPE_ICON = {
  story: "📗", bug: "🐞", task: "✅", "sub-task": "↳",
  epic: "⚡", feature: "✨", improvement: "🔧", spike: "🔬",
  initiative: "🎯", risk: "⚠️", milestone: "🏁", default: "📌"
};

const PRIORITY_ICON = {
  blocker: "🔴", critical: "🔴", highest: "🔴",
  high: "🟠", medium: "🟡", low: "🟢", lowest: "⚪", default: "🔵"
};

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  loadSavedConfig();
  populateProjectBadges();
  initDateDefaults();
  renderKPIs([]);
  renderCharts([]);
});

function loadSavedConfig() {
  safeSet("cfgBaseUrl",    localStorage.getItem(LS.BASE_URL)    || "https://lilly-jira.atlassian.net");
  safeSet("cfgEmail",      localStorage.getItem(LS.EMAIL)       || "");
  safeSet("cfgToken",      localStorage.getItem(LS.TOKEN)       || "");
  safeSet("cfgProjects",   localStorage.getItem(LS.PROJECTS)    || "EAA,ASO,KILO");
  safeSet("cfgClaudeUrl",  localStorage.getItem(LS.CLAUDE_URL)  || "https://lilly-code-server.api.gateway.llm.lilly.com");
  safeSet("cfgClaudeKey",  localStorage.getItem(LS.CLAUDE_KEY)  || "");
  safeSet("cfgClaudeModel",localStorage.getItem(LS.CLAUDE_MODEL)|| "claude-3.7-sonnet-20250219-v1");
}

function safeSet(id, val) {
  const el = document.getElementById(id);
  if (el && val !== null) el.value = val;
}

function populateProjectBadges() {
  const projects = getProjects();
  const el = document.getElementById("projectBadges");
  el.innerHTML = projects.map(p => `<span class="project-badge">${p}</span>`).join("");
}

function getProjects() {
  const raw = (document.getElementById("cfgProjects")?.value || localStorage.getItem(LS.PROJECTS) || "EAA,ASO,KILO");
  return raw.split(",").map(s => s.trim()).filter(Boolean);
}

function initDateDefaults() {
  const now = new Date();
  const from = new Date(now); from.setMonth(from.getMonth() - 3);
  document.getElementById("filterDateFrom").value = from.toISOString().slice(0, 10);
  document.getElementById("filterDateTo").value   = now.toISOString().slice(0, 10);
}

// ── Settings panel ────────────────────────────────────────────────────────────
function toggleSettings() {
  document.getElementById("settingsOverlay").classList.toggle("active");
  document.getElementById("settingsPanel").classList.toggle("active");
}

function clearCreds() {
  Object.values(LS).forEach(k => localStorage.removeItem(k));
  loadSavedConfig();
  alert("Saved credentials cleared.");
}

function saveAndLoad() {
  localStorage.setItem(LS.BASE_URL,    document.getElementById("cfgBaseUrl").value.replace(/\/$/, ""));
  localStorage.setItem(LS.EMAIL,       document.getElementById("cfgEmail").value);
  localStorage.setItem(LS.TOKEN,       document.getElementById("cfgToken").value);
  localStorage.setItem(LS.PROJECTS,    document.getElementById("cfgProjects").value);
  localStorage.setItem(LS.CLAUDE_URL,  document.getElementById("cfgClaudeUrl").value.replace(/\/$/, ""));
  localStorage.setItem(LS.CLAUDE_KEY,  document.getElementById("cfgClaudeKey").value);
  localStorage.setItem(LS.CLAUDE_MODEL,document.getElementById("cfgClaudeModel").value);
  toggleSettings();
  populateProjectBadges();
  refreshData();
}

// ── Refresh / Fetch ───────────────────────────────────────────────────────────
async function refreshData() {
  const baseUrl = localStorage.getItem(LS.BASE_URL) || document.getElementById("cfgBaseUrl").value;
  const email   = localStorage.getItem(LS.EMAIL)    || document.getElementById("cfgEmail").value;
  const token   = localStorage.getItem(LS.TOKEN)    || document.getElementById("cfgToken").value;

  if (!email || !token) {
    toggleSettings();
    return;
  }

  showLoading("Connecting to Jira…");
  allIssues = [];

  const projects = getProjects();
  const auth = btoa(`${email}:${token}`);

  for (const proj of projects) {
    setLoadingMsg(`Fetching ${proj} issues…`);
    try {
      const issues = await fetchProjectIssues(baseUrl, auth, proj);
      allIssues.push(...issues);
    } catch (err) {
      console.error(`Failed to fetch ${proj}:`, err);
      showToast(`⚠️ ${proj}: ${err.message}`, "error");
    }
  }

  hideLoading();
  document.getElementById("lastUpdated").textContent = "Updated " + new Date().toLocaleTimeString();

  buildFilterOptions();
  applyFilters();
}

// ── Jira REST API ─────────────────────────────────────────────────────────────
async function fetchProjectIssues(baseUrl, auth, projectKey) {
  const maxResults = JIRA_PAGE_SIZE;
  let startAt = 0;
  let total = Infinity;
  const results = [];

  while (startAt < total && startAt < MAX_ISSUES_PER_PROJ) {
    const jql = encodeURIComponent(
      `project = ${projectKey} ORDER BY updated DESC`
    );
    const fields = [
      "summary","status","issuetype","priority","assignee","reporter",
      "created","updated","duedate","labels","fixVersions","components",
      "sprint","customfield_10020", // sprint field (common)
      "customfield_10016",          // story points
      "parent","subtasks","comment",
      "description","resolutiondate","resolution",
      "timeoriginalestimate","timespent","timeestimate"
    ].join(",");

    const url = `${baseUrl}/rest/api/3/search?jql=${jql}&startAt=${startAt}&maxResults=${maxResults}&fields=${fields}`;

    const resp = await fetch(url, {
      headers: {
        "Authorization": `Basic ${auth}`,
        "Accept": "application/json",
        "Content-Type": "application/json"
      }
    });

    if (!resp.ok) {
      const msg = await resp.text();
      throw new Error(`HTTP ${resp.status}: ${msg.slice(0, 200)}`);
    }

    const data = await resp.json();
    total = data.total;
    if (data.issues.length === 0) break;

    for (const raw of data.issues) {
      results.push(normalizeIssue(raw, projectKey));
    }

    startAt += data.issues.length;
    setLoadingMsg(`Fetching ${projectKey}… (${results.length}/${total})`);
  }

  return results;
}

function normalizeIssue(raw, projectKey) {
  const f = raw.fields;
  // Sprint: try customfield_10020 (Jira Software) first
  const sprintArr = f.customfield_10020 || f.sprint || [];
  const sprint = Array.isArray(sprintArr) && sprintArr.length > 0
    ? (sprintArr[sprintArr.length - 1].name || sprintArr[sprintArr.length - 1])
    : (typeof sprintArr === "string" ? sprintArr : "");

  return {
    key:         raw.key,
    project:     projectKey,
    summary:     f.summary || "",
    type:        (f.issuetype?.name || "").toLowerCase(),
    typeDisplay: f.issuetype?.name || "Unknown",
    status:      (f.status?.name || "").toLowerCase().replace(/\s+/g, ""),
    statusDisplay: f.status?.name || "Unknown",
    statusCategory: (f.status?.statusCategory?.key || "").toLowerCase(),
    priority:    (f.priority?.name || "").toLowerCase(),
    priorityDisplay: f.priority?.name || "Unknown",
    assignee:    f.assignee?.displayName || "Unassigned",
    assigneeEmail: f.assignee?.emailAddress || "",
    reporter:    f.reporter?.displayName || "",
    created:     f.created ? f.created.slice(0, 10) : "",
    updated:     f.updated ? f.updated.slice(0, 10) : "",
    duedate:     f.duedate || "",
    resolved:    f.resolutiondate ? f.resolutiondate.slice(0, 10) : "",
    labels:      f.labels || [],
    components:  (f.components || []).map(c => c.name),
    fixVersions: (f.fixVersions || []).map(v => v.name),
    sprint:      sprint,
    storyPoints: f.customfield_10016 || null,
    timeSpent:   f.timespent || 0,
    timeEstimate:f.timeoriginalestimate || 0,
    parent:      f.parent?.key || "",
    url:         `${localStorage.getItem(LS.BASE_URL)}/browse/${raw.key}`,
    isOverdue:   f.duedate && f.resolutiondate === null && new Date(f.duedate) < new Date(),
    description: extractTextFromADF(f.description),
    commentCount: f.comment?.total || 0,
  };
}

// Atlassian Document Format → plain text (shallow)
function extractTextFromADF(adf) {
  if (!adf) return "";
  if (typeof adf === "string") return adf;
  const parts = [];
  function walk(node) {
    if (!node) return;
    if (node.type === "text") parts.push(node.text || "");
    if (node.content) node.content.forEach(walk);
  }
  walk(adf);
  return parts.join(" ").slice(0, 500);
}

// ── Demo data ─────────────────────────────────────────────────────────────────
function loadDemoData() {
  toggleSettings();
  showLoading("Loading demo data…");
  setTimeout(() => {
    allIssues = generateDemoIssues();
    hideLoading();
    document.getElementById("lastUpdated").textContent = "Demo data loaded";
    buildFilterOptions();
    applyFilters();
  }, 400);
}

function generateDemoIssues() {
  const projects = ["EAA", "ASO", "KILO"];
  const types = ["Story","Bug","Task","Epic","Sub-task","Improvement","Spike"];
  const statuses = [
    {name:"To Do",cat:"new"},{name:"In Progress",cat:"indeterminate"},
    {name:"In Review",cat:"indeterminate"},{name:"Done",cat:"done"},
    {name:"Blocked",cat:"new"},{name:"Closed",cat:"done"}
  ];
  const priorities = ["Blocker","Critical","High","Medium","Low","Lowest"];
  const assignees = [
    "Alice Johnson","Bob Martinez","Carol Zhang","David Kim",
    "Emma Wilson","Frank Lee","Unassigned"
  ];
  const sprints = ["Sprint 42","Sprint 43","Sprint 44","Backlog"];
  const labels = ["frontend","backend","api","auth","performance","security","ux","data","infra"];

  const issues = [];
  let counter = 1;

  for (const proj of projects) {
    const count = proj === "EAA" ? 55 : proj === "ASO" ? 40 : 35;
    for (let i = 0; i < count; i++) {
      const st = statuses[Math.floor(Math.random() * statuses.length)];
      const created = randomDate(180);
      const updated = randomDate(30, new Date(created));
      const due = Math.random() > 0.4 ? randomDate(-30, new Date(updated)) : "";
      const isDone = st.cat === "done";
      issues.push({
        key: `${proj}-${counter++}`,
        project: proj,
        summary: randomSummary(proj),
        type: types[Math.floor(Math.random()*types.length)].toLowerCase(),
        typeDisplay: types[Math.floor(Math.random()*types.length)],
        status: st.name.toLowerCase().replace(/\s+/g,""),
        statusDisplay: st.name,
        statusCategory: st.cat,
        priority: priorities[Math.floor(Math.random()*priorities.length)].toLowerCase(),
        priorityDisplay: priorities[Math.floor(Math.random()*priorities.length)],
        assignee: assignees[Math.floor(Math.random()*assignees.length)],
        assigneeEmail: "",
        reporter: assignees[Math.floor(Math.random()*assignees.length)],
        created, updated,
        duedate: due,
        resolved: isDone ? updated : "",
        labels: randomSubset(labels, 2),
        components: [],
        fixVersions: [],
        sprint: sprints[Math.floor(Math.random()*sprints.length)],
        storyPoints: [1,2,3,5,8,13][Math.floor(Math.random()*6)],
        timeSpent: 0, timeEstimate: 0,
        parent: "",
        url: `#${proj}-${counter-1}`,
        isOverdue: due && !isDone && new Date(due) < new Date(),
        description: "",
        commentCount: Math.floor(Math.random()*8),
      });
    }
  }
  return issues;
}

const SUMMARIES = {
  EAA: ["Implement SSO integration","Fix token refresh race condition","Add MFA enrollment flow",
        "Update RBAC policy engine","Audit log service refactor","JWT validation edge case",
        "API gateway rate limiting","OAuth scope alignment","Session timeout configuration",
        "Certificate rotation automation","Access review dashboard","Permission sync job"],
  ASO: ["Onboard new service catalog","SLA reporting dashboard","Incident routing logic",
        "Change advisory board automation","CMDB sync pipeline","Alert aggregation service",
        "Runbook generator","On-call schedule integration","Post-incident review workflow",
        "Monitoring coverage gaps","Service dependency mapping","Escalation policy update"],
  KILO: ["Model deployment pipeline","Feature store integration","Inference latency optimization",
         "Data drift detection","A/B testing framework","Model versioning strategy",
         "GPU resource scheduler","Training data validation","Explainability dashboard",
         "Batch prediction job","Real-time scoring API","Model registry UI"],
};

function randomSummary(proj) {
  const arr = SUMMARIES[proj] || SUMMARIES.EAA;
  return arr[Math.floor(Math.random()*arr.length)] + (Math.random()>.6 ? " v"+(Math.ceil(Math.random()*3)) : "");
}

function randomDate(daysAgo, base) {
  const now = base || new Date();
  const d = new Date(now);
  d.setDate(d.getDate() - Math.floor(Math.random() * Math.abs(daysAgo)) * (daysAgo > 0 ? 1 : -1));
  return d.toISOString().slice(0, 10);
}

function randomSubset(arr, max) {
  return arr.filter(() => Math.random() > 0.7).slice(0, max);
}

// ── Build filter options ──────────────────────────────────────────────────────
function buildFilterOptions() {
  const projects   = [...new Set(allIssues.map(i => i.project))].sort();
  const assignees  = [...new Set(allIssues.map(i => i.assignee))].sort();
  const statuses   = [...new Set(allIssues.map(i => i.statusDisplay))].sort();
  const types      = [...new Set(allIssues.map(i => i.typeDisplay))].sort();
  const priorities = [...new Set(allIssues.map(i => i.priorityDisplay))].sort();
  const sprints    = [...new Set(allIssues.map(i => i.sprint).filter(Boolean))].sort();

  buildMultiSelect("filterProject",  projects);
  buildMultiSelect("filterStatus",   statuses);
  buildMultiSelect("filterType",     types);
  buildMultiSelect("filterPriority", priorities);
  buildSelectOptions("filterAssignee", assignees, "All Assignees");
  buildSelectOptions("filterSprint",   sprints,   "All Sprints");
}

function buildMultiSelect(containerId, items) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = items.map(item =>
    `<span class="chip" data-value="${escHtml(item)}" onclick="toggleChip(this)">${escHtml(item)}</span>`
  ).join("");
}

function toggleChip(el) {
  el.classList.toggle("active");
  applyFilters();
}

function getActiveChips(containerId) {
  return [...document.querySelectorAll(`#${containerId} .chip.active`)].map(c => c.dataset.value);
}

function buildSelectOptions(id, items, placeholder) {
  const el = document.getElementById(id);
  if (!el) return;
  const cur = el.value;
  el.innerHTML = `<option value="">${placeholder}</option>` +
    items.map(i => `<option value="${escHtml(i)}">${escHtml(i)}</option>`).join("");
  if (items.includes(cur)) el.value = cur;
}

// ── Apply filters ─────────────────────────────────────────────────────────────
function applyFilters() {
  const projects   = getActiveChips("filterProject");
  const statuses   = getActiveChips("filterStatus");
  const types      = getActiveChips("filterType");
  const priorities = getActiveChips("filterPriority");
  const assignee   = document.getElementById("filterAssignee")?.value || "";
  const sprint     = document.getElementById("filterSprint")?.value   || "";
  const dateFrom   = document.getElementById("filterDateFrom")?.value || "";
  const dateTo     = document.getElementById("filterDateTo")?.value   || "";
  const search     = (document.getElementById("filterSearch")?.value || "").toLowerCase();

  filtered = allIssues.filter(issue => {
    if (projects.length   && !projects.includes(issue.project))         return false;
    if (statuses.length   && !statuses.includes(issue.statusDisplay))   return false;
    if (types.length      && !types.includes(issue.typeDisplay))        return false;
    if (priorities.length && !priorities.includes(issue.priorityDisplay)) return false;
    if (assignee && issue.assignee !== assignee)                         return false;
    if (sprint   && issue.sprint   !== sprint)                           return false;
    if (dateFrom && issue.updated < dateFrom)                            return false;
    if (dateTo   && issue.updated > dateTo)                              return false;
    if (search) {
      const hay = `${issue.key} ${issue.summary} ${issue.labels.join(" ")}`.toLowerCase();
      if (!hay.includes(search)) return false;
    }
    return true;
  });

  currentPage = 1;
  renderKPIs(filtered);
  renderCharts(filtered);
  renderTable();
}

function clearFilters() {
  document.querySelectorAll(".chip.active").forEach(c => c.classList.remove("active"));
  ["filterAssignee","filterSprint"].forEach(id => {
    const el = document.getElementById(id); if (el) el.value = "";
  });
  ["filterSearch"].forEach(id => {
    const el = document.getElementById(id); if (el) el.value = "";
  });
  initDateDefaults();
  applyFilters();
}

// ── KPI Strip ─────────────────────────────────────────────────────────────────
function renderKPIs(issues) {
  const total    = issues.length;
  const done     = issues.filter(i => i.statusCategory === "done").length;
  const inProg   = issues.filter(i => i.statusCategory === "indeterminate").length;
  const todo     = issues.filter(i => i.statusCategory === "new" && i.status !== "blocked").length;
  const blocked  = issues.filter(i => i.status === "blocked").length;
  const overdue  = issues.filter(i => i.isOverdue).length;
  const pct      = total > 0 ? Math.round((done / total) * 100) : 0;

  setKPI("kpiTotal",      total);
  setKPI("kpiDone",       done);
  setKPI("kpiInProgress", inProg);
  setKPI("kpiTodo",       todo);
  setKPI("kpiBlocked",    blocked);
  setKPI("kpiOverdue",    overdue);
  setKPI("kpiVelocity",   pct + "%");
}

function setKPI(id, val) {
  const el = document.getElementById(id);
  if (el) el.querySelector(".kpi-val").textContent = val;
}

// ── Charts ────────────────────────────────────────────────────────────────────
const CHART_COLORS = [
  "#58a6ff","#3fb950","#d29922","#f85149","#bc8cff",
  "#e3b341","#79c0ff","#56d364","#ffa657","#ff7b72",
  "#d2a8ff","#ffd978"
];

function renderCharts(issues) {
  renderDoughnut("chartStatus",   groupBy(issues, "statusDisplay"));
  renderDoughnut("chartType",     groupBy(issues, "typeDisplay"));
  renderBar("chartAssignee",      groupBy(issues, "assignee"));
  renderDoughnut("chartPriority", groupBy(issues, "priorityDisplay"));
  renderTimeline("chartTimeline", issues);
}

function groupBy(issues, key) {
  const map = {};
  for (const i of issues) {
    const val = i[key] || "Unknown";
    map[val] = (map[val] || 0) + 1;
  }
  // Sort by count desc
  return Object.fromEntries(Object.entries(map).sort((a,b) => b[1]-a[1]));
}

function renderDoughnut(canvasId, data) {
  const ctx = document.getElementById(canvasId)?.getContext("2d");
  if (!ctx) return;
  const labels = Object.keys(data);
  const values = Object.values(data);
  if (charts[canvasId]) {
    // Update in place — avoids destroy/recreate flicker
    charts[canvasId].data.labels = labels;
    charts[canvasId].data.datasets[0].data = values;
    charts[canvasId].update("none");
    return;
  }
  charts[canvasId] = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{ data: values, backgroundColor: CHART_COLORS, borderWidth: 2, borderColor: "#1c2128" }]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: {
        legend: { position:"right", labels:{ color:"#8b949e", font:{size:11}, boxWidth:12 } },
        tooltip: { callbacks: { label: c => ` ${c.label}: ${c.raw}` } }
      }
    }
  });
}

function renderBar(canvasId, data) {
  const ctx = document.getElementById(canvasId)?.getContext("2d");
  if (!ctx) return;
  const top12   = Object.fromEntries(Object.entries(data).slice(0, 12));
  const labels  = Object.keys(top12);
  const values  = Object.values(top12);
  if (charts[canvasId]) {
    charts[canvasId].data.labels = labels;
    charts[canvasId].data.datasets[0].data = values;
    charts[canvasId].update("none");
    return;
  }
  charts[canvasId] = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: CHART_COLORS,
        borderRadius: 4, borderWidth: 0
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: true, indexAxis: "y",
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: "#30363d" }, ticks: { color: "#8b949e" } },
        y: { grid: { display: false }, ticks: { color: "#8b949e", font: { size: 11 } } }
      }
    }
  });
}

function renderTimeline(canvasId, issues) {
  const ctx = document.getElementById(canvasId)?.getContext("2d");
  if (!ctx) return;
  if (charts[canvasId]) charts[canvasId].destroy();
  if (!issues.length) { charts[canvasId] = null; return; }

  // Build weekly buckets over last 12 weeks
  const weeks = {};
  const now = new Date();
  for (let w = 11; w >= 0; w--) {
    const d = new Date(now);
    d.setDate(d.getDate() - w * 7);
    weeks[isoWeek(d)] = { created: 0, resolved: 0 };
  }
  const weekKeys = Object.keys(weeks).sort();
  const oldest = weekKeys[0];

  for (const iss of issues) {
    if (iss.created >= oldest) {
      const wk = isoWeek(new Date(iss.created));
      if (weeks[wk]) weeks[wk].created++;
    }
    if (iss.resolved >= oldest) {
      const wk = isoWeek(new Date(iss.resolved));
      if (weeks[wk]) weeks[wk].resolved++;
    }
  }

  charts[canvasId] = new Chart(ctx, {
    type: "line",
    data: {
      labels: weekKeys,
      datasets: [
        {
          label: "Created",
          data: weekKeys.map(w => weeks[w].created),
          borderColor: "#58a6ff", backgroundColor: "rgba(88,166,255,.15)",
          tension: 0.3, fill: true, pointRadius: 3
        },
        {
          label: "Resolved",
          data: weekKeys.map(w => weeks[w].resolved),
          borderColor: "#3fb950", backgroundColor: "rgba(63,185,80,.1)",
          tension: 0.3, fill: true, pointRadius: 3
        }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend: { labels: { color: "#8b949e" } } },
      scales: {
        x: { grid: { color: "#30363d" }, ticks: { color: "#8b949e" } },
        y: { grid: { color: "#30363d" }, ticks: { color: "#8b949e" }, beginAtZero: true }
      }
    }
  });
}

function isoWeek(d) {
  const dt = new Date(d);
  dt.setHours(0, 0, 0, 0);
  dt.setDate(dt.getDate() + 3 - (dt.getDay() + 6) % 7);
  const week1 = new Date(dt.getFullYear(), 0, 4);
  const wk = 1 + Math.round(((dt - week1) / 86400000 - 3 + (week1.getDay() + 6) % 7) / 7);
  return `${dt.getFullYear()}-W${String(wk).padStart(2,"0")}`;
}

// ── Sort ──────────────────────────────────────────────────────────────────────
function sortBy(col) {
  if (sortCol === col) {
    sortDir = sortDir === "asc" ? "desc" : "asc";
  } else {
    sortCol = col; sortDir = "asc";
  }
  renderTable();
}

function sortedIssues(issues) {
  return [...issues].sort((a, b) => {
    let va = a[sortCol] ?? ""; let vb = b[sortCol] ?? "";
    if (va < vb) return sortDir === "asc" ? -1 : 1;
    if (va > vb) return sortDir === "asc" ? 1 : -1;
    return 0;
  });
}

// ── Table render ──────────────────────────────────────────────────────────────
function renderTable() {
  const groupByVal = document.getElementById("groupBy")?.value || "";
  const pageSize   = parseInt(document.getElementById("pageSize")?.value || String(DEFAULT_PAGE_SIZE)) || filtered.length;
  const sorted     = sortedIssues(filtered);
  const totalRows  = sorted.length;
  const totalPages = pageSize > 0 ? Math.ceil(totalRows / pageSize) : 1;

  currentPage = Math.min(currentPage, Math.max(1, totalPages));
  const start = (currentPage - 1) * pageSize;
  const page  = pageSize > 0 ? sorted.slice(start, start + pageSize) : sorted;

  document.getElementById("tableCount").textContent = `${totalRows} issues`;

  const tbody = document.getElementById("issueTableBody");
  if (!page.length) {
    tbody.innerHTML = `<tr><td colspan="11" class="table-empty">No issues match the current filters.</td></tr>`;
    document.getElementById("pagination").innerHTML = "";
    return;
  }

  let html = "";
  if (groupByVal) {
    const groups = {};
    for (const iss of page) {
      const k = iss[groupByVal === "type" ? "typeDisplay" : groupByVal] || "—";
      (groups[k] = groups[k] || []).push(iss);
    }
    for (const [grpName, grpIssues] of Object.entries(groups)) {
      html += `<tr class="group-header"><td colspan="11">${escHtml(grpName)} (${grpIssues.length})</td></tr>`;
      html += grpIssues.map(renderRow).join("");
    }
  } else {
    html = page.map(renderRow).join("");
  }

  tbody.innerHTML = html;
  renderPagination(totalPages);
}

function renderRow(iss) {
  const today = new Date().toISOString().slice(0, 10);
  const overdue = iss.duedate && iss.resolved === "" && iss.duedate < today;
  return `<tr${overdue ? ' style="background:rgba(248,81,73,.05)"' : ""}>
    <td><a class="issue-key" href="${escHtml(iss.url)}" target="_blank">${escHtml(iss.key)}</a></td>
    <td style="max-width:340px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${escHtml(iss.summary)}">${escHtml(iss.summary)}</td>
    <td>${typeIcon(iss.typeDisplay)}</td>
    <td>${statusPill(iss)}</td>
    <td>${priorityIcon(iss.priorityDisplay)}</td>
    <td style="white-space:nowrap">${escHtml(iss.assignee)}</td>
    <td style="white-space:nowrap;font-size:11px;color:var(--text2)">${escHtml(iss.sprint)}</td>
    <td style="white-space:nowrap;font-size:11px;color:var(--text2)">${iss.created}</td>
    <td style="white-space:nowrap;font-size:11px;color:var(--text2)">${iss.updated}</td>
    <td style="white-space:nowrap;font-size:11px;color:${overdue?"var(--red)":"var(--text2)"}">${iss.duedate || "—"}</td>
    <td>${iss.labels.map(l=>`<span class="label-chip">${escHtml(l)}</span>`).join("")}</td>
  </tr>`;
}

function typeIcon(type) {
  const t = (type||"").toLowerCase();
  const icon = TYPE_ICON[t] || TYPE_ICON.default;
  return `<span title="${escHtml(type)}">${icon} <span style="font-size:11px;color:var(--text2)">${escHtml(type)}</span></span>`;
}

function statusPill(iss) {
  const cat = iss.statusCategory;
  let cls = "pill-default";
  if (cat === "done") cls = "pill-done";
  else if (cat === "indeterminate") {
    cls = iss.status === "inreview" || iss.status === "review" ? "pill-review" : "pill-inprog";
  } else if (iss.status === "blocked") cls = "pill-blocked";
  else if (cat === "new") cls = "pill-todo";
  return `<span class="pill ${cls}">${escHtml(iss.statusDisplay)}</span>`;
}

function priorityIcon(priority) {
  const p = (priority||"").toLowerCase();
  const icon = PRIORITY_ICON[p] || PRIORITY_ICON.default;
  let cls = "pri-medium";
  if (["blocker","critical","highest"].includes(p)) cls = "pri-critical";
  else if (p === "high")   cls = "pri-high";
  else if (p === "low")    cls = "pri-low";
  else if (p === "lowest") cls = "pri-lowest";
  return `<span class="pri ${cls}">${icon} ${escHtml(priority)}</span>`;
}

function renderPagination(totalPages) {
  const el = document.getElementById("pagination");
  if (totalPages <= 1) { el.innerHTML = ""; return; }

  let html = "";
  const range = pagRange(currentPage, totalPages);
  for (const p of range) {
    if (p === "…") {
      html += `<span class="page-info">…</span>`;
    } else {
      html += `<button class="page-btn${p===currentPage?" active":""}" onclick="goPage(${p})">${p}</button>`;
    }
  }
  el.innerHTML = html +
    `<span class="page-info">Page ${currentPage} of ${totalPages} · ${filtered.length} issues</span>`;
}

function pagRange(cur, total) {
  if (total <= 7) return Array.from({length:total},(_,i)=>i+1);
  const pages = [1];
  if (cur > 3) pages.push("…");
  for (let p = Math.max(2, cur-1); p <= Math.min(total-1, cur+1); p++) pages.push(p);
  if (cur < total - 2) pages.push("…");
  pages.push(total);
  return pages;
}

function goPage(p) {
  currentPage = p;
  renderTable();
  document.querySelector(".table-section")?.scrollIntoView({behavior:"smooth"});
}

// ── AI Summary (Claude via Lilly LLM Gateway) ─────────────────────────────────
async function generateSummary() {
  if (!filtered.length) {
    document.getElementById("summaryBody").innerHTML =
      `<p class="summary-placeholder">No issues to summarize. Load data first.</p>`;
    return;
  }

  const apiUrl   = (localStorage.getItem(LS.CLAUDE_URL) || "").replace(/\/$/, "");
  const apiKey   = localStorage.getItem(LS.CLAUDE_KEY) || "";
  const model    = localStorage.getItem(LS.CLAUDE_MODEL) || "claude-3.7-sonnet-20250219-v1";

  const body = document.getElementById("summaryBody");
  body.innerHTML = `<p class="summary-placeholder">⏳ Generating summary…</p>`;

  // Build a rich context digest
  const byStatus   = groupBy(filtered, "statusDisplay");
  const byType     = groupBy(filtered, "typeDisplay");
  const byAssignee = groupBy(filtered, "assignee");
  const byPriority = groupBy(filtered, "priorityDisplay");
  const byProject  = groupBy(filtered, "project");
  const overdue    = filtered.filter(i => i.isOverdue);
  const blocked    = filtered.filter(i => i.status === "blocked");
  const highPri    = filtered.filter(i => ["blocker","critical","high"].includes(i.priority));
  const done       = filtered.filter(i => i.statusCategory === "done");
  const inProg     = filtered.filter(i => i.statusCategory === "indeterminate");

  const context = `
You are an expert Scrum Master summarizing a Jira sprint/project status update for executives.

DASHBOARD SNAPSHOT (${new Date().toLocaleDateString()}):
Total issues in view: ${filtered.length}
Projects: ${Object.entries(byProject).map(([k,v])=>`${k}(${v})`).join(", ")}

STATUS BREAKDOWN:
${Object.entries(byStatus).map(([k,v])=>`- ${k}: ${v}`).join("\n")}

ISSUE TYPES:
${Object.entries(byType).map(([k,v])=>`- ${k}: ${v}`).join("\n")}

BY ASSIGNEE (top 8):
${Object.entries(byAssignee).slice(0,8).map(([k,v])=>`- ${k}: ${v}`).join("\n")}

PRIORITY BREAKDOWN:
${Object.entries(byPriority).map(([k,v])=>`- ${k}: ${v}`).join("\n")}

OVERDUE ISSUES (${overdue.length}):
${overdue.slice(0,5).map(i=>`- ${i.key} [${i.assignee}] Due:${i.duedate} — ${i.summary.slice(0,80)}`).join("\n") || "None"}

BLOCKED ISSUES (${blocked.length}):
${blocked.slice(0,5).map(i=>`- ${i.key} [${i.assignee}] — ${i.summary.slice(0,80)}`).join("\n") || "None"}

HIGH PRIORITY OPEN (${highPri.filter(i=>i.statusCategory!=="done").length}):
${highPri.filter(i=>i.statusCategory!=="done").slice(0,5).map(i=>`- ${i.key} [${i.priority}/${i.statusDisplay}] ${i.summary.slice(0,80)}`).join("\n") || "None"}

IN PROGRESS (${inProg.length}):
${inProg.slice(0,5).map(i=>`- ${i.key} [${i.assignee}] ${i.summary.slice(0,80)}`).join("\n") || "None"}

Completion rate: ${filtered.length > 0 ? Math.round((done.length/filtered.length)*100) : 0}%
`.trim();

  const prompt = `${context}

Please produce a concise executive status update covering:
1. **Overall Health** — Is the team on track? Key metrics.
2. **Progress This Period** — What's been completed, momentum.
3. **Risks & Blockers** — Overdue items, blocked issues, capacity concerns.
4. **Workload Distribution** — Any imbalances across assignees.
5. **Recommended Actions** — 2-3 specific, actionable recommendations for leadership.

Keep it crisp and executive-ready. Use bullet points under each heading.`;

  try {
    let summaryText;

    if (apiUrl && apiKey) {
      // Route through server-side proxy — auth handled by llm_gateway.py (AWS Secrets)
      const proxyUrl = apiUrl.startsWith("/api/") ? apiUrl : "/api/llm-proxy";
      const resp = await fetch(proxyUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: model,
          max_tokens: 1024,
          messages: [{ role: "user", content: prompt }]
        })
      });

      if (!resp.ok) {
        const errText = await resp.text();
        throw new Error(`Claude API error ${resp.status}: ${errText.slice(0, 200)}`);
      }

      const data = await resp.json();
      summaryText = data.content?.[0]?.text || data.completion || "No response";
    } else {
      // Fallback: rule-based summary
      summaryText = buildRuleBasedSummary(filtered, byStatus, byAssignee, byPriority, overdue, blocked, done, inProg);
    }

    body.innerHTML = `<div class="summary-content">${markdownToHtml(summaryText)}</div>`;
  } catch (err) {
    console.error("Summary error:", err);
    // Always fall back gracefully
    const fallback = buildRuleBasedSummary(filtered, byStatus, byAssignee, byPriority, overdue, blocked, done, inProg);
    body.innerHTML = `
      <div class="summary-content">${markdownToHtml(fallback)}</div>
      <p style="color:var(--red);font-size:12px;margin-top:8px">⚠️ Claude API unavailable (${escHtml(err.message)}). Showing rule-based summary. Configure API key in Settings.</p>`;
  }
}

function buildRuleBasedSummary(issues, byStatus, byAssignee, byPriority, overdue, blocked, done, inProg) {
  const total = issues.length;
  const pct   = total > 0 ? Math.round((done.length/total)*100) : 0;
  const topAssignee = Object.entries(byAssignee).sort((a,b)=>b[1]-a[1])[0];

  return `### Overall Health
- **${pct}% completion rate** across ${total} issues in the current view.
- ${done.length} issues done · ${inProg.length} in progress · ${blocked.length} blocked · ${overdue.length} overdue.

### Progress This Period
- Status distribution: ${Object.entries(byStatus).map(([k,v])=>`${k}: ${v}`).join(" · ")}
- ${inProg.length} issues are actively being worked on.

### Risks & Blockers
${overdue.length > 0 ? `- ⚠️ **${overdue.length} overdue issues** require immediate attention.` : "- No overdue issues. ✅"}
${blocked.length > 0 ? `- 🔴 **${blocked.length} blocked issues** need impediment resolution.` : "- No blocked issues. ✅"}
${(byPriority["Blocker"]||0)+(byPriority["Critical"]||0) > 0 ? `- 🔴 ${(byPriority["Blocker"]||0)+(byPriority["Critical"]||0)} Blocker/Critical priority items open.` : ""}

### Workload Distribution
- ${Object.keys(byAssignee).length} team members with assigned work.
${topAssignee ? `- Highest load: **${topAssignee[0]}** (${topAssignee[1]} issues).` : ""}

### Recommended Actions
- ${overdue.length > 0 ? `Triage ${overdue.length} overdue issue(s) and re-prioritize or reassign.` : "Maintain current velocity."}
- ${blocked.length > 0 ? `Resolve impediments on ${blocked.length} blocked issue(s) in next standup.` : "Continue sprint execution."}
- Review completion rate trend and adjust sprint capacity if needed.`;
}

// Minimal markdown → HTML for summary display
// Input is HTML-escaped first to prevent XSS from LLM output,
// then safe markdown patterns are applied on the escaped text.
function markdownToHtml(text) {
  return String(text || "")
    .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
    .replace(/\*\*(.+?)\*\*/g,"<strong>$1</strong>")
    .replace(/\*(.+?)\*/g,"<em>$1</em>")
    .replace(/^### (.+)$/gm,"<h3>$1</h3>")
    .replace(/^## (.+)$/gm,"<h3>$1</h3>")
    .replace(/^# (.+)$/gm,"<h3>$1</h3>")
    .replace(/^[-*] (.+)$/gm,"<li>$1</li>")
    .replace(/(<li>.*<\/li>\n?)+/g, m => `<ul>${m}</ul>`)
    .replace(/\n\n+/g,"<br/><br/>")
    .replace(/\n/g,"<br/>");
}

// ── Loading helpers ───────────────────────────────────────────────────────────
function showLoading(msg) {
  document.getElementById("loadingOverlay").classList.add("active");
  document.getElementById("loadingMsg").textContent = msg || "Loading…";
}
function hideLoading() {
  document.getElementById("loadingOverlay").classList.remove("active");
}
function setLoadingMsg(msg) {
  document.getElementById("loadingMsg").textContent = msg;
}

function showToast(msg) {
  console.warn(msg);
}

// ── Utilities ─────────────────────────────────────────────────────────────────
function escHtml(s) {
  return String(s || "")
    .replace(/&/g,  "&amp;")
    .replace(/</g,  "&lt;")
    .replace(/>/g,  "&gt;")
    .replace(/"/g,  "&quot;")
    .replace(/'/g,  "&#39;")
    .replace(/`/g,  "&#96;")
    .replace(/\//g, "&#x2F;");
}
