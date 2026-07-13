const logEl = document.getElementById("log");
const controlsEl = document.getElementById("controls");
const statusEl = document.getElementById("status");
const killBtn = document.getElementById("killBtn");
const liveScorecardEl = document.getElementById("liveScorecard");
const inningsSummariesEl = document.getElementById("inningsSummaries");

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
  } else if (data.type === "state") {
    renderScorecard(data.data);
  } else if (data.type === "innings") {
    renderInningsSummary(data.data);
  }
});

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s === null || s === undefined ? "" : String(s);
  return div.innerHTML;
}

function renderScorecard(state) {
  const parts = [];

  parts.push(
    '<div class="team-line"><span>' + escapeHtml(state.battingTeam) + "</span>" +
    '<span class="score">' + state.score + "/" + state.wickets + "</span></div>"
  );
  parts.push(
    '<div class="sub-line">Overs: ' + Number(state.overs).toFixed(1) + "/" + state.totalOvers +
    "  ·  CRR: " + Number(state.crr).toFixed(2) + "</div>"
  );

  if (state.target !== null && state.target !== undefined) {
    const need = Math.max(state.target - state.score, 0);
    parts.push(
      '<div class="target-line">Need ' + need + " more vs " + escapeHtml(state.bowlingTeam) +
      "  ·  RRR: " + Number(state.requiredRunRate).toFixed(2) + "</div>"
    );
  }

  parts.push("<h3>Batting</h3><table>");
  (state.batsmen || []).forEach((b) => {
    parts.push(
      "<tr" + (b.onStrike ? ' class="on-strike"' : "") + '><td class="name">' +
      escapeHtml(b.name) + '</td><td class="num">' + b.runs + " (" + b.balls + ")</td></tr>"
    );
  });
  parts.push("</table>");

  if (state.bowler) {
    parts.push(
      "<h3>Bowling</h3><table><tr>" +
      '<td class="name">' + escapeHtml(state.bowler.name) + '</td><td class="num">' +
      state.bowler.wickets + "/" + state.bowler.runs + " (" + Number(state.bowler.overs).toFixed(1) +
      ")</td></tr></table>"
    );
  }

  liveScorecardEl.innerHTML = parts.join("");
}

function renderInningsSummary(innings) {
  const parts = [];
  parts.push('<div class="innings-summary">');
  parts.push(
    '<div class="team-line"><span>' + escapeHtml(innings.battingTeam) + " innings</span>" +
    '<span class="score">' + innings.score + "/" + innings.wickets + " (" +
    Number(innings.overs).toFixed(1) + ")</span></div>"
  );
  parts.push('<div class="sub-line">Extras: ' + innings.extras + "</div>");

  parts.push("<h3>Batting</h3><table>");
  (innings.battingCard || []).forEach((b) => {
    let name = b.name;
    if (b.captain) name += " (c)";
    if (b.keeper) name += " (wk)";
    parts.push(
      '<tr><td class="name">' + escapeHtml(name) + "</td>" +
      '<td class="dismissal">' + escapeHtml(b.dismissal) + "</td>" +
      '<td class="num">' + b.runs + " (" + b.balls + ")</td></tr>"
    );
  });
  parts.push("</table>");

  parts.push("<h3>Bowling</h3><table>");
  (innings.bowlingCard || []).forEach((bw) => {
    parts.push(
      '<tr><td class="name">' + escapeHtml(bw.name) + '</td><td class="num">' +
      Number(bw.overs).toFixed(1) + "-" + bw.maidens + "-" + bw.runs + "-" + bw.wickets +
      " (" + Number(bw.economy).toFixed(2) + ")</td></tr>"
    );
  });
  parts.push("</table>");

  if ((innings.fow || []).length) {
    parts.push("<h3>Fall of Wickets</h3><div class=\"fow-line\">");
    parts.push(
      innings.fow
        .map((f) => f.runs + "/" + f.wicket + " " + escapeHtml(f.player) + " (" + Number(f.overs).toFixed(1) + ")")
        .join(", ")
    );
    parts.push("</div>");
  }

  parts.push("</div>");

  const wrapper = document.createElement("div");
  wrapper.innerHTML = parts.join("");
  inningsSummariesEl.appendChild(wrapper.firstElementChild);
}
