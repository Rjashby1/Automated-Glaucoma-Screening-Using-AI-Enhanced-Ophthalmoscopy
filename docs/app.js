async function loadJson(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Could not load ${path}`);
  return await response.json();
}

async function loadCsv(path) {
  const text = await (await fetch(path)).text();
  const lines = text.trim().split(/?
/);
  const headers = lines[0].split(",");
  return lines.slice(1).map(line => {
    const values = line.match(/(".*?"|[^",]+)(?=\s*,|\s*$)/g) || [];
    const row = {};
    headers.forEach((header, index) => {
      row[header] = (values[index] || "").replace(/^"|"$/g, "");
    });
    return row;
  });
}

function renderKpis(kpis) {
  const grid = document.getElementById("kpi-grid");
  grid.innerHTML = "";
  kpis.sort((a, b) => Number(a.priority) - Number(b.priority)).forEach(kpi => {
    const card = document.createElement("article");
    card.className = "kpi-card";
    card.innerHTML = `
      <div class="kpi-label">${kpi.label}</div>
      <div class="kpi-value">${kpi.display_value}</div>
      <div class="kpi-context">${kpi.context}</div>
      <small>${kpi.source}</small>
    `;
    grid.appendChild(card);
  });
}

function renderStory(sections) {
  const container = document.getElementById("story-sections");
  container.innerHTML = "";
  sections.sort((a, b) => Number(a.dashboard_priority) - Number(b.dashboard_priority)).forEach(section => {
    const card = document.createElement("article");
    card.className = "story-card";
    card.innerHTML = `
      <h3>${section.title}</h3>
      <p><strong>${section.one_sentence_takeaway}</strong></p>
      <p>${section.long_takeaway}</p>
      <small>Source notebooks: ${section.source_notebooks.join(", ")}</small>
    `;
    container.appendChild(card);
  });
}

function renderClaims(claims) {
  const container = document.getElementById("claims-table");
  const rows = claims.map(row => `
    <tr>
      <td>${row.claim_id}</td>
      <td>${row.claim}</td>
      <td>${row.supporting_metric}</td>
      <td>${row.value || ""}</td>
      <td>${row.interpretation_strength}</td>
      <td>${row.caveat}</td>
    </tr>
  `).join("");

  container.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Claim</th>
          <th>Evidence</th>
          <th>Value</th>
          <th>Strength</th>
          <th>Caveat</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

async function main() {
  const [kpis, story, claims] = await Promise.all([
    loadJson("dashboard_data/dashboard_kpi_cards.json"),
    loadJson("dashboard_data/dashboard_story_sections.json"),
    loadJson("dashboard_data/final_claims_evidence_matrix.json"),
  ]);

  renderKpis(kpis);
  renderStory(story);
  renderClaims(claims);
}

main().catch(error => {
  document.body.insertAdjacentHTML("beforeend", `<pre>${error}</pre>`);
});
