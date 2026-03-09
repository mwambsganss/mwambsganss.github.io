import { useState, useMemo, useCallback, useEffect } from "react";

// ─────────────────────────────────────────────────────────────────
// Lilly Brand Colors
// Primary: #C8102E (Lilly Red), White, Dark Gray #1A1A1A, Mid Gray #6B6B6B, Light Gray #F5F5F5
// ─────────────────────────────────────────────────────────────────

const DONE_STATUSES = new Set(["Done","Live Service","Hypercare","Cancelled","Retired"]);

const DEFAULT_PROJECT_COLORS = [
  { accent: "#C8102E", light: "#FFF0F2" },
  { accent: "#0057A8", light: "#EBF3FF" },
  { accent: "#00703C", light: "#EDFAF3" },
  { accent: "#6B3FA0", light: "#F3EEFF" },
  { accent: "#E8830C", light: "#FFF4E5" },
  { accent: "#0087C1", light: "#E5F5FF" },
];

const STATUS_COLOR = {
  "Done": "#00703C", "Live Service": "#00703C", "Hypercare": "#00703C",
  "In Development": "#C8102E", "In Progress": "#0057A8", "Dev in Progress": "#0057A8",
  "Testing in Progress": "#6B3FA0", "In Review": "#0057A8", "Approved": "#00703C",
  "Blocked": "#C8102E", "On Hold": "#E8830C",
  "Cancelled": "#6B6B6B", "Retired": "#6B6B6B",
  "Backlog": "#6B6B6B", "To Do": "#6B6B6B",
  "Ready for Development": "#6B3FA0",
  "Automation Opportunity": "#E8830C", "Exploration": "#0087C1",
  "POT/POC": "#C8102E", "Architect Gate": "#6B3FA0",
  "Team & Vendor Formation": "#E8830C", "Capability Evaluation": "#0087C1",
};

const TYPE_ICON = {
  "Story": "📖", "Task": "✅", "Bug": "🐛", "Enhancement": "⚡",
  "Release": "🚀", "Automation Project": "🤖", "Test Automation": "🧪",
  "Epic": "🎯", "Sub-task": "◻", "Consultation": "💬", "Test": "🔬",
  "Test Execution": "▶", "Test Plan": "📋", "Feature": "✨",
  "Initiative": "🌟", "Demand Management": "📊",
};

const PRIORITY_STYLE = {
  "High":    { c: "#C8102E", label: "High" },
  "Highest": { c: "#8B0000", label: "Highest" },
  "Medium":  { c: "#E8830C", label: "Medium" },
  "Low":     { c: "#00703C", label: "Low" },
  "Lowest":  { c: "#6B6B6B", label: "Lowest" },
  "Not Set": { c: "#C0C0C0", label: "—" },
};

// ── Helpers ──
function getUniq(issues, field) {
  return ["All", ...[...new Set(issues.map(i => i[field]))].filter(Boolean).sort()];
}

// ── Parse Jira project URL → { baseUrl, projectKey } ──
function parseJiraUrl(url) {
  try {
    const u = new URL(url.trim());
    const projectMatch = u.pathname.match(/\/(?:jira\/software\/projects|browse)\/([A-Z][A-Z0-9_-]+)/i);
    if (projectMatch) {
      return { baseUrl: `${u.protocol}//${u.hostname}`, projectKey: projectMatch[1].toUpperCase() };
    }
    const segments = u.pathname.split("/").filter(Boolean);
    const key = segments.find(s => /^[A-Z][A-Z0-9_-]{1,20}$/i.test(s));
    if (key) return { baseUrl: `${u.protocol}//${u.hostname}`, projectKey: key.toUpperCase() };
    return null;
  } catch { return null; }
}

// ─────────────────────────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────────────────────────

function StatusPill({ status }) {
  const c = STATUS_COLOR[status] || "#6B6B6B";
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 5,
      background: c + "14", color: c, border: `1px solid ${c}30`,
      padding: "2px 8px", borderRadius: 3, fontSize: 11, fontWeight: 600,
      whiteSpace: "nowrap", fontFamily: "Arial, sans-serif"
    }}>
      <span style={{ width: 6, height: 6, borderRadius: "50%", background: c, flexShrink: 0 }} />
      {status}
    </span>
  );
}

function LabelEl({ children, style = {} }) {
  return (
    <label style={{
      fontSize: 10, fontWeight: 700, color: "#6B6B6B",
      letterSpacing: ".06em", fontFamily: "Arial, sans-serif",
      textTransform: "uppercase", display: "block", marginBottom: 4,
      ...style
    }}>{children}</label>
  );
}

function SelectEl({ label, value, onChange, options }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <LabelEl>{label}</LabelEl>
      <select value={value} onChange={e => onChange(e.target.value)} style={{
        fontFamily: "Arial, sans-serif", fontSize: 12, padding: "6px 10px",
        border: "1px solid #D0D0D0", borderRadius: 3, background: "#fff",
        color: "#1A1A1A", cursor: "pointer", minWidth: 140, outline: "none"
      }}>
        {options.slice(0, 60).map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}

function DateField({ label, value, onChange }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <LabelEl>{label}</LabelEl>
      <input type="date" value={value} onChange={e => onChange(e.target.value)} style={{
        fontFamily: "Arial, sans-serif", fontSize: 12, padding: "6px 10px",
        border: "1px solid #D0D0D0", borderRadius: 3, color: "#1A1A1A",
        background: "#fff", outline: "none"
      }} />
    </div>
  );
}

function StatCard({ value, label, color, sub }) {
  return (
    <div style={{
      background: "#fff", border: "1px solid #E8E8E8", borderTop: `3px solid ${color}`,
      borderRadius: 4, padding: "14px 16px", boxShadow: "0 1px 3px rgba(0,0,0,.05)"
    }}>
      <div style={{ fontSize: 28, fontWeight: 700, color, fontFamily: "Arial Black, Arial, sans-serif", lineHeight: 1 }}>{value.toLocaleString()}</div>
      <div style={{ fontSize: 11, fontWeight: 700, color: "#1A1A1A", marginTop: 4, fontFamily: "Arial, sans-serif" }}>{label}</div>
      {sub && <div style={{ fontSize: 10, color: "#6B6B6B", marginTop: 2, fontFamily: "Arial, sans-serif" }}>{sub}</div>}
    </div>
  );
}

function InputEl({ value, onChange, placeholder, type = "text", style = {} }) {
  return (
    <input
      type={type} value={value}
      onChange={e => onChange(e.target.value)}
      placeholder={placeholder}
      style={{
        fontFamily: "Arial, sans-serif", fontSize: 12, padding: "7px 10px",
        border: "1px solid #D0D0D0", borderRadius: 3, color: "#1A1A1A",
        background: "#fff", outline: "none", width: "100%", ...style
      }}
    />
  );
}

