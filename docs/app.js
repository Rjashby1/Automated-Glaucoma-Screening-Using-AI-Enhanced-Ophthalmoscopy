const DATA = "dashboard_data/";
const FIG = "dashboard_assets/figures/";

const $ = (selector) => document.querySelector(selector);

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function prettyCondition(value) {
  const text = String(value ?? "");
  const mapping = {
    "zero_shot_notebook_10_on_clinical_test": "N12 zero-shot",
    "clinical_adapt_25pct": "N12 clinical-only 25%",
    "clinical_adapt_50pct": "N12 clinical-only 50%",
    "clinical_adapt_75pct": "N12 clinical-only 75%",
    "zero_shot_notebook10_on_hybrid50_clinical_holdout": "N13 zero-shot",
    "hybrid_public_plus_50pct_clinical_preaugmentation": "N13 hybrid public + clinical",
  };
  return mapping[text] || text.replaceAll("_", " ");
}

function prettyStrategy(value) {
  const text = String(value ?? "");
  const mapping = {
    "clinical_only_fine_tuning": "Clinical-only fine-tuning",
    "hybrid_public_clinical_preaugmentation": "Hybrid public + clinical",
  };
  return mapping[text] || text.replaceAll("_", " ");
}

function prettyScope(value) {
  return String(value ?? "")
    .replace("within_notebook_same_clinical_split", "Within-notebook same clinical split")
    .replace("same_public_test_split", "Same public test split")
    .replaceAll("_", " ");
}

function prettyStage(value) {
  return String(value ?? "")
    .replace("Notebook 07 selected public model", "N07 selected public")
    .replace("Notebook 10 long public model", "N10 long public")
    .replace("Notebook 13 hybrid public-clinical model", "N13 hybrid");
}

function showError(container, error) {
  container.classList.remove("loading");
  container.innerHTML = `<div class="error-box">Could not load this dashboard section.\n${escapeHtml(error.message || error)}</div>`;
}

async function fetchText(path) {
  const response = await fetch(`${path}?v=${Date.now()}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${path}: HTTP ${response.status}`);
  }
  return await response.text();
}

async function fetchJson(path) {
  const text = await fetchText(path);
  return JSON.parse(text);
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;

  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    const next = text[i + 1];

    if (char === '"' && inQuotes && next === '"') {
      field += '"';
      i += 1;
      continue;
    }

    if (char === '"') {
      inQuotes = !inQuotes;
      continue;
    }

    if (char === "," && !inQuotes) {
      row.push(field);
      field = "";
      continue;
    }

    if ((char === "\n" || char === "\r") && !inQuotes) {
      if (char === "\r" && next === "\n") i += 1;
      row.push(field);
      field = "";
      if (row.some((value) => value.length > 0)) rows.push(row);
      row = [];
      continue;
    }

    field += char;
  }

  row.push(field);
  if (row.some((value) => value.length > 0)) rows.push(row);

  const headers = rows.shift() || [];
  return rows.map((values) => {
    const record = {};
    headers.forEach((header, index) => {
      record[header] = values[index] ?? "";
    });
    return record;
  });
}

async function fetchCsv(path) {
  return parseCsv(await fetchText(path));
}

function number(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function fmt(value, digits = 3) {
  const parsed = number(value);
  return parsed === null ? "—" : parsed.toFixed(digits);
}

function asList(value) {
  if (Array.isArray(value)) return value;
  if (value === null || value === undefined || value === "") return [];
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (trimmed.startsWith("[") && trimmed.endsWith("]")) {
      try {
        const parsed = JSON.parse(trimmed.replaceAll("'", '"'));
        return Array.isArray(parsed) ? parsed : [trimmed];
      } catch {
        return [trimmed];
      }
    }
    return trimmed.split(/[;,]/).map((item) => item.trim()).filter(Boolean);
  }
  return [String(value)];
}

