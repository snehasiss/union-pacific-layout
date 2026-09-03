(() => {
  const state = { type: "all", status: "", reportingMark: "", search: "" };
  const grid = document.querySelector("#roster-grid");
  const summary = document.querySelector("#result-summary");
  const empty = document.querySelector("#roster-empty");
  const error = document.querySelector("#roster-error");
  const clear = document.querySelector("#clear-filters");
  const search = document.querySelector("#search");
  const reportingMark = document.querySelector("#reporting-mark");
  const status = document.querySelector("#status");
  const createDialog = document.querySelector("#create-dialog");
  const createForm = document.querySelector("#create-form");
  let assets = [];

  const label = (value) => {
    if (value === null || value === undefined || value === "") return "—";
    const text = String(value).replaceAll("_", " ");
    return text === text.toLowerCase() ? text.replace(/\b[a-z]/g, (letter) => letter.toUpperCase()) : text;
  };
  function render() {
    const visible = assets;
    grid.replaceChildren();
    for (const asset of visible) {
      const card = document.createElement("a");
      card.className = "asset-card";
      card.href = `/assets/${encodeURIComponent(asset.identity.id)}`;
      const top = document.createElement("div"); top.className = "card-topline";
      const kind = document.createElement("span"); kind.className = "asset-kind";
      if (asset.identity.entity_type === "loco" && ["steam", "diesel", "turbine"].includes(asset.loco_type)) {
        const icon = document.createElement("img"); icon.className = "asset-kind-icon";
        icon.src = `/static/img/${asset.loco_type}-locomotive.svg`;
        icon.alt = `${label(asset.loco_type)} locomotive`;
        kind.append(icon);
      }
      const kindName = document.createElement("span"); kindName.textContent = label(asset.identity.entity_type); kind.append(kindName);
      const assetStatus = document.createElement("span"); assetStatus.className = "status-chip"; assetStatus.dataset.status = asset.model.status; assetStatus.textContent = label(asset.model.status);
      top.append(kind, assetStatus);
      const name = document.createElement("h2"); name.textContent = `${asset.identity.reporting_mark} ${asset.identity.road_number}`;
      const prototype = document.createElement("p"); prototype.textContent = `${label(asset.prototype.model)}${asset.prototype.nickname ? ` · ${label(asset.prototype.nickname)}` : ""}`;
      const footer = document.createElement("div"); footer.className = "card-footer";
      const id = document.createElement("span"); id.textContent = asset.identity.id;
      const scale = document.createElement("span"); scale.textContent = label(asset.model.scale);
      footer.append(id, scale); card.append(top, name, prototype, footer); grid.append(card);
    }
    grid.setAttribute("aria-busy", "false");
    summary.textContent = `${visible.length} ${visible.length === 1 ? "asset" : "assets"} shown`;
    empty.hidden = visible.length !== 0;
    clear.hidden = !state.status && !state.reportingMark && !state.search && state.type === "all";
  }

  async function load() {
    grid.setAttribute("aria-busy", "true"); error.hidden = true;
    const query = new URLSearchParams();
    if (state.type !== "all") query.set("type", state.type);
    if (state.status) query.set("status", state.status);
    if (state.reportingMark) query.set("reporting_mark", state.reportingMark);
    if (state.search) query.set("q", state.search);
    try {
      const response = await fetch(`/api/assets?${query}`, { headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error("Unable to load roster.");
      assets = (await response.json()).assets; render();
    } catch (_) {
      grid.setAttribute("aria-busy", "false"); summary.textContent = "Roster unavailable"; error.hidden = false;
    }
  }

  document.querySelectorAll("[data-type]").forEach((button) => button.addEventListener("click", () => {
    state.type = button.dataset.type;
    document.querySelectorAll("[data-type]").forEach((item) => item.classList.toggle("is-selected", item === button));
    load();
  }));
  let searchTimer;
  search.addEventListener("input", () => {
    state.search = search.value.trim();
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(load, 150);
  });
  reportingMark.addEventListener("input", () => { state.reportingMark = reportingMark.value.trim(); load(); });
  status.addEventListener("change", () => { state.status = status.value; load(); });
  clear.addEventListener("click", () => {
    Object.assign(state, { type: "all", status: "", reportingMark: "", search: "" });
    search.value = ""; reportingMark.value = ""; status.value = "";
    document.querySelectorAll("[data-type]").forEach((item) => item.classList.toggle("is-selected", item.dataset.type === "all")); load();
  });
  document.querySelector("#create-asset").addEventListener("click", () => {
    document.querySelector("#create-message").textContent = "";
    createDialog.showModal();
  });
  document.querySelector("#create-cancel").addEventListener("click", () => createDialog.close());
  createForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const save = document.querySelector("#create-save");
    const message = document.querySelector("#create-message");
    const roadNumber = document.querySelector("#create-road-number").value.trim();
    const payload = {
      type: document.querySelector("#create-type").value,
      railroad: document.querySelector("#create-railroad").value.trim(),
      reporting_mark: document.querySelector("#create-reporting-mark").value.trim(),
    };
    if (roadNumber) payload.road_number = roadNumber;
    save.disabled = true; message.textContent = "Creating record…";
    try {
      const response = await fetch("/assets", { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(payload) });
      const asset = await response.json();
      if (!response.ok) throw new Error(asset.error || "Creation failed.");
      window.location.assign(`/assets/${encodeURIComponent(asset.identity.id)}`);
    } catch (error) {
      message.textContent = error.message; save.disabled = false;
    }
  });
  load();
})();
