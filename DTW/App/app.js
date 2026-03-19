/* ═══════════════════════════════════════════════════════════════════════════
   Design Thinking Workshop App — Frontend JS
   ═══════════════════════════════════════════════════════════════════════════ */

"use strict";

// ── State ──────────────────────────────────────────────────────────────────────
const state = {
  view:               "landing",
  sessionId:          null,
  sessionData:        null,
  displayName:        null,
  isFacilitator:      false,
  socket:             null,
  exercises:          [],        // full exercises.json catalog
  currentExerciseMeta: null,
  summaryVisible:     false,
  identity:           null,      // {name, email, is_facilitator} from /api/me
};

// ── Init ───────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
  try {
    const resp = await fetch("/exercises.json");
    state.exercises = await resp.json();
  } catch (e) {
    console.error("Failed to load exercises.json:", e);
  }
  renderExercisePicker();
  await initAuth();
});

// ── View management ────────────────────────────────────────────────────────────
function showView(viewName) {
  document.querySelectorAll(".view").forEach(el => el.classList.remove("active"));
  const target = document.getElementById("view-" + viewName);
  if (target) target.classList.add("active");
  state.view = viewName;
}

// ── Auth via keychain SSO (/api/me) ────────────────────────────────────────────
async function initAuth() {
  // Dismiss the login overlay immediately (no MSAL redirect needed)
  const loginOverlay = document.getElementById("loginOverlay");
  if (loginOverlay) loginOverlay.classList.remove("active");

  try {
    const resp = await fetch("/api/me");
    const me   = await resp.json();

    if (me.name) {
      state.displayName = me.name;
      state.identity    = me;

      // Show identity hint on landing
      const idEl = document.getElementById("landing-identity");
      if (idEl) idEl.textContent = `Signed in as ${me.name}`;

      // Pre-fill participant name input (read-only since we know who they are)
      const nameInput = document.getElementById("join-display-name");
      if (nameInput) {
        nameInput.value    = me.name;
        nameInput.readOnly = true;
        nameInput.style.background = "var(--bg2)";
        nameInput.style.color      = "var(--text2)";
      }

      // Show Facilitator button only if on the whitelist
      if (me.is_facilitator) {
        const btn = document.getElementById("fac-login-btn");
        const div = document.getElementById("fac-divider");
        if (btn) { btn.style.display = "block"; btn.textContent = `Facilitate as ${me.name.split(" ")[0]}`; }
        if (div) div.style.display   = "block";
      }
    } else {
      // Server running without keychain (e.g. non-Mac) — show facilitator button for PIN fallback
      const btn = document.getElementById("fac-login-btn");
      const div = document.getElementById("fac-divider");
      if (btn) btn.style.display = "block";
      if (div) div.style.display = "block";
    }
  } catch (e) {
    console.warn("Could not fetch identity:", e);
    const btn = document.getElementById("fac-login-btn");
    const div = document.getElementById("fac-divider");
    if (btn) btn.style.display = "block";
    if (div) div.style.display = "block";
  }
}

function showJoin() {
  showView("join");
}

function showFacilitatorAccess() {
  if (state.identity && state.identity.is_facilitator) {
    showSessionPicker();
  } else {
    showView("facilitator-login");
  }
}

async function facilitatorPinLogin() {
  const name = document.getElementById("fac-login-name").value.trim();
  if (!name) { showToast("Enter your name.", true); return; }

  showLoading("Verifying…");
  try {
    const resp = await fetch("/api/facilitator-auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "Access denied");
    state.displayName = data.name;
    state.identity    = { name: data.name, is_facilitator: true };
    showSessionPicker();
  } catch (e) {
    showToast(e.message, true);
  } finally {
    hideLoading();
  }
}

// ── Session picker ─────────────────────────────────────────────────────────────
async function showSessionPicker() {
  showView("session-picker");

  const greeting = document.getElementById("session-picker-greeting");
  if (greeting && state.identity) {
    greeting.textContent = `Welcome, ${state.identity.name}. Click a session to start facilitating.`;
  }

  showLoading("Loading sessions…");
  try {
    const resp = await fetch("/api/sessions");
    const sessions = await resp.json();
    renderSessionPicker(sessions);
  } catch (e) {
    showToast("Failed to load sessions: " + e.message, true);
  } finally {
    hideLoading();
  }
}

function renderSessionPicker(sessions) {
  const list  = document.getElementById("session-picker-list");
  const empty = document.getElementById("session-picker-empty");
  if (!list) return;

  list.innerHTML = "";

  if (!sessions.length) {
    list.style.display  = "none";
    if (empty) empty.style.display = "block";
    return;
  }

  list.style.display  = "flex";
  if (empty) empty.style.display = "none";

  sessions.forEach(s => {
    const progress = s.exercise_count
      ? `${s.current_exercise_index + 1} / ${s.exercise_count} exercises`
      : "No exercises";
    const date = s.created_at ? s.created_at.slice(0, 10) : "";
    const card = document.createElement("div");
    card.className = "session-pick-card";
    card.innerHTML = `
      <div class="session-pick-main" style="cursor:pointer;" onclick="enterSessionAsFacilitator('${escHtml(s.session_id)}')">
        <div class="session-pick-name">${escHtml(s.session_name)}</div>
        <div class="session-pick-meta">${escHtml(progress)} &nbsp;·&nbsp; ${escHtml(date)}</div>
      </div>
      <div class="session-pick-right">
        <span class="session-pick-code">${escHtml(s.room_code)}</span>
        <span class="session-pick-participants">${s.participant_count} participant${s.participant_count !== 1 ? "s" : ""}</span>
        <button class="btn-session-del" onclick="deleteSession(event,'${escHtml(s.session_id)}')" title="Delete session">🗑</button>
      </div>`;
    list.appendChild(card);
  });
}

async function createTestSession() {
  showLoading("Creating test session…");
  try {
    const resp = await fetch("/api/sessions/test", { method: "POST" });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "Failed");
    showToast(`Test session created — room ${data.room_code}`);
    await showSessionPicker();
  } catch (e) {
    showToast(e.message, true);
    hideLoading();
  }
}

