let toastTimer = null;

function showToast(message, kind="ok"){
  const t = $("toast");
  if (!t) return;
  t.className = `toast ${kind}`;
  t.style.display = "flex";
  const tag = t.querySelector(".tag");
  const msg = t.querySelector(".msg");
  if (tag) tag.textContent = kind.toUpperCase();
  if (msg) msg.textContent = message;

  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.style.display = "none"; }, 2800);
}

function fmtDate(iso){
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleString();
}

function escapeHtml(str){
  return String(str ?? "")
    .replaceAll("&","&amp;")
    .replaceAll("<","&lt;")
    .replaceAll(">","&gt;");
}

function setRawJson(detailsId, data){
  const el = $(detailsId);
  if (!el) return;
  const pre = el.querySelector("pre");
  if (pre) pre.textContent = JSON.stringify(data, null, 2);
}

function renderAppointmentsTable(containerId, appts, { showPatient=false, showGp=false, actions=null } = {}){
  const el = $(containerId);
  if (!el) return;

  if (!Array.isArray(appts) || appts.length === 0) {
    el.innerHTML = `<span class="pill">No appointments found.</span>`;
    return;
  }

  const rows = appts.map(a => {
    const actCell = actions ? actions(a) : "";
    return `
      <tr>
        <td>${a.id}</td>
        ${showPatient ? `<td>${escapeHtml(a.patient ?? a.patient_username ?? "")}</td>` : ``}
        ${showGp ? `<td>${escapeHtml(a.gp ?? a.gp_username ?? "")}</td>` : ``}
        <td>${fmtDate(a.start_time)}</td>
        <td>${fmtDate(a.end_time)}</td>
        <td>${escapeHtml(a.status)}</td>
        <td>${escapeHtml(a.reason || "")}</td>
        ${actions ? `<td>${actCell}</td>` : ``}
      </tr>
    `;
  }).join("");

  el.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>ID</th>
          ${showPatient ? `<th>Patient</th>` : ``}
          ${showGp ? `<th>GP</th>` : ``}
          <th>Start</th>
          <th>End</th>
          <th>Status</th>
          <th>Reason</th>
          ${actions ? `<th>Actions</th>` : ``}
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderAvailability(containerId, data, onPickSlot){
  const el = $(containerId);
  if (!el) return;

  const slots = (data && data.available) ? data.available : [];
  if (!slots.length) {
    el.innerHTML = `<span class="pill">No slots available for that date/GP.</span>`;
    return;
  }

  const rows = slots.slice(0, 60).map((s, idx) => `
    <tr>
      <td>${idx+1}</td>
      <td>${fmtDate(s.start_time)}</td>
      <td>${fmtDate(s.end_time)}</td>
      <td>
        <div class="actions-inline">
          <button class="btn ok" data-pick="${idx}">Select</button>
        </div>
      </td>
    </tr>
  `).join("");

  el.innerHTML = `
    <table>
      <thead><tr><th>#</th><th>Start</th><th>End</th><th></th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
    <div style="margin-top:10px" class="small">Tip: click <b>Select</b> to auto-fill the booking form.</div>
  `;

  if (typeof onPickSlot === "function") {
    el.querySelectorAll("button[data-pick]").forEach(btn => {
      btn.onclick = () => {
        const i = Number(btn.getAttribute("data-pick"));
        onPickSlot(slots[i]);
      };
    });
  }
}

function renderKeyValue(containerId, obj){
  const el = $(containerId);
  if (!el) return;
  if (!obj || typeof obj !== "object") {
    el.innerHTML = `<span class="pill">No data.</span>`;
    return;
  }
  const entries = Object.entries(obj);
  const html = entries.map(([k,v]) => `
    <tr>
      <td style="width:220px"><span class="muted">${escapeHtml(k)}</span></td>
      <td>${escapeHtml(typeof v === "object" ? JSON.stringify(v) : v)}</td>
    </tr>
  `).join("");
  el.innerHTML = `
    <table>
      <thead><tr><th>Field</th><th>Value</th></tr></thead>
      <tbody>${html}</tbody>
    </table>
  `;
}

function renderEntriesTable(containerId, entries){
  const el = $(containerId);
  if (!el) return;
  if (!Array.isArray(entries) || entries.length === 0) {
    el.innerHTML = `<span class="pill">No record entries found.</span>`;
    return;
  }

  const rows = entries.map(e => `
    <tr>
      <td>${e.id}</td>
      <td>${escapeHtml(e.type)}</td>
      <td>${escapeHtml(e.title || "")}</td>
      <td>${escapeHtml(e.content || "")}</td>
      <td>${escapeHtml(e.created_by_username || e.created_by || "")}</td>
      <td>${fmtDate(e.created_at)}</td>
    </tr>
  `).join("");

  el.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>ID</th><th>Type</th><th>Title</th><th>Content</th><th>Created by</th><th>Created</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderAuditTable(containerId, logs){
  const el = $(containerId);
  if (!el) return;

  if (!Array.isArray(logs) || logs.length === 0) {
    el.innerHTML = `<span class="pill">No audit logs match those filters.</span>`;
    return;
  }

  const rows = logs.map(l => `
    <tr>
      <td>${fmtDate(l.timestamp)}</td>
      <td>${escapeHtml(l.username)} <span class="pill">${escapeHtml(l.role)}</span></td>
      <td>${escapeHtml(l.action)}</td>
      <td>${escapeHtml(l.object_type)}</td>
      <td><span class="small">${escapeHtml(JSON.stringify(l.metadata || {}))}</span></td>
      <td><span class="small">${escapeHtml(l.ip_address || "")}</span></td>
    </tr>
  `).join("");

  el.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Time</th><th>User</th><th>Action</th><th>Object</th><th>Metadata</th><th>IP</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}
