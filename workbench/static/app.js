(() => {
  "use strict";
  const root = document.getElementById("view-root");
  const live = document.getElementById("live-region");
  const state = {
    view: "workbench",
    projects: [],
    current: null,
    tab: "brief",
    skills: [],
    registry: null,
    error: "",
    notice: "",
    previewAnswers: {},
    preview: null,
    evaluation: null,
    history: [],
    loading: true,
    loadingProjectId: null,
    recovery: null,
    saving: false,
  };
  const esc = (value) => String(value ?? "");
  const el = (tag, attrs = {}, children = []) => {
    const node = document.createElement(tag);
    Object.entries(attrs).forEach(([key, value]) => {
      if (key === "class") node.className = value;
      else if (key === "text") node.textContent = value;
      else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
      else if (value !== false && value != null)
        node.setAttribute(key, value === true ? "" : value);
    });
    children.forEach((child) => node.append(child));
    return node;
  };
  const button = (text, className, handler) =>
    el("button", { class: className, type: "button", text, onclick: handler });
  const field = (label, key, value, opts = {}) => {
    const wrap = el("div", { class: `field${opts.full ? " full" : ""}` });
    const input = opts.textarea
      ? el("textarea", { id: `field-${key}`, rows: opts.rows || 4 })
      : opts.select
        ? el(
            "select",
            { id: `field-${key}` },
            opts.options.map(([v, t]) => el("option", { value: v, text: t })),
          )
        : el("input", { id: `field-${key}`, type: opts.type || "text" });
    input.value = value ?? "";
    if (opts.select) input.value = value || opts.options[0][0];
    input.addEventListener("input", () => updateDraft(key, input.value));
    wrap.append(el("label", { for: `field-${key}`, text: label }), input);
    if (opts.hint)
      wrap.append(el("span", { class: "field-hint", text: opts.hint }));
    return wrap;
  };
  const announce = (message) => {
    live.textContent = message;
  };
  const syncLiveRegion = () => {
    const message =
      state.error ||
      state.notice ||
      state.recovery?.message ||
      (state.loading ? "Loading workbench." : "") ||
      (state.loadingProjectId ? "Loading project." : "");
    live.textContent = message;
    live.setAttribute("role", state.error ? "alert" : "status");
  };
  const draftDefaults = (kind = "assistant") => ({
    title: "",
    slug: "",
    code: "aj05",
    family: "core-capability",
    kind,
    purpose: "",
    audience: "",
    source_text: "",
    source_reference: "",
    instructions: "",
    output_contract: "",
    constraints: "",
    target: "offline-specification",
    phase: "draft",
    evidence: "",
    client_org: "",
    parent_capability: "",
    bfs_firewall: false,
    visibility_lock: "",
    skill_ids: [],
    workflow_steps:
      kind === "workflow"
        ? [
            "Clarify the intended outcome",
            "Gather the relevant context",
            "Offer the next useful step",
          ]
        : [],
    decision:
      kind === "decision-tool"
        ? {
            start: "start",
            nodes: [
              {
                id: "start",
                question: "Is the request clear?",
                yes: "answer",
                no: "clarify",
              },
              { id: "answer", result: "Proceed with the agreed scope." },
              { id: "clarify", result: "Ask for missing context." },
            ],
          }
        : { start: "start", nodes: [] },
    eval_cases: [],
  });
  const template = (kind) => {
    const d = draftDefaults(kind);
    if (kind === "decision-tool") {
      d.title = "A small decision guide";
      d.slug = "decision-guide";
      d.purpose =
        "Help someone make a repeatable decision with visible reasoning.";
      d.audience = "People who need a clear next step.";
      d.instructions =
        "Ask one question at a time. Explain the path before recommending the next step.";
      d.output_contract =
        "A concise recommendation and the reasoning path that led there.";
    }
    if (kind === "workflow") {
      d.title = "A steady workflow";
      d.slug = "steady-workflow";
      d.purpose = "Turn a recurring task into a calm, inspectable sequence.";
      d.audience = "Someone doing this task for the first time.";
      d.instructions =
        "Guide the person through each step, checking context when the path changes.";
      d.output_contract =
        "An ordered checklist with decisions and evidence called out.";
    }
    return d;
  };
  const draftFields = [
    "title",
    "slug",
    "code",
    "family",
    "kind",
    "purpose",
    "audience",
    "source_text",
    "source_reference",
    "instructions",
    "output_contract",
    "constraints",
    "target",
    "phase",
    "evidence",
    "client_org",
    "parent_capability",
    "bfs_firewall",
    "visibility_lock",
    "skill_ids",
    "workflow_steps",
    "decision",
    "eval_cases",
  ];
  const draftPayload = (project) =>
    Object.fromEntries(draftFields.map((key) => [key, project[key]]));
  async function api(path, options = {}) {
    const response = await fetch(path, {
      cache: "no-store",
      ...options,
      headers: {
        ...(options.body
          ? { "Content-Type": "application/json", "X-Foundry-Request": "1" }
          : {}),
        ...(options.headers || {}),
      },
    });
    const type = response.headers.get("content-type") || "";
    if (!response.ok) {
      let message = `Request failed (${response.status})`;
      if (type.includes("json")) {
        const body = await response.json();
        message = body.error || message;
      }
      throw new Error(message);
    }
    return type.includes("json") ? response.json() : response;
  }
  async function loadProjects() {
    try {
      const data = await api("/api/projects");
      state.projects = Array.isArray(data.projects) ? data.projects : [];
    } catch (error) {
      state.error = error.message;
      state.projects = [];
    }
    document.getElementById("project-count").textContent =
      state.projects.length;
  }
  async function loadProject(id, force = false) {
    if (!force && !canLeaveCurrent()) return;
    state.loadingProjectId = id;
    state.recovery = null;
    render();
    try {
      state.current = await api(`/api/projects/${encodeURIComponent(id)}`);
      const [history, evaluations] = await Promise.allSettled([
        api(`/api/projects/${encodeURIComponent(id)}/history`),
        api(`/api/projects/${encodeURIComponent(id)}/evaluations`),
      ]);
      state.history =
        history.status === "fulfilled" && Array.isArray(history.value.history)
          ? history.value.history
          : [];
      state.evaluation =
        evaluations.status === "fulfilled" &&
        Array.isArray(evaluations.value.evaluations)
          ? evaluations.value.evaluations[0] || null
          : null;
      state.error = "";
      state.notice = "";
      state.preview = null;
      state.previewAnswers = {};
      state.loadingProjectId = null;
      render();
    } catch (error) {
      state.loadingProjectId = null;
      state.error = error.message;
      render();
    }
  }
  function canLeaveCurrent() {
    return (
      !state.current?._dirty ||
      window.confirm("This project has unsaved changes. Leave without saving?")
    );
  }
  function requireSavedProject(action) {
    if (!state.current?.id) {
      state.error = `Save the project before ${action}.`;
      render();
      return false;
    }
    if (state.current._dirty) {
      state.error = `Save your changes before ${action}.`;
      render();
      return false;
    }
    return true;
  }
  function updateDraft(key, value) {
    if (!state.current) return;
    state.current[key] = value;
    state.current._dirty = true;
    const marker = document.querySelector(".save-state");
    if (marker) {
      marker.textContent = "Unsaved changes";
      marker.classList.add("dirty");
    }
  }
  function makeHeader(kicker, title, description, action) {
    const wrap = el("div", { class: "view-heading" });
    const left = el("div", {}, [
      el("div", { class: "kicker-line" }, [
        el("b", { text: kicker }),
        el("span", { text: " / private desk" }),
      ]),
      el("h2", { text: title }),
      el("p", { text: description }),
    ]);
    wrap.append(left);
    if (action) wrap.append(action);
    return wrap;
  }
  function showError() {
    return state.error
      ? el("div", {
          class: "error-box",
          role: "alert",
          "aria-live": "assertive",
          "aria-atomic": "true",
          text: state.error,
        })
      : null;
  }
  function render() {
    root.replaceChildren();
    const titles = {
      workbench: ["WORKBENCH", "Your capability desk"],
      projects: ["PROJECTS", "Saved capability projects"],
      skills: ["SKILLZ CATALOG", "A shared shelf of contracts"],
      universe: ["UNIVERSE", "Seven elements, one working map"],
      registry: ["REGISTRY", "Governed relationships"],
    };
    document.getElementById("view-kicker").textContent = titles[state.view][0];
    document.getElementById("view-title").textContent = titles[state.view][1];
    document
      .querySelectorAll(".nav-item")
      .forEach((item) =>
        item.classList.toggle("active", item.dataset.view === state.view),
      );
    if (state.view === "workbench") root.append(workbenchView());
    if (state.view === "projects") root.append(projectsView());
    if (state.view === "skills") root.append(skillsView());
    if (state.view === "universe") root.append(universeView());
    if (state.view === "registry") root.append(registryView());
    syncLiveRegion();
  }
  function workbenchView() {
    const section = el("section");
    if (state.error) section.append(showError());
    section.append(
      el("div", { class: "hero" }, [
        el("div", { class: "kicker-line" }, [
          el("b", { text: "A GOOD PLACE TO BEGIN" }),
          el("span", { text: "·" }),
          el("span", { text: "AskJamie Found-Ry" }),
        ]),
        el("h2", { text: "Make the next step easier to see." }),
        el("p", {
          text: "Shape a capability with a clear brief, a dependable behavior, and evidence you can return to. Your saved work stays local and private.",
        }),
      ]),
    );
    const grid = el("div", { class: "overview-grid" });
    if (state.loading) {
      grid.append(
        el(
          "article",
          {
            class: "desk-card status-box empty-card loading-box",
            role: "status",
            "aria-live": "polite",
            "aria-atomic": "true",
          },
          [
            el("div", {
              class: "empty-stamp",
              text: state.projects.length
                ? "Refreshing saved work"
                : "Loading saved work",
            }),
            el("h3", {
              text: state.projects.length
                ? "The desk is reconnecting"
                : "Getting the desk ready",
            }),
            el("p", {
              text: state.projects.length
                ? "The saved projects list is being refreshed."
                : "Saved projects are loading. The first screen is still coming together.",
            }),
          ],
        ),
      );
    }
    const card = el("article", { class: "desk-card empty-card" });
    card.append(
      el("div", {
        class: "empty-stamp",
        text: state.projects.length
          ? `${state.projects.length} project${state.projects.length === 1 ? "" : "s"} on the desk`
          : "The desk is ready",
      }),
    );
    card.append(
      el("h3", {
        text: state.projects.length
          ? "Continue a capability"
          : "Nothing has been saved yet",
      }),
    );
    card.append(
      el("p", {
        text: state.projects.length
          ? "Pick up a draft from Projects, or open a fresh starting point."
          : "Choose a starting point when you know what you want to shape. The blank state is intentional.",
      }),
    );
    const actions = el("div", { class: "card-actions" });
    actions.append(
      button("＋ Create a project", "primary-button", () => openDialog()),
    );
    if (state.projects.length)
      actions.append(
        button("Open Projects", "quiet-button", () => navigate("projects")),
      );
    card.append(actions);
    grid.append(card);
    const side = el("article", { class: "desk-card" });
    side.append(
      el("h3", { text: "A steady rhythm" }),
      el("p", { text: "The workbench keeps the important questions close." }),
    );
    const facts = [
      ["01", "Brief", "Name the purpose before polishing the package."],
      ["02", "Behavior", "Make the promise and boundaries visible."],
      ["03", "Evidence", "Keep sources and checks attached to the work."],
    ];
    side.append(
      el(
        "div",
        { class: "fact-list" },
        facts.map(([mark, title, desc]) =>
          el("div", { class: "fact" }, [
            el("span", { class: "fact-mark", text: mark }),
            el("div", {}, [
              el("strong", { text: title }),
              el("span", { text: desc }),
            ]),
          ]),
        ),
      ),
    );
    grid.append(side);
    section.append(grid);
    const strip = el("section", {
      class: "desk-card",
      style: "margin-top:22px",
    });
    strip.append(
      el("h3", { text: "Three useful starts" }),
      el("p", {
        text: "These are templates, not seeded projects. Choose one to open the Create dialog, then save it explicitly.",
      }),
    );
    const stripGrid = el("div", { class: "template-strip" });
    [
      [
        "blank",
        "Blank capability",
        "A clean brief for an assistant or new idea.",
      ],
      [
        "decision-tool",
        "Decision guide",
        "A visible yes / no path with a deterministic preview.",
      ],
      [
        "workflow",
        "Guided workflow",
        "An ordered sequence with room for judgment.",
      ],
    ].forEach(([kind, title, text]) => {
      const b = button("", "mini-template", () => openDialog(kind));
      b.append(el("strong", { text: title }), el("span", { text }));
      stripGrid.append(b);
    });
    strip.append(stripGrid);
    section.append(strip);
    return section;
  }
  function projectsView() {
    const section = el("section");
    section.append(
      makeHeader(
        "THE PROJECT SHELF",
        "Saved capability projects",
        "Drafts are editable, revisioned, and private. No project is implied until you save it.",
         el("div", { class: "top-actions" }, [
           button("Download backup", "quiet-button", downloadBackup),
           button("Import backup", "quiet-button", chooseBackup),
           button("＋ New project", "primary-button", () => openDialog()),
         ]),
      ),
    );
    if (state.error) section.append(showError());
    const layout = el("div", { class: "project-layout" });
    const list = el("aside", { class: "panel project-list" });
    list.append(
      el("div", { class: "project-list-head" }, [
        el("span", { text: `${state.projects.length} saved` }),
        el("span", { text: "local" }),
      ]),
    );
    if (!state.projects.length)
      list.append(
        el("p", {
          class: "field-hint",
          style: "padding:12px",
          text: "Saved projects will appear here.",
        }),
      );
    state.projects.forEach((project) => {
      const row = button(
        "",
        `project-row${state.current && state.current.id === project.id ? " selected" : ""}`,
        () => loadProject(project.id),
      );
      row.append(
        el("strong", { text: project.title || "Untitled capability" }),
        el("small", {
          text: `${project.code || "no code"} · revision ${project.revision || 0}`,
        }),
      );
      list.append(row);
    });
    layout.append(list);
    if (state.loadingProjectId) {
      const loading = el("article", {
        class: "panel desk-card empty-card status-box",
        role: "status",
        "aria-live": "polite",
        "aria-atomic": "true",
      });
      loading.append(
        el("div", { class: "empty-stamp", text: "Loading project" }),
        el("h3", { text: "Reopening the saved revision" }),
        el("p", {
          text: "The selected project is loading. Keep the list open while the saved copy catches up.",
        }),
      );
      layout.append(loading);
    } else if (state.current) layout.append(editorView());
    else {
      const empty = el("article", { class: "panel desk-card empty-card" });
      empty.append(
        el("div", { class: "empty-stamp", text: "Choose a project" }),
        el("h3", { text: "The editor is waiting" }),
        el("p", {
          text: "Select a saved project, or create a template draft to begin shaping one.",
        }),
      );
      layout.append(empty);
    }
    section.append(layout);
    return section;
  }
  function editorView() {
    const project = state.current;
    const editor = el("article", { class: "panel editor" });
    const head = el("div", { class: "editor-head" });
    const heading = el("div");
    heading.append(
      el("div", { class: "kicker-line" }, [
        el("b", { text: project.code || "AJ05" }),
        el("span", { text: ` / ${project.kind || "assistant"}` }),
      ]),
      el("h2", { text: project.title || "Untitled capability" }),
      el("p", {
        text: `${project.visibility || "private"} · revision ${project.revision || 0}`,
      }),
    );
    head.append(
      heading,
      el("div", { class: "editor-head-actions" }, [
        el("div", {
          class: `save-state${project._dirty ? " dirty" : ""}`,
          role: "status",
          "aria-live": "polite",
          "aria-atomic": "true",
          text: project._dirty ? "Unsaved changes" : "Saved locally",
        }),
        button("Duplicate", "quiet-button", duplicateProject),
        button("Delete", "danger-button", deleteProject),
      ]),
    );
    const lifecycle = el("div", { class: "lifecycle-strip" });
    lifecycle.append(
      el("span", { class: "badge", text: `Phase: ${project.phase || "draft"}` }),
      el("span", {
        class: "badge neutral",
        text: `Target: ${project.target || "offline-specification"}`,
      }),
      el("span", {
        class: "field-hint",
        text: "Reference → shape → evidence → review",
      }),
    );
    editor.append(lifecycle);
    editor.append(head);
    if (state.error) editor.append(showError());
    if (state.notice)
      editor.append(
        el("div", {
          class: "success-box status-box",
          role: "status",
          "aria-live": "polite",
          "aria-atomic": "true",
          text: state.notice,
        }),
      );
    if (state.recovery && state.recovery.projectId === project.id) {
      const recovery = el("div", {
        class: "recovery-box status-box",
        role: "status",
        "aria-live": "polite",
        "aria-atomic": "true",
      });
      recovery.append(
        el("strong", { text: "Stale save detected" }),
        el("p", { text: state.recovery.message }),
        el("div", { class: "card-actions" }, [
          button("Reload saved copy", "quiet-button", () =>
            loadProject(project.id, true),
          ),
        ]),
      );
      editor.append(recovery);
    }
    const tabs = el("div", { class: "editor-tabs", role: "tablist" });
    [
      ["brief", "Brief"],
      ["behavior", "Behavior"],
      [
        project.kind === "workflow" ? "workflow" : "decision",
        "Decision / Workflow",
      ],
      ["evidence", "Evidence"],
      ["package", "Package"],
    ].forEach(([key, label]) => {
      const b = button(
        label,
        `editor-tab${state.tab === key ? " active" : ""}`,
        () => {
          state.tab = key;
          render();
        },
      );
      b.setAttribute("role", "tab");
      b.setAttribute("aria-selected", state.tab === key);
      tabs.append(b);
    });
    editor.append(tabs);
    if (state.tab === "brief") editor.append(briefPanel(project));
    if (state.tab === "behavior") editor.append(behaviorPanel(project));
    if (state.tab === "decision") editor.append(decisionPanel(project));
    if (state.tab === "workflow") editor.append(workflowPanel(project));
    if (state.tab === "evidence") editor.append(evidencePanel(project));
    if (state.tab === "package") editor.append(packagePanel(project));
    const footer = el("div", { class: "editor-footer" });
    footer.append(
      el("span", {
        class: "field-hint",
        text: "Changes are held here until you save.",
      }),
    );
    const actions = el("div", { class: "top-actions" });
    const save = button("Save changes", "primary-button", saveProject);
    save.disabled = state.saving;
    actions.append(save);
    footer.append(actions);
    editor.append(footer);
    return editor;
  }
  function briefPanel(p) {
    const form = el("div", { class: "field-grid" });
    form.append(
      field("Title", "title", p.title),
      field("Slug", "slug", p.slug, {
        hint: "Lowercase letters, digits, and single interior hyphens.",
      }),
      field("Capability code", "code", p.code, {
        hint: "Default AJ05. Reserved codes are checked at export.",
      }),
      field("Family", "family", p.family, {
        select: true,
        options: [
          ["core-capability", "Core capability"],
          ["brandguard", "BrandGuard"],
          ["enterprise-sleuth", "Enterprise Sleuth"],
          ["client-overlay", "Client overlay"],
          ["conversation-design", "Conversation design"],
          ["rag-experiment", "RAG experiment"],
        ],
      }),
      field("Kind", "kind", p.kind, {
        select: true,
        options: [
          ["assistant", "Assistant"],
          ["decision-tool", "Decision tool"],
          ["workflow", "Workflow"],
        ],
      }),
      field("Audience", "audience", p.audience),
      field("Purpose", "purpose", p.purpose, { full: true, textarea: true }),
      field("Constraints", "constraints", p.constraints, {
        full: true,
        textarea: true,
      }),
      field("Delivery target", "target", p.target, {
        select: true,
        options: [
          ["offline-specification", "Offline specification"],
          ["openai-custom-gpt", "OpenAI Custom GPT"],
          ["microsoft-copilot", "Microsoft Copilot"],
          ["gemini-gem", "Gemini Gem"],
          ["workflow-checklist", "Workflow checklist"],
        ],
        hint: "A planning target only. Nothing is provisioned by this workbench.",
      }),
      field("Lifecycle phase", "phase", p.phase, {
        select: true,
        options: [
          ["draft", "Draft"],
          ["shaping", "Shaping"],
          ["evidence", "Evidence"],
          ["review", "Ready for review"],
        ],
      }),
    );
    return form;
  }
  function behaviorPanel(p) {
    const panel = el("div");
    const form = el("div", { class: "field-grid" });
    form.append(
      field("Instructions", "instructions", p.instructions, {
        full: true,
        textarea: true,
        rows: 7,
      }),
      field("Output contract", "output_contract", p.output_contract, {
        full: true,
        textarea: true,
        rows: 5,
      }),
    );
    const heading = el("div", { class: "subsection-head" });
    heading.append(el("h4", { text: "Protection and lineage" }));
    form.append(heading);
    form.append(
      field("Client organization", "client_org", p.client_org),
      field("Parent capability", "parent_capability", p.parent_capability),
      field("Visibility lock", "visibility_lock", p.visibility_lock, {
        hint: "Permanent private is irreversible once protected.",
      }),
    );
    const toggle = el("label", { class: "toggle-row", for: "bfs-firewall" });
    const check = el("input", { id: "bfs-firewall", type: "checkbox" });
    check.checked = !!p.bfs_firewall;
    check.addEventListener("change", () =>
      updateDraft("bfs_firewall", check.checked),
    );
    toggle.append(
      check,
      el("span", { text: "BFS firewall: keep client-bound material isolated" }),
    );
    form.append(toggle);
    panel.append(form);
    panel.append(evaluationEditor(p));
    return panel;
  }
  function evaluationEditor(p) {
    const panel = el("div");
    const heading = el("div", { class: "subsection-head" });
    heading.append(
      el("h4", { text: "Evaluation cases" }),
      button("＋ Add case", "quiet-button", () => {
        p.eval_cases = [
          ...(p.eval_cases || []),
          p.kind === "decision-tool"
            ? { name: "New path", answers: {}, expected_result: "" }
            : {
                name: "New response check",
                input: "",
                response: "",
                required: [],
                forbidden: [],
              },
        ];
        p._dirty = true;
        render();
      }),
    );
    panel.append(heading);
    const list = el("div", { class: "guided-list" });
    (p.eval_cases || []).forEach((item, index) => {
      const card = el("div", { class: "node-card" });
      const header = el("header");
      header.append(
        el("strong", { text: `CASE ${index + 1}` }),
        button("Remove", "icon-button", () => {
          p.eval_cases.splice(index, 1);
          p._dirty = true;
          render();
        }),
      );
      card.append(header);
      card.append(field("Case name", `case-name-${index}`, item.name || ""));
      card
        .querySelector(`#field-case-name-${index}`)
        .addEventListener("input", (event) => {
          item.name = event.target.value;
          p._dirty = true;
        });
      if (p.kind === "decision-tool") {
        (p.decision?.nodes || [])
          .filter((node) => node.question !== undefined)
          .forEach((node, questionIndex) => {
            const label = el("label", {
              text: `${node.id}: ${node.question}`,
              for: `answer-${index}-${questionIndex}`,
            });
            const select = el("select", {
              id: `answer-${index}-${questionIndex}`,
            });
            [
              ["", "Unanswered"],
              ["true", "Yes"],
              ["false", "No"],
            ].forEach(([value, text]) =>
              select.append(el("option", { value, text })),
            );
            select.value =
              item.answers?.[node.id] === undefined
                ? ""
                : String(item.answers[node.id]);
            select.addEventListener("change", () => {
              item.answers ||= {};
              if (select.value === "") delete item.answers[node.id];
              else item.answers[node.id] = select.value === "true";
              p._dirty = true;
            });
            card.append(label, select);
          });
        card.append(
          field(
            "Expected result",
            `case-result-${index}`,
            item.expected_result || "",
            { textarea: true },
          ),
        );
        card
          .querySelector(`#field-case-result-${index}`)
          .addEventListener("input", (event) => {
            item.expected_result = event.target.value;
            p._dirty = true;
          });
      } else {
        card.append(
          field("Input", `case-input-${index}`, item.input || "", {
            textarea: true,
          }),
          field(
            "Supplied response",
            `case-response-${index}`,
            item.response || "",
            { textarea: true },
          ),
          field(
            "Required phrases",
            `case-required-${index}`,
            (item.required || []).join(", "),
            { hint: "Comma-separated exact checks. This does not run an AI." },
          ),
          field(
            "Forbidden phrases",
            `case-forbidden-${index}`,
            (item.forbidden || []).join(", "),
            { hint: "Comma-separated exact checks." },
          ),
        );
        ["input", "response"].forEach((key) =>
          card
            .querySelector(`#field-case-${key}-${index}`)
            .addEventListener("input", (event) => {
              item[key] = event.target.value;
              p._dirty = true;
            }),
        );
        ["required", "forbidden"].forEach((key) =>
          card
            .querySelector(`#field-case-${key}-${index}`)
            .addEventListener("input", (event) => {
              item[key] = event.target.value
                .split(",")
                .map((value) => value.trim())
                .filter(Boolean);
              p._dirty = true;
            }),
        );
      }
      list.append(card);
    });
    if (!(p.eval_cases || []).length)
      list.append(
        el("p", {
          class: "field-hint",
          text: "No cases yet. An empty suite is recorded as unrun, not passed.",
        }),
      );
    panel.append(list);
    return panel;
  }
  function workflowPanel(p) {
    const panel = el("div");
    const head = el("div", { class: "subsection-head" }, [
      el("h4", { text: "Ordered workflow steps" }),
      button("＋ Add step", "quiet-button", () => {
        p.workflow_steps = [...(p.workflow_steps || []), "New step"];
        p._dirty = true;
        render();
      }),
    ]);
    panel.append(head);
    const list = el("div", { class: "guided-list" });
    (p.workflow_steps || []).forEach((step, index) => {
      const item = el("div", { class: "guided-item" });
      item.append(
        el("span", {
          class: "guided-number",
          text: String(index + 1).padStart(2, "0"),
        }),
      );
      const input = el("input", {
        value: step,
        "aria-label": `Workflow step ${index + 1}`,
      });
      input.addEventListener("input", () => {
        p.workflow_steps[index] = input.value;
        p._dirty = true;
      });
      item.append(
        input,
        el("div", { class: "inline-actions" }, [
          button("×", "icon-button", () => {
            p.workflow_steps.splice(index, 1);
            p._dirty = true;
            render();
          }),
        ]),
      );
      list.append(item);
    });
    panel.append(list);
    return panel;
  }
  function decisionPanel(p) {
    if (!p.decision || !Array.isArray(p.decision.nodes))
      p.decision = draftDefaults("decision-tool").decision;
    const panel = el("div");
    panel.append(
      el("p", {
        class: "field-hint",
        text: "Build the path in plain language. Preview follows the answers you provide and stops at the first unanswered question.",
      }),
    );
    panel.append(field("Start node ID", "decision-start", p.decision.start));
    panel
      .querySelector("#field-decision-start")
      .addEventListener("input", (event) => {
        p.decision.start = event.target.value;
        p._dirty = true;
      });
    const list = el("div", { class: "guided-list" });
    p.decision.nodes.forEach((node, index) => {
      const card = el("div", { class: "node-card" });
      const header = el("header");
      header.append(
        el("strong", {
          text:
            node.id === p.decision.start ? "START NODE" : `NODE ${index + 1}`,
        }),
        button("Remove", "icon-button", () => {
          p.decision.nodes.splice(index, 1);
          p._dirty = true;
          render();
        }),
      );
      card.append(header);
      card.append(
        field("Node ID", `node-id-${index}`, node.id, {
          hint: "Use short lowercase IDs.",
        }),
      );
      card
        .querySelector(`#field-node-id-${index}`)
        .addEventListener("input", (event) => {
          node.id = event.target.value;
          p._dirty = true;
        });
      if (node.question !== undefined) {
        card.append(
          field("Question", `node-q-${index}`, node.question, {
            textarea: true,
          }),
        );
        card
          .querySelector(`#field-node-q-${index}`)
          .addEventListener("input", (event) => {
            node.question = event.target.value;
            p._dirty = true;
          });
        card.append(
          field("Yes → node ID", `node-y-${index}`, node.yes || ""),
          field("No → node ID", `node-n-${index}`, node.no || ""),
        );
        ["y", "n"].forEach((dir) =>
          card
            .querySelector(`#field-node-${dir}-${index}`)
            .addEventListener("input", (event) => {
              node[dir === "y" ? "yes" : "no"] = event.target.value;
              p._dirty = true;
            }),
        );
      } else {
        card.append(
          field("Result", `node-r-${index}`, node.result || "", {
            textarea: true,
          }),
        );
        card
          .querySelector(`#field-node-r-${index}`)
          .addEventListener("input", (event) => {
            node.result = event.target.value;
            p._dirty = true;
          });
      }
      list.append(card);
    });
    panel.append(list);
    const add = el("div", { class: "card-actions" });
    add.append(
      button("＋ Question node", "quiet-button", () => {
        p.decision.nodes.push({
          id: `question-${p.decision.nodes.length}`,
          question: "What should we check?",
          yes: "",
          no: "",
        });
        p._dirty = true;
        render();
      }),
      button("＋ Result node", "quiet-button", () => {
        p.decision.nodes.push({
          id: `result-${p.decision.nodes.length}`,
          result: "Add the outcome.",
        });
        p._dirty = true;
        render();
      }),
    );
    panel.append(add);
    const preview = el("div", {
      class: "panel",
      style: "margin-top:20px;padding:15px",
    });
    preview.append(
      el("h3", { text: "Preview path" }),
      el("p", {
        class: "field-hint",
        text: p._dirty
          ? "Save changes before running the deterministic preview."
          : `Runs saved revision ${p.revision}. Choose answers to explore the path.`,
      }),
    );
    if (state.preview) {
      preview.append(
        el("p", {
          text: state.preview.complete
            ? state.preview.result
            : state.preview.next
              ? state.preview.next.question
              : "The path needs attention.",
        }),
      );
      if (!state.preview.complete && state.preview.next) {
        const answerRow = el("div", { class: "card-actions" });
        answerRow.append(
          button("Yes", "primary-button", () =>
            runPreview({
              ...state.previewAnswers,
              [state.preview.next.id]: true,
            }),
          ),
          button("No", "quiet-button", () =>
            runPreview({
              ...state.previewAnswers,
              [state.preview.next.id]: false,
            }),
          ),
        );
        preview.append(answerRow);
      }
      preview.append(
        button("Restart preview", "quiet-button", () => runPreview({})),
      );
    } else
      preview.append(
        button("Start preview", "primary-button", () => runPreview({})),
      );
    panel.append(preview);
    return panel;
  }
  function evidencePanel(p) {
    const panel = el("div");
    panel.append(
      field("Source text", "source_text", p.source_text, {
        full: true,
        textarea: true,
        rows: 8,
      }),
      field("Source reference", "source_reference", p.source_reference, {
        full: true,
        hint: "A provenance note or stable locator. This does not fetch remote content.",
      }),
      field("Evidence notes", "evidence", p.evidence, {
        full: true,
        textarea: true,
        rows: 4,
        hint: "Record what has been checked and what remains unknown.",
      }),
    );
    const heading = el("div", { class: "subsection-head" });
    heading.append(el("h4", { text: "Skillz references" }));
    panel.append(heading);
    const skillSearch = el("input", {
      type: "search",
      placeholder: "Search all Skillz metadata",
      "aria-label": "Search Skillz metadata",
    });
    const toolbar = el("div", { class: "catalog-toolbar" }, [skillSearch]);
    panel.append(toolbar);
    const picker = el("div", { class: "skill-picker" });
    const selected = new Set(p.skill_ids || []);
    const renderSkillChoices = () => {
      picker.replaceChildren();
      const term = skillSearch.value.toLowerCase();
      const skills = state.skills.filter((skill) =>
        `${skill.id} ${skill.name} ${skill.family} ${skill.description}`
          .toLowerCase()
          .includes(term),
      );
      if (!skills.length) {
        picker.append(
          el("p", {
            class: "field-hint",
            text: state.skills.length
              ? "No Skillz entries match that search."
              : "Start the backend to load the committed Skillz snapshot.",
          }),
        );
      }
      skills.forEach((skill) => {
        const label = el("label", { class: "skill-choice" });
        const input = el("input", { type: "checkbox", value: skill.id });
        input.checked = selected.has(skill.id);
        input.addEventListener("change", () => {
          p.skill_ids = [
            ...(p.skill_ids || []).filter((id) => id !== skill.id),
            ...(input.checked ? [skill.id] : []),
          ];
          p._dirty = true;
        });
        const text = el("span");
        text.append(
          el("strong", { text: skill.name || skill.id }),
          el("small", { text: skill.description || "Catalog metadata" }),
        );
        text.append(
          el("div", { class: "skill-meta" }, [
            el("span", {
              class: "badge",
              text: skill.family || "unclassified",
            }),
            el("span", {
              class: "badge neutral",
              text: skill.maturity || "unknown",
            }),
            el("span", {
              class: "badge neutral",
              text: skill.evidenceStatus || "unverified",
            }),
          ]),
        );
        label.append(input, text);
        picker.append(label);
      });
    };
    skillSearch.addEventListener("input", renderSkillChoices);
    renderSkillChoices();
    panel.append(picker);
    return panel;
  }
  function packagePanel(p) {
    const panel = el("div");
    panel.append(
      el("p", {
        text: "The package is private by default. Validate before export. A registry proposal may be included in an export, but the canonical registry is never updated by saving.",
      }),
    );
    const actions = el("div", { class: "card-actions" });
    actions.append(
      button("Validate project", "quiet-button", validateProject),
      button("Run evaluations", "quiet-button", runEvaluations),
      button("Download private ZIP", "primary-button", exportProject),
    );
    panel.append(actions);
    if (state.evaluation) {
      const resultBox = el("div", {
        class: "panel",
        style: "margin-top:20px;padding:15px",
      });
      resultBox.append(
        el("h3", { text: "Latest evaluation" }),
        el("p", {
          class: "field-hint",
          text: `Revision ${state.evaluation.revision} · ${state.evaluation.evaluated_at || "recorded now"}`,
        }),
      );
      if (state.evaluation.revision !== p.revision)
        resultBox.append(
          el("p", {
            class: "field-hint",
            text: "These results belong to an earlier revision. Run evaluations again to check the current draft.",
          }),
        );
      const cases = el("div", { class: "guided-list" });
      (state.evaluation.cases || []).forEach((item) => {
        const row = el("div", { class: "guided-item evidence-row" });
        row.append(
          el("strong", { text: item.name || "Unnamed case" }),
          el("span", {
            class: `badge ${["pass", "passed"].includes(item.status) ? "" : "neutral"}`,
            text: item.status || "unrun",
          }),
          el("span", { class: "field-hint", text: item.detail || "" }),
        );
        cases.append(row);
      });
      resultBox.append(cases);
      panel.append(resultBox);
    }
    const historyBox = el("div", {
      class: "panel",
      style: "margin-top:20px;padding:15px",
    });
    historyBox.append(
      el("h3", { text: "Revision history" }),
      el("p", {
        class: "field-hint",
        text: state.history.length
          ? "Saved snapshots are retained by the backend."
          : "No saved history is available yet.",
      }),
    );
    const historyList = el("div", { class: "guided-list" });
    state.history.forEach((item) => {
      const row = el("div", { class: "guided-item evidence-row" });
      row.append(
        el("strong", { text: `Revision ${item.revision}` }),
        el("span", { class: "field-hint", text: item.updated_at || "" }),
      );
      historyList.append(row);
    });
    historyBox.append(historyList);
    panel.append(historyBox);
    return panel;
  }
  async function saveProject() {
    if (!state.current || state.saving) return;
    state.saving = true;
    render();
    const p = draftPayload(state.current);
    const projectId = state.current.id;
    try {
      const saved = projectId
        ? await api(`/api/projects/${encodeURIComponent(projectId)}`, {
            method: "PUT",
            body: JSON.stringify({ ...p, revision: state.current.revision }),
          })
        : await api("/api/projects", {
            method: "POST",
            body: JSON.stringify(p),
          });
      state.current = saved;
      state.preview = null;
      state.previewAnswers = {};
      const history = await api(
        `/api/projects/${encodeURIComponent(saved.id)}/history`,
      );
      state.history = history.history || [];
      state.projects = [
        ...state.projects.filter((item) => item.id !== saved.id),
        saved,
      ];
      state.notice = "Saved. The desk has a new revision.";
      state.error = "";
      state.recovery = null;
      await loadProjects();
      state.saving = false;
      render();
      announce("Project saved");
    } catch (error) {
      state.saving = false;
      state.notice = "";
      state.error = error.message;
      state.recovery = error.message.includes("stale revision")
        ? {
            projectId,
            message:
              "The saved copy changed while you were editing. Reload the saved copy to reconcile, or keep editing and save again.",
          }
        : null;
      render();
    }
  }
  async function createProject(kind) {
    if (!canLeaveCurrent()) return;
    kind = kind === "blank" ? "assistant" : kind;
    const payload = template(kind);
    try {
      const saved = await api("/api/projects", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      state.projects.push(saved);
      state.current = saved;
      state.view = "projects";
      state.tab = "brief";
      state.error = "";
      state.notice = "Draft created. Nothing is published.";
      state.preview = null;
      state.previewAnswers = {};
      state.evaluation = null;
      state.history = [];
      state.recovery = null;
      await loadProjects();
      render();
      announce("Draft created");
    } catch (error) {
      state.error = error.message;
      render();
    }
  }
  async function validateProject() {
    if (!requireSavedProject("validating")) return;
    try {
      const result = await api(
        `/api/projects/${encodeURIComponent(state.current.id)}/validate`,
      );
      state.notice = result.valid
        ? `Ready to export: ${result.repo || "private package"}.`
        : `Needs attention: ${(result.errors || []).join(" ")}`;
      state.error =
        result.warnings && result.warnings.length
          ? result.warnings.join(" ")
          : "";
      state.recovery = null;
      render();
    } catch (error) {
      state.error = error.message;
      render();
    }
  }
  async function runPreview(answers = state.previewAnswers) {
    if (!requireSavedProject("running a preview")) return;
    try {
      state.previewAnswers = answers;
      const result = await api(
        `/api/projects/${encodeURIComponent(state.current.id)}/preview`,
        { method: "POST", body: JSON.stringify({ answers }) },
      );
      state.preview = result;
      state.notice = "";
      state.error = "";
      render();
    } catch (error) {
      state.error = error.message;
      render();
    }
  }
  async function runEvaluations() {
    if (!requireSavedProject("running evaluations")) return;
    try {
      const result = await api(
        `/api/projects/${encodeURIComponent(state.current.id)}/evaluate`,
        { method: "POST", body: "{}" },
      );
      state.evaluation = result;
      state.notice = `Evaluated revision ${result.revision}: ${result.passed} passed, ${result.failed} failed, ${result.unrun} unrun.`;
      render();
    } catch (error) {
      state.error = error.message;
      render();
    }
  }
  async function exportProject() {
    if (!requireSavedProject("exporting")) return;
    try {
      const response = await api(
        `/api/projects/${encodeURIComponent(state.current.id)}/export`,
      );
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${state.current.slug || "askjamie-project"}.zip`;
      document.body.append(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
      announce("Private ZIP downloaded");
    } catch (error) {
      state.error = error.message;
      render();
    }
  }
  async function downloadBackup() {
    try {
      const response = await api("/api/backup");
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "askjamie-workbench-backup-v1.json";
      document.body.append(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
      state.notice = "Private backup downloaded.";
      state.error = "";
      render();
      announce("Private backup downloaded");
    } catch (error) {
      state.error = error.message;
      render();
    }
  }
  function chooseBackup() {
    const input = el("input", {
      type: "file",
      accept: "application/json,.json",
      "aria-label": "Choose a workbench backup",
    });
    input.addEventListener("change", () => {
      if (input.files?.[0]) importBackup(input.files[0]);
    });
    input.click();
  }
  async function importBackup(file) {
    if (!canLeaveCurrent()) return;
    const confirmed = window.confirm(
      "Importing a backup replaces every saved local project, its history, and evaluations. Continue?",
    );
    if (!confirmed) return;
    try {
      const backup = JSON.parse(await file.text());
      const result = await api("/api/import", {
        method: "POST",
        body: JSON.stringify({ backup, confirm: true }),
      });
      state.current = null;
      state.history = [];
      state.evaluation = null;
      state.preview = null;
      state.previewAnswers = {};
      state.recovery = null;
      state.notice = `Imported ${result.imported} project${result.imported === 1 ? "" : "s"}.`;
      state.error = "";
      await loadProjects();
      render();
      announce("Backup imported");
    } catch (error) {
      state.error = `Backup import failed: ${error.message}`;
      render();
    }
  }
  async function duplicateProject() {
    if (!requireSavedProject("duplicating")) return;
    if (
      !window.confirm(
        "Duplicate this saved project as a new private draft without its evaluation history?",
      )
    )
      return;
    try {
      const duplicate = await api(
        `/api/projects/${encodeURIComponent(state.current.id)}/duplicate`,
        { method: "POST", body: JSON.stringify({ confirm: true }) },
      );
      state.current = duplicate;
      state.history = [{ revision: 1, updated_at: duplicate.updated_at }];
      state.evaluation = null;
      state.preview = null;
      state.previewAnswers = {};
      state.notice = "Private copy created. Its evaluation history starts fresh.";
      state.error = "";
      await loadProjects();
      render();
      announce("Project duplicated");
    } catch (error) {
      state.error = error.message;
      render();
    }
  }
  async function deleteProject() {
    if (!requireSavedProject("deleting")) return;
    if (
      !window.confirm(
        "Delete this saved project, its revision history, and evaluations? This cannot be undone.",
      )
    )
      return;
    const projectId = state.current.id;
    try {
      await api(`/api/projects/${encodeURIComponent(projectId)}`, {
        method: "DELETE",
        body: JSON.stringify({ confirm: true }),
      });
      state.current = null;
      state.history = [];
      state.evaluation = null;
      state.preview = null;
      state.previewAnswers = {};
      state.notice = "Project deleted from the local workbench.";
      state.error = "";
      await loadProjects();
      render();
      announce("Project deleted");
    } catch (error) {
      state.error = error.message;
      render();
    }
  }
  function navigate(view) {
    if (view === state.view || !canLeaveCurrent()) return;
    state.view = view;
    state.error = "";
    state.notice = "";
    state.recovery = null;
    render();
    if (view === "skills" && !state.skills.length)
      api("/api/skills")
        .then((data) => {
          state.skills = data.skills || [];
          render();
        })
        .catch(() => {});
    if (view === "registry" && !state.registry)
      api("/api/registry")
        .then((data) => {
          state.registry = data;
          render();
        })
        .catch((error) => {
          state.error = error.message;
          render();
        });
  }
  function skillsView() {
    const section = el("section");
    section.append(
      makeHeader(
        "SHARED REFERENCE",
        "Skillz catalog",
        "A read-only view of the committed Skillz metadata snapshot. A selected contract is reference, not execution.",
      ),
    );
    const toolbar = el("div", { class: "catalog-toolbar" });
    const search = el("input", {
      type: "search",
      placeholder: "Search names, families, descriptions",
      "aria-label": "Search Skillz catalog",
    });
    toolbar.append(search);
    section.append(toolbar);
    const grid = el("div", { class: "catalog-grid" });
    const renderCards = () => {
      grid.replaceChildren();
      const term = search.value.toLowerCase();
      const skills = state.skills.filter((skill) =>
        `${skill.name} ${skill.family} ${skill.description}`
          .toLowerCase()
          .includes(term),
      );
      if (!skills.length)
        grid.append(
          el("p", {
            class: "field-hint",
            text: state.skills.length
              ? "No catalog entries match that search."
              : "Start the backend to load the committed metadata snapshot.",
          }),
        );
      skills.slice(0, 60).forEach((skill) => {
        const card = el("article", { class: "catalog-card" });
        card.append(
          el("h3", { text: skill.name || skill.id }),
          el("p", { text: skill.description || "No description recorded." }),
        );
        card.append(
          el("span", { class: "badge", text: skill.family || "unclassified" }),
          el("span", {
            class: "badge neutral",
            text: `${skill.maturity || "unknown"} · ${skill.evidenceStatus || "unverified"}`,
          }),
        );
        if (skill.sourceUrl)
          card.append(
            el("p", { style: "margin-top:10px" }, [
              el("a", {
                href: skill.sourceUrl,
                target: "_blank",
                rel: "noreferrer",
                text: "View source ↗",
              }),
            ]),
          );
        grid.append(card);
      });
    };
    search.addEventListener("input", renderCards);
    renderCards();
    section.append(grid);
    return section;
  }
  function universeView() {
    const section = el("section");
    section.append(
      makeHeader(
        "THE SEVEN ELEMENTS",
        "Seven elements, one working map",
        "OverKill is the centroid and baseline pattern. Its Found-Ry mentors the regional Found-Rys, and each can learn from the others.",
      ),
    );
    const map = el("div", { class: "universe-map" });
    [
      ["ask", "AskJamie", "Interpretive intelligence and clear next steps."],
      [
        "overkill",
        "OverKill Hill",
        "Centroid, baseline pattern, and systems practice.",
      ],
      [
        "glee",
        "Glee-fully Tools",
        "Approachable personal tools and everyday execution.",
      ],
    ].forEach(([className, title, desc]) => {
      const ring = el("div", { class: `ring ${className}` });
      ring.append(
        el("span", { text: title }),
        el("span", { class: "ring-tag", text: desc }),
      );
      map.append(ring);
    });
    map.append(el("div", { class: "shared-skillz", text: "Skillz" }));
    section.append(map);
    const legend = el("div", { class: "universe-legend" });
    [
      ["OverKill Found-Ry", "Public mentor pattern and regional workbench"],
      ["Glee-fully Found-Ry", "Glee-fully fabrication and governance"],
      ["AskJamie Found-Ry", "This private capability workbench"],
      ["Skillz", "Shared, provenance-bearing catalog"],
    ].forEach(([title, desc]) =>
      legend.append(
        el("div", { class: "legend-item" }, [
          el("strong", { text: title }),
          el("span", { text: desc }),
        ]),
      ),
    );
    section.append(legend);
    section.append(el("p", { text: "AskJamie and Glee-fully borrow and adapt mentor patterns. Either may mentor OverKill Found-Ry or its peer in return. Skillz remains the shared catalog across all three regions." }));
    return section;
  }
  function registryView() {
    const section = el("section");
    section.append(
      makeHeader(
        "READ-ONLY GOVERNANCE",
        "Governed relationships",
        "The registry is a record of intent and lineage. It does not prove a remote repository exists or is operational.",
      ),
    );
    if (state.registry?.note)
      section.append(
        el("div", { class: "success-box", text: state.registry.note }),
      );
    const panel = el("div", { class: "panel", style: "padding:8px" });
    const table = el("table", { class: "registry-table" });
    table.append(
      el("thead", {}, [
        el(
          "tr",
          {},
          ["Code", "Repository", "Status", "Visibility"].map((text) =>
            el("th", { text }),
          ),
        ),
      ]),
    );
    const body = el("tbody");
    const repos = state.registry?.repositories || [];
    if (!repos.length)
      body.append(
        el("tr", {}, [
          el("td", {
            colspan: "4",
            class: "field-hint",
            text: "Start the backend to read the canonical registry.",
          }),
        ]),
      );
    repos.forEach((repo) =>
      body.append(
        el("tr", {}, [
          el("td", { text: repo.code || repo.id || "Unknown" }),
          el("td", {}, [
            el("strong", {
              text: repo.repo || repo.name || repo.repository || "Unnamed",
            }),
            el("small", {
              text: repo.display_name || repo.purpose || repo.description || "",
            }),
          ]),
          el("td", { text: repo.status || "recorded" }),
          el("td", { text: repo.visibility || "private" }),
        ]),
      ),
    );
    table.append(body);
    panel.append(table);
    section.append(panel);
    return section;
  }
  function openDialog(templateKind = "blank") {
    const dialog = document.getElementById("new-project-dialog");
    const choice = dialog.querySelector(
      `input[name="template"][value="${templateKind}"]`,
    );
    if (choice) choice.checked = true;
    dialog.showModal();
  }
  document
    .getElementById("new-project-form")
    .addEventListener("submit", (event) => {
      event.preventDefault();
      if (event.submitter?.value === "cancel") {
        event.currentTarget.closest("dialog").close();
        return;
      }
      const kind = new FormData(event.currentTarget).get("template");
      event.currentTarget.closest("dialog").close();
      createProject(kind === "blank" ? "assistant" : kind);
    });
  document
    .getElementById("new-project-button")
    .addEventListener("click", () => openDialog());
  document
    .getElementById("refresh-button")
    .addEventListener("click", async () => {
      state.loading = true;
      render();
      await loadProjects();
      if (state.current?.id) await loadProject(state.current.id);
      else render();
      state.loading = false;
      render();
      announce("Refreshed");
    });
  document
    .querySelectorAll(".nav-item")
    .forEach((item) =>
      item.addEventListener("click", () => navigate(item.dataset.view)),
    );
  window.addEventListener("beforeunload", (event) => {
    if (state.current?._dirty) {
      event.preventDefault();
      event.returnValue = "";
    }
  });
  state.loading = true;
  render();
  Promise.all([
    loadProjects(),
    api("/api/skills")
      .then((data) => {
        state.skills = data.skills || [];
      })
      .catch((error) => {
        state.error = error.message;
      }),
  ]).then(() => {
    state.loading = false;
    render();
  });
})();
