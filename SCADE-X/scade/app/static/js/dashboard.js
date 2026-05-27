const PAGE_SIZE = 25;
let allCases    = [];
let showAll     = false;
let currentPage = 1;

async function loadStats() {
  const res  = await fetch("/api/stats");
  const data = await res.json();
  if (data.status) return;
  document.getElementById("kpi-total").textContent    = data.total;
  document.getElementById("kpi-flagged").textContent  = data.flagged;
  document.getElementById("kpi-avg").textContent      = data.avg_score.toFixed(3);
  document.getElementById("kpi-critical").textContent = data.critical;
}

let hasSecurity = false;

async function loadCases() {
  const res = await fetch("/api/cases");
  allCases  = await res.json();
  if (!allCases.length) return;

  hasSecurity = allCases.some(c => c.security_score != null);
  if (hasSecurity) {
    document.getElementById("th-security").style.display = "";
  }

  document.getElementById("pipeline-notice").style.display = "none";
  document.getElementById("cases-table").style.display     = "table";

  currentPage = 1;
  renderTable();
  renderHistogram(allCases);
  renderDonut(allCases.filter(c => c.flagged));
}

function visibleCases() {
  return showAll ? allCases : allCases.filter(c => c.flagged);
}

function renderTable() {
  const rows    = visibleCases();
  const total   = rows.length;
  const pages   = Math.max(1, Math.ceil(total / PAGE_SIZE));
  currentPage   = Math.min(currentPage, pages);
  const start   = (currentPage - 1) * PAGE_SIZE;
  const slice   = rows.slice(start, start + PAGE_SIZE);

  const tbody = document.getElementById("cases-body");
  tbody.innerHTML = "";

  slice.forEach(c => {
    const sc = c.composite_score;

    // Composite score — color by severity
    const scoreColor = sc < 0.5   ? "#ef4444"
                     : sc < 0.875 ? "#f59e0b"
                     :              "#525252";
    const barColor   = sc < 0.5   ? "rgba(239,68,68,0.7)"
                     : sc < 0.875 ? "rgba(245,158,11,0.7)"
                     :              "#2a2a2a";

    // Risk badge — colored only for flagged rows
    const riskColor  = c.risk_level === "CRITICAL" ? { bg:"rgba(239,68,68,0.12)",  border:"rgba(239,68,68,0.35)",  text:"#ef4444" }
                     : c.risk_level === "HIGH"     ? { bg:"rgba(245,158,11,0.12)", border:"rgba(245,158,11,0.35)", text:"#f59e0b" }
                     :                               { bg:"rgba(148,163,184,0.08)", border:"#1e1e1e",               text:"#94a3b8" };

    // Left-border accent on flagged rows
    const rowAccent  = c.risk_level === "CRITICAL" ? "#ef4444"
                     : c.risk_level === "HIGH"     ? "#f59e0b"
                     :                               "#525252";

    const flagMark = (!showAll || c.flagged) ? "" :
      `<span style="color:var(--muted);font-size:11px;margin-left:6px">normal</span>`;

    const row = document.createElement("tr");
    row.style.cursor = "pointer";
    if (c.flagged) {
      row.style.borderLeft = `2px solid ${rowAccent}`;
    } else {
      row.style.opacity = "0.35";
    }
    row.addEventListener("click", () => window.location = `/case/${c.case_id}`);
    row.innerHTML = `
      <td style="color:var(--white);font-weight:500;padding-left:${c.flagged ? '10px' : '12px'}">${c.case_id}${flagMark}</td>
      <td>
        <div class="score-bar-wrap">
          <div class="score-bar">
            <div class="score-bar-fill" style="width:${sc*100}%;background:${barColor}"></div>
          </div>
          <span style="color:${scoreColor};font-weight:${c.flagged ? '600' : '400'}">${sc.toFixed(3)}</span>
        </div>
      </td>
      <td style="color:var(--muted)">${c.cf_score.toFixed(3)}</td>
      <td style="color:var(--muted)">${c.time_score.toFixed(3)}</td>
      <td style="color:var(--muted)">${c.resource_score.toFixed(3)}</td>
      <td style="color:var(--muted)">${c.amount_score.toFixed(3)}</td>
      ${hasSecurity ? `<td style="color:var(--muted)">${c.security_score != null ? c.security_score.toFixed(3) : "—"}</td>` : ""}
      <td style="color:var(--text)">${(c.matched_attack || "—").replace(/_/g," ")}</td>
      <td>${c.flagged
        ? `<span style="background:${riskColor.bg};border:1px solid ${riskColor.border};color:${riskColor.text};padding:2px 8px;border-radius:3px;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.05em">${c.risk_level}</span>`
        : "—"}</td>
    `;
    tbody.appendChild(row);
  });

  // Pagination controls
  const pg = document.getElementById("pagination");
  if (total > PAGE_SIZE) {
    pg.style.display = "flex";
    document.getElementById("page-info").textContent =
      `Page ${currentPage} of ${pages}  (${total} cases)`;
    document.getElementById("prev-btn").disabled = currentPage === 1;
    document.getElementById("next-btn").disabled = currentPage === pages;
  } else {
    pg.style.display = "none";
  }

  // Section title
  const flaggedCount = allCases.filter(c => c.flagged).length;
  document.getElementById("cases-title").textContent = showAll
    ? `All Cases  (${allCases.length} total, ${flaggedCount} flagged)`
    : `Flagged Cases — Investigation Queue  (${flaggedCount})`;
  document.getElementById("toggle-btn").textContent = showAll
    ? "Show Flagged Only"
    : "Show All Cases";
}

