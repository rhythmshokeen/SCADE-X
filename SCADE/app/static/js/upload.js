const FIELDS = [
  { key: "case_id",     label: "Case ID",     required: true,  hint: "Purchase order number" },
  { key: "activity",    label: "Activity",    required: true,  hint: "Event or step name" },
  { key: "timestamp",   label: "Timestamp",   required: true,  hint: "When the step happened" },
  { key: "user",        label: "User",        required: false, hint: "Who performed the step" },
  { key: "amount",      label: "Amount",      required: false, hint: "Monetary value" },
  { key: "supplier_id", label: "Supplier ID", required: false, hint: "Vendor or supplier code" },
];

let detectedColumns  = [];
let suggestedMapping = {};
let filePreview      = [];

// ── Drag & drop ─────────────────────────────────────────────
const zone = document.getElementById("drop-zone");
zone.addEventListener("dragover",  e => { e.preventDefault(); zone.classList.add("drag-over"); });
zone.addEventListener("dragleave", ()  => zone.classList.remove("drag-over"));
zone.addEventListener("drop",      e  => {
  e.preventDefault();
  zone.classList.remove("drag-over");
  const f = e.dataTransfer.files[0];
  if (f) handleFile(f);
});

// ── File selected ────────────────────────────────────────────
async function handleFile(file) {
  if (!file) return;
  zone.classList.add("uploading");
  zone.querySelector(".drop-label").textContent = `Uploading ${file.name}…`;

  const form = new FormData();
  form.append("file", file);
  const res  = await fetch("/api/upload", { method: "POST", body: form });
  const data = await res.json();
  zone.classList.remove("uploading");

  if (data.error) {
    zone.querySelector(".drop-label").textContent = `Error: ${data.error}`;
    zone.classList.add("drop-error");
    return;
  }

  detectedColumns  = data.columns;
  suggestedMapping = data.suggested_map;
  filePreview      = data.preview;

  document.getElementById("file-info").style.display = "flex";
  document.getElementById("file-name").textContent   = `✓  ${file.name}`;
  document.getElementById("file-rows").textContent   = `${data.row_count.toLocaleString()} rows · ${data.columns.length} columns`;
  zone.querySelector(".drop-label").textContent = "File loaded — map your columns below";
  zone.querySelector(".drop-sub").textContent   = "Click to replace file";

  renderMapping();
  renderPreview();
  document.getElementById("mapping-section").style.display = "block";
  document.getElementById("mapping-section").scrollIntoView({ behavior: "smooth", block: "start" });
}

// ── Column mapping UI ─────────────────────────────────────────
function renderMapping() {
  const grid = document.getElementById("mapping-grid");
  grid.innerHTML = "";
  FIELDS.forEach(field => {
    const suggested = suggestedMapping[field.key] || "";
    const options = detectedColumns.map(c =>
      `<option value="${esc(c)}"${c === suggested ? " selected" : ""}>${esc(c)}</option>`
    ).join("");
    grid.innerHTML += `
      <div class="map-row">
        <div class="map-field">
          <span class="map-label">${field.label}
            ${field.required
              ? '<span class="req">required</span>'
              : '<span class="opt">optional</span>'}
          </span>
          <span class="map-hint">${field.hint}</span>
        </div>
        <div class="map-arrow">→</div>
        <select class="map-select" id="map-${field.key}">
          ${field.required ? "" : '<option value="">— not in my file —</option>'}
          ${options}
        </select>
        <span class="map-detected" id="detect-${field.key}">${suggested ? "✓ auto-detected" : ""}</span>
      </div>`;
  });
}

function renderPreview() {
  if (!filePreview.length) return;
  const cols = Object.keys(filePreview[0]);
  let html = `<table class="cases-table"><thead><tr>${cols.map(c=>`<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>`;
  filePreview.forEach(row => {
    html += `<tr>${cols.map(c=>`<td>${esc(String(row[c]??''))}</td>`).join("")}</tr>`;
  });
  html += "</tbody></table>";
  document.getElementById("preview-table").innerHTML = html;
}

// ── Run analysis ──────────────────────────────────────────────
async function runAnalysis() {
  const mapping = {};
  let valid = true;
  FIELDS.forEach(field => {
    const sel = document.getElementById(`map-${field.key}`);
    const val = sel ? sel.value : "";
    if (field.required && !val) { sel.style.borderColor = "var(--red)"; valid = false; }
    else { if (sel) sel.style.borderColor = ""; if (val) mapping[field.key] = val; }
  });
  if (!valid) {
    document.querySelector(".section-sub").textContent = "⚠ Please map all required fields before running.";
    return;
  }

  document.getElementById("mapping-section").style.display  = "none";
  document.getElementById("progress-section").style.display = "block";

  const steps = [
    "Ingesting your data…",
    "Learning the normal process…",
    "Scoring all cases…",
    "Mapping anomaly patterns…",
    "Finishing up…",
  ];
  let i = 0;
  const label  = document.getElementById("progress-label");
  const ticker = setInterval(() => { if (i < steps.length-1) label.textContent = steps[++i]; }, 4000);

  const res  = await fetch("/api/configure", {
    method: "POST", headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ mapping }),
  });
  clearInterval(ticker);
  const data = await res.json();

  if (data.error) {
    document.getElementById("progress-section").style.display = "none";
    document.getElementById("mapping-section").style.display  = "block";
    document.querySelector(".section-sub").textContent = `⚠ ${data.error}`;
    return;
  }
  label.textContent = "Done! Redirecting to dashboard…";
  setTimeout(() => window.location = "/", 1200);
}

// ── Security log upload ───────────────────────────────────────
async function handleSecurityFile(file) {
  if (!file) return;
  const status   = document.getElementById("sec-status");
  const filename = document.getElementById("sec-filename");
  status.textContent = "Uploading…";
  filename.textContent = file.name;

  const form = new FormData();
  form.append("file", file);
  const res  = await fetch("/api/upload-security", { method: "POST", body: form });
  const data = await res.json();

  if (data.error) {
    status.style.color   = "var(--red)";
    status.textContent   = `Error: ${data.error}`;
    filename.textContent = "Upload failed";
    return;
  }
  status.style.color   = "var(--green)";
  status.textContent   = `✓ ${data.row_count.toLocaleString()} security events loaded`;
}

const esc = s => String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
