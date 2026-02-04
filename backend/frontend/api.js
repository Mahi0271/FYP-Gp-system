const API_BASE = ""; // same origin

function $(id){ return document.getElementById(id); }

function getToken(){
  return localStorage.getItem("jwt_access") || "";
}
function setToken(token){
  localStorage.setItem("jwt_access", token);
}
function clearToken(){
  localStorage.removeItem("jwt_access");
  localStorage.removeItem("me_role");
  localStorage.removeItem("me_username");
  localStorage.removeItem("me_id");
}

async function apiFetch(path, opts = {}){
  const headers = opts.headers ? {...opts.headers} : {};
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
    body: hasBody ? (opts.body instanceof FormData ? opts.body : JSON.stringify(opts.body)) : undefined,
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

async function fetchMe(){
  const me = await apiFetch("/api/accounts/me/");
  localStorage.setItem("me_role", me.role || "");
  localStorage.setItem("me_username", me.username || "");
  localStorage.setItem("me_id", String(me.id ?? ""));
  return me;
}

function go(url){
  window.location.href = url;
}

function roleHome(role){
  const r = String(role || "").toUpperCase();
  if (r === "PATIENT") return "patient.html";
  if (r === "GP") return "gp.html";
  if (r === "RECEPTIONIST") return "receptionist.html";
  if (r === "PRACTICE_MANAGER") return "manager.html";
  return "index.html";
}

async function requireAuth(allowedRoles = null){
  const token = getToken();
  if (!token) go("index.html");

  let me;
  try {
    me = await fetchMe();
  } catch (e) {
    clearToken();
    go("index.html");
    return null;
  }

  if (allowedRoles && Array.isArray(allowedRoles) && allowedRoles.length) {
    const ok = allowedRoles.map(x => String(x).toUpperCase()).includes(String(me.role).toUpperCase());
    if (!ok) {
      // wrong role -> send to their own page
      go(roleHome(me.role));
      return null;
    }
  }

  return me;
}

function mountTopbar(me){
  const role = (me?.role || localStorage.getItem("me_role") || "").toUpperCase();
  const username = me?.username || localStorage.getItem("me_username") || "user";

  const roleText = role ? `${username} (${role})` : username;
  const el = $("whoami");
  if (el) el.textContent = roleText;

  const btnSwitch = $("btnSwitch");
  if (btnSwitch) btnSwitch.onclick = () => { clearToken(); go("index.html"); };

  const btnLogout = $("btnLogout");
  if (btnLogout) btnLogout.onclick = () => { clearToken(); go("index.html"); };
}
