/* =============================================
   GP Secure System — Shared Utilities
   ============================================= */

/* ---- Toast ---- */
let _toastTimer = null;
function showToast(message, kind = "ok") {
  const t = $("toast");
  if (!t) return;
  t.className = `toast ${kind}`;
  t.style.display = "flex";
  const tagEl = t.querySelector(".tag");
  const msgEl = t.querySelector(".msg");
  if (tagEl) tagEl.textContent = kind === "ok" ? "OK" : kind === "err" ? "Error" : "Notice";
  if (msgEl) msgEl.textContent = message;
  if (_toastTimer) clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => { t.style.display = "none"; }, 3200);
}

/* ---- Date helpers ---- */
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

/* ---- Security ---- */
function escapeHtml(str) {
  return String(str ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

/* ---- Badge helpers ---- */
function badgeHtml(status) {
  const s = String(status || "").toLowerCase();
  return `<span class="badge badge-${s}">${escapeHtml(status)}</span>`;
}

function entryTypeBadge(type) {
  const t = String(type || "").toLowerCase();
  return `<span class="badge badge-${t}">${escapeHtml(type)}</span>`;
}

function roleBadge(role) {
  const r = String(role || "").toLowerCase();
  return `<span class="badge badge-${r}">${escapeHtml(role)}</span>`;
}

/* ---- Sidebar navigation ---- */
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
}

/* ---- Modal helpers ---- */
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
  // Close when clicking the overlay background
  overlay.addEventListener("click", e => {
    if (e.target === overlay) closeModal(modalId);
  });
  // Close buttons inside
  overlay.querySelectorAll(".modal-close").forEach(btn => {
    btn.addEventListener("click", () => closeModal(modalId));
  });
}

/* ---- Appointments table ---- */
function renderAppointmentsTable(containerId, appts, { showPatient = false, showGp = false, actions = null } = {}) {
  const el = $(containerId);
  if (!el) return;

  if (!Array.isArray(appts) || appts.length === 0) {
    el.innerHTML = `<div class="empty-state"><div class="empty-icon">📅</div><div>No appointments found.</div></div>`;
    return;
  }

  const rows = appts.map(a => `
    <tr>
      <td>${fmtDate(a.start_time)}</td>
      ${showPatient ? `<td>Patient #${escapeHtml(String(a.patient ?? "—"))}</td>` : ""}
      ${showGp      ? `<td>GP #${escapeHtml(String(a.gp ?? "—"))}</td>` : ""}
      <td>${badgeHtml(a.status)}</td>
      <td>${escapeHtml(a.reason || "—")}</td>
      ${actions ? `<td><div class="td-actions">${actions(a)}</div></td>` : ""}
    </tr>
  `).join("");

  el.innerHTML = `
    <div class="table-wrap">
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

/* ---- Clinical entries list ---- */
function renderEntryCards(containerId, entries) {
  const el = $(containerId);
  if (!el) return;

  if (!Array.isArray(entries) || entries.length === 0) {
    el.innerHTML = `<div class="empty-state"><div class="empty-icon">📋</div><div>No clinical entries yet.</div></div>`;
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
        Added by ${escapeHtml(e.created_by_username || "unknown")} · ${fmtDate(e.created_at)}
      </div>
    </div>`).join("")}</div>`;
}

/* ---- Audit log table ---- */
function renderAuditTable(containerId, logs) {
  const el = $(containerId);
  if (!el) return;

  if (!Array.isArray(logs) || logs.length === 0) {
    el.innerHTML = `<div class="empty-state"><div class="empty-icon">🔍</div><div>No audit logs match those filters.</div></div>`;
    return;
  }

  const rows = logs.map(l => `
    <tr>
      <td>${fmtDate(l.timestamp)}</td>
      <td>${escapeHtml(l.username || "—")} ${roleBadge(l.role)}</td>
      <td><code>${escapeHtml(l.action)}</code></td>
      <td>${escapeHtml(l.object_type || "—")}</td>
      <td class="small">${escapeHtml(JSON.stringify(l.metadata || {}))}</td>
      <td class="small">${escapeHtml(l.ip_address || "—")}</td>
    </tr>`).join("");

  el.innerHTML = `
    <div class="table-wrap">
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

/* ---- MFA shared logic ---- */
async function loadMfaSection(statusId, setupAreaId, disableAreaId) {
  try {
    const me = await fetchMe();
    const enabled = me.mfa_enabled;
    if ($(statusId)) {
      $(statusId).innerHTML = enabled
        ? `<span class="badge badge-confirmed">Enabled</span>`
        : `<span class="badge badge-cancelled">Disabled</span>`;
    }
    if ($(setupAreaId))   $(setupAreaId).style.display   = enabled ? "none"  : "block";
    if ($(disableAreaId)) $(disableAreaId).style.display = enabled ? "block" : "none";
  } catch(e) {
    showToast(e.message, "err");
  }
}

function setupMfa() {
  loadMfaSection("mfaStatus", "mfaSetupArea", "mfaDisableArea");

  $("btnMfaSetup").onclick = async () => {
    try {
      const data = await apiFetch("/api/accounts/mfa/setup/", { method: "POST" });
      // Display secret in groups of 4 for easy manual entry
      $("mfaSecret").textContent = data.secret.match(/.{1,4}/g).join(" ");
      // Render QR code (white bg for maximum camera contrast)
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
