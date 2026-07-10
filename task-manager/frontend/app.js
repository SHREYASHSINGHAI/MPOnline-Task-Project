/* ================================================================
   app.js  --  Task Manager Frontend  |  Vanilla JavaScript
   Responsibilities:
     - Load tasks on startup
     - CRUD operations via Fetch API → Flask backend
     - Search / filter logic
     - Modal handling (add, edit, delete)
     - Dashboard statistics updates
     - Toast notifications
     - Skeleton loading states
   ================================================================ */

"use strict";

// ── Configuration ─────────────────────────────────────────────
const API_BASE = "http://localhost:5000/api";

// ── State ─────────────────────────────────────────────────────
let tasks         = [];        // current task list shown
let editMode      = false;     // true → PUT, false → POST
let deleteTaskId  = null;      // id pending deletion

// ── DOM references ────────────────────────────────────────────
const tbody        = document.getElementById("tbody");
const tblCount     = document.getElementById("tbl-count");
const inpSearch    = document.getElementById("inp-search");
const selStatus    = document.getElementById("sel-status");

// stats
const sTotal   = document.getElementById("s-total");
const sDone    = document.getElementById("s-done");
const sPending = document.getElementById("s-pending");
const sEmp     = document.getElementById("s-emp");

// form modal
const formOverlay  = document.getElementById("form-overlay");
const modalTitle   = document.getElementById("modal-title");
const taskForm     = document.getElementById("task-form");
const fId          = document.getElementById("f-id");
const fEmp         = document.getElementById("f-emp");
const fTitle       = document.getElementById("f-title");
const fDone        = document.getElementById("f-done");
const togLabel     = document.getElementById("tog-label");
const btnSubmit    = document.getElementById("btn-form-submit");
const errEmp       = document.getElementById("err-emp");
const errTitle     = document.getElementById("err-title");

// delete modal
const delOverlay   = document.getElementById("del-overlay");
const btnDelConf   = document.getElementById("btn-del-confirm");


// ═══════════════════════════════════════════════════════════════
//  UTILITIES
// ═══════════════════════════════════════════════════════════════

