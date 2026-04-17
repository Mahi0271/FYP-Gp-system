/* =============================================
   GP Secure System — API Client
   ============================================= */

const API_BASE = "";

function $(id) { return document.getElementById(id); }

/* ---- Token helpers ---- */
function getToken()        { return localStorage.getItem("jwt_access")   || ""; }
function getRefreshToken() { return localStorage.getItem("jwt_refresh")  || ""; }
function setToken(access, refresh) {
  localStorage.setItem("jwt_access", access);
  if (refresh !== undefined) localStorage.setItem("jwt_refresh", refresh);
}
function clearToken() {
  localStorage.removeItem("jwt_access");
  localStorage.removeItem("jwt_refresh");
  localStorage.removeItem("me_role");
  localStorage.removeItem("me_username");
  localStorage.removeItem("me_id");
  localStorage.removeItem("me_mfa");
}

/* ---- Core fetch ---- */
async function apiFetch(path, opts = {}) {
  const headers = { ...(opts.headers || {}) };
  headers["Accept"] = "application/json";

  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const hasBody = opts.body !== undefined && opts.body !== null;
  if (hasBody && !(opts.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(API_BASE + path, {
    method: opts.method || "GET",
    headers,
    body: hasBody
      ? opts.body instanceof FormData ? opts.body : JSON.stringify(opts.body)
      : undefined,
  });

  let data = null;
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) {
    data = await res.json().catch(() => null);
  } else {
    const txt = await res.text().catch(() => "");
    data = txt ? { detail: txt } : null;
  }

  if (!res.ok) {
    const msg =
      (data && (data.detail || data.error)) ||
      (data && typeof data === "object" ? JSON.stringify(data) : "") ||
      `Request failed (${res.status})`;
    throw new Error(msg);
  }
  return data;
}

/* ---- /me ---- */
async function fetchMe() {
  const me = await apiFetch("/api/accounts/me/");
  localStorage.setItem("me_role", me.role || "");
  localStorage.setItem("me_username", me.username || "");
  localStorage.setItem("me_id", String(me.id ?? ""));
  localStorage.setItem("me_mfa", me.mfa_enabled ? "1" : "0");
  return me;
}

/* ---- Navigation ---- */
function go(url) { window.location.href = url; }

function roleHome(role) {
  const r = String(role || "").toUpperCase();
  if (r === "PATIENT")          return "patient.html";
  if (r === "GP")               return "gp.html";
  if (r === "RECEPTIONIST")     return "receptionist.html";
  if (r === "PRACTICE_MANAGER") return "manager.html";
  return "index.html";
}

/* ---- Auth guard ---- */
async function requireAuth(allowedRoles = null) {
  if (!getToken()) { go("index.html"); return null; }

  let me;
  try { me = await fetchMe(); }
  catch (e) { clearToken(); go("index.html"); return null; }

  if (allowedRoles && allowedRoles.length) {
    const allowed = allowedRoles.map(x => String(x).toUpperCase());
    if (!allowed.includes(String(me.role || "").toUpperCase())) {
      go(roleHome(me.role));
      return null;
    }
  }
  return me;
}

/* ---- Sidebar user block ---- */
function mountSidebar(me) {
  const username = me?.username || localStorage.getItem("me_username") || "user";
  const role     = me?.role     || localStorage.getItem("me_role")     || "";

  const avatarEl = $("sidebarAvatar");
  if (avatarEl) avatarEl.textContent = username.charAt(0).toUpperCase();

  const usernameEl = $("sidebarUsername");
  if (usernameEl) usernameEl.textContent = username;

  const roleEl = $("sidebarRole");
  if (roleEl) roleEl.textContent = role.replace("_", " ").toLowerCase();

  const logoutBtn = $("btnLogout");
  if (logoutBtn) logoutBtn.onclick = async () => {
    const refresh = getRefreshToken();
    if (refresh) {
      try { await apiFetch("/api/accounts/logout/", { method: "POST", body: { refresh } }); }
      catch (_) { /* blacklist failed — clear locally anyway */ }
    }
    clearToken();
    go("index.html");
  };

  // Hook up shell controls defined in common.js
  if (typeof mountShell === "function") mountShell();
}
