// Order matches the normal procurement sequence
const STEP_ORDER = [
  "Create Purchase Requisition",
  "Manager Approval",
  "Send RFQ to Supplier",
  "Receive Supplier Quote",
  "Create Purchase Order",
  "Goods Receipt",
  "Invoice Verification",
  "Payment Release",
];

const STEP_DESCRIPTIONS = {
  "Create Purchase Requisition": "Internal request to purchase goods or services",
  "Manager Approval":            "Line manager or budget holder approves the request",
  "Send RFQ to Supplier":        "Request for Quotation sent to potential suppliers",
  "Receive Supplier Quote":      "Supplier submits a price quote",
  "Create Purchase Order":       "Formal purchase order issued to the supplier",
  "Goods Receipt":               "Physical goods received and logged in the warehouse",
  "Invoice Verification":        "Supplier invoice matched against PO and goods receipt",
  "Payment Release":             "Finance approves and releases payment to supplier",
};

let activityMap = {};   // { step: [alias, ...] }

// ── Boot ─────────────────────────────────────────────────────
async function load() {
  const res  = await fetch("/api/activity-map");
  activityMap = await res.json();
  render();
}

// ── Render all step cards ─────────────────────────────────────
function render() {
  const list = document.getElementById("activity-list");
  list.innerHTML = "";

  STEP_ORDER.forEach((step, idx) => {
    const aliases = activityMap[step] || [];
    list.innerHTML += `
      <div class="step-card" id="card-${idx}">
        <div class="step-header">
          <div class="step-meta">
            <span class="step-number">${idx + 1}</span>
            <div>
              <div class="step-name">${step}</div>
              <div class="step-desc">${STEP_DESCRIPTIONS[step] || ""}</div>
            </div>
          </div>
          <span class="alias-count" id="count-${idx}">
            ${aliases.length} alias${aliases.length !== 1 ? "es" : ""}
          </span>
        </div>

        <div class="alias-area">
          <div class="alias-tags" id="tags-${idx}">
            ${aliases.map(a => aliasTag(idx, a)).join("")}
            <div class="alias-add-wrap">
              <input
                class="alias-input"
                id="input-${idx}"
                placeholder="Type an alias and press Enter"
                onkeydown="handleKey(event, ${idx}, '${escQ(step)}')"
              />
            </div>
          </div>
        </div>
      </div>`;
  });
}

function aliasTag(idx, alias) {
  return `
    <span class="alias-tag">
      ${escH(alias)}
      <button class="tag-remove" onclick="removeAlias(${idx}, '${escQ(alias)}')" title="Remove">×</button>
    </span>`;
}

// ── Alias operations ──────────────────────────────────────────
function handleKey(e, idx, step) {
  if (e.key !== "Enter" && e.key !== ",") return;
  e.preventDefault();
  const input = document.getElementById(`input-${idx}`);
  const value = input.value.trim().replace(/,$/, "");
  if (!value) return;
  addAlias(idx, step, value);
  input.value = "";
}

function addAlias(idx, step, alias) {
  if (!activityMap[step]) activityMap[step] = [];
  if (activityMap[step].includes(alias)) return;
  activityMap[step].push(alias);
  refreshCard(idx, step);
}

function removeAlias(idx, alias) {
  const step = STEP_ORDER[idx];
  activityMap[step] = (activityMap[step] || []).filter(a => a !== alias);
  refreshCard(idx, step);
}

function refreshCard(idx, step) {
  const aliases  = activityMap[step] || [];
  const tagsEl   = document.getElementById(`tags-${idx}`);
  const countEl  = document.getElementById(`count-${idx}`);

  tagsEl.innerHTML =
    aliases.map(a => aliasTag(idx, a)).join("") +
    `<div class="alias-add-wrap">
       <input class="alias-input" id="input-${idx}"
         placeholder="Type an alias and press Enter"
         onkeydown="handleKey(event, ${idx}, '${escQ(step)}')"/>
     </div>`;

  countEl.textContent = `${aliases.length} alias${aliases.length !== 1 ? "es" : ""}`;
}

// ── Save ──────────────────────────────────────────────────────
async function saveAll() {
  const status = document.getElementById("save-status");
  status.textContent = "Saving…";

  const res = await fetch("/api/activity-map", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify(activityMap),
  });

  if (res.ok) {
    status.textContent = "";
    const banner = document.getElementById("save-banner");
    banner.style.display = "block";
    setTimeout(() => banner.style.display = "none", 2000);
  } else {
    status.textContent = "Save failed — check console";
  }
}

async function resetToDefaults() {
  if (!confirm("Reset all aliases to the built-in defaults?")) return;
  const res = await fetch("/api/activity-map/reset", { method: "POST" });
  activityMap = await res.json();
  render();
}

// ── Helpers ───────────────────────────────────────────────────
const escH = s => s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
const escQ = s => s.replace(/'/g, "\\'");

load();