async function deleteSession(event, sessionId) {
  event.stopPropagation();
  if (!confirm("Delete this session and all its artifacts? This cannot be undone.")) return;
  try {
    const resp = await fetch(`/api/sessions/${sessionId}`, { method: "DELETE" });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "Failed");
    showToast("Session deleted.");
    await showSessionPicker();
  } catch (e) {
    showToast(e.message, true);
  }
}

async function enterSessionAsFacilitator(sessionId) {
  showLoading("Entering session…");
  try {
    const resp = await fetch(`/api/sessions/${sessionId}`);
    if (!resp.ok) throw new Error("Session not found");
    const s = await resp.json();
    state.sessionId     = s.session_id;
    state.isFacilitator = true;
    showView("facilitator");
    connectSocket(true);
  } catch (e) {
    showToast(e.message, true);
    hideLoading();
  }
}

// ── Exercise picker (facilitator setup) ───────────────────────────────────────
let pickerOrder = [];   // current ordered list of exercise IDs
let dragSrcIdx  = null;

function renderExercisePicker() {
  if (!state.exercises.length) return;
  const container = document.getElementById("exercise-picker-list");
  if (!container) return;

  // Init pickerOrder: intros_outcomes first, then persona_cards + executive_summary, then the rest
  if (!pickerOrder.length) {
    const priority = ["intros_outcomes", "persona_cards", "executive_summary"];
    const rest = state.exercises
      .map(e => e.id)
      .filter(id => !priority.includes(id));
    pickerOrder = [...priority.filter(id => state.exercises.find(e => e.id === id)), ...rest];
  }

  container.innerHTML = "";
  pickerOrder.forEach((exId, idx) => {
    const ex  = state.exercises.find(e => e.id === exId);
    if (!ex) return;
    const item = document.createElement("div");
    item.className   = "ex-pick-item";
    item.draggable   = true;
    item.dataset.idx = idx;
    item.dataset.id  = exId;
    item.innerHTML = `
      <span class="ex-pick-drag" title="Drag to reorder">⠿</span>
      <input type="checkbox" id="ex-${exId}" checked
             onchange="updatePickerCount()"/>
      <label class="ex-pick-name" for="ex-${exId}">${escHtml(ex.name)}</label>
      <span class="phase-badge ex-pick-phase" data-phase="${ex.phase}">${escHtml(ex.phase_name)}</span>
    `;
    item.addEventListener("dragstart", e => {
      dragSrcIdx = idx;
      item.classList.add("dragging");
      e.dataTransfer.effectAllowed = "move";
    });
    item.addEventListener("dragend", () => {
      item.classList.remove("dragging");
      dragSrcIdx = null;
      document.querySelectorAll(".ex-pick-item").forEach(i => i.classList.remove("drag-over"));
    });
    item.addEventListener("dragover", e => {
      e.preventDefault();
      e.dataTransfer.dropEffect = "move";
      document.querySelectorAll(".ex-pick-item").forEach(i => i.classList.remove("drag-over"));
      item.classList.add("drag-over");
    });
    item.addEventListener("drop", e => {
      e.preventDefault();
      if (dragSrcIdx === null || dragSrcIdx === idx) return;
      const [moved] = pickerOrder.splice(dragSrcIdx, 1);
      pickerOrder.splice(idx, 0, moved);
      renderExercisePicker();
    });
    container.appendChild(item);
  });
  updatePickerCount();
}

function updatePickerCount() {
  const total    = pickerOrder.length;
  const selected = pickerOrder.filter(id => {
    const cb = document.getElementById("ex-" + id);
    return cb && cb.checked;
  }).length;
  const el = document.getElementById("ex-picker-count");
  if (el) el.textContent = `${selected} of ${total} selected`;
}

