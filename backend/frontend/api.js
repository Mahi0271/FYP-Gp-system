/* =============================================
   GP Secure System — API Client  (api.js)

   This file is loaded on every page of the frontend.
   It provides:
     - JWT token storage and retrieval from localStorage
     - apiFetch()   — a wrapper around fetch() that adds auth headers,
                       serialises request bodies, and throws on errors
     - fetchMe()    — calls /api/accounts/me/ to get the current user's info
                       and caches the result in localStorage
     - requireAuth() — guards dashboard pages; redirects to login if the JWT
                       is missing or expired
     - mountSidebar() — populates the sidebar avatar/username/role and wires
                        up the logout button
     - go() / roleHome() — navigation helpers
   ============================================= */

const API_BASE = "";  // same origin — all API calls go to the Django backend

// Shorthand for document.getElementById — used throughout all HTML pages
function $(id) { return document.getElementById(id); }

/* ---- JWT Token helpers ----
   Tokens are stored in localStorage so they survive page refreshes.
   clearToken() removes everything when the user logs out or the token expires.
*/
function getToken()        { return localStorage.getItem("jwt_access")   || ""; }
function getRefreshToken() { return localStorage.getItem("jwt_refresh")  || ""; }
function setToken(access, refresh) {
  localStorage.setItem("jwt_access", access);
  if (refresh !== undefined) localStorage.setItem("jwt_refresh", refresh);
}
function clearToken() {
  // Wipe all session state so a subsequent visit starts clean
  localStorage.removeItem("jwt_access");
  localStorage.removeItem("jwt_refresh");
  localStorage.removeItem("me_role");
  localStorage.removeItem("me_username");
  localStorage.removeItem("me_id");
  localStorage.removeItem("me_mfa");
}

/* ---- Core fetch wrapper ----
   Every API call in this app goes through apiFetch().
   It automatically:
     1. Attaches the JWT access token as an Authorization: Bearer header
     2. Sets Content-Type: application/json for object bodies
     3. Parses the response as JSON (or falls back to plain text)
     4. Throws a descriptive Error for any non-2xx response
*/
async function apiFetch(path, opts = {}) {
  const headers = { ...(opts.headers || {}) };
  headers["Accept"] = "application/json";

  // Attach the stored JWT if we have one
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const hasBody = opts.body !== undefined && opts.body !== null;
  if (hasBody && !(opts.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(API_BASE + path, {
    method: opts.method || "GET",
    headers,
    // Stringify plain objects; pass FormData unchanged
    body: hasBody
      ? opts.body instanceof FormData ? opts.body : JSON.stringify(opts.body)
      : undefined,
  });

  // Try to parse the response body regardless of status code
  let data = null;
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) {
    data = await res.json().catch(() => null);
  } else {
    const txt = await res.text().catch(() => "");
    data = txt ? { detail: txt } : null;
  }

  if (!res.ok) {
    // Pull the most descriptive error message out of the response body
    const msg =
      (data && (data.detail || data.error)) ||
      (data && typeof data === "object" ? JSON.stringify(data) : "") ||
      `Request failed (${res.status})`;
    throw new Error(msg);
  }
  return data;
}

/* ---- Current user info ----
   Calls /api/accounts/me/ and caches the result in localStorage.
   Other pages read from localStorage instead of making a new request
   when they only need the role or username.
*/
async function fetchMe() {
  const me = await apiFetch("/api/accounts/me/");
  localStorage.setItem("me_role", me.role || "");
  localStorage.setItem("me_username", me.username || "");
  localStorage.setItem("me_id", String(me.id ?? ""));
  localStorage.setItem("me_mfa", me.mfa_enabled ? "1" : "0");
  return me;
}

/* ---- Navigation helpers ---- */
function go(url) { window.location.href = url; }

// Maps a user's role to their home page
function roleHome(role) {
  const r = String(role || "").toUpperCase();
  if (r === "PATIENT")          return "patient.html";
  if (r === "GP")               return "gp.html";
  if (r === "RECEPTIONIST")     return "receptionist.html";
  if (r === "PRACTICE_MANAGER") return "manager.html";
  return "index.html";
}

/* ---- Auth guard ----
   Every protected dashboard page calls requireAuth() at the top.
   If no JWT exists, or the token is invalid, the user is sent back to login.
   If allowedRoles is provided, users with the wrong role are redirected
   to their own dashboard instead of seeing an error.
*/
async function requireAuth(allowedRoles = null) {
  if (!getToken()) { go("index.html"); return null; }  // no token at all — go to login

  let me;
  try { me = await fetchMe(); }
  catch (e) { clearToken(); go("index.html"); return null; }  // token rejected by server

  if (allowedRoles && allowedRoles.length) {
    const allowed = allowedRoles.map(x => String(x).toUpperCase());
    if (!allowed.includes(String(me.role || "").toUpperCase())) {
      go(roleHome(me.role));  // wrong role — redirect to their own page
      return null;
    }
  }
  return me;
}

/* ---- Sidebar population ----
   Fills in the avatar initial, username, and role label in the sidebar.
   Also wires up the logout button so it blacklists the refresh token
   on the server before clearing local storage.
*/
function mountSidebar(me) {
  const username = me?.username || localStorage.getItem("me_username") || "user";
  const role     = me?.role     || localStorage.getItem("me_role")     || "";

  // Avatar shows the first letter of the username as a coloured circle
  const avatarEl = $("sidebarAvatar");
  if (avatarEl) avatarEl.textContent = username.charAt(0).toUpperCase();

  const usernameEl = $("sidebarUsername");
  if (usernameEl) usernameEl.textContent = username;

  // Display role in a friendly format: "PRACTICE_MANAGER" → "practice manager"
  const roleEl = $("sidebarRole");
  if (roleEl) roleEl.textContent = role.replace("_", " ").toLowerCase();

  const logoutBtn = $("btnLogout");
  if (logoutBtn) logoutBtn.onclick = async () => {
    const refresh = getRefreshToken();
    if (refresh) {
      // Tell the server to blacklist this refresh token so it can't be reused
      try { await apiFetch("/api/accounts/logout/", { method: "POST", body: { refresh } }); }
      catch (_) { /* blacklist failed — clear locally anyway so the user is still logged out */ }
    }
    clearToken();
    go("index.html");
  };

  // Wire up theme toggle and sidebar collapse (defined in common.js)
  if (typeof mountShell === "function") mountShell();
}