/** Escape HTML to prevent XSS */
function esc(str) {
  return String(str)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

/** Format a timestamp string to readable date */
function fmtDate(dt) {
  if (!dt) return "—";
  return new Date(dt).toLocaleDateString("en-IN", {
    day: "2-digit", month: "short", year: "numeric",
  });
}

/** Get initials from a full name (up to 2 letters) */
function initials(name) {
  return name.trim().split(/\s+/).slice(0, 2).map(w => w[0].toUpperCase()).join("");
}

/** Deterministic avatar colour from name */
const AVATAR_PALETTES = [
  { bg: "#7c3aed", border: "#5b21b6" },
  { bg: "#0891b2", border: "#0e7490" },
  { bg: "#059669", border: "#065f46" },
  { bg: "#d97706", border: "#92400e" },
  { bg: "#e11d48", border: "#9f1239" },
  { bg: "#2563eb", border: "#1e40af" },
  { bg: "#7c3aed", border: "#5b21b6" },
];
function avatarColor(name) {
  let h = 0;
  for (const c of name) h = (h << 5) - h + c.charCodeAt(0);
  return AVATAR_PALETTES[Math.abs(h) % AVATAR_PALETTES.length];
}

/** Animate a counter from 0 to target */
function animateNum(el, target) {
  let cur = 0;
  const step = Math.max(1, Math.ceil(target / 30));
  const t = setInterval(() => {
    cur = Math.min(cur + step, target);
    el.textContent = cur;
    if (cur >= target) clearInterval(t);
  }, 28);
}


// ═══════════════════════════════════════════════════════════════
//  TOAST NOTIFICATIONS
// ═══════════════════════════════════════════════════════════════

const ICONS = { success: "✅", error: "❌", info: "ℹ️" };

function toast(msg, type = "success") {
  const box = document.getElementById("toasts");
  const el  = document.createElement("div");
  el.className = `toast ${type}`;
  el.innerHTML = `<span class="toast-ico">${ICONS[type]}</span><span>${msg}</span>`;
  box.appendChild(el);
  setTimeout(() => {
    el.classList.add("out");
    el.addEventListener("animationend", () => el.remove(), { once: true });
  }, 3400);
}


// ═══════════════════════════════════════════════════════════════
//  STATS
// ═══════════════════════════════════════════════════════════════

async function loadStats() {
  try {
    const res  = await fetch(`${API_BASE}/stats`);
    const json = await res.json();
    if (!json.success) return;
    const { total, completed, pending, employees } = json.data;
    animateNum(sTotal,   total);
    animateNum(sDone,    completed);
    animateNum(sPending, pending);
    animateNum(sEmp,     employees);
  } catch (_) { /* ignore */ }
}


// ═══════════════════════════════════════════════════════════════
//  FETCH & RENDER TASKS
// ═══════════════════════════════════════════════════════════════

async function loadTasks() {
  renderSkeleton();
  const search = inpSearch.value.trim();
  const status = selStatus.value;

  const p = new URLSearchParams();
  if (search) p.set("search",    search);
  if (status) p.set("completed", status);

  try {
    const res  = await fetch(`${API_BASE}/tasks?${p}`);
    const json = await res.json();
    if (!json.success) throw new Error(json.error || "Server error");
    tasks = json.data;
    renderTable(tasks);
  } catch (e) {
    tbody.innerHTML = `
      <tr><td colspan="6">
        <div class="empty">
          <div class="big">⚠️</div>
          <p><strong>Cannot connect to Flask server.</strong><br/>
          Make sure <code>python app.py</code> is running on port 5000.<br/>
          <small style="color:var(--txt-muted)">${esc(e.message)}</small></p>
        </div>
      </td></tr>`;
    tblCount.textContent = "Error";
  }
}

function renderSkeleton() {
  tblCount.textContent = "Loading…";
  tbody.innerHTML = Array.from({ length: 6 }, () => `
    <tr>
      <td><span class="sk" style="width:32px;height:32px;border-radius:8px;display:inline-block"></span></td>
      <td><div style="display:flex;align-items:center;gap:10px">
            <span class="sk" style="width:34px;height:34px;border-radius:50%;display:inline-block"></span>
            <span class="sk" style="width:130px;height:13px;display:inline-block"></span>
          </div></td>
      <td><span class="sk" style="width:170px;height:13px;display:inline-block"></span></td>
      <td><span class="sk" style="width:82px;height:24px;border-radius:20px;display:inline-block"></span></td>
      <td><span class="sk" style="width:88px;height:13px;display:inline-block"></span></td>
      <td><div style="display:flex;justify-content:center;gap:7px">
            <span class="sk" style="width:34px;height:34px;border-radius:8px;display:inline-block"></span>
            <span class="sk" style="width:34px;height:34px;border-radius:8px;display:inline-block"></span>
            <span class="sk" style="width:34px;height:34px;border-radius:8px;display:inline-block"></span>
          </div></td>
    </tr>`).join("");
}

function renderTable(list) {
  tblCount.textContent = `${list.length} task${list.length !== 1 ? "s" : ""}`;

  if (list.length === 0) {
    tbody.innerHTML = `
      <tr><td colspan="6">
        <div class="empty">
          <div class="big">📭</div>
          <p>No tasks found.<br/>Click <strong>Add Task</strong> to create one.</p>
        </div>
      </td></tr>`;
    return;
  }

  tbody.innerHTML = list.map(t => {
    const av   = avatarColor(t.employee_name);
    const done = t.completed;
    return `
      <tr data-id="${t.task_id}">
        <td><span class="id-badge">${t.task_id}</span></td>
        <td>
          <div class="emp-cell">
            <div class="avatar" style="background:${av.bg};border-color:${av.border}">
              ${initials(t.employee_name)}
            </div>
            <span>${esc(t.employee_name)}</span>
          </div>
        </td>
        <td>${esc(t.task_title)}</td>
        <td>
          <span class="badge ${done ? "badge-done" : "badge-pending"}">
            ${done ? "✓ Done" : "⏳ Pending"}
          </span>
        </td>
        <td style="color:var(--txt-muted);font-size:.8rem">${fmtDate(t.created_at)}</td>
        <td class="act-cell">
          <div class="act-row">
            <button class="btn-icon toggle"
              title="${done ? "Mark as Pending" : "Mark as Done"}"
              aria-label="${done ? "Mark as Pending" : "Mark as Done"}"
              onclick="handleToggle(${t.task_id},${done})">
              ${done ? "↩" : "✓"}
            </button>
            <button class="btn-icon edit"
              title="Edit task" aria-label="Edit task"
              onclick="openEdit(${t.task_id})">✏️</button>
            <button class="btn-icon del"
              title="Delete task" aria-label="Delete task"
              onclick="openDelete(${t.task_id})">🗑</button>
          </div>
        </td>
      </tr>`;
  }).join("");
}


// ═══════════════════════════════════════════════════════════════
//  ADD MODAL
// ═══════════════════════════════════════════════════════════════

function openAdd() {
  editMode = false;
  modalTitle.textContent  = "Add New Task";
  btnSubmit.textContent   = "Create Task";
  taskForm.reset();
  fId.value = "";
  clearErrors();
  updateTogLabel();
  formOverlay.classList.add("open");
  setTimeout(() => fEmp.focus(), 80);
}

function closeForm() {
  formOverlay.classList.remove("open");
}


// ═══════════════════════════════════════════════════════════════
//  EDIT MODAL
// ═══════════════════════════════════════════════════════════════

function openEdit(id) {
  const task = tasks.find(t => t.task_id === id);
  if (!task) return;

  editMode = true;
  modalTitle.textContent  = "Edit Task";
  btnSubmit.textContent   = "Save Changes";
  clearErrors();

  fId.value           = task.task_id;
  fEmp.value          = task.employee_name;
  fTitle.value        = task.task_title;
  fDone.checked       = task.completed;
  updateTogLabel();

  formOverlay.classList.add("open");
  setTimeout(() => fEmp.focus(), 80);
}


// ═══════════════════════════════════════════════════════════════
//  FORM VALIDATION & SUBMIT
// ═══════════════════════════════════════════════════════════════

function clearErrors() {
  errEmp.classList.remove("show");
  errTitle.classList.remove("show");
  fEmp.style.borderColor   = "";
  fTitle.style.borderColor = "";
}

function validate() {
  let ok = true;
  clearErrors();
  if (!fEmp.value.trim()) {
    errEmp.classList.add("show"); fEmp.style.borderColor = "var(--clr-rose)"; ok = false;
  }
  if (!fTitle.value.trim()) {
    errTitle.classList.add("show"); fTitle.style.borderColor = "var(--clr-rose)"; ok = false;
  }
  return ok;
}

fDone.addEventListener("change", updateTogLabel);
function updateTogLabel() {
  togLabel.textContent = fDone.checked ? "Marked as Completed ✅" : "Mark as Pending ⏳";
}

taskForm.addEventListener("submit", async e => {
  e.preventDefault();
  if (!validate()) return;

  const payload = {
    employee_name: fEmp.value.trim(),
    task_title:    fTitle.value.trim(),
    completed:     fDone.checked,
  };

  btnSubmit.disabled    = true;
  btnSubmit.innerHTML   = '<span class="spinner"></span>';

  try {
    let url    = `${API_BASE}/tasks`;
    let method = "POST";
    if (editMode) { url = `${API_BASE}/tasks/${fId.value}`; method = "PUT"; }

    const res  = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const json = await res.json();
    if (!json.success) throw new Error(json.error || "Request failed");

    toast(editMode ? "Task updated successfully!" : "Task created successfully!");
    closeForm();
    await Promise.all([loadTasks(), loadStats()]);
  } catch (err) {
    toast(err.message || "Something went wrong.", "error");
  } finally {
    btnSubmit.disabled  = false;
    btnSubmit.textContent = editMode ? "Save Changes" : "Create Task";
  }
});


// ═══════════════════════════════════════════════════════════════
//  QUICK TOGGLE COMPLETION
// ═══════════════════════════════════════════════════════════════

async function handleToggle(id, current) {
  try {
    const res  = await fetch(`${API_BASE}/tasks/${id}`, {
      method:  "PUT",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ completed: !current }),
    });
    const json = await res.json();
    if (!json.success) throw new Error(json.error);
    toast(
      !current ? "Task marked as completed ✅" : "Task marked as pending ⏳",
      "info"
    );
    await Promise.all([loadTasks(), loadStats()]);
  } catch (err) {
    toast(err.message || "Update failed.", "error");
  }
}


