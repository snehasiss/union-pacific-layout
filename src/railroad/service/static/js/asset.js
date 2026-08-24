(() => {
  const entityId = document.body.dataset.assetId;
  const loading = document.querySelector("#asset-loading");
  const content = document.querySelector("#asset-content");
  const error = document.querySelector("#asset-error");
  const panels = Object.fromEntries(["view", "update", "retire", "media"].map((tab) => [tab, document.querySelector(`#panel-${tab}`)]));
  const label = (value) => value ? String(value).replaceAll("_", " ") : "—";
  const safe = (value) => String(label(value)).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
  const safeValue = (value) => String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
  const field = (name, value) => `<dt>${safe(name)}</dt><dd>${safe(value)}</dd>`;
  const panel = (title, fields) => `<section class="detail-panel"><h2>${safe(title)}</h2><dl class="detail-list">${fields.join("")}</dl></section>`;
  const options = {
    purpose: ["passenger", "freight", "switcher", "logger", "machine", "special"], scale: ["HO", "OO"],
    status: ["intent", "spotted", "bought", "shipped", "parked", "stored", "active", "repair", "missed"],
    type: ["dc", "dcc"], loco_type: ["steam", "diesel", "turbine"],
    car_type: ["passenger", "observation", "luggage", "brakevan", "hopper", "gondola", "wagon", "tanker", "flatcar", "intermodal", "reefer", "power", "pantry", "caboose"],
    mow_type: ["crane", "snowplow", "cleaner", "tamper", "mpv"]
  };
  let asset;

  function activate(tab) {
    document.querySelectorAll("[data-tab]").forEach((button) => { const selected = button.dataset.tab === tab; button.classList.toggle("is-selected", selected); button.setAttribute("aria-selected", selected); });
    Object.entries(panels).forEach(([name, element]) => { element.hidden = name !== tab; });
    if (tab === "media") loadMedia();
  }

  function renderView() {
    const type = asset.identity.entity_type;
    const typeField = type === "loco" ? field("Type", asset.loco_type) : type === "car" ? field("Type", asset.car_type) : field("Type", asset.mow_type);
    panels.view.innerHTML = `<div class="details-grid">${panel("Identity", [field("Record", asset.identity.id), field("Railroad", asset.identity.railroad), field("Reporting mark", asset.identity.reporting_mark), field("Road number", asset.identity.road_number), typeField])}${panel("Prototype", [field("Builder", asset.prototype.builder), field("Model", asset.prototype.model), field("Nickname", asset.prototype.nickname), field("Purpose", asset.prototype.purpose)])}${panel("Model", [field("Maker", asset.model.maker), field("Product", asset.model.product), field("Scale", asset.model.scale), field("Status", asset.model.status), field("Source", asset.model.source), field("Price", asset.model.price), field("Acquired", asset.model.acquired), field("Note", asset.model.note)])}${panel("Control", [field("Type", asset.control.type), field("Decoder", asset.control.decoder), field("Address", asset.control.address), field("Sound", asset.control.sound), field("Lighting", asset.control.light), field("Smoke", asset.control.smoke)])}</div>`;
  }

  function input(section, name, value, extra = {}) {
    const id = `field-${section}-${name}`; const valueText = value ?? ""; const choice = options[name];
    const type = extra.type || (name === "price" || name === "address" ? "number" : name === "acquired" ? "date" : "text");
    let control;
    if (choice) control = `<select id="${id}" data-section="${section}" data-name="${name}">${choice.map((item) => `<option value="${item}"${item === value ? " selected" : ""}>${label(item)}</option>`).join("")}</select>`;
    else if (type === "checkbox") control = `<input id="${id}" type="checkbox" data-section="${section}" data-name="${name}"${value ? " checked" : ""}>`;
    else control = `<input id="${id}" type="${type}" data-section="${section}" data-name="${name}" value="${safeValue(valueText)}"${extra.readonly ? " readonly" : ""}${extra.required ? " required" : ""}${type === "number" ? " step=\"any\"" : ""}>`;
    return `<label class="${extra.wide ? "field--wide" : ""}${type === "checkbox" ? " checkbox-field" : ""}" for="${id}">${extra.label || label(name)}${control}</label>`;
  }

  function formSection(title, section, fields) { return `<section class="form-section"><h2>${title}</h2><div class="field-grid">${fields.join("")}</div></section>`; }

  function renderUpdate() {
    if (asset.model.status === "retired") { panels.update.innerHTML = '<p class="empty-state">Retired records are view-only.</p>'; return; }
    const kind = asset.identity.entity_type; const kindField = kind === "loco" ? "loco_type" : kind === "car" ? "car_type" : "mow_type";
    panels.update.innerHTML = `<form id="update-form"><div class="form-grid">${formSection("Identity", "identity", [input("identity", "id", asset.identity.id, { label: "Record / ID", readonly: true }), input("identity", "railroad", asset.identity.railroad, { required: true }), input("identity", "reporting_mark", asset.identity.reporting_mark, { required: true }), input("identity", "road_number", asset.identity.road_number, { required: true }), input("identity", kindField, asset[kindField], { section: "asset" })])}${formSection("Prototype", "prototype", [input("prototype", "builder", asset.prototype.builder, { required: true }), input("prototype", "model", asset.prototype.model, { required: true }), input("prototype", "nickname", asset.prototype.nickname), input("prototype", "purpose", asset.prototype.purpose)])}${formSection("Model", "model", [input("model", "maker", asset.model.maker), input("model", "product", asset.model.product), input("model", "scale", asset.model.scale), input("model", "status", asset.model.status), input("model", "source", asset.model.source), input("model", "price", asset.model.price), input("model", "acquired", asset.model.acquired), input("model", "note", asset.model.note, { wide: true })])}${formSection("Control", "control", [input("control", "type", asset.control.type), input("control", "decoder", asset.control.decoder), input("control", "address", asset.control.address), input("control", "sound", asset.control.sound, { type: "checkbox" }), input("control", "light", asset.control.light, { type: "checkbox" }), input("control", "smoke", asset.control.smoke, { type: "checkbox" })])}</div><div class="save-row"><p class="save-message" id="update-message" aria-live="polite"></p><button class="save-button" type="submit">Save changes</button></div></form>`;
    document.querySelector("#update-form").addEventListener("submit", saveUpdate);
  }

  async function saveUpdate(event) {
    event.preventDefault(); const patch = {};
    event.currentTarget.querySelectorAll("[data-section][data-name]").forEach((control) => {
      if (control.readOnly) return; const section = control.dataset.section; const name = control.dataset.name;
      const value = control.type === "checkbox" ? control.checked : control.value === "" ? null : control.type === "number" ? Number(control.value) : control.value;
      (patch[section] ||= {})[name] = value;
    });
    const kind = asset.identity.entity_type; const kindField = kind === "loco" ? "loco_type" : kind === "car" ? "car_type" : "mow_type";
    patch[kindField] = patch.identity[kindField]; delete patch.identity[kindField];
    const response = await fetch(`/assets/${encodeURIComponent(entityId)}/update`, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(patch) });
    const message = document.querySelector("#update-message");
    if (!response.ok) { message.textContent = (await response.json()).error || "Update failed."; return; }
    asset = await response.json(); message.textContent = "Saved."; renderAll();
  }

  function renderRetire() {
    if (asset.model.status === "retired") { panels.retire.innerHTML = '<div class="retire-card"><h2>Already retired</h2><p>This asset is not included in the active roster.</p></div>'; return; }
    panels.retire.innerHTML = '<div class="retire-card"><h2>Retire this asset</h2><p>Retirement permanently removes this equipment from active roster searches. Its record remains available for reference.</p><p id="retire-warning" class="retire-warning" hidden>Retiring this asset</p><label class="checkbox-field"><input id="retire-confirm" type="checkbox">I understand that this asset will be retired.</label><div class="save-row"><button id="retire-save" class="save-button" type="button" disabled>Save</button></div></div>';
    const confirm = document.querySelector("#retire-confirm"); confirm.addEventListener("change", () => { document.querySelector("#retire-warning").hidden = !confirm.checked; document.querySelector("#retire-save").disabled = !confirm.checked; });
    document.querySelector("#retire-save").addEventListener("click", async () => { const response = await fetch(`/assets/${encodeURIComponent(entityId)}/retire`, { method: "POST" }); if (response.ok) window.location.reload(); });
  }

  async function loadMedia() {
    if (panels.media.dataset.loaded) return; panels.media.dataset.loaded = "true"; panels.media.innerHTML = '<p>Loading media…</p>';
    const response = await fetch(`/api/assets/${encodeURIComponent(entityId)}/media`); const payload = await response.json();
    if (!payload.media.length) { panels.media.innerHTML = '<p class="empty-state">No curated representative image is available for this asset yet.</p>'; return; }
    panels.media.innerHTML = `<div class="media-grid">${payload.media.map((item) => `<article class="media-card"><img src="${safe(item.url)}" alt="${safe(item.title)}" loading="lazy"><div class="media-caption"><h2>${safe(item.title)}</h2><p>${safe(item.description)}</p><p>Photo: <a href="${safe(item.source_url)}" target="_blank" rel="noopener noreferrer">${safe(item.credit)}</a> · <a href="${safe(item.license_url)}" target="_blank" rel="noopener noreferrer">${safe(item.license)}</a></p></div></article>`).join("")}</div>`;
  }

  function renderAll() {
    const heading = document.createElement("div"); const title = document.createElement("h1"); title.textContent = `${asset.identity.reporting_mark} ${asset.identity.road_number}`; const subtitle = document.createElement("p"); subtitle.className = "asset-subtitle"; subtitle.textContent = `${label(asset.identity.entity_type)} · ${asset.prototype.model}${asset.prototype.nickname ? ` · ${asset.prototype.nickname}` : ""}`; heading.append(title, subtitle);
    const status = document.createElement("span"); status.className = "status-chip asset-status"; status.dataset.status = asset.model.status; status.textContent = label(asset.model.status); loading.replaceChildren(heading, status);
    renderView(); renderUpdate(); renderRetire(); panels.media.dataset.loaded = ""; panels.media.innerHTML = ""; content.hidden = false;
  }

  document.querySelectorAll("[data-tab]").forEach((button) => button.addEventListener("click", () => activate(button.dataset.tab)));
  fetch(`/api/assets/${encodeURIComponent(entityId)}`, { headers: { Accept: "application/json" } }).then((response) => { if (!response.ok) throw new Error(); return response.json(); }).then((payload) => { asset = payload; renderAll(); }).catch(() => { loading.hidden = true; error.hidden = false; });
})();
