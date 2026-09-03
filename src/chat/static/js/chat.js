(() => {
  const thread = document.querySelector("#thread");
  const composer = document.querySelector("#composer");
  const input = document.querySelector("#message");

  const text = (value) => {
    if (value === null || value === undefined || value === "") return "—";
    if (typeof value === "boolean") return value ? "Yes" : "No";
    if (typeof value === "object") return JSON.stringify(value);
    const rendered = String(value).replaceAll("_", " ");
    return ["dc", "dcc"].includes(rendered.toLowerCase()) ? rendered.toUpperCase() : rendered;
  };
  const label = (value) => text(value).replace(/\b[a-z]/g, (letter) => letter.toUpperCase());
  const summary = (asset) => `${asset.identity.reporting_mark} ${asset.identity.road_number}`;

  function addMessage(content, user = false) {
    const article = document.createElement("article");
    article.className = `message ${user ? "user" : "assistant"}`;
    const avatar = document.createElement("span");
    avatar.className = "avatar";
    avatar.textContent = user ? "You" : "UP";
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = content;
    article.append(avatar, bubble);
    thread.append(article);
    thread.scrollTop = thread.scrollHeight;
    return bubble;
  }

  function showResults(bubble, assets) {
    if (!assets.length) return;
    const list = document.createElement("div");
    list.className = "result-list";
    for (const asset of assets.slice(0, 50)) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "result";
      const name = document.createElement("strong");
      name.textContent = summary(asset);
      const description = document.createElement("small");
      description.textContent = `${label(asset.identity.entity_type)} · ${label(asset.prototype.model)} · ${label(asset.model.status)}`;
      button.append(name, description);
      button.addEventListener("click", () => showAsset(asset));
      list.append(button);
    }
    bubble.append(list);
  }

  async function showMedia(record, entityId) {
    try {
      const response = await fetch(`/api/assets/${encodeURIComponent(entityId)}/media`);
      if (!response.ok) return;
      const payload = await response.json();
      if (!payload.media?.length) return;

      const group = document.createElement("section");
      group.className = "asset-group asset-media";
      const heading = document.createElement("h4");
      heading.textContent = "Media";
      group.append(heading);
      for (const item of payload.media) {
        const figure = document.createElement("figure");
        const image = document.createElement("img");
        image.src = item.url;
        image.alt = item.title || `${entityId} ${item.kind || "asset"} image`;
        image.loading = "lazy";
        const caption = document.createElement("figcaption");
        const title = document.createElement("strong");
        title.textContent = item.title || `${label(item.kind)} image`;
        const credit = document.createElement("small");
        credit.textContent = [item.description, item.credit ? `Photo: ${item.credit}` : ""].filter(Boolean).join(" · ");
        caption.append(title, credit);
        figure.append(image, caption);
        group.append(figure);
      }
      record.append(group);
      thread.scrollTop = thread.scrollHeight;
    } catch (_error) {
      // Media is optional; asset details remain usable if it cannot be loaded.
    }
  }

  function showAsset(asset, targetBubble = null) {
    const bubble = targetBubble || addMessage(`Asset details for ${summary(asset)}.`);
    const record = document.createElement("section");
    record.className = "asset-details";
    const header = document.createElement("header");
    const identity = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = summary(asset);
    const subtitle = document.createElement("small");
    subtitle.textContent = `${label(asset.identity.entity_type)} · ${asset.identity.id}`;
    identity.append(title, subtitle);
    const edit = document.createElement("button");
    edit.type = "button";
    edit.textContent = "Edit";
    edit.addEventListener("click", () => openForm(asset));
    header.append(identity, edit);

    record.append(header);
    for (const groupName of ["identity", "prototype", "model", "control"]) {
      const group = document.createElement("section");
      group.className = "asset-group";
      const heading = document.createElement("h4");
      heading.textContent = label(groupName);
      const fields = document.createElement("dl");
      for (const [name, value] of Object.entries(asset[groupName] || {})) {
        const term = document.createElement("dt");
        term.textContent = label(name);
        const definition = document.createElement("dd");
        definition.textContent = text(value);
        fields.append(term, definition);
      }
      group.append(heading, fields);
      record.append(group);
    }
    bubble.append(record);
    showMedia(record, asset.identity.id);
  }

  function addField(form, name, labelText, value, kind = "input", options = []) {
    const wrapper = document.createElement("label");
    wrapper.textContent = labelText;
    const control = document.createElement(kind === "textarea" ? "textarea" : kind === "select" ? "select" : "input");
    control.name = name;
    if (kind === "select") {
      for (const optionValue of options) {
        const option = document.createElement("option");
        option.value = optionValue;
        option.textContent = label(optionValue);
        control.append(option);
      }
    }
    control.value = value ?? "";
    if (["railroad", "reporting_mark", "road_number"].includes(name)) control.required = true;
    wrapper.append(control);
    form.append(wrapper);
    return control;
  }

  function openForm(asset = null) {
    const createMode = !asset;
    const bubble = addMessage(createMode ? "Complete the new asset form before saving." : `Update ${asset.identity.id}.`);
    const form = document.createElement("form");
    form.className = "inline-form";
    const heading = document.createElement("strong");
    heading.textContent = createMode ? "Create asset" : `Update ${asset.identity.id}`;
    form.append(heading);
    const type = addField(form, "type", "Equipment type", asset?.identity.entity_type || "loco", "select", ["loco", "car", "mow"]);
    type.disabled = !createMode;
    addField(form, "railroad", "Railroad", asset?.identity.railroad || "Union Pacific");
    addField(form, "reporting_mark", "Reporting mark", asset?.identity.reporting_mark || "UP");
    addField(form, "road_number", "Road number", asset?.identity.road_number || "");
    addField(form, "builder", "Prototype builder", asset?.prototype.builder || "");
    addField(form, "prototype_model", "Prototype model", asset?.prototype.model || "");
    addField(form, "nickname", "Nickname", asset?.prototype.nickname || "");
    addField(form, "status", "Status", asset?.model.status || "stored", "select", ["intent", "spotted", "bought", "shipped", "parked", "stored", "active", "repair", "retired", "missed"]);
    addField(form, "note", "Notes", asset?.model.note || "", "textarea");
    const message = document.createElement("p");
    message.className = "form-message";
    message.setAttribute("role", "status");
    const actions = document.createElement("footer");
    const cancel = document.createElement("button");
    cancel.type = "button";
    cancel.textContent = "Cancel";
    cancel.addEventListener("click", () => { form.remove(); bubble.firstChild.textContent = "Edit cancelled."; });
    const save = document.createElement("button");
    save.type = "submit";
    save.className = "save";
    save.textContent = "Save asset";
    actions.append(cancel, save);
    form.append(message, actions);
    bubble.append(form);

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      save.disabled = true;
      message.textContent = "Saving…";
      const data = new FormData(form);
      const identity = {
        railroad: data.get("railroad").trim(),
        reporting_mark: data.get("reporting_mark").trim(),
        road_number: data.get("road_number").trim(),
      };
      const patch = {
        identity,
        prototype: {
          builder: data.get("builder").trim() || "Unknown",
          model: data.get("prototype_model").trim() || "Unknown",
          nickname: data.get("nickname").trim() || null,
        },
        model: {
          status: data.get("status"),
          note: data.get("note").trim() || null,
        },
      };
      const payload = createMode ? {
        type: type.value,
        railroad: identity.railroad,
        reporting_mark: identity.reporting_mark,
        road_number: identity.road_number,
        patch: { prototype: patch.prototype, model: patch.model },
      } : patch;
      const url = createMode ? "/api/assets" : `/api/assets/${encodeURIComponent(asset.identity.id)}`;
      try {
        const response = await fetch(url, {
          method: createMode ? "POST" : "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const saved = await response.json();
        if (!response.ok) throw new Error(saved.error || "Save failed.");
        form.remove();
        bubble.firstChild.textContent = `${saved.identity.id} was saved successfully.`;
        showAsset(saved);
      } catch (error) {
        message.textContent = error.message;
        save.disabled = false;
      }
    });
  }

  async function submitMessage(value) {
    addMessage(value, true);
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: value }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "Request failed.");
      const bubble = addMessage(payload.reply);
      if (payload.assets) showResults(bubble, payload.assets);
      if (payload.asset && payload.intent === "detail") showAsset(payload.asset, bubble);
      if (payload.intent === "create") openForm();
      if (payload.intent === "update" && payload.asset) openForm(payload.asset);
    } catch (error) {
      addMessage(error.message);
    }
  }

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      composer.requestSubmit();
    }
  });
  composer.addEventListener("submit", (event) => {
    event.preventDefault();
    const value = input.value.trim();
    if (!value) return;
    input.value = "";
    submitMessage(value);
  });
  document.querySelectorAll("[data-prompt]").forEach((button) => button.addEventListener("click", () => submitMessage(button.dataset.prompt)));
  document.querySelector("[data-action='create']").addEventListener("click", () => {
    addMessage("Create a new asset.", true);
    openForm();
  });
  document.querySelector("#new-chat").addEventListener("click", () => {
    thread.replaceChildren();
    addMessage("New conversation started. Type an asset search and press Enter.");
    input.focus();
  });
})();
