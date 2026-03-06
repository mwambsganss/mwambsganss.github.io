# Jira Executive Dashboard

Interactive executive dashboard for Jira projects **EAA**, **ASO**, and **KILO** — built as a single-page HTML app that runs entirely in the browser.

## Features

| Category | What's included |
|---|---|
| **Data** | All Jira issue types: Stories, Bugs, Tasks, Epics, Sub-tasks, Improvements, Spikes, Initiatives |
| **Filters** | Project, Assignee, Status, Issue Type, Priority, Sprint, Date Range, Free-text search |
| **KPIs** | Total · Done · In Progress · To Do · Blocked · Overdue · Completion % |
| **Charts** | Status donut · Type donut · Assignee bar · Priority donut · Created vs. Resolved timeline |
| **Table** | Sortable, paginated, group-by (status/assignee/type/project/priority/sprint) |
| **AI Summary** | Scrum Master status update via Claude (Lilly LLM Gateway) with rule-based fallback |

---

## Quick Start

### 1. Open the dashboard

Open `index.html` in your browser (double-click, or serve locally).

> **Note:** The Jira REST API requires credentials — browsers will block cross-origin requests unless the dashboard is served from a local server or the same origin. Run a simple server:
> ```bash
> cd "Jira Dashboard"
> python3 -m http.server 8080
> # then open http://localhost:8080
> ```

### 2. Configure credentials (⚙️ Settings)

Click **⚙️ Settings** in the top-right and fill in:

| Field | Value |
|---|---|
| Jira Base URL | `https://lilly-jira.atlassian.net` |
| Email | Your Lilly email |
| API Token | Generate at https://id.atlassian.com/manage-profile/security/api-tokens |
| Projects | `EAA,ASO,KILO` (pre-filled) |
| Gateway Base URL | `https://lilly-code-server.api.gateway.llm.lilly.com` |
| API Key / Token | Your Lilly Code / LLM Gateway API key |
| Model | `sonnet-latest` or `claude-sonnet-4-6` |

Click **Save & Load** — the dashboard fetches all issues from all three projects.

### 3. Try demo data

Not ready with credentials? Click **⚙️ Settings → Load Demo Data** for ~130 realistic sample issues across all three projects.

---

## Using the Dashboard

### Filtering

- **Chip selectors** (Project, Status, Type, Priority) — click multiple chips to OR-filter within a category
- **Dropdowns** (Assignee, Sprint) — single-select
- **Date Range** — filters on the `updated` date of issues
- **Search** — matches key, summary, and labels
- **Clear** button resets all filters

### AI Summary

1. Apply any filters to scope the view
2. Click **Generate Summary** in the *Scrum Master Summary* panel
3. Claude produces a structured executive update covering health, progress, risks, workload, and recommendations

If the Claude API is unreachable, a rule-based summary is shown automatically.

### Table

- Click any column header to sort
- Use **Group by** to cluster by status, assignee, type, etc.
- Click an issue key to open it in Jira

---

## File Structure

```
Jira Dashboard/
├── index.html    # Shell, layout, filter UI, settings panel
├── styles.css    # Dark-theme design system
├── app.js        # Jira REST API, filters, charts, AI summaries
└── README.md     # This file
```

---

## Adding the Atlassian MCP (future)

When the Atlassian MCP server is available, add it globally:

```bash
claude mcp add --transport http atlassian https://<mcp-server-url> \
  --header "Authorization: Bearer <token>"
```

The dashboard's `fetchProjectIssues()` function in `app.js` can then be adapted to route through the MCP instead of the REST API for richer data (attachments, linked issues, etc.).

---

## Jira Projects

| Key | Board | Type |
|---|---|---|
| EAA | [boards/13539](https://lilly-jira.atlassian.net/jira/software/c/projects/EAA/boards/13539) | Software (Scrum) |
| ASO | [board](https://lilly-jira.atlassian.net/jira/core/projects/ASO/board) | Business (Kanban) |
| KILO | [boards/7113](https://lilly-jira.atlassian.net/jira/software/c/projects/KILO/boards/7113) | Software (Scrum) |

---

## Security Notes

- Credentials are stored in `localStorage` in your browser only
- No data is sent to any third party
- API token is base64-encoded in the `Authorization` header (standard Jira Basic Auth)
- The Claude API call goes directly to the Lilly LLM Gateway — no data leaves Lilly's environment