// ═══════════════════════════════════════════════════════════════
//  DELETE
// ═══════════════════════════════════════════════════════════════

function openDelete(id) {
  deleteTaskId = id;
  delOverlay.classList.add("open");
}

function closeDelete() {
  delOverlay.classList.remove("open");
  deleteTaskId = null;
}

btnDelConf.addEventListener("click", async () => {
  if (!deleteTaskId) return;
  btnDelConf.disabled   = true;
  btnDelConf.innerHTML  = '<span class="spinner"></span>';

  try {
    const res  = await fetch(`${API_BASE}/tasks/${deleteTaskId}`, { method: "DELETE" });
    const json = await res.json();
    if (!json.success) throw new Error(json.error);
    toast("Task deleted.", "info");
    closeDelete();
    await Promise.all([loadTasks(), loadStats()]);
  } catch (err) {
    toast(err.message || "Delete failed.", "error");
  } finally {
    btnDelConf.disabled     = false;
    btnDelConf.textContent  = "Delete";
  }
});


// ═══════════════════════════════════════════════════════════════
//  EVENT WIRING
// ═══════════════════════════════════════════════════════════════

// Header add button
document.getElementById("btn-open-add").addEventListener("click", openAdd);

// Form modal close
document.getElementById("btn-form-close").addEventListener("click",  closeForm);
document.getElementById("btn-form-cancel").addEventListener("click", closeForm);

// Delete modal close
document.getElementById("btn-del-cancel").addEventListener("click", closeDelete);

// Click outside modal to close
formOverlay.addEventListener("click", e => { if (e.target === formOverlay) closeForm(); });
delOverlay.addEventListener("click",  e => { if (e.target === delOverlay)  closeDelete(); });

// Escape key
document.addEventListener("keydown", e => {
  if (e.key === "Escape") {
    if (formOverlay.classList.contains("open")) closeForm();
    if (delOverlay.classList.contains("open"))  closeDelete();
  }
});

// Search (debounced 280ms)
let searchTimer;
inpSearch.addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(loadTasks, 280);
});

// Status filter
selStatus.addEventListener("change", loadTasks);


// ═══════════════════════════════════════════════════════════════
//  INIT
// ═══════════════════════════════════════════════════════════════

(async function init() {
  await Promise.all([loadStats(), loadTasks()]);
})();
