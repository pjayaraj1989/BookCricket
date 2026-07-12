const logEl = document.getElementById("log");
const controlsEl = document.getElementById("controls");
const statusEl = document.getElementById("status");
const killBtn = document.getElementById("killBtn");

const socket = io();

killBtn.addEventListener("click", () => {
  if (!confirm("Stop the BookCricket server? This ends the game for anyone connected.")) return;
  killBtn.disabled = true;
  killBtn.textContent = "Stopping…";
  appendLine("Server is shutting down…", "fore-lightred_ex");
  fetch("shutdown", { method: "POST" }).catch(() => {});
});

function appendLine(text, color) {
  const line = document.createElement("div");
  line.className = "line" + (color ? " c-" + color : "");
  line.textContent = text;
  logEl.appendChild(line);
  logEl.scrollTop = logEl.scrollHeight;
}

function appendChoiceEcho(text) {
  const line = document.createElement("div");
  line.className = "line echo";
  line.textContent = "> " + text;
  logEl.appendChild(line);
  logEl.scrollTop = logEl.scrollHeight;
}

function clearControls() {
  controlsEl.innerHTML = "";
}

function submit(value, echoText) {
  socket.emit("client_input", value);
  if (echoText !== undefined) appendChoiceEcho(echoText);
  clearControls();
  const p = document.createElement("p");
  p.className = "hint";
  p.textContent = "…";
  controlsEl.appendChild(p);
}

function looksLikeContinuePrompt(prompt) {
  const p = prompt.toLowerCase();
  return p.includes("continue") || p.includes("press enter") || p.includes("press any key");
}

function renderChoose(msg, options) {
  clearControls();
  const group = document.createElement("div");
  group.className = "choice-group";
  options.forEach((opt, idx) => {
    const btn = document.createElement("button");
    btn.className = "choice-btn";
    btn.textContent = idx + ". " + opt;
    btn.addEventListener("click", () => submit(opt, msg ? msg + " -> " + opt : opt));
    group.appendChild(btn);
  });
  controlsEl.appendChild(group);
}

function renderInput(prompt) {
  clearControls();
  const trimmed = (prompt || "").trim();

  if (looksLikeContinuePrompt(trimmed)) {
    const btn = document.createElement("button");
    btn.className = "choice-btn continue-btn";
    btn.textContent = "Continue ▶";
    btn.addEventListener("click", () => submit("", "continue"));
    controlsEl.appendChild(btn);
    btn.focus();
    return;
  }

  if (trimmed) {
    const label = document.createElement("p");
    label.className = "prompt";
    label.textContent = trimmed;
    controlsEl.appendChild(label);
  }

  const form = document.createElement("form");
  form.className = "input-form";
  const field = document.createElement("input");
  field.type = "text";
  field.autocomplete = "off";
  const sendBtn = document.createElement("button");
  sendBtn.type = "submit";
  sendBtn.textContent = "Send";

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    submit(field.value, field.value === "" ? "(enter)" : field.value);
  });

  form.appendChild(field);
  form.appendChild(sendBtn);
  controlsEl.appendChild(form);
  field.focus();
}

socket.on("connect", () => {
  statusEl.textContent = "connected";
  statusEl.className = "status ok";
});

socket.on("disconnect", () => {
  statusEl.textContent = "disconnected";
  statusEl.className = "status err";
  clearControls();
  const p = document.createElement("p");
  p.className = "hint";
  p.textContent = "Connection lost. Refresh the page to start a new match.";
  controlsEl.appendChild(p);
});

socket.on("server_event", (data) => {
  if (data.type === "output") {
    appendLine(data.text, data.color);
  } else if (data.type === "choose") {
    appendLine(data.msg, null);
    renderChoose(data.msg, data.options);
  } else if (data.type === "input") {
    renderInput(data.prompt);
  }
});