function selectAllExercises() {
  document.querySelectorAll(".ex-pick-item input[type=checkbox]").forEach(cb => cb.checked = true);
  updatePickerCount();
}
function deselectAllExercises() {
  document.querySelectorAll(".ex-pick-item input[type=checkbox]").forEach(cb => cb.checked = false);
  updatePickerCount();
}

function getSelectedExerciseOrder() {
  const selected = pickerOrder.filter(id => {
    const cb = document.getElementById("ex-" + id);
    return cb && cb.checked;
  });
  return selected;
}

// ── Session creation ───────────────────────────────────────────────────────────
async function createSession() {
  const name  = document.getElementById("setup-session-name").value.trim();
  const order = getSelectedExerciseOrder();

  if (!name)         { showToast("Please enter a session name.", true); document.getElementById("setup-session-name").focus(); return; }
  if (!order.length) { showToast("Please select at least one exercise.", true); return; }

  showLoading("Creating session…");
  try {
    const resp = await fetch("/api/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_name:   name,
        exercise_order: order,
      }),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "Failed to create session");

    state.sessionId     = data.session_id;
    state.isFacilitator = true;

    document.getElementById("created-room-code").textContent    = data.room_code;
    document.getElementById("created-session-name").textContent = name;
    showView("session-created");
  } catch (e) {
    showToast(e.message, true);
  } finally {
    hideLoading();
  }
}

function enterFacilitatorDashboard() {
  showView("facilitator");
  connectSocket(true);
  refreshArtifacts();
}

function goHome() {
  // Disconnect socket if active
  if (state.socket) {
    state.socket.disconnect();
    state.socket = null;
  }
  // Reset session state
  state.sessionId     = null;
  state.sessionData   = null;
  state.displayName   = null;
  state.isFacilitator = false;
  hideLoading();
  showView("landing");
}

// ── Participant join ───────────────────────────────────────────────────────────
function joinSession() {
  const code = document.getElementById("join-room-code").value.trim().toUpperCase();
  if (!code || code.length !== 6) { showToast("Enter the 6-character room code.", true); return; }

  const name = state.displayName || document.getElementById("join-display-name").value.trim();
  if (!name) { showToast("Enter your display name.", true); return; }
  state.displayName = name;
  state.displayRole = document.getElementById("join-role")?.value.trim() || "";

  showLoading("Joining…");
  fetch(`/api/sessions/${code}`)
    .then(r => {
      if (!r.ok) throw new Error("Room code not found.");
      return r.json();
    })
    .then(s => {
      state.sessionId = s.session_id;
      showView("participant");
      connectSocket(false);
    })
    .catch(e => { showToast(e.message, true); hideLoading(); });
}

// ── Socket.IO ──────────────────────────────────────────────────────────────────
function connectSocket(isFacilitator) {
  if (state.socket) {
    state.socket.disconnect();
  }
  const socket = io();
  state.socket = socket;

  socket.on("connect", () => {
    if (isFacilitator) {
      socket.emit("facilitator_join", {
        session_id: state.sessionId,
      });
    } else {
      socket.emit("join_session", {
        session_id:   state.sessionId,
        display_name: state.displayName,
        role:         state.displayRole || "",
      });
    }
  });

  socket.on("session_state", (s) => {
    state.sessionData = s;
    hideLoading();
    if (isFacilitator) {
      renderFacilitatorDashboard(s);
    } else {
      renderParticipantView(s);
    }
  });

  socket.on("new_message", (msg) => {
    appendMessageToView(msg);
  });

  socket.on("exercise_changed", (data) => {
    updateCurrentExercise(data.exercise_meta, data.index);
    // Reload messages for new exercise from session state
    if (state.sessionData) {
      const exState = state.sessionData.exercises[data.exercise_id];
      const msgs = exState ? exState.messages : [];
      if (state.isFacilitator) {
        renderChatWindow("fac-chat-window", msgs);
        updateMessageCount("fac-msg-count", msgs.length);
      } else {
        renderChatWindow("par-chat-window", msgs);
        updateMessageCount("par-msg-count", msgs.length);
        // Hide previous summary
        document.getElementById("par-summary-banner").classList.remove("visible");
      }
    }
  });

  socket.on("summary_ready", (data) => {
    state.sessionData = state.sessionData || {};
    if (!state.sessionData.exercises) state.sessionData.exercises = {};
    if (!state.sessionData.exercises[data.exercise_id])
      state.sessionData.exercises[data.exercise_id] = {};
    state.sessionData.exercises[data.exercise_id].summary = data.summary_text;

    if (state.isFacilitator) {
      showSummaryModal(data);
      hideLoading();
      refreshArtifacts();
    } else {
      showParticipantSummary(data.summary_text);
      refreshArtifacts();  // show new artifact in participant panel
    }
  });

  socket.on("participant_joined", (data) => {
    showToast(`${data.name} joined the workshop`);
    // Update participant count in header
    if (state.sessionData) {
      if (!state.sessionData.participants) state.sessionData.participants = [];
      if (!state.sessionData.participants.find(p => p.name === data.name)) {
        state.sessionData.participants.push({ name: data.name, role: data.role || "" });
      }
      updateParticipantDisplay();
    }
  });

  socket.on("error", (data) => {
    showToast(data.message, true);
    hideLoading();
  });

  socket.on("disconnect", () => {
    showToast("Disconnected — attempting to reconnect…");
  });
}

