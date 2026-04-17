/* =============================================
   GP Secure System — Shared Utilities
   ============================================= */

/* ---- Icon library (Lucide-inspired SVG paths) ---- */
const ICONS = {
  dashboard:  '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>',
  calendar:   '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
  record:     '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
  user:       '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
  users:      '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
  audit:      '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>',
  idcard:     '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="M15 8h3"/><path d="M15 12h3"/><path d="M7 16h10"/></svg>',
  close:      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
  moon:       '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
  sun:        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><line x1="12" y1="2" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="22"/><line x1="4.22" y1="4.22" x2="6.34" y2="6.34"/><line x1="17.66" y1="17.66" x2="19.78" y2="19.78"/><line x1="2" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="22" y2="12"/><line x1="4.22" y1="19.78" x2="6.34" y2="17.66"/><line x1="17.66" y1="6.34" x2="19.78" y2="4.22"/></svg>',
  menu:       '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>',
  sidebar:    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/></svg>',
  refresh:    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>',
  plus:       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
  logout:     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>',
  shield:     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
  lock:       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
  check:      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
  info:       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
  warning:    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
  trendUp:    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
  heart:      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>',
  activity:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
  clock:      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
  search:     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
  copy:       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
  qr:         '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><line x1="14" y1="14" x2="14" y2="21"/><line x1="17" y1="14" x2="17" y2="17"/><line x1="14" y1="17" x2="17" y2="17"/><line x1="20" y1="17" x2="20" y2="21"/><line x1="17" y1="21" x2="21" y2="21"/></svg>',
  arrowLeft:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>',
  arrowRight: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
  mail:       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>',
  bell:       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>',
};

function icon(name, sizePx) {
  const svg = ICONS[name] || "";
  if (!sizePx) return svg;
  return svg.replace(/width="\d+"/, `width="${sizePx}"`).replace(/height="\d+"/, `height="${sizePx}"`);
}

/* =============================================
   Theme handling
   ============================================= */
function initTheme() {
  const stored = localStorage.getItem("theme");
  const prefersLight = window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches;
  const theme = stored || (prefersLight ? "light" : "dark");
  document.documentElement.setAttribute("data-theme", theme);
}
function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "dark";
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("theme", next);
}
initTheme();

/* =============================================
   Toast
   ============================================= */
let _toastTimer = null;
function showToast(message, kind = "ok") {
  const t = $("toast");
  if (!t) return;
  t.className = `toast ${kind} show`;
  const tagEl = t.querySelector(".tag");
  const msgEl = t.querySelector(".msg");
  if (tagEl) tagEl.textContent = kind === "ok" ? "Success" : kind === "err" ? "Error" : "Notice";
  if (msgEl) msgEl.textContent = message;
  if (_toastTimer) clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => { t.classList.remove("show"); }, 3600);
}

/* =============================================
   Date helpers
   ============================================= */
function fmtDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleString(undefined, {
    day: "2-digit", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit"
  });
}
function fmtDateOnly(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleDateString(undefined, { day: "2-digit", month: "short", year: "numeric" });
}
function fmtTime(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}
function todayISO() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`;
}

/* =============================================
   Security
   ============================================= */
function escapeHtml(str) {
  return String(str ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

/* =============================================
   Badge helpers
   ============================================= */
function badgeHtml(status) {
  const s = String(status || "").toLowerCase();
  const label = String(status || "").charAt(0) + String(status || "").slice(1).toLowerCase();
  return `<span class="badge badge-${s}">${escapeHtml(label)}</span>`;
}
function entryTypeBadge(type) {
  const t = String(type || "").toLowerCase();
  const label = t.charAt(0).toUpperCase() + t.slice(1);
  return `<span class="badge badge-${t}">${escapeHtml(label)}</span>`;
}
function roleBadge(role) {
  const r = String(role || "").toLowerCase();
  const label = String(role || "").replace("_", " ").toLowerCase().replace(/\b\w/g, c => c.toUpperCase());
  return `<span class="badge badge-${r}">${escapeHtml(label)}</span>`;
}

/* =============================================
   Navigation (section switching with topbar title sync)
   ============================================= */
const SECTION_TITLES = {
  dashboard:   { title: "Overview",        sub: "A summary of your activity." },
  appointments:{ title: "Appointments",    sub: "Manage your bookings and schedule." },
  record:      { title: "Medical Record",  sub: "Your clinical notes, diagnoses, and prescriptions." },
  patients:    { title: "Patients",        sub: "Manage patient records and details." },
  audits:      { title: "Audit Logs",      sub: "Review every privileged action in the system." },
  account:     { title: "Account",         sub: "Security and profile settings." },
};

function initNav(defaultSection) {
  const links = document.querySelectorAll(".nav-link[data-section]");
  links.forEach(link => {
    link.addEventListener("click", e => {
      e.preventDefault();
      showSection(link.dataset.section);
    });
  });
  showSection(defaultSection || links[0]?.dataset.section || "");
}

function showSection(name) {
  document.querySelectorAll(".section").forEach(s => s.classList.remove("active"));
  document.querySelectorAll(".nav-link").forEach(l => l.classList.remove("active"));

  const section = document.getElementById(`section-${name}`);
  if (section) section.classList.add("active");

  const link = document.querySelector(`.nav-link[data-section="${name}"]`);
  if (link) link.classList.add("active");

  // Update topbar title
  const meta = SECTION_TITLES[name] || {};
  const titleEl = $("topbarTitle");
  if (titleEl && meta.title) titleEl.textContent = meta.title;

  // Close mobile sidebar on navigation
  document.querySelector(".app")?.classList.remove("sidebar-open");
}

/* =============================================
   Modal helpers
   ============================================= */
function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add("open");
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove("open");
}
function initModalClose(modalId) {
  const overlay = document.getElementById(modalId);
  if (!overlay) return;
  overlay.addEventListener("click", e => {
    if (e.target === overlay) closeModal(modalId);
  });
  overlay.querySelectorAll(".modal-close").forEach(btn => {
    btn.addEventListener("click", () => closeModal(modalId));
  });
}

// Global Esc key closes any open modal
document.addEventListener("keydown", e => {
  if (e.key === "Escape") {
    document.querySelectorAll(".modal-overlay.open").forEach(m => m.classList.remove("open"));
  }
});

/* =============================================
   App shell wire-up (theme toggle, sidebar toggle)
   ============================================= */
function mountShell() {
  const themeBtn = $("btnTheme");
  if (themeBtn) themeBtn.onclick = toggleTheme;

  const menuBtn = $("btnMenu");
  if (menuBtn) {
    menuBtn.onclick = () => {
      const app = document.querySelector(".app");
      if (window.innerWidth <= 900) app?.classList.toggle("sidebar-open");
      else app?.classList.toggle("sidebar-collapsed");
    };
  }
}

/* =============================================
   Empty state helper
   ============================================= */
function emptyState(iconName, title, subtitle) {
  return `
    <div class="empty-state">
      <div class="empty-icon">${icon(iconName || "info", 20)}</div>
      <div class="empty-title">${escapeHtml(title || "Nothing here yet")}</div>
      ${subtitle ? `<p>${escapeHtml(subtitle)}</p>` : ""}
    </div>`;
}

/* =============================================
   Appointments table
   ============================================= */
function renderAppointmentsTable(containerId, appts, { showPatient = false, showGp = false, actions = null, compact = false } = {}) {
  const el = $(containerId);
  if (!el) return;

  if (!Array.isArray(appts) || appts.length === 0) {
    el.innerHTML = emptyState("calendar", "No appointments", "There's nothing scheduled in this view yet.");
    return;
  }

  const rows = appts.map(a => `
    <tr>
      <td>
        <div class="td-primary">${fmtDateOnly(a.start_time)}</div>
        <div class="td-muted small">${fmtTime(a.start_time)}</div>
      </td>
      ${showPatient ? `<td><span class="avatar-sm">P</span>Patient #${escapeHtml(String(a.patient ?? "—"))}</td>` : ""}
      ${showGp      ? `<td><span class="avatar-sm">G</span>GP #${escapeHtml(String(a.gp ?? "—"))}</td>` : ""}
      <td>${badgeHtml(a.status)}</td>
      <td class="td-muted">${escapeHtml(a.reason || "—")}</td>
      ${actions ? `<td><div class="td-actions">${actions(a)}</div></td>` : ""}
    </tr>
  `).join("");

  el.innerHTML = `
    <div class="table-wrap${compact ? "" : " scroll"}">
      <table>
        <thead>
          <tr>
            <th>Date &amp; Time</th>
            ${showPatient ? "<th>Patient</th>" : ""}
            ${showGp      ? "<th>GP</th>" : ""}
            <th>Status</th>
            <th>Reason</th>
            ${actions ? "<th>Actions</th>" : ""}
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}

/* =============================================
   Clinical entries list
   ============================================= */