function renderKpis(kpis) {
  const grid = $("#kpi-grid");
  grid.classList.remove("loading");

  if (!kpis.length) {
    grid.innerHTML = `<div class="error-box">No KPI records were loaded.</div>`;
    return;
  }

  grid.innerHTML = kpis
    .slice()
    .sort((a, b) => Number(a.priority || 99) - Number(b.priority || 99))
    .map((kpi) => `
      <article class="kpi-card">
        <div class="kpi-label">${escapeHtml(kpi.label)}</div>
        <div class="kpi-value">${escapeHtml(kpi.display_value)}</div>
        <div class="kpi-context">${escapeHtml(kpi.context)}</div>
        <div class="kpi-source">${escapeHtml(kpi.source)}</div>
      </article>
    `)
    .join("");
}

function renderStory(sections) {
  const container = $("#story-sections");
  container.classList.remove("loading");

  if (!sections.length) {
    container.innerHTML = `<div class="error-box">No storyboard records were loaded.</div>`;
    return;
  }

  container.innerHTML = sections
    .slice()
    .sort((a, b) => Number(a.dashboard_priority || 99) - Number(b.dashboard_priority || 99))
    .map((section, index) => {
      const notebooks = asList(section.source_notebooks);
      const figures = asList(section.figure_ids);
      return `
        <article class="story-card">
          <div class="story-card-number">${index + 1}</div>
          <h3>${escapeHtml(section.title)}</h3>
          <p><strong>${escapeHtml(section.one_sentence_takeaway)}</strong></p>
          <p>${escapeHtml(section.long_takeaway)}</p>
          <div class="story-meta">
            ${notebooks.map((nb) => `<span class="pill">Notebook ${escapeHtml(nb)}</span>`).join("")}
            ${figures.map((fig) => `<span class="pill">${escapeHtml(String(fig).replaceAll("_", " "))}</span>`).join("")}
          </div>
        </article>
      `;
    })
    .join("");
}