// ── Facilitator dashboard render ───────────────────────────────────────────────
function renderFacilitatorDashboard(s) {
  // Top bar
  document.getElementById("fac-topbar-session").textContent = s.session_name;
  document.getElementById("fac-topbar-code").textContent = s.room_code;
  // Show facilitator's real name in topbar if available
  const nameEl = document.getElementById("fac-topbar-participants");
  if (nameEl && state.displayName) nameEl.title = `Facilitating as ${state.displayName}`;
  updateParticipantDisplay();

  // Exercise list in sidebar
  renderFacilitatorExerciseList(s);

  // Current exercise card
  const idx  = s.current_exercise_index;
  const exId = s.exercise_order[idx];
  const exMeta = state.exercises.find(e => e.id === exId) || {};
  renderExerciseCard(exMeta);

  // Chat messages for current exercise
  const exState  = s.exercises[exId] || {};
  const messages = exState.messages || [];
  renderChatWindow("fac-chat-window", messages);
  updateMessageCount("fac-msg-count", messages.length);

  // Control button states
  updateNavButtons(s);

  // Load any existing artifacts
  refreshArtifacts();
}

function renderFacilitatorExerciseList(s) {
  const list = document.getElementById("fac-exercise-list");
  if (!list) return;
  const idx = s.current_exercise_index;
  list.innerHTML = s.exercise_order.map((exId, i) => {
    const ex  = state.exercises.find(e => e.id === exId) || { name: exId, phase: 1 };
    const cls = i === idx ? "active" : (i < idx ? "completed" : "");
    const hasSummary = !!(s.exercises[exId] && s.exercises[exId].summary);
    return `<div class="ex-list-item ${cls}" onclick="facilitatorGoTo(${i})" title="Jump to this exercise">
      <span class="ex-list-num">${i + 1}</span>
      <span class="ex-list-name">${escHtml(ex.name)}</span>
      ${hasSummary ? '<span class="ex-list-summary-dot" title="Summary generated">✦</span>' : ""}
      <span class="phase-badge" data-phase="${ex.phase}" style="font-size:9px;padding:1px 7px;">${ex.phase}</span>
    </div>`;
  }).join("");
}

async function facilitatorGoTo(index) {
  if (!state.sessionId) return;
  if (state.sessionData && state.sessionData.current_exercise_index === index) return;
  showLoading("Switching exercise…");
  try {
    const resp = await fetch(`/api/sessions/${state.sessionId}/goto`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ index }),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "Failed");
    if (state.sessionData) state.sessionData.current_exercise_index = data.current_exercise_index;
  } catch (e) {
    showToast(e.message, true);
  } finally {
    hideLoading();
  }
}

function updateParticipantDisplay() {
  const s = state.sessionData;
  if (!s) return;
  const participants = s.participants || [];
  document.getElementById("fac-topbar-participants").textContent =
    `${participants.length} participant${participants.length !== 1 ? "s" : ""}`;

  const list = document.getElementById("fac-participant-list");
  if (list) {
    list.innerHTML = participants.map(p => `
      <div class="participant-chip">
        <span class="participant-name">${escHtml(p.name)}</span>${p.role ? `<span class="participant-role">${escHtml(p.role)}</span>` : ""}
      </div>`).join("");
  }
}

function renderExerciseCard(ex) {
  const badge = document.getElementById("fac-phase-badge");
  if (badge) {
    badge.dataset.phase  = ex.phase || 1;
    badge.textContent    = `Phase ${ex.phase || 1} — ${escHtml(ex.phase_name || "")}`;
  }
  setText("fac-exercise-title",   ex.name || "");
  setText("fac-exercise-desc",    ex.description || "");
  setText("fac-exercise-outcome", ex.desired_outcome || "");
  state.currentExerciseMeta = ex;
}

function updateNavButtons(s) {
  const idx    = s.current_exercise_index;
  const maxIdx = s.exercise_order.length - 1;
  const btnBack = document.getElementById("btn-back");
  const btnNext = document.getElementById("btn-next");
  if (btnBack) btnBack.disabled = idx <= 0;
  if (btnNext) btnNext.disabled = idx >= maxIdx;
}