// ─────────────────────────────────────────────────────────────────
// Empty State — shown when no Jira projects are connected
// ─────────────────────────────────────────────────────────────────
function EmptyState({ onOpenSettings }) {
  return (
    <div style={{
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
      minHeight: "60vh", gap: 20, padding: "48px 24px", textAlign: "center"
    }}>
      <div style={{ fontSize: 56 }}>🔗</div>
      <div>
        <div style={{ fontSize: 22, fontWeight: 700, color: "#1A1A1A", fontFamily: "Arial Black, Arial, sans-serif", marginBottom: 8 }}>
          No Jira Projects Connected
        </div>
        <div style={{ fontSize: 14, color: "#6B6B6B", maxWidth: 440, lineHeight: 1.7 }}>
          This dashboard connects directly to your Jira projects in real time.
          Click <strong>⚙️ Settings</strong> to add your project URLs, Jira credentials,
          and LLM Gateway key.
        </div>
      </div>
      <button
        onClick={onOpenSettings}
        style={{
          fontFamily: "Arial Black, Arial, sans-serif", fontSize: 14, fontWeight: 700,
          padding: "12px 28px", border: "none", borderRadius: 4,
          background: "#C8102E", color: "#fff", cursor: "pointer",
          display: "flex", alignItems: "center", gap: 8,
          boxShadow: "0 2px 8px rgba(200,16,46,.35)"
        }}
      >
        ⚙️ Open Settings
      </button>
      <div style={{ fontSize: 12, color: "#C0C0C0" }}>
        Issues are fetched directly from the Jira REST API and never stored externally.
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────
// Settings Modal
// ─────────────────────────────────────────────────────────────────
function SettingsModal({ onClose, onSave, initialSettings, hasData }) {
  const [jiraUrls, setJiraUrls]   = useState(initialSettings.jiraUrls  || "");
  const [jiraToken, setJiraToken] = useState(initialSettings.jiraToken || "");
  const [jiraEmail, setJiraEmail] = useState(initialSettings.jiraEmail || "");
  const [llmUrl,   setLlmUrl]     = useState(initialSettings.llmUrl    || "https://lilly-code-server.api.gateway.llm.lilly.com");
  const [llmKey,   setLlmKey]     = useState(initialSettings.llmKey    || "");
  const [llmModel, setLlmModel]   = useState(initialSettings.llmModel  || "claude-sonnet-4-20250514");
  const [fetchStatus, setFetchStatus] = useState(null);
  const [isFetching, setIsFetching]   = useState(false);

  async function handleFetchProjects() {
    const urls = jiraUrls.split("\n").map(s => s.trim()).filter(Boolean);
    if (!urls.length)   { setFetchStatus({ type: "error", msg: "Enter at least one Jira project URL." }); return; }
    if (!jiraToken)     { setFetchStatus({ type: "error", msg: "Enter your Jira API token." }); return; }
    if (!jiraEmail)     { setFetchStatus({ type: "error", msg: "Enter your Jira account email." }); return; }

    setIsFetching(true);
    setFetchStatus({ type: "info", msg: "Connecting to Jira..." });

    const parsed = urls.map(u => parseJiraUrl(u)).filter(Boolean);
    if (!parsed.length) {
      setFetchStatus({ type: "error", msg: "Could not parse any valid Jira project URLs. Paste the full board or backlog URL." });
      setIsFetching(false);
      return;
    }

    const allIssues = [];
    const errors = [];

    for (const { baseUrl, projectKey } of parsed) {
      const authHeader = "Basic " + btoa(`${jiraEmail}:${jiraToken}`);
      const apiBase    = `${baseUrl}/rest/api/3`;
      let startAt = 0;
      const maxResults = 100;
      let totalFetched = 0;
      let totalAvailable = Infinity;

      setFetchStatus({ type: "info", msg: `Fetching ${projectKey} (${baseUrl})...` });

      try {
        while (totalFetched < totalAvailable && totalFetched < 2000) {
          const jql = encodeURIComponent(`project = ${projectKey} ORDER BY updated DESC`);
          const url = `${apiBase}/search?jql=${jql}&startAt=${startAt}&maxResults=${maxResults}&fields=summary,status,issuetype,priority,assignee,updated,created,duedate,labels`;
          const resp = await fetch(url, {
            headers: { "Authorization": authHeader, "Accept": "application/json" }
          });
          if (!resp.ok) {
            const errText = await resp.text();
            throw new Error(`HTTP ${resp.status}: ${errText.slice(0, 200)}`);
          }
          const data = await resp.json();
          totalAvailable = data.total;
          if (!data.issues?.length) break;

          for (const issue of data.issues) {
            const f = issue.fields;
            allIssues.push({
              key:        issue.key,
              project:    projectKey,
              summary:    f.summary || "",
              status:     f.status?.name || "",
              statusCat:  f.status?.statusCategory?.name || f.status?.name || "",
              issueType:  f.issuetype?.name || "",
              priority:   f.priority?.name || "Not Set",
              assignee:   f.assignee?.displayName || "Unassigned",
              updated:    (f.updated  || "").slice(0, 10),
              created:    (f.created  || "").slice(0, 10),
              dueDate:    (f.duedate  || "").slice(0, 10),
              labels:     (f.labels   || []),
              completed:  DONE_STATUSES.has(f.status?.name || "") ? (f.updated || "").slice(0, 10) : "",
              url:        `${baseUrl}/browse/${issue.key}`
            });
          }

          totalFetched += data.issues.length;
          startAt      += maxResults;
          if (totalFetched >= totalAvailable) break;
        }
      } catch (err) {
        errors.push(`${projectKey}: ${err.message}`);
      }
    }

    setIsFetching(false);

    if (errors.length && !allIssues.length) {
      setFetchStatus({ type: "error", msg: `Failed to fetch: ${errors.join("; ")}` });
    } else {
      const msg = `✓ Loaded ${allIssues.length.toLocaleString()} issues from ${parsed.length - errors.length} project(s).${errors.length ? ` Errors: ${errors.join("; ")}` : ""}`;
      setFetchStatus({ type: "success", msg });
      onSave({ jiraUrls, jiraToken, jiraEmail, llmUrl, llmKey, llmModel, liveIssues: allIssues });
    }
  }

  function handleSaveSettingsOnly() {
    onSave({ jiraUrls, jiraToken, jiraEmail, llmUrl, llmKey, llmModel, liveIssues: null });
    onClose();
  }

  return (
    <div style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,.55)", zIndex: 1000,
      display: "flex", alignItems: "center", justifyContent: "center"
    }} onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
      <div style={{
        background: "#fff", borderRadius: 6, width: "min(700px, 96vw)", maxHeight: "92vh",
        overflow: "auto", boxShadow: "0 8px 40px rgba(0,0,0,.25)"
      }}>

        {/* Modal header */}
        <div style={{ background: "#C8102E", padding: "16px 22px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <div style={{ fontSize: 15, fontWeight: 700, color: "#fff", fontFamily: "Arial Black, Arial, sans-serif" }}>⚙️ Dashboard Settings</div>
            <div style={{ fontSize: 11, color: "rgba(255,255,255,.8)", marginTop: 2 }}>Connect Jira projects and configure the AI provider</div>
          </div>
          <button onClick={onClose} style={{ background: "rgba(255,255,255,.2)", border: "none", color: "#fff", borderRadius: 3, padding: "4px 12px", cursor: "pointer", fontSize: 16 }}>✕</button>
        </div>

        <div style={{ padding: 26, display: "flex", flexDirection: "column", gap: 26 }}>

          {/* ── JIRA CONNECTION ── */}
          <section>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#1A1A1A", marginBottom: 14, paddingBottom: 8, borderBottom: "2px solid #C8102E", display: "flex", alignItems: "center", gap: 8 }}>
              🔗 Jira Project Connections
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <div>
                <LabelEl>Jira Project URLs — one per line</LabelEl>
                <textarea
                  value={jiraUrls}
                  onChange={e => setJiraUrls(e.target.value)}
                  placeholder={"https://lilly-jira.atlassian.net/jira/software/projects/EAA/boards\nhttps://lilly-jira.atlassian.net/jira/software/projects/ASO/boards\nhttps://lilly-jira.atlassian.net/jira/software/projects/KILO/boards"}
                  rows={4}
                  style={{
                    width: "100%", fontFamily: "monospace", fontSize: 12, padding: "8px 10px",
                    border: "1px solid #D0D0D0", borderRadius: 3, color: "#1A1A1A",
                    resize: "vertical", outline: "none", lineHeight: 1.6
                  }}
                />
                <div style={{ fontSize: 11, color: "#6B6B6B", marginTop: 4, lineHeight: 1.5 }}>
                  Paste the URL of any Jira board, backlog, or browse page — the project key is extracted automatically.
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
                <div>
                  <LabelEl>Jira Account Email</LabelEl>
                  <InputEl value={jiraEmail} onChange={setJiraEmail} placeholder="your.name@lilly.com" type="email" />
                </div>
                <div>
                  <LabelEl>Jira API Token</LabelEl>
                  <InputEl value={jiraToken} onChange={setJiraToken} placeholder="Atlassian API token" type="password" />
                  <div style={{ fontSize: 10, color: "#6B6B6B", marginTop: 4 }}>
                    Generate at:{" "}
                    <a href="https://id.atlassian.com/manage-profile/security/api-tokens" target="_blank" rel="noopener noreferrer" style={{ color: "#0057A8" }}>
                      id.atlassian.com → API Tokens
                    </a>
                  </div>
                </div>
              </div>

              {fetchStatus && (
                <div style={{
                  padding: "10px 14px", borderRadius: 3, fontSize: 12, lineHeight: 1.6,
                  background: fetchStatus.type === "error" ? "#FFF0F2" : fetchStatus.type === "success" ? "#EDFAF3" : "#EBF3FF",
                  color:      fetchStatus.type === "error" ? "#C8102E" : fetchStatus.type === "success" ? "#00703C" : "#0057A8",
                  border:     `1px solid ${fetchStatus.type === "error" ? "#C8102E30" : fetchStatus.type === "success" ? "#00703C30" : "#0057A830"}`,
                }}>
                  {fetchStatus.msg}
                </div>
              )}

              <button
                onClick={handleFetchProjects}
                disabled={isFetching}
                style={{
                  fontFamily: "Arial, sans-serif", fontSize: 12, fontWeight: 700,
                  padding: "10px 20px", border: "none", borderRadius: 3,
                  background: isFetching ? "#E8E8E8" : "#0057A8",
                  color: isFetching ? "#6B6B6B" : "#fff",
                  cursor: isFetching ? "not-allowed" : "pointer",
                  alignSelf: "flex-start", display: "flex", alignItems: "center", gap: 8
                }}
              >
                {isFetching
                  ? <>{[0,1,2].map(i => <span key={i} style={{ width: 6, height: 6, borderRadius: "50%", background: "#6B6B6B", display: "inline-block", animation: `spin 1.2s ${i*.2}s infinite` }} />)}<span>Fetching...</span></>
                  : "🔄 Connect & Fetch Issues"
                }
              </button>
            </div>
          </section>

          {/* ── LLM GATEWAY ── */}
          <section>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#1A1A1A", marginBottom: 14, paddingBottom: 8, borderBottom: "2px solid #C8102E", display: "flex", alignItems: "center", gap: 8 }}>
              🤖 LLM Gateway — AI Executive Summary
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <div>
                <LabelEl>LLM Gateway Base URL</LabelEl>
                <InputEl value={llmUrl} onChange={setLlmUrl} placeholder="https://lilly-code-server.api.gateway.llm.lilly.com" />
                <div style={{ fontSize: 10, color: "#6B6B6B", marginTop: 3 }}>Your Lilly LLM Gateway endpoint (no trailing slash)</div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
                <div>
                  <LabelEl>API Key / Bearer Token</LabelEl>
                  <InputEl value={llmKey} onChange={setLlmKey} placeholder="sk-..." type="password" />
                  <div style={{ fontSize: 10, color: "#6B6B6B", marginTop: 3 }}>Obtained from Lilly Code or the LLM Gateway team</div>
                </div>
                <div>
                  <LabelEl>Model Name</LabelEl>
                  <InputEl value={llmModel} onChange={setLlmModel} placeholder="claude-sonnet-4-20250514" />
                  <div style={{ fontSize: 10, color: "#6B6B6B", marginTop: 3 }}>e.g. claude-sonnet-4-20250514, gpt-4o</div>
                </div>
              </div>
            </div>
          </section>

          {/* Security note */}
          <div style={{ fontSize: 11, color: "#6B6B6B", background: "#FAFAFA", border: "1px solid #E8E8E8", borderRadius: 3, padding: "10px 14px", lineHeight: 1.6 }}>
            🔒 <strong>Security note:</strong> All credentials are held only in browser memory for this session. They are never sent anywhere except directly to the Jira and LLM Gateway APIs you configure above.
          </div>

          {/* Actions */}
          <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", paddingTop: 6, borderTop: "1px solid #E8E8E8" }}>
            {hasData && (
              <button onClick={onClose} style={{
                fontFamily: "Arial, sans-serif", fontSize: 12, fontWeight: 600, padding: "8px 20px",
                border: "1px solid #D0D0D0", borderRadius: 3, background: "#fff", color: "#1A1A1A", cursor: "pointer"
              }}>Cancel</button>
            )}
            <button onClick={handleSaveSettingsOnly} style={{
              fontFamily: "Arial, sans-serif", fontSize: 12, fontWeight: 700, padding: "8px 20px",
              border: "none", borderRadius: 3, background: "#6B6B6B", color: "#fff", cursor: "pointer"
            }}>💾 Save Credentials Only</button>
            <button onClick={handleFetchProjects} disabled={isFetching} style={{
              fontFamily: "Arial, sans-serif", fontSize: 12, fontWeight: 700, padding: "8px 20px",
              border: "none", borderRadius: 3,
              background: isFetching ? "#E8E8E8" : "#C8102E",
              color: isFetching ? "#6B6B6B" : "#fff",
              cursor: isFetching ? "not-allowed" : "pointer"
            }}>
              {isFetching ? "Fetching..." : "🔄 Save & Load Issues"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────
// Main Dashboard
// ─────────────────────────────────────────────────────────────────
export default function Dashboard() {
  // ── Data ──
  const [issues, setIssues]     = useState([]);   // populated only via live Jira fetch
  const [projects, setProjects] = useState({});   // derived from live issues

  const hasData = issues.length > 0;

  // ── Settings ──
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState({
    jiraUrls:  "",
    jiraToken: "",
    jiraEmail: "",
    llmUrl:    "https://lilly-code-server.api.gateway.llm.lilly.com",
    llmKey:    "",
    llmModel:  "claude-sonnet-4-20250514",
  });

  // ── Filters ──
  const [filters, setFilters] = useState({
    project: "All", status: "All", issueType: "All",
    priority: "All", assignee: "All", search: "",
    createdFrom: "", createdTo: "",
    completedFrom: "", completedTo: "",
    updatedFrom: "", updatedTo: "",
  });
  const [sortCol, setSortCol]   = useState("updated");
  const [sortDir, setSortDir]   = useState("desc");
  const [view, setView]         = useState("table");
  const [page, setPage]         = useState(0);
  const [expandedKey, setExpandedKey] = useState(null);
  const [showDateFilters, setShowDateFilters] = useState(false);

  // ── AI ──
  const [aiSummary, setAiSummary]             = useState("");
  const [aiLoading, setAiLoading]             = useState(false);
  const [summaryCollapsed, setSummaryCollapsed] = useState(false);

  // ── Email ──
  const [emailTo, setEmailTo]           = useState("");
  const [emailCc, setEmailCc]           = useState("");
  const [emailStatus, setEmailStatus]   = useState(null);
  const [showEmailPanel, setShowEmailPanel] = useState(false);

  const PAGE_SIZE = 50;

  const setFilter = (k, v) => setFilters(f => ({ ...f, [k]: v }));
  const clearFilters = () => setFilters({
    project: "All", status: "All", issueType: "All", priority: "All",
    assignee: "All", search: "",
    createdFrom: "", createdTo: "", completedFrom: "", completedTo: "",
    updatedFrom: "", updatedTo: ""
  });

  const hasDateFilters = !!(filters.createdFrom || filters.createdTo || filters.completedFrom || filters.completedTo || filters.updatedFrom || filters.updatedTo);
  const hasAnyFilter   = Object.entries(filters).some(([, v]) => v && v !== "All" && v !== "");

  // Derived filter options
  const ALL_STATUSES   = useMemo(() => getUniq(issues, "status"),    [issues]);
  const ALL_PROJECTS   = useMemo(() => getUniq(issues, "project"),   [issues]);
  const ALL_TYPES      = useMemo(() => getUniq(issues, "issueType"), [issues]);
  const ALL_PRIORITIES = useMemo(() => getUniq(issues, "priority"),  [issues]);
  const ALL_ASSIGNEES  = useMemo(() => getUniq(issues, "assignee"),  [issues]);

  // Filtered + sorted issues
  const filtered = useMemo(() => {
    let r = issues;
    if (filters.project   !== "All") r = r.filter(i => i.project   === filters.project);
    if (filters.status    !== "All") r = r.filter(i => i.status    === filters.status);
    if (filters.issueType !== "All") r = r.filter(i => i.issueType === filters.issueType);
    if (filters.priority  !== "All") r = r.filter(i => i.priority  === filters.priority);
    if (filters.assignee  !== "All") r = r.filter(i => i.assignee  === filters.assignee);
    if (filters.search) {
      const q = filters.search.toLowerCase();
      r = r.filter(i => i.summary.toLowerCase().includes(q) || i.key.toLowerCase().includes(q) || i.assignee.toLowerCase().includes(q));
    }
    if (filters.createdFrom)   r = r.filter(i => i.created >= filters.createdFrom);
    if (filters.createdTo)     r = r.filter(i => i.created <= filters.createdTo);
    if (filters.completedFrom) r = r.filter(i => i.completed && i.completed >= filters.completedFrom);
    if (filters.completedTo)   r = r.filter(i => i.completed && i.completed <= filters.completedTo);
    if (filters.updatedFrom)   r = r.filter(i => i.updated >= filters.updatedFrom);
    if (filters.updatedTo)     r = r.filter(i => i.updated <= filters.updatedTo);
    return [...r].sort((a, b) => {
      const av = a[sortCol] || "", bv = b[sortCol] || "";
      return sortDir === "asc" ? av.localeCompare(bv) : bv.localeCompare(av);
    });
  }, [issues, filters, sortCol, sortDir]);

  useEffect(() => setPage(0), [filters, sortCol, sortDir, issues]);
  useEffect(() => { setAiSummary(""); }, [filters]);

  const paged      = useMemo(() => filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE), [filtered, page]);
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);

  const stats = useMemo(() => {
    const byStatus = {}, byProject = {}, byType = {};
    let high = 0, overdue = 0;
    const today = new Date().toISOString().slice(0, 10);
    filtered.forEach(i => {
      byStatus[i.status]     = (byStatus[i.status]     || 0) + 1;
      byProject[i.project]   = (byProject[i.project]   || 0) + 1;
      byType[i.issueType]    = (byType[i.issueType]    || 0) + 1;
      if (i.priority === "High" || i.priority === "Highest") high++;
      if (i.dueDate && i.dueDate < today && i.statusCat !== "Done") overdue++;
    });
    const inProgress = (byStatus["In Progress"] || 0) + (byStatus["In Development"] || 0) + (byStatus["Dev in Progress"] || 0);
    const done       = (byStatus["Done"] || 0) + (byStatus["Live Service"] || 0) + (byStatus["Hypercare"] || 0);
    const blocked    = (byStatus["Blocked"] || 0) + (byStatus["On Hold"] || 0);
    return { total: filtered.length, inProgress, done, blocked, high, overdue, byStatus, byProject, byType };
  }, [filtered]);

  const kanbanGroups = useMemo(() => {
    const g = {};
    filtered.forEach(i => { if (!g[i.status]) g[i.status] = []; g[i.status].push(i); });
    return g;
  }, [filtered]);

  const handleSort = col => {
    if (sortCol === col) setSortDir(d => d === "asc" ? "desc" : "asc");
    else { setSortCol(col); setSortDir("asc"); }
  };

  // ── Settings save handler ──
  function handleSaveSettings(newSettings) {
    setSettings(prev => ({ ...prev, ...newSettings }));
    if (newSettings.liveIssues?.length > 0) {
      setIssues(newSettings.liveIssues);
      // Build projects color map
      const keys = [...new Set(newSettings.liveIssues.map(i => i.project))].filter(Boolean).sort();
      setProjects(Object.fromEntries(keys.map((k, i) => [k, DEFAULT_PROJECT_COLORS[i % DEFAULT_PROJECT_COLORS.length]])));
      setShowSettings(false);
    }
  }

  // ── AI Summary via LLM Gateway ──
  const formatSummaryAsText = useCallback(() => {
    if (!aiSummary) return "";
    const date = new Date().toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" });
    const activeFilters = Object.entries(filters).filter(([, v]) => v && v !== "All" && v !== "").map(([k, v]) => `${k}: ${v}`).join(" | ");
    return [
      "LILLY ENTERPRISE AUTOMATION — EXECUTIVE PORTFOLIO BRIEFING",
      date,
      activeFilters ? `Filters: ${activeFilters}` : `All ${filtered.length.toLocaleString()} issues`,
      "",
      aiSummary,
      "", "—",
      "Generated by Scrum Master Dashboard · Lilly Jira · LLM Gateway",
    ].join("\n");
  }, [aiSummary, filters, filtered.length]);

  const handleSendEmail = useCallback(async () => {
    if (!emailTo.trim() || !aiSummary) return;
    setEmailStatus("sending");
    const date    = new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
    const subject = encodeURIComponent(`Lilly Portfolio Executive Briefing — ${date}`);
    const body    = encodeURIComponent(formatSummaryAsText());
    const cc      = emailCc.trim() ? `&cc=${encodeURIComponent(emailCc.trim())}` : "";
    try {
      window.location.href = `mailto:${encodeURIComponent(emailTo.trim())}?subject=${subject}${cc}&body=${body}`;
      setEmailStatus("sent");
      setTimeout(() => setEmailStatus(null), 4000);
    } catch {
      setEmailStatus("error");
      setTimeout(() => setEmailStatus(null), 4000);
    }
  }, [emailTo, emailCc, aiSummary, formatSummaryAsText]);

  const handleCopyToClipboard = useCallback(() => {
    navigator.clipboard.writeText(formatSummaryAsText()).then(() => {
      setEmailStatus("copied");
      setTimeout(() => setEmailStatus(null), 2500);
    }).catch(() => setEmailStatus("error"));
  }, [formatSummaryAsText]);

  const generateAI = useCallback(async () => {
    const { llmUrl, llmKey, llmModel } = settings;
    if (!llmKey) {
      setAiSummary("⚙️ LLM Gateway not configured.\n\nClick ⚙️ Settings and enter your LLM Gateway URL and API key.");
      return;
    }
    setAiLoading(true);
    setAiSummary("");

    const sample = filtered.slice(0, 50).map(i =>
      `[${i.key}|${i.project}] ${i.summary} | ${i.status} | ${i.issueType} | ${i.assignee} | Updated: ${i.updated}${i.completed ? " | Completed: " + i.completed : ""}`
    ).join("\n");

    const activeFilters = Object.entries(filters).filter(([, v]) => v && v !== "All").map(([k, v]) => `${k}=${v}`).join(", ");
    const prompt = `You are a Scrum Master producing a structured executive portfolio status briefing for Eli Lilly leadership. Active filters: ${activeFilters || "none"}. Total matching issues: ${filtered.length}.

Sample issues (up to 50):
${sample}

Respond using EXACTLY this format — no deviations. Each section header on its own line followed by a colon. Write 2-4 concise sentences per section grounded in the data.

PORTFOLIO OVERVIEW:
IN PROGRESS:
RECENTLY COMPLETED:
KEY RISKS:
BLOCKERS:
RECOMMENDED ACTIONS:`;

    try {
      const res = await fetch(`${llmUrl.replace(/\/$/, "")}/v1/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": llmKey,
          "anthropic-version": "2023-06-01"
        },
        body: JSON.stringify({
          model: llmModel,
          max_tokens: 1200,
          messages: [{ role: "user", content: prompt }]
        })
      });
      if (!res.ok) { const e = await res.text(); throw new Error(`HTTP ${res.status}: ${e.slice(0, 300)}`); }
      const d = await res.json();
      setAiSummary(d.content?.[0]?.text || "Could not generate summary.");
    } catch (err) {
      setAiSummary(`Error: ${err.message}\n\nCheck your LLM Gateway URL and API key in ⚙️ Settings.`);
    }
    setAiLoading(false);
  }, [filtered, filters, settings]);

  const SECTION_ICONS = {
    "PORTFOLIO OVERVIEW":  { icon: "📊", color: "#C8102E" },
    "IN PROGRESS":         { icon: "🔄", color: "#0057A8" },
    "RECENTLY COMPLETED":  { icon: "✅", color: "#00703C" },
    "KEY RISKS":           { icon: "⚠️", color: "#E8830C" },
    "BLOCKERS":            { icon: "🚫", color: "#C8102E" },
    "RECOMMENDED ACTIONS": { icon: "💡", color: "#6B3FA0" },
  };

  const TH = ({ col, label, style = {} }) => (
    <th onClick={() => handleSort(col)} style={{
      padding: "10px 14px", textAlign: "left",
      color: sortCol === col ? "#C8102E" : "#6B6B6B",
      fontWeight: 700, cursor: "pointer", whiteSpace: "nowrap",
      userSelect: "none", fontSize: 11, letterSpacing: ".05em",
      textTransform: "uppercase", fontFamily: "Arial, sans-serif",
      borderBottom: "2px solid #E8E8E8", background: "#FAFAFA", ...style
    }}>
      {label}{sortCol === col ? (sortDir === "asc" ? " ↑" : " ↓") : ""}
    </th>
  );

  const BTN = ({ active, onClick, children, style = {} }) => (
    <button onClick={onClick} style={{
      fontFamily: "Arial, sans-serif", fontSize: 12, fontWeight: 600,
      padding: "7px 14px", border: active ? "none" : "1px solid #D0D0D0",
      borderRadius: 3, cursor: "pointer",
      background: active ? "#C8102E" : "#fff",
      color: active ? "#fff" : "#1A1A1A",
      transition: "all .15s", ...style
    }}>{children}</button>
  );

  const projectKeys = Object.keys(projects);

  // ─────────────────────────────────────────────────────────────────
  return (
    <div style={{ fontFamily: "Arial, sans-serif", background: "#F5F5F5", minHeight: "100vh", color: "#1A1A1A" }}>
      <style>{`
        * { box-sizing: border-box; }
        input, select, textarea { outline: none; transition: border-color .15s; }
        input:focus, select:focus, textarea:focus { border-color: #C8102E !important; }
        .row-hover:hover { background: #FFF8F8 !important; }
        @keyframes spin { 0%,100%{opacity:.3} 50%{opacity:1} }
      `}</style>

      {/* Settings Modal */}
      {showSettings && (
        <SettingsModal
          onClose={() => setShowSettings(false)}
          onSave={handleSaveSettings}
          initialSettings={settings}
          hasData={hasData}
        />
      )}

      {/* ── HEADER ── */}
      <div style={{ background: "#C8102E", padding: "0 24px", display: "flex", alignItems: "stretch", minHeight: 60 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16, flex: 1 }}>
          <div style={{ borderRight: "1px solid rgba(255,255,255,.3)", paddingRight: 16, marginRight: 4 }}>
            <div style={{ fontSize: 9, color: "rgba(255,255,255,.7)", letterSpacing: ".12em", fontWeight: 700, textTransform: "uppercase" }}>Eli Lilly and Company</div>
            <div style={{ fontSize: 17, fontWeight: 700, color: "#fff", letterSpacing: "-.01em", fontFamily: "Arial Black, Arial, sans-serif" }}>Scrum Master Dashboard</div>
          </div>
          {hasData && (
            <div style={{ fontSize: 12, color: "rgba(255,255,255,.8)" }}>
              {projectKeys.join(" · ")} &nbsp;|&nbsp;
              <strong style={{ color: "#fff" }}>{issues.length.toLocaleString()}</strong> issues &nbsp;|&nbsp;
              <span style={{ fontSize: 10, background: "rgba(255,255,255,.25)", padding: "1px 8px", borderRadius: 10, fontWeight: 700, color: "#fff" }}>
                ● LIVE
              </span>
            </div>
          )}
          {!hasData && (
            <div style={{ fontSize: 12, color: "rgba(255,255,255,.6)" }}>No projects connected</div>
          )}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 6, paddingRight: 130 }}>
          {hasData && ["table", "kanban", "charts"].map(v => (
            <button key={v} onClick={() => setView(v)} style={{
              background: view === v ? "rgba(255,255,255,.25)" : "transparent",
              border: "1px solid rgba(255,255,255,.4)", borderRadius: 3,
              color: "#fff", fontFamily: "Arial, sans-serif", fontWeight: 600,
              fontSize: 11, padding: "5px 12px", cursor: "pointer"
            }}>{v === "table" ? "📋 Table" : v === "kanban" ? "🗂 Board" : "📊 Charts"}</button>
          ))}
          <button
            onClick={() => setShowSettings(true)}
            title="Settings"
            style={{
              background: "rgba(255,255,255,.15)", border: "1px solid rgba(255,255,255,.5)",
              borderRadius: 3, color: "#fff", fontFamily: "Arial, sans-serif", fontWeight: 700,
              fontSize: 14, padding: "5px 12px", cursor: "pointer", marginLeft: 8
            }}
          >⚙️</button>
        </div>
      </div>

      {/* ── EMPTY STATE ── */}
      {!hasData && (
        <EmptyState onOpenSettings={() => setShowSettings(true)} />
      )}

      {/* ── MAIN CONTENT (only when data is loaded) ── */}
      {hasData && (
        <div style={{ padding: "20px 24px" }}>

          {/* STAT CARDS */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: 12, marginBottom: 20 }}>
            <StatCard value={stats.total}      label="Total Issues"      color="#1A1A1A" sub="Filtered view" />
            <StatCard value={stats.inProgress} label="In Progress"       color="#0057A8" />
            <StatCard value={stats.done}       label="Completed"         color="#00703C" />
            <StatCard value={stats.blocked}    label="Blocked / On Hold" color="#C8102E" />
            <StatCard value={stats.high}       label="High Priority"     color="#E8830C" />
            <StatCard value={stats.overdue}    label="Overdue"           color="#8B0000" />
          </div>

          {/* PROJECT PILLS */}
          <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap", alignItems: "center" }}>
            {projectKeys.map(proj => {
              const pc      = projects[proj];
              const cnt     = stats.byProject[proj] || 0;
              const isActive = filters.project === proj;
              return (
                <div key={proj}
                  onClick={() => setFilter("project", isActive ? "All" : proj)}
                  style={{
                    background: isActive ? pc.accent : "#fff",
                    border: `2px solid ${isActive ? pc.accent : "#E8E8E8"}`,
                    borderRadius: 4, padding: "10px 20px", cursor: "pointer",
                    display: "flex", alignItems: "center", gap: 10, transition: "all .15s",
                    boxShadow: isActive ? `0 2px 8px ${pc.accent}40` : "0 1px 3px rgba(0,0,0,.05)"
                  }}
                >
                  <div style={{ width: 10, height: 10, borderRadius: 2, background: isActive ? "#fff" : pc.accent }} />
                  <span style={{ fontWeight: 700, fontSize: 13, color: isActive ? "#fff" : pc.accent }}>{proj}</span>
                  <span style={{ fontSize: 20, fontWeight: 700, color: isActive ? "#fff" : "#1A1A1A", marginLeft: 4 }}>{cnt.toLocaleString()}</span>
                </div>
              );
            })}
            <button
              onClick={() => setShowSettings(true)}
              style={{
                fontFamily: "Arial, sans-serif", fontSize: 11, fontWeight: 600,
                padding: "6px 14px", border: "1px dashed #C8102E50", borderRadius: 4,
                background: "#FFF0F2", color: "#C8102E", cursor: "pointer"
              }}
            >⚙️ Manage Projects</button>
          </div>

          {/* FILTERS */}
          <div style={{ background: "#fff", border: "1px solid #E8E8E8", borderRadius: 4, padding: 16, marginBottom: 16, boxShadow: "0 1px 3px rgba(0,0,0,.05)" }}>
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "flex-end" }}>
              <SelectEl label="Project"  value={filters.project}   onChange={v => setFilter("project", v)}   options={ALL_PROJECTS} />
              <SelectEl label="Status"   value={filters.status}    onChange={v => setFilter("status", v)}    options={ALL_STATUSES} />
              <SelectEl label="Type"     value={filters.issueType} onChange={v => setFilter("issueType", v)} options={ALL_TYPES} />
              <SelectEl label="Priority" value={filters.priority}  onChange={v => setFilter("priority", v)}  options={ALL_PRIORITIES} />
              <SelectEl label="Assignee" value={filters.assignee}  onChange={v => setFilter("assignee", v)}  options={ALL_ASSIGNEES} />
              <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
                <LabelEl>Search</LabelEl>
                <input
                  type="text" placeholder="Key, summary, assignee..."
                  value={filters.search} onChange={e => setFilter("search", e.target.value)}
                  style={{ fontFamily: "Arial, sans-serif", fontSize: 12, padding: "6px 10px", border: "1px solid #D0D0D0", borderRadius: 3, color: "#1A1A1A", width: 200, outline: "none" }}
                />
              </div>
              <div style={{ display: "flex", gap: 8, alignItems: "flex-end" }}>
                <BTN active={showDateFilters} onClick={() => setShowDateFilters(s => !s)} style={{ height: 32 }}>
                  📅 Date Filters{hasDateFilters ? " ●" : ""}
                </BTN>
                {hasAnyFilter && (
                  <BTN onClick={clearFilters} style={{ height: 32, color: "#C8102E", borderColor: "#C8102E" }}>✕ Clear</BTN>
                )}
              </div>
            </div>

            {showDateFilters && (
              <div style={{ marginTop: 14, paddingTop: 14, borderTop: "1px solid #E8E8E8", display: "flex", gap: 16, flexWrap: "wrap" }}>
                <div>
                  <div style={{ fontSize: 10, fontWeight: 700, color: "#6B6B6B", marginBottom: 6, textTransform: "uppercase", letterSpacing: ".06em" }}>Date Created</div>
                  <div style={{ display: "flex", gap: 8 }}>
                    <DateField label="From" value={filters.createdFrom} onChange={v => setFilter("createdFrom", v)} />
                    <DateField label="To"   value={filters.createdTo}   onChange={v => setFilter("createdTo",   v)} />
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 10, fontWeight: 700, color: "#6B6B6B", marginBottom: 6, textTransform: "uppercase", letterSpacing: ".06em" }}>Date Completed</div>
                  <div style={{ display: "flex", gap: 8 }}>
                    <DateField label="From" value={filters.completedFrom} onChange={v => setFilter("completedFrom", v)} />
                    <DateField label="To"   value={filters.completedTo}   onChange={v => setFilter("completedTo",   v)} />
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 10, fontWeight: 700, color: "#6B6B6B", marginBottom: 6, textTransform: "uppercase", letterSpacing: ".06em" }}>Date Updated</div>
                  <div style={{ display: "flex", gap: 8 }}>
                    <DateField label="From" value={filters.updatedFrom} onChange={v => setFilter("updatedFrom", v)} />
                    <DateField label="To"   value={filters.updatedTo}   onChange={v => setFilter("updatedTo",   v)} />
                  </div>
                </div>
                <div style={{ fontSize: 11, color: "#6B6B6B", alignSelf: "flex-end", maxWidth: 220, lineHeight: 1.5, paddingBottom: 6 }}>
                  <strong>Note:</strong> "Date Completed" uses last-updated for issues in terminal statuses.
                </div>
              </div>
            )}

            <div style={{ marginTop: 10, fontSize: 12, color: "#6B6B6B", display: "flex", gap: 16 }}>
              <span>Showing <strong style={{ color: "#C8102E" }}>{filtered.length.toLocaleString()}</strong> of {issues.length.toLocaleString()} issues</span>
              {hasDateFilters && <span style={{ color: "#E8830C", fontWeight: 600 }}>● Date filters active</span>}
            </div>
          </div>

          {/* AI SUMMARY */}
          <div style={{ background: "#fff", border: "1px solid #E8E8E8", borderRadius: 4, padding: 16, marginBottom: 16, boxShadow: "0 1px 3px rgba(0,0,0,.05)" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 8 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <button onClick={() => setSummaryCollapsed(c => !c)}
                  style={{ background: "none", border: "none", cursor: "pointer", color: "#6B6B6B", fontSize: 14, padding: 0 }}>
                  {summaryCollapsed ? "▶" : "▼"}
                </button>
                <span style={{ fontSize: 13, fontWeight: 700, color: "#1A1A1A" }}>AI Executive Summary</span>
                <span style={{
                  fontSize: 10, padding: "1px 8px", borderRadius: 10, fontWeight: 700,
                  background: settings.llmKey ? "#0057A8" : "#E8E8E8",
                  color: settings.llmKey ? "#fff" : "#6B6B6B"
                }}>
                  {settings.llmKey ? "LLM GATEWAY" : "NOT CONFIGURED"}
                </span>
                {!aiSummary && !aiLoading && (
                  <span style={{ fontSize: 11, color: settings.llmKey ? "#6B6B6B" : "#C8102E" }}>
                    {settings.llmKey ? "Ready to generate" : "Configure in ⚙️ Settings"}
                  </span>
                )}
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                {!settings.llmKey && (
                  <button onClick={() => setShowSettings(true)} style={{
                    fontFamily: "Arial, sans-serif", fontSize: 12, fontWeight: 600,
                    padding: "7px 14px", border: "1px solid #D0D0D0", borderRadius: 3,
                    background: "#fff", color: "#1A1A1A", cursor: "pointer"
                  }}>⚙️ Configure</button>
                )}
                <button onClick={generateAI} disabled={aiLoading} style={{
                  fontFamily: "Arial, sans-serif", fontSize: 12, fontWeight: 700,
                  padding: "7px 16px", border: "none", borderRadius: 3,
                  background: aiLoading ? "#E8E8E8" : "#C8102E",
                  color: aiLoading ? "#6B6B6B" : "#fff",
                  cursor: aiLoading ? "not-allowed" : "pointer"
                }}>
                  {aiLoading ? "Generating..." : "✦ Generate Summary"}
                </button>
              </div>
            </div>

            {!summaryCollapsed && (
              <div style={{ marginTop: 12 }}>
                {aiLoading && (
                  <div style={{ display: "flex", gap: 6, padding: "10px 0", alignItems: "center" }}>
                    {[0,1,2].map(i => (
                      <div key={i} style={{ width: 8, height: 8, borderRadius: "50%", background: "#C8102E", animation: `spin 1.2s ${i*.2}s infinite` }} />
                    ))}
                    <span style={{ fontSize: 12, color: "#6B6B6B", marginLeft: 6 }}>Analyzing {filtered.length.toLocaleString()} issues via LLM Gateway...</span>
                  </div>
                )}

                {aiSummary && !aiLoading && (
                  <div>
                    <div style={{ background: "#FAFAFA", border: "1px solid #E8E8E8", borderRadius: 4, padding: 16 }}>
                      {aiSummary.split("\n").map((line, i) => {
                        const trimmed = line.trim();
                        const hk = Object.keys(SECTION_ICONS).find(k => trimmed.startsWith(k + ":"));
                        if (hk) {
                          const { icon, color } = SECTION_ICONS[hk];
                          return (
                            <div key={i} style={{
                              display: "flex", alignItems: "center", gap: 8,
                              background: color + "0D", border: `1px solid ${color}20`,
                              borderRadius: 3, padding: "7px 12px",
                              marginTop: i === 0 ? 0 : 14, marginBottom: 6
                            }}>
                              <span style={{ fontSize: 14 }}>{icon}</span>
                              <span style={{ fontSize: 12, fontWeight: 700, color, letterSpacing: ".05em" }}>{hk}</span>
                            </div>
                          );
                        }
                        if (!trimmed) return null;
                        return <p key={i} style={{ fontSize: 13, lineHeight: 1.7, color: "#1A1A1A", margin: "0 0 4px 0", paddingLeft: 4 }}>{trimmed}</p>;
                      })}
                    </div>
                    <div style={{ marginTop: 10, fontSize: 11, color: "#6B6B6B", fontStyle: "italic" }}>
                      Generated {new Date().toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })} · {filtered.length.toLocaleString()} issues · via LLM Gateway
                    </div>
                    <div style={{ marginTop: 12, borderTop: "1px solid #E8E8E8", paddingTop: 12 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: showEmailPanel ? 10 : 0 }}>
                        <button onClick={() => setShowEmailPanel(s => !s)} style={{ background: "none", border: "none", cursor: "pointer", color: "#6B6B6B", fontSize: 14, padding: 0 }}>
                          {showEmailPanel ? "▼" : "▶"}
                        </button>
                        <span style={{ fontSize: 12, fontWeight: 700, color: "#1A1A1A" }}>📧 Send Summary</span>
                        <button onClick={handleCopyToClipboard} style={{
                          marginLeft: "auto", fontFamily: "Arial, sans-serif", fontSize: 11,
                          padding: "4px 12px", border: "1px solid #D0D0D0", borderRadius: 3,
                          background: "#fff", cursor: "pointer", color: "#1A1A1A"
                        }}>
                          {emailStatus === "copied" ? "✓ Copied!" : "📋 Copy Text"}
                        </button>
                      </div>
                      {showEmailPanel && (
                        <div style={{ background: "#FAFAFA", border: "1px solid #E8E8E8", borderRadius: 4, padding: 14 }}>
                          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
                            <div>
                              <LabelEl>To *</LabelEl>
                              <InputEl value={emailTo} onChange={setEmailTo} placeholder="recipient@lilly.com" type="email"
                                style={{ border: `1px solid ${emailTo ? "#C8102E" : "#D0D0D0"}` }} />
                            </div>
                            <div>
                              <LabelEl>CC</LabelEl>
                              <InputEl value={emailCc} onChange={setEmailCc} placeholder="cc@lilly.com" type="email" />
                            </div>
                          </div>
                          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                            <button onClick={handleSendEmail} disabled={!emailTo.trim()} style={{
                              fontFamily: "Arial, sans-serif", fontSize: 12, fontWeight: 700, padding: "7px 20px",
                              border: "none", borderRadius: 3,
                              background: emailTo.trim() ? "#C8102E" : "#E8E8E8",
                              color: emailTo.trim() ? "#fff" : "#6B6B6B",
                              cursor: emailTo.trim() ? "pointer" : "not-allowed"
                            }}>Send via Email</button>
                            {emailStatus === "sent"  && <span style={{ fontSize: 12, color: "#00703C", fontWeight: 600 }}>✓ Email client opened</span>}
                            {emailStatus === "error" && <span style={{ fontSize: 12, color: "#C8102E", fontWeight: 600 }}>✗ Use Copy Text instead</span>}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* ── TABLE VIEW ── */}
          {view === "table" && (
            <div style={{ background: "#fff", border: "1px solid #E8E8E8", borderRadius: 4, overflow: "hidden", boxShadow: "0 1px 3px rgba(0,0,0,.05)" }}>
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                  <thead>
                    <tr>
                      <TH col="key"       label="Issue" />
                      <TH col="project"   label="Project" />
                      <TH col="issueType" label="Type" />
                      <TH col="summary"   label="Summary" style={{ minWidth: 280 }} />
                      <TH col="status"    label="Status" />
                      <TH col="priority"  label="Priority" />
                      <TH col="assignee"  label="Assignee" />
                      <TH col="created"   label="Created" />
                      <TH col="updated"   label="Updated" />
                      <TH col="completed" label="Completed" />
                      <TH col="dueDate"   label="Due" />
                    </tr>
                  </thead>
                  <tbody>
                    {paged.map((issue, idx) => {
                      const pc         = projects[issue.project] || { accent: "#6B6B6B", light: "#F5F5F5" };
                      const pr         = PRIORITY_STYLE[issue.priority] || PRIORITY_STYLE["Not Set"];
                      const today      = new Date().toISOString().slice(0, 10);
                      const isOverdue  = issue.dueDate && issue.dueDate < today && issue.statusCat !== "Done";
                      const isExpanded = expandedKey === issue.key;
                      return (
                        <>
                          <tr key={issue.key} className="row-hover"
                            onClick={() => setExpandedKey(isExpanded ? null : issue.key)}
                            style={{ borderBottom: "1px solid #F0F0F0", background: idx % 2 === 0 ? "#fff" : "#FAFAFA", cursor: "pointer" }}
                          >
                            <td style={{ padding: "10px 14px", whiteSpace: "nowrap" }}>
                              <a href={issue.url} target="_blank" rel="noopener noreferrer"
                                onClick={e => e.stopPropagation()}
                                style={{ color: pc.accent, textDecoration: "none", fontWeight: 700, fontSize: 12 }}>
                                {issue.key}
                              </a>
                            </td>
                            <td style={{ padding: "10px 14px" }}>
                              <span style={{ background: pc.light, color: pc.accent, padding: "2px 8px", borderRadius: 3, fontSize: 11, fontWeight: 700, border: `1px solid ${pc.accent}30` }}>
                                {issue.project}
                              </span>
                            </td>
                            <td style={{ padding: "10px 14px", color: "#6B6B6B", fontSize: 12, whiteSpace: "nowrap" }}>
                              {TYPE_ICON[issue.issueType] || "◻"} {issue.issueType}
                            </td>
                            <td style={{ padding: "10px 14px", maxWidth: 320, color: "#1A1A1A" }}>
                              <div style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{issue.summary}</div>
                            </td>
                            <td style={{ padding: "10px 14px" }}><StatusPill status={issue.status} /></td>
                            <td style={{ padding: "10px 14px" }}>
                              <span style={{ color: pr.c, fontWeight: 700, fontSize: 12 }}>{pr.label}</span>
                            </td>
                            <td style={{ padding: "10px 14px", fontSize: 12, color: "#6B6B6B", whiteSpace: "nowrap" }}>
                              {issue.assignee === "Unassigned" ? <span style={{ color: "#C0C0C0" }}>—</span> : issue.assignee}
                            </td>
                            <td style={{ padding: "10px 14px", fontSize: 12, color: "#6B6B6B", whiteSpace: "nowrap" }}>{issue.created || "—"}</td>
                            <td style={{ padding: "10px 14px", fontSize: 12, color: "#6B6B6B", whiteSpace: "nowrap" }}>{issue.updated}</td>
                            <td style={{ padding: "10px 14px", fontSize: 12, whiteSpace: "nowrap" }}>
                              {issue.completed ? <span style={{ color: "#00703C", fontWeight: 600 }}>✓ {issue.completed}</span> : <span style={{ color: "#C0C0C0" }}>—</span>}
                            </td>
                            <td style={{ padding: "10px 14px", fontSize: 12, whiteSpace: "nowrap", color: isOverdue ? "#C8102E" : "#6B6B6B", fontWeight: isOverdue ? 700 : 400 }}>
                              {issue.dueDate || "—"}{isOverdue && <span style={{ marginLeft: 4, fontSize: 10 }}>OVERDUE</span>}
                            </td>
                          </tr>
                          {isExpanded && (
                            <tr key={issue.key + "-exp"} style={{ background: "#FFF8F8", borderBottom: "2px solid #C8102E20" }}>
                              <td colSpan={11} style={{ padding: "12px 20px" }}>
                                <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
                                  <div>
                                    <div style={{ fontSize: 10, fontWeight: 700, color: "#6B6B6B", letterSpacing: ".06em", marginBottom: 4, textTransform: "uppercase" }}>Full Summary</div>
                                    <div style={{ fontSize: 13, color: "#1A1A1A", maxWidth: 520, lineHeight: 1.6 }}>{issue.summary}</div>
                                  </div>
                                  {issue.labels.length > 0 && (
                                    <div>
                                      <div style={{ fontSize: 10, fontWeight: 700, color: "#6B6B6B", letterSpacing: ".06em", marginBottom: 4, textTransform: "uppercase" }}>Labels</div>
                                      <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                                        {issue.labels.map(l => <span key={l} style={{ background: "#EBF3FF", color: "#0057A8", padding: "2px 8px", borderRadius: 3, fontSize: 11 }}>{l}</span>)}
                                      </div>
                                    </div>
                                  )}
                                  {issue.completed && (
                                    <div>
                                      <div style={{ fontSize: 10, fontWeight: 700, color: "#6B6B6B", letterSpacing: ".06em", marginBottom: 4, textTransform: "uppercase" }}>Completed</div>
                                      <div style={{ fontSize: 12, color: "#00703C", fontWeight: 600 }}>{issue.completed}</div>
                                    </div>
                                  )}
                                  <div>
                                    <div style={{ fontSize: 10, fontWeight: 700, color: "#6B6B6B", letterSpacing: ".06em", marginBottom: 4, textTransform: "uppercase" }}>Open in Jira</div>
                                    <a href={issue.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: 12, color: "#C8102E", fontWeight: 600 }}>↗ {issue.key}</a>
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )}
                        </>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              {filtered.length === 0 && (
                <div style={{ textAlign: "center", padding: 48, color: "#6B6B6B", fontSize: 14 }}>No issues match the current filters.</div>
              )}
              {totalPages > 1 && (
                <div style={{ padding: "12px 16px", borderTop: "1px solid #E8E8E8", display: "flex", alignItems: "center", gap: 8, background: "#FAFAFA" }}>
                  <BTN onClick={() => setPage(p => Math.max(0, p - 1))}            active={false} style={{ padding: "5px 12px" }}>← Prev</BTN>
                  <BTN onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} active={false} style={{ padding: "5px 12px" }}>Next →</BTN>
                  <span style={{ fontSize: 12, color: "#6B6B6B", marginLeft: 8 }}>Page {page + 1} of {totalPages} · {filtered.length.toLocaleString()} issues</span>
                </div>
              )}
            </div>
          )}

          {/* ── KANBAN VIEW ── */}
          {view === "kanban" && (
            <div style={{ overflowX: "auto", paddingBottom: 12 }}>
              <div style={{ display: "flex", gap: 12, minWidth: "max-content" }}>
                {Object.entries(kanbanGroups).sort((a, b) => b[1].length - a[1].length).slice(0, 10).map(([status, statusIssues]) => {
                  const c = STATUS_COLOR[status] || "#6B6B6B";
                  return (
                    <div key={status} style={{ width: 280, background: "#fff", border: "1px solid #E8E8E8", borderRadius: 4, overflow: "hidden", flexShrink: 0, boxShadow: "0 1px 3px rgba(0,0,0,.05)" }}>
                      <div style={{ padding: "10px 14px", background: c + "10", borderBottom: `3px solid ${c}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ fontSize: 11, fontWeight: 700, color: c, textTransform: "uppercase", letterSpacing: ".06em" }}>{status}</span>
                        <span style={{ fontSize: 13, fontWeight: 700, color: c, background: c + "20", padding: "1px 8px", borderRadius: 10 }}>{statusIssues.length}</span>
                      </div>
                      <div style={{ padding: 8, maxHeight: 560, overflowY: "auto" }}>
                        {statusIssues.slice(0, 30).map(issue => {
                          const pc = projects[issue.project] || { accent: "#6B6B6B" };
                          return (
                            <div key={issue.key} style={{ background: "#FAFAFA", border: "1px solid #E8E8E8", borderRadius: 3, padding: "10px 12px", marginBottom: 6 }}>
                              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                                <a href={issue.url} target="_blank" rel="noopener noreferrer" style={{ color: pc.accent, textDecoration: "none", fontSize: 11, fontWeight: 700 }}>{issue.key}</a>
                                <span style={{ fontSize: 10, color: "#6B6B6B" }}>{issue.completed || issue.updated}</span>
                              </div>
                              <div style={{ fontSize: 12, color: "#1A1A1A", lineHeight: 1.5, marginBottom: 6 }}>{issue.summary.slice(0, 75)}{issue.summary.length > 75 ? "…" : ""}</div>
                              <div style={{ display: "flex", justifyContent: "space-between" }}>
                                <span style={{ fontSize: 10, color: "#6B6B6B" }}>{TYPE_ICON[issue.issueType]} {issue.issueType}</span>
                                <span style={{ fontSize: 10, color: "#6B6B6B" }}>{issue.assignee !== "Unassigned" ? issue.assignee.split(" ")[0] : "—"}</span>
                              </div>
                            </div>
                          );
                        })}
                        {statusIssues.length > 30 && (
                          <div style={{ textAlign: "center", fontSize: 11, color: "#6B6B6B", padding: 8, background: "#F0F0F0", borderRadius: 3 }}>+{statusIssues.length - 30} more</div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* ── CHARTS VIEW ── */}
          {view === "charts" && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: 16 }}>
              {[
                { title: "Issues by Status",  data: stats.byStatus,  colorFn: k => STATUS_COLOR[k] || "#6B6B6B" },
                { title: "Issues by Project", data: stats.byProject, colorFn: k => projects[k]?.accent || "#6B6B6B" },
                { title: "Issues by Type",    data: stats.byType,    colorFn: () => "#0057A8" },
              ].map(({ title, data, colorFn }) => {
                const sorted = Object.entries(data).sort((a, b) => b[1] - a[1]).slice(0, 15);
                const max    = sorted[0]?.[1] || 1;
                return (
                  <div key={title} style={{ background: "#fff", border: "1px solid #E8E8E8", borderRadius: 4, padding: 20, boxShadow: "0 1px 3px rgba(0,0,0,.05)" }}>
                    <div style={{ fontSize: 13, fontWeight: 700, color: "#1A1A1A", marginBottom: 16, paddingBottom: 10, borderBottom: "2px solid #C8102E" }}>{title}</div>
                    {sorted.map(([k, v]) => {
                      const bc = colorFn(k);
                      return (
                        <div key={k} style={{ marginBottom: 8 }}>
                          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                            <span style={{ fontSize: 12, color: "#1A1A1A", maxWidth: 220, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{k}</span>
                            <span style={{ fontSize: 12, color: bc, fontWeight: 700 }}>{v.toLocaleString()}</span>
                          </div>
                          <div style={{ height: 6, background: "#F0F0F0", borderRadius: 3, overflow: "hidden" }}>
                            <div style={{ height: "100%", width: `${(v / max) * 100}%`, background: bc, borderRadius: 3, transition: "width .4s" }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          )}

          {/* FOOTER */}
          <div style={{ marginTop: 24, borderTop: "1px solid #E8E8E8", paddingTop: 14, display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 8 }}>
            <span style={{ fontSize: 11, color: "#6B6B6B" }}>
              Lilly Enterprise Automation · {projectKeys.join(" / ")} · Live Jira · {new Date().toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}
            </span>
            <span style={{ fontSize: 11, color: "#C0C0C0" }}>© {new Date().getFullYear()} Eli Lilly and Company</span>
          </div>
        </div>
      )}
    </div>
  );
}