function renderTable(container, rows, columns) {
  if (!rows.length) {
    container.innerHTML = `<div class="error-box">No table records were loaded.</div>`;
    return;
  }

  container.innerHTML = `
    <table>
      <thead>
        <tr>${columns.map((column) => `<th>${escapeHtml(column.label)}</th>`).join("")}</tr>
      </thead>
      <tbody>
        ${rows.map((row) => `
          <tr>
            ${columns.map((column) => `<td>${escapeHtml(column.render ? column.render(row) : row[column.key])}</td>`).join("")}
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function renderPublicPerformance(rows) {
  const container = $("#public-summary");
  const table = $("#public-table");
  container.classList.remove("loading");

  const maxDice = Math.max(...rows.map((row) => number(row.public_test_mean_foreground_dice) || 0), 0.9);

  container.innerHTML = `
    <div>
      ${rows.map((row) => {
        const value = number(row.public_test_mean_foreground_dice) || 0;
        const width = Math.max(2, Math.min(100, (value / maxDice) * 100));
        return `
          <div class="bar-row">
            <div class="bar-label">${escapeHtml(prettyStage(row.model_stage))}</div>
            <div class="bar-track"><div class="bar-fill" style="--w:${width}%"></div></div>
            <div class="bar-value">${fmt(value)}</div>
          </div>
        `;
      }).join("")}
    </div>
  `;

  renderTable(table, rows, [
    { key: "notebook", label: "Notebook" },
    { key: "model_stage", label: "Model stage", render: (row) => prettyStage(row.model_stage) },
    { key: "public_test_mean_foreground_dice", label: "Mean Dice", render: (row) => fmt(row.public_test_mean_foreground_dice) },
    { key: "public_test_cdr_mae", label: "CDR MAE", render: (row) => fmt(row.public_test_cdr_mae) },
    { key: "delta_public_mean_dice_vs_notebook07", label: "Δ Mean Dice vs N07", render: (row) => fmt(row.delta_public_mean_dice_vs_notebook07) },
  ]);
}

function renderClinicalStrategy(rows) {
  const container = $("#clinical-summary");
  const table = $("#clinical-table");
  container.classList.remove("loading");

  const maxDice = Math.max(...rows.map((row) => number(row.patient_weighted_mean_foreground_dice) || 0), 0.4);

  container.innerHTML = `
    <div>
      <h3>Patient-weighted clinical mean Dice</h3>
      ${rows.map((row) => {
        const value = number(row.patient_weighted_mean_foreground_dice) || 0;
        const width = Math.max(2, Math.min(100, (value / maxDice) * 100));
        const fillClass = String(row.notebook) === "13" ? "bar-fill clinical" : "bar-fill";
        return `
          <div class="bar-row">
            <div class="bar-label">${escapeHtml(prettyCondition(row.condition))}</div>
            <div class="bar-track"><div class="${fillClass}" style="--w:${width}%"></div></div>
            <div class="bar-value">${fmt(value)}</div>
          </div>
        `;
      }).join("")}
    </div>
  `;

  renderTable(table, rows, [
    { key: "notebook", label: "Notebook" },
    { key: "strategy_family", label: "Strategy family", render: (row) => prettyStrategy(row.strategy_family) },
    { key: "condition", label: "Condition", render: (row) => prettyCondition(row.condition) },
    { key: "patient_weighted_mean_foreground_dice", label: "Patient Dice", render: (row) => fmt(row.patient_weighted_mean_foreground_dice) },
    { key: "delta_vs_internal_zero_patient_weighted_mean_dice", label: "Δ vs internal zero-shot", render: (row) => fmt(row.delta_vs_internal_zero_patient_weighted_mean_dice) },
    { key: "patient_weighted_cdr_abs_error", label: "Patient CDR error", render: (row) => fmt(row.patient_weighted_cdr_abs_error) },
    { key: "comparison_scope", label: "Comparison scope", render: (row) => prettyScope(row.comparison_scope) },
  ]);
}

const figures = [
  {
    id: "pipeline_storyboard",
    title: "Pipeline storyboard",
    file: "pipeline_storyboard.png",
    featured: true,
    caption: "End-to-end project pipeline from public data engineering through hybrid training and dashboard assets."
  },
  {
    id: "data_composition",
    title: "Data composition",
    file: "data_composition.png",
    caption: "Public split sizes, clinical mask-ready sample count, and Notebook 13 clinical train/holdout split."
  },
  {
    id: "public_performance_trajectory",
    title: "Public performance trajectory",
    file: "public_performance_trajectory.png",
    caption: "Held-out public Dice metrics for the selected public model, long-trained public model, and hybrid model."
  },
  {
    id: "public_to_clinical_gap",
    title: "Public-to-clinical gap",
    file: "public_to_clinical_gap.png",
    caption: "Public test performance remained much higher than clinical patient-weighted performance."
  },
  {
    id: "clinical_strategy_dice",
    title: "Clinical strategy Dice comparison",
    file: "clinical_strategy_dice.png",
    caption: "Patient-weighted clinical Dice across clinical-only adaptation and hybrid training conditions."
  },
  {
    id: "clinical_strategy_cdr",
    title: "Clinical strategy CDR error comparison",
    file: "clinical_strategy_cdr.png",
    caption: "Patient-weighted CDR absolute error across clinical strategy conditions."
  },
  {
    id: "evidence_matrix",
    title: "Evidence matrix",
    file: "evidence_matrix.png",
    featured: true,
    caption: "Final project claims linked to metrics, interpretation strength, and caveats."
  },
];

function renderFigures() {
  const grid = $("#figure-grid");
  grid.innerHTML = figures.map((figure) => {
    const src = `${FIG}${figure.file}?v=${Date.now()}`;
    const cleanSrc = `${FIG}${figure.file}`;
    return `
      <article class="figure-card ${figure.featured ? "featured" : ""}">
        <img src="${src}" alt="${escapeHtml(figure.title)}" data-src="${cleanSrc}" data-title="${escapeHtml(figure.title)}" data-caption="${escapeHtml(figure.caption)}">
        <h3>${escapeHtml(figure.title)}</h3>
        <p class="figure-caption">${escapeHtml(figure.caption)}</p>
        <div class="figure-actions">
          <button class="button enlarge-button" type="button" data-src="${cleanSrc}" data-title="${escapeHtml(figure.title)}" data-caption="${escapeHtml(figure.caption)}">View enlarged</button>
          <a class="button secondary" href="${cleanSrc}" target="_blank" rel="noopener">Open full-size PNG</a>
        </div>
      </article>
    `;
  }).join("");

  grid.querySelectorAll("img, .enlarge-button").forEach((item) => {
    item.addEventListener("click", () => openFigure(item.dataset.src, item.dataset.title, item.dataset.caption));
  });
}

function openFigure(src, title, caption) {
  const dialog = $("#figure-dialog");
  $("#dialog-title").textContent = title || "Figure";
  $("#dialog-caption").textContent = caption || "";
  $("#dialog-image").src = `${src}?v=${Date.now()}`;
  $("#dialog-image").alt = title || "Figure";
  $("#dialog-open").href = src;
  if (typeof dialog.showModal === "function") {
    dialog.showModal();
  } else {
    window.open(src, "_blank", "noopener");
  }
}

function renderClaims(claims) {
  const container = $("#claims-table");
  container.classList.remove("loading");

  if (!claims.length) {
    container.innerHTML = `<div class="error-box">No claims/evidence records were loaded.</div>`;
    return;
  }

  container.innerHTML = claims.map((claim) => `
    <article class="claim-card">
      <div class="claim-head">
        <div class="claim-id">${escapeHtml(claim.claim_id)}</div>
        <h3>${escapeHtml(claim.claim)}</h3>
      </div>
      <div class="claim-evidence">
        <div class="evidence-item"><small>Evidence</small><div>${escapeHtml(claim.supporting_metric)}</div></div>
        <div class="evidence-item"><small>Value</small><div>${claim.value === null || claim.value === "" ? "—" : escapeHtml(fmt(claim.value))}</div></div>
        <div class="evidence-item"><small>Strength</small><div>${escapeHtml(String(claim.interpretation_strength).replaceAll("_", " "))}</div></div>
        <div class="evidence-item"><small>Notebooks</small><div>${escapeHtml(String(claim.supporting_notebooks).replaceAll(";", ", "))}</div></div>
      </div>
      <p><strong>Caveat:</strong> ${escapeHtml(claim.caveat)}</p>
    </article>
  `).join("");
}

function renderDataLinks() {
  const links = [
    ["dashboard_kpi_cards.json", "KPI cards JSON"],
    ["dashboard_story_sections.json", "Storyboard sections JSON"],
    ["public_model_performance_summary.csv", "Public model performance CSV"],
    ["clinical_transfer_summary.csv", "Clinical transfer CSV"],
    ["clinical_strategy_comparison_summary.csv", "Clinical strategy comparison CSV"],
    ["public_clinical_tradeoff_summary.csv", "Public-clinical tradeoff CSV"],
    ["final_claims_evidence_matrix.csv", "Claims/evidence CSV"],
    ["final_claims_evidence_matrix.json", "Claims/evidence JSON"],
    ["model_development_registry.csv", "Model development registry CSV"],
    ["final_project_interpretation.md", "Final project interpretation"],
  ];

  $("#data-links").innerHTML = links.map(([file, title]) => `
    <a class="data-link" href="${DATA}${file}" target="_blank" rel="noopener">
      <strong>${escapeHtml(title)}</strong>
      <span>${escapeHtml(file)}</span>
    </a>
  `).join("");
}

async function main() {
  renderFigures();
  renderDataLinks();

  $("#dialog-close").addEventListener("click", () => $("#figure-dialog").close());

  const tasks = [
    fetchJson(`${DATA}dashboard_kpi_cards.json`).then(renderKpis).catch((error) => showError($("#kpi-grid"), error)),
    fetchJson(`${DATA}dashboard_story_sections.json`).then(renderStory).catch((error) => showError($("#story-sections"), error)),
    fetchJson(`${DATA}final_claims_evidence_matrix.json`).then(renderClaims).catch((error) => showError($("#claims-table"), error)),
    fetchCsv(`${DATA}public_model_performance_summary.csv`).then(renderPublicPerformance).catch((error) => showError($("#public-summary"), error)),
    fetchCsv(`${DATA}clinical_strategy_comparison_summary.csv`).then(renderClinicalStrategy).catch((error) => showError($("#clinical-summary"), error)),
  ];

  await Promise.allSettled(tasks);
}

main();