// ── Participant view render ────────────────────────────────────────────────────
function renderParticipantView(s) {
  document.getElementById("par-topbar-session").textContent = s.session_name;
  document.getElementById("par-topbar-name").textContent    = state.displayName;

  const idx  = s.current_exercise_index;
  const exId = s.exercise_order[idx];
  const ex   = state.exercises.find(e => e.id === exId) || {};

  updateParticipantExercise(ex);

  const messages = (s.exercises[exId] || {}).messages || [];
  renderChatWindow("par-chat-window", messages);
  updateMessageCount("par-msg-count", messages.length);

  // If there's already a summary for this exercise, show it
  const summary = (s.exercises[exId] || {}).summary;
  if (summary) showParticipantSummary(summary);

  // Load any existing artifacts
  refreshArtifacts();
}

function updateParticipantExercise(ex) {
  const badge = document.getElementById("par-phase-badge");
  if (badge) {
    badge.dataset.phase = ex.phase || 1;
    badge.textContent   = `Phase ${ex.phase || 1} — ${escHtml(ex.phase_name || "")}`;
  }
  setText("par-exercise-title",        ex.name || "Loading…");
  setText("par-exercise-desc",         ex.description || "");
  setText("par-exercise-outcome",      ex.desired_outcome || "");
  setText("par-exercise-instructions", ex.instructions || "");
  setText("par-chat-title",            ex.name || "Chat");

  // Hide old summary when exercise changes
  const banner = document.getElementById("par-summary-banner");
  if (banner) banner.classList.remove("visible");
}

// ── Current exercise update (on exercise_changed event) ───────────────────────
function updateCurrentExercise(exMeta, idx) {
  if (state.sessionData) {
    state.sessionData.current_exercise_index = idx;
  }
  if (state.isFacilitator) {
    renderExerciseCard(exMeta);
    if (state.sessionData) {
      renderFacilitatorExerciseList(state.sessionData);
      updateNavButtons(state.sessionData);
    }
    showToast(`Moved to: ${exMeta.name}`);
  } else {
    updateParticipantExercise(exMeta);
  }
  state.currentExerciseMeta = exMeta;
}

// ── Chat ───────────────────────────────────────────────────────────────────────
function renderChatWindow(windowId, messages) {
  const win = document.getElementById(windowId);
  if (!win) return;
  if (!messages.length) {
    win.innerHTML = `<div class="chat-empty">${state.isFacilitator
      ? "No messages yet. Participants will appear here in real time."
      : "Be the first to share your thoughts!"}</div>`;
    return;
  }
  win.innerHTML = "";
  messages.forEach((msg, i) => {
    const prev = i > 0 ? messages[i - 1] : null;
    win.appendChild(buildMessageEl(msg, prev));
  });
  scrollChatToBottom(win);
}

function appendMessageToView(msg) {
  // Update session data
  if (state.sessionData && msg.exercise_id) {
    const exState = state.sessionData.exercises[msg.exercise_id];
    if (exState) exState.messages.push(msg);
  }

  // Determine which chat window(s) to update
  const winId = state.isFacilitator ? "fac-chat-window" : "par-chat-window";
  const win   = document.getElementById(winId);
  if (!win) return;

  // Only show if message belongs to current exercise
  const s    = state.sessionData;
  const exId = s ? s.exercise_order[s.current_exercise_index] : null;
  if (msg.exercise_id && exId && msg.exercise_id !== exId) return;

  // Remove "empty" placeholder
  const empty = win.querySelector(".chat-empty");
  if (empty) empty.remove();

  // Get last message for collapse logic
  const lastEl  = win.lastElementChild;
  const lastMsg = lastEl ? {
    sender:    lastEl.dataset.sender,
    timestamp: lastEl.dataset.ts,
  } : null;

  const el = buildMessageEl(msg, lastMsg);
  win.appendChild(el);
  scrollChatToBottom(win);

  // Update count
  const countId = state.isFacilitator ? "fac-msg-count" : "par-msg-count";
  const countEl = document.getElementById(countId);
  if (countEl) {
    const n = win.querySelectorAll(".message").length;
    updateMessageCount(countId, n);
  }
}

function buildMessageEl(msg, prevMsg) {
  const collapse = shouldCollapse(msg, prevMsg);
  const div = document.createElement("div");
  div.className         = `message${collapse ? " collapsed" : ""}`;
  div.dataset.sender    = msg.sender;
  div.dataset.ts        = msg.timestamp;

  div.innerHTML = `
    <div class="message-avatar">${escHtml(getInitials(msg.sender))}</div>
    <div class="message-body">
      <div class="message-header">
        <span class="message-sender">${escHtml(msg.sender)}</span>
        <span class="message-time">${formatTime(msg.timestamp)}</span>
      </div>
      <div class="message-text">${escHtml(msg.text)}</div>
    </div>`;
  return div;
}

function shouldCollapse(msg, prevMsg) {
  if (!prevMsg) return false;
  if (msg.sender !== prevMsg.sender) return false;
  // Collapse if within 2 minutes
  try {
    const d1 = new Date(prevMsg.timestamp);
    const d2 = new Date(msg.timestamp);
    return (d2 - d1) < 2 * 60 * 1000;
  } catch { return false; }
}