function toggleView() {
  showAll     = !showAll;
  currentPage = 1;
  renderTable();
}

function changePage(delta) {
  currentPage += delta;
  renderTable();
  document.getElementById("cases-table").scrollIntoView({ behavior: "smooth", block: "start" });
}

async function rerunAnalysis() {
  const btn    = document.getElementById("rerun-btn");
  const status = document.getElementById("rerun-status");
  btn.disabled    = true;
  btn.textContent = "Running…";
  status.style.display = "block";
  status.textContent   = "Re-running pipeline — this may take 10–30 seconds…";

  const res  = await fetch("/api/rerun", { method: "POST" });
  const data = await res.json();

  btn.disabled    = false;
  btn.textContent = "↺ Re-run";

  if (data.error) {
    status.style.color   = "var(--red)";
    status.textContent   = `Error: ${data.error}`;
    return;
  }

  status.style.color = "var(--green)";
  status.textContent = "Done — refreshing results…";
  setTimeout(() => window.location.reload(), 800);
}

function renderHistogram(cases) {
  const BINS  = 20;
  const WIDTH = 1 / BINS;
  const labels = Array.from({length: BINS}, (_, i) => (i * WIDTH).toFixed(2));
  const counts = labels.map((_, i) =>
    cases.filter(c => c.composite_score >= i*WIDTH && c.composite_score < (i+1)*WIDTH).length
  );

  new Chart(document.getElementById("scoreHistogram"), {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Cases",
        data: counts,
        backgroundColor: labels.map((_, i) =>
          i * WIDTH < 0.875 ? "rgba(239,68,68,0.75)" : "rgba(80,80,80,0.6)"
        ),
        borderWidth: 0,
        borderRadius: 2,
      }]
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        x: {
          title: { display: true, text: "Composite Score", color: "#525252" },
          ticks: { color: "#525252" },
          grid:  { color: "#1e1e1e" },
        },
        y: {
          title: { display: true, text: "Cases", color: "#525252" },
          ticks: { color: "#525252" },
          grid:  { color: "#1e1e1e" },
          beginAtZero: true,
        },
      }
    }
  });
}

function renderDonut(flagged) {
  const counts = {};
  flagged.forEach(c => {
    const k = (c.matched_attack || "unknown").replace(/_/g, " ");
    counts[k] = (counts[k] || 0) + 1;
  });

  new Chart(document.getElementById("attackDonut"), {
    type: "doughnut",
    data: {
      labels: Object.keys(counts),
      datasets: [{
        data: Object.values(counts),
        backgroundColor: ["#ef4444","#f59e0b","#6366f1","#22c55e","#ec4899"],
        borderWidth: 1,
        borderColor: "#000",
      }]
    },
    options: {
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: "#848484", padding: 14, font: { size: 12 } },
        },
      },
    }
  });
}

async function loadRiskLists() {
  const [suppRes, userRes] = await Promise.all([
    fetch("/api/suppliers"),
    fetch("/api/users"),
  ]);
  const suppliers = await suppRes.json();
  const users     = await userRes.json();

  const supList = document.getElementById("supplier-risk-list");
  if (suppliers.length) {
    suppliers.slice(0, 6).forEach(s => {
      supList.innerHTML += `
        <div class="risk-item">
          <span>${s.supplier_id}</span>
          <span class="risk-count">${s.flagged_cases} flagged</span>
        </div>`;
    });
  } else {
    supList.innerHTML = '<p style="color:var(--muted);font-size:13px">No data yet</p>';
  }

  const userList = document.getElementById("user-risk-list");
  if (users.length) {
    users.slice(0, 6).forEach(u => {
      userList.innerHTML += `
        <div class="risk-item">
          <span>${u.user}</span>
          <span class="risk-count">${u.flagged_cases} flagged</span>
        </div>`;
    });
  } else {
    userList.innerHTML = '<p style="color:var(--muted);font-size:13px">No data yet</p>';
  }
}

async function checkDataSource() {
  const res  = await fetch("/api/data-source");
  const data = await res.json();

  if (data.source === "none") {
    document.querySelector(".kpi-grid").style.display   = "none";
    document.querySelector(".charts-row").style.display = "none";
    document.querySelector(".section").style.display    = "none";
    document.querySelectorAll(".charts-row").forEach(el => el.style.display = "none");
    document.getElementById("pipeline-notice").style.display = "none";

    document.querySelector("main").insertAdjacentHTML("beforeend", `
      <div class="empty-state">
        <div class="empty-icon">📂</div>
        <div class="empty-title">No data loaded yet</div>
        <div class="empty-sub">
          Upload your procurement event log to start detecting anomalies.
          SCADE will learn your normal process and flag anything suspicious.
        </div>
        <a href="/upload" class="btn-primary" style="text-decoration:none">Upload Data →</a>
      </div>`);
    return false;
  }

  if (data.source === "synthetic") {
    document.querySelector("main").insertAdjacentHTML("afterbegin", `
      <div id="demo-banner" style="
        background:var(--surface2);border:1px solid var(--border);
        border-radius:6px;padding:10px 16px;margin-bottom:20px;
        display:flex;justify-content:space-between;align-items:center;font-size:13px">
        <span style="color:var(--muted)">Showing <strong style="color:var(--text)">demo data</strong> — upload your own file to analyse real procurement logs.</span>
        <a href="/upload" style="color:var(--white);font-weight:600;text-decoration:none;font-size:13px">Upload now →</a>
      </div>`);
  }

  return true;
}

async function init() {
  const hasData = await checkDataSource();
  if (!hasData) return;
  loadStats();
  loadCases();
  loadRiskLists();
}

init();