function renderEntryCards(containerId, entries) {
  const el = $(containerId);
  if (!el) return;

  if (!Array.isArray(entries) || entries.length === 0) {
    el.innerHTML = emptyState("record", "No clinical entries", "Your medical record is empty. Entries added by your GP will appear here.");
    return;
  }

  el.innerHTML = `<div class="entry-list">${entries.map(e => `
    <div class="entry-card">
      <div class="entry-card-header">
        ${entryTypeBadge(e.type)}
        <span class="entry-card-title">${escapeHtml(e.title || "(no title)")}</span>
      </div>
      <div class="entry-card-content">${escapeHtml(e.content || "")}</div>
      <div class="entry-card-meta">
        Added by <strong>${escapeHtml(e.created_by_username || "unknown")}</strong> · ${fmtDate(e.created_at)}
      </div>
    </div>`).join("")}</div>`;
}

/* =============================================
   Audit log table
   ============================================= */
function renderAuditTable(containerId, logs) {
  const el = $(containerId);
  if (!el) return;

  if (!Array.isArray(logs) || logs.length === 0) {
    el.innerHTML = emptyState("audit", "No audit logs", "No events match the current filters.");
    return;
  }

  const rows = logs.map(l => `
    <tr>
      <td>
        <div class="td-primary">${fmtDateOnly(l.timestamp)}</div>
        <div class="td-muted small">${fmtTime(l.timestamp)}</div>
      </td>
      <td>${escapeHtml(l.username || "—")} ${roleBadge(l.role)}</td>
      <td><code style="font-size:12px;color:var(--brand);background:var(--brand-bg);padding:2px 7px;border-radius:5px;">${escapeHtml(l.action)}</code></td>
      <td class="td-muted">${escapeHtml(l.object_type || "—")}</td>
      <td class="small td-muted" style="max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(JSON.stringify(l.metadata || {}))}</td>
      <td class="small td-muted">${escapeHtml(l.ip_address || "—")}</td>
    </tr>`).join("");

  el.innerHTML = `
    <div class="table-wrap scroll">
      <table>
        <thead>
          <tr>
            <th>Timestamp</th><th>User</th><th>Action</th><th>Object</th><th>Metadata</th><th>IP</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}

/* =============================================
   MFA shared logic
   ============================================= */
async function loadMfaSection(statusId, setupAreaId, disableAreaId) {
  try {
    const me = await fetchMe();
    const enabled = me.mfa_enabled;
    if ($(statusId)) {
      $(statusId).innerHTML = enabled
        ? `<span class="badge badge-enabled">Enabled</span>`
        : `<span class="badge badge-disabled">Disabled</span>`;
    }
    if ($(setupAreaId))   $(setupAreaId).style.display   = enabled ? "none"  : "block";
    if ($(disableAreaId)) $(disableAreaId).style.display = enabled ? "flex"  : "none";
  } catch(e) {
    showToast(e.message, "err");
  }
}

function setupMfa() {
  loadMfaSection("mfaStatus", "mfaSetupArea", "mfaDisableArea");

  $("btnMfaSetup").onclick = async () => {
    try {
      const data = await apiFetch("/api/accounts/mfa/setup/", { method: "POST" });
      $("mfaSecret").textContent = data.secret.match(/.{1,4}/g).join(" ");
      const container = $("mfaQrContainer");
      container.innerHTML = "";
      new QRCode(container, {
        text: data.otpauth_url,
        width: 200,
        height: 200,
        colorDark: "#000000",
        colorLight: "#ffffff",
      });
      $("mfaSetupResult").style.display = "flex";
    } catch(e) { showToast(e.message, "err"); }
  };

  $("btnCopySecret").onclick = () => {
    const raw = $("mfaSecret").textContent.replaceAll(" ", "");
    navigator.clipboard.writeText(raw)
      .then(() => showToast("Secret key copied to clipboard.", "ok"))
      .catch(() => showToast("Copy failed — select the key and copy manually.", "warn"));
  };

  $("btnMfaEnable").onclick = async () => {
    const code = $("mfaEnableCode").value.trim();
    if (!code) { showToast("Enter the 6-digit code from your app.", "warn"); return; }
    try {
      await apiFetch("/api/accounts/mfa/enable/", { method: "POST", body: { code } });
      showToast("MFA enabled successfully!", "ok");
      $("mfaSetupResult").style.display = "none";
      $("mfaEnableCode").value = "";
      loadMfaSection("mfaStatus", "mfaSetupArea", "mfaDisableArea");
    } catch(e) { showToast(e.message, "err"); }
  };

  $("btnMfaDisable").onclick = async () => {
    const code = $("mfaDisableCode").value.trim();
    if (!code) { showToast("Enter your authenticator code.", "warn"); return; }
    try {
      await apiFetch("/api/accounts/mfa/disable/", { method: "POST", body: { code } });
      showToast("MFA has been disabled.", "ok");
      $("mfaDisableCode").value = "";
      loadMfaSection("mfaStatus", "mfaSetupArea", "mfaDisableArea");
    } catch(e) { showToast(e.message, "err"); }
  };
}