function scrollChatToBottom(win) {
  requestAnimationFrame(() => { win.scrollTop = win.scrollHeight; });
}

function updateMessageCount(elId, n) {
  const el = document.getElementById(elId);
  if (el) el.textContent = `${n} message${n !== 1 ? "s" : ""}`;
}

function sendMessage(role) {
  const inputId = role === "facilitator" ? "fac-chat-input" : "par-chat-input";
  const input   = document.getElementById(inputId);
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;

  const s   = state.sessionData;
  const idx = s ? s.current_exercise_index : 0;
  const exId = s ? (s.exercise_order[idx] || "") : "";

  const sender = role === "facilitator"
    ? (state.displayName || "Facilitator")
    : (state.displayName || "Participant");

  state.socket && state.socket.emit("send_message", {
    session_id:  state.sessionId,
    sender,
    text,
    exercise_id: exId,
  });
  input.value = "";
  input.style.height = "auto";
}

// ── Facilitator exercise controls ──────────────────────────────────────────────
async function facilitatorAdvance() {
  closeSummary();
  showLoading("Advancing exercise…");
  try {
    const resp = await fetch(`/api/sessions/${state.sessionId}/advance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "Failed");
    if (state.sessionData) state.sessionData.current_exercise_index = data.current_exercise_index;
  } catch (e) {
    showToast(e.message, true);
  } finally {
    hideLoading();
  }
}

async function facilitatorBack() {
  showLoading("Going back…");
  try {
    const resp = await fetch(`/api/sessions/${state.sessionId}/back`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "Failed");
    if (state.sessionData) state.sessionData.current_exercise_index = data.current_exercise_index;
  } catch (e) {
    showToast(e.message, true);
  } finally {
    hideLoading();
  }
}

async function triggerAISummary() {
  showLoading("Generating AI summary… this may take 10–20 seconds");
  try {
    const resp = await fetch(`/api/sessions/${state.sessionId}/summary`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "Failed");
    // summary_ready event will handle the rest
  } catch (e) {
    showToast(e.message, true);
    hideLoading();
  }
}

// ── Summary modal (facilitator) ────────────────────────────────────────────────
function showSummaryModal(data) {
  const ex = state.currentExerciseMeta || {};
  const badge = document.getElementById("summary-phase-badge");
  if (badge) { badge.dataset.phase = ex.phase || 1; badge.textContent = ex.phase_name || ""; }
  setText("summary-title", ex.name || "Exercise Summary");
  document.getElementById("summary-body").innerHTML = markdownToHtml(data.summary_text);
  document.getElementById("summary-overlay").classList.add("visible");
  state.summaryVisible = true;
}

function closeSummary() {
  document.getElementById("summary-overlay").classList.remove("visible");
  state.summaryVisible = false;
}

// ── Participant summary banner ─────────────────────────────────────────────────
function showParticipantSummary(summaryText) {
  const banner  = document.getElementById("par-summary-banner");
  const content = document.getElementById("par-summary-content");
  if (!banner || !content) return;
  content.innerHTML = markdownToHtml(summaryText);
  banner.classList.add("visible");
  // Scroll to summary
  requestAnimationFrame(() => { banner.scrollIntoView({ behavior: "smooth", block: "start" }); });
}

// ── Exercise panel toggle (participant) ────────────────────────────────────────
function toggleExercisePanel() {
  const panel = document.getElementById("par-exercise-panel");
  if (!panel) return;
  panel.classList.toggle("collapsed");
  panel.classList.toggle("expanded");
}

// ── Export ─────────────────────────────────────────────────────────────────────
function exportSession() {
  if (!state.sessionId) return;
  window.open(`/api/sessions/${state.sessionId}/export`, "_blank");
}

function exportChatLog() {
  if (!state.sessionId) return;
  window.open(`/api/sessions/${state.sessionId}/export-chat`, "_blank");
}

// ── Artifacts ───────────────────────────────────────────────────────────────────
async function refreshArtifacts() {
  if (!state.sessionId) return;
  try {
    const resp = await fetch(`/api/sessions/${state.sessionId}/artifacts`);
    if (!resp.ok) return;
    const artifacts = await resp.json();
    renderArtifacts(artifacts);
    renderParticipantArtifacts(artifacts);
  } catch (_) {}
}

function renderParticipantArtifacts(artifacts) {
  const container = document.getElementById("par-artifacts");
  const list = document.getElementById("par-artifact-list");
  if (!container || !list) return;
  if (!artifacts.length) {
    container.style.display = "none";
    return;
  }
  container.style.display = "block";
  const byLabel = {};
  artifacts.forEach(a => {
    if (!byLabel[a.label]) byLabel[a.label] = [];
    byLabel[a.label].push(a);
  });
  list.innerHTML = Object.entries(byLabel).map(([label, files]) => {
    const links = files.map(f =>
      `<a href="${escHtml(f.url)}" download style="color:var(--blue);text-decoration:none;font-size:11px;font-weight:600;">${f.type}</a>`
    ).join(" · ");
    return `<div style="display:flex;justify-content:space-between;align-items:center;padding:4px 0;border-bottom:1px solid var(--border);">
      <span style="font-size:12px;color:var(--text2);flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escHtml(label)}</span>
      <span style="flex-shrink:0;margin-left:8px;">${links}</span>
    </div>`;
  }).join("");
}

function renderArtifacts(artifacts) {
  const el = document.getElementById("fac-artifact-list");
  if (!el) return;
  if (!artifacts.length) {
    el.innerHTML = '<span style="color:var(--text3);">No summaries yet.</span>';
    return;
  }
  // Group by label (exercise name)
  const byLabel = {};
  artifacts.forEach(a => {
    if (!byLabel[a.label]) byLabel[a.label] = [];
    byLabel[a.label].push(a);
  });
  const rows = Object.entries(byLabel).map(([label, files]) => {
    const links = files.map(f =>
      `<a href="${escHtml(f.url)}" download style="color:var(--blue);text-decoration:none;font-size:11px;font-weight:600;">${f.type}</a>`
    ).join(" · ");
    // Use first file's filename for the delete action (deletes all files for that label)
    const delButtons = files.map(f =>
      `<button class="btn-artifact-del" onclick="deleteArtifact('${escHtml(f.filename)}')" title="Delete ${f.type}">✕</button>`
    ).join("");
    return `<div style="display:flex;justify-content:space-between;align-items:center;padding:4px 0;border-bottom:1px solid var(--border);gap:6px;">
      <span style="font-size:12px;color:var(--text2);flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${escHtml(label)}">${escHtml(label)}</span>
      <span style="flex-shrink:0;display:flex;align-items:center;gap:4px;">${links}${delButtons}</span>
    </div>`;
  }).join("");
  el.innerHTML = rows;
}

async function deleteArtifact(filename) {
  if (!state.sessionId) return;
  try {
    const resp = await fetch(`/api/sessions/${state.sessionId}/artifacts/${encodeURIComponent(filename)}`, {
      method: "DELETE",
    });
    if (!resp.ok) { const d = await resp.json(); throw new Error(d.error || "Failed"); }
    refreshArtifacts();
  } catch (e) {
    showToast(e.message, true);
  }
}

// ── Edit exercises modal ────────────────────────────────────────────────────────
let editPickerOrder = [];
let editDragSrcIdx  = null;

function openEditExercises() {
  if (!state.exercises.length || !state.sessionData) return;
  // Init from current session order
  editPickerOrder = [...(state.sessionData.exercise_order || [])];
  renderEditExercisePicker();
  document.getElementById("edit-exercises-overlay").classList.add("visible");
}

function closeEditExercises() {
  document.getElementById("edit-exercises-overlay").classList.remove("visible");
  editPickerOrder = [];
}

function renderEditExercisePicker() {
  const container = document.getElementById("edit-exercise-picker-list");
  if (!container) return;
  container.innerHTML = "";

  // Show all exercises; those in editPickerOrder are checked
  const allIds = state.exercises.map(e => e.id);
  // Build display order: editPickerOrder first (checked), then unchecked ones appended
  const unchecked = allIds.filter(id => !editPickerOrder.includes(id));
  const displayOrder = [...editPickerOrder, ...unchecked];

  displayOrder.forEach((exId, idx) => {
    const ex = state.exercises.find(e => e.id === exId);
    if (!ex) return;
    const isChecked = editPickerOrder.includes(exId);
    const item = document.createElement("div");
    item.className   = "ex-pick-item";
    item.draggable   = isChecked;
    item.dataset.idx = idx;
    item.dataset.id  = exId;
    item.innerHTML = `
      <span class="ex-pick-drag" style="${isChecked ? "" : "opacity:.2;cursor:default;"}">⠿</span>
      <input type="checkbox" id="edit-ex-${exId}" ${isChecked ? "checked" : ""}
             onchange="editExToggle('${exId}')"/>
      <label class="ex-pick-name" for="edit-ex-${exId}">${escHtml(ex.name)}</label>
      <span class="phase-badge ex-pick-phase" data-phase="${ex.phase}">${escHtml(ex.phase_name)}</span>
    `;
    if (isChecked) {
      item.addEventListener("dragstart", e => {
        editDragSrcIdx = editPickerOrder.indexOf(exId);
        item.classList.add("dragging");
        e.dataTransfer.effectAllowed = "move";
      });
      item.addEventListener("dragend", () => {
        item.classList.remove("dragging");
        editDragSrcIdx = null;
        container.querySelectorAll(".ex-pick-item").forEach(i => i.classList.remove("drag-over"));
      });
      item.addEventListener("dragover", e => {
        if (editDragSrcIdx === null) return;
        e.preventDefault();
        container.querySelectorAll(".ex-pick-item").forEach(i => i.classList.remove("drag-over"));
        item.classList.add("drag-over");
      });
      item.addEventListener("drop", e => {
        e.preventDefault();
        const targetIdx = editPickerOrder.indexOf(exId);
        if (editDragSrcIdx === null || editDragSrcIdx === targetIdx) return;
        const [moved] = editPickerOrder.splice(editDragSrcIdx, 1);
        editPickerOrder.splice(targetIdx, 0, moved);
        renderEditExercisePicker();
      });
    }
    container.appendChild(item);
  });
  updateEditPickerCount();
}

function editExToggle(exId) {
  const idx = editPickerOrder.indexOf(exId);
  if (idx === -1) {
    editPickerOrder.push(exId);
  } else {
    editPickerOrder.splice(idx, 1);
  }
  renderEditExercisePicker();
}

function editExSelectAll() {
  editPickerOrder = state.exercises.map(e => e.id);
  renderEditExercisePicker();
}

function editExDeselectAll() {
  editPickerOrder = [];
  renderEditExercisePicker();
}

function updateEditPickerCount() {
  const el = document.getElementById("edit-ex-picker-count");
  if (el) el.textContent = `${editPickerOrder.length} of ${state.exercises.length} selected`;
}

async function saveEditExercises() {
  if (!editPickerOrder.length) { showToast("Select at least one exercise.", true); return; }
  showLoading("Saving exercise list…");
  try {
    const resp = await fetch(`/api/sessions/${state.sessionId}/exercises`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ exercise_order: editPickerOrder }),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "Failed to update exercises");
    closeEditExercises();
    showToast("Exercise list updated.");
  } catch (e) {
    showToast(e.message, true);
  } finally {
    hideLoading();
  }
}

// ── Utilities (copied from Jira Dashboard app.js patterns) ────────────────────
function escHtml(s) {
  return String(s || "")
    .replace(/&/g,  "&amp;")
    .replace(/</g,  "&lt;")
    .replace(/>/g,  "&gt;")
    .replace(/"/g,  "&quot;")
    .replace(/'/g,  "&#39;");
}

function markdownToHtml(text) {
  return String(text || "")
    .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
    .replace(/\*\*(.+?)\*\*/g,"<strong>$1</strong>")
    .replace(/\*(.+?)\*/g,"<em>$1</em>")
    .replace(/^### (.+)$/gm,"<h3>$1</h3>")
    .replace(/^## (.+)$/gm,"<h3>$1</h3>")
    .replace(/^# (.+)$/gm,"<h3>$1</h3>")
    .replace(/^[-*] (.+)$/gm,"<li>$1</li>")
    .replace(/(<li>[\s\S]*?<\/li>\n?)+/g, m => `<ul>${m}</ul>`)
    .replace(/^\d+\. (.+)$/gm,"<li>$1</li>")
    .replace(/\n\n+/g,"<br/><br/>")
    .replace(/\n/g,"<br/>");
}

function getInitials(name) {
  if (!name) return "?";
  const parts = String(name).trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function formatTime(iso) {
  if (!iso) return "";
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch { return iso.slice(11, 16); }
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function showLoading(msg) {
  document.getElementById("loadingOverlay").classList.add("active");
  document.getElementById("loadingMsg").textContent = msg || "Loading…";
}

function hideLoading() {
  document.getElementById("loadingOverlay").classList.remove("active");
}

let _toastTimer = null;
function showToast(msg, isError = false) {
  const el = document.getElementById("toast");
  if (!el) return;
  clearTimeout(_toastTimer);

  // Build inner content: message text + close button for errors
  if (isError) {
    el.innerHTML = `<span class="toast-msg">${escHtml(msg)}</span><button class="toast-copy" onclick="copyToastMsg(this)" title="Copy error">&#x2398;</button><button class="toast-close" onclick="dismissToast()" title="Dismiss">&times;</button>`;
    el.className = "toast show error";
    // No auto-dismiss for errors — user must click ×
  } else {
    el.textContent = msg;
    el.className   = "toast show";
    _toastTimer = setTimeout(() => { el.classList.remove("show"); }, 3500);
  }
}

function dismissToast() {
  const el = document.getElementById("toast");
  if (el) el.classList.remove("show");
  clearTimeout(_toastTimer);
}

function copyToastMsg(btn) {
  const msgEl = btn.closest(".toast")?.querySelector(".toast-msg");
  if (!msgEl) return;
  navigator.clipboard.writeText(msgEl.textContent).then(() => {
    btn.textContent = "✓";
    setTimeout(() => { btn.innerHTML = "&#x2398;"; }, 1500);
  });
}

// Auto-resize textarea
document.addEventListener("input", e => {
  if (e.target.classList.contains("chat-input")) {
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 100) + "px";
  }
});
