const logEl = document.getElementById("log");
const controlsEl = document.getElementById("controls");
const statusEl = document.getElementById("status");
const killBtn = document.getElementById("killBtn");
const declareBtn = document.getElementById("declareBtn");
const liveScorecardEl = document.getElementById("liveScorecard");
const inningsSummariesEl = document.getElementById("inningsSummaries");
const eventPaneEl = document.getElementById("eventPane");
const runRateGraphEl = document.getElementById("runRateGraph");
const runRateLegendEl = document.getElementById("runRateLegend");
const runRateSvgEl = document.getElementById("runRateSvg");
const simOverlayEl = document.getElementById("simOverlay");
const triviaPanelEl = document.getElementById("triviaPanel");
const nextBatsmenCardEl = document.getElementById("nextBatsmenCard");
const nextBatsmenListEl = document.getElementById("nextBatsmenList");

function showSimOverlay(title, teams) {
  if (!simOverlayEl) return;
  simOverlayEl.innerHTML = "";
  const spinner = document.createElement("div");
  spinner.className = "sim-spinner";
  const t = document.createElement("div");
  t.className = "sim-title";
  t.textContent = "Simulating " + title;
  const who = document.createElement("div");
  who.className = "sim-teams";
  who.textContent = teams;
  const sub = document.createElement("div");
  sub.className = "sim-sub";
  sub.textContent = "playing out the match…";
  simOverlayEl.append(spinner, t, who, sub);
  simOverlayEl.classList.add("visible");
}

function hideSimOverlay() {
  if (simOverlayEl) simOverlayEl.classList.remove("visible");
}

const socket = io();

// persistent per-browser id: ties a resumed game back to the same browser's
// save list, even after a disconnect or a server restart
function getClientId() {
  let id = null;
  try { id = localStorage.getItem("bc_client_id"); } catch (e) {}
  if (!id) {
    id = "c-" + Math.random().toString(36).slice(2) + Date.now().toString(36);
    try { localStorage.setItem("bc_client_id", id); } catch (e) {}
  }
  return id;
}
const clientId = getClientId();
let gameStarted = false;

// intro splash: prefer a user-supplied cover (resources/misc/intro.png/jpg/
// ...), fall back to the built-in vector art; fades out on its own or on click
const introEl = document.getElementById("introSplash");
if (introEl) {
  const coverImg = introEl.querySelector("img");
  coverImg.addEventListener("error", () => { coverImg.src = "cover.svg"; }, { once: true });
  coverImg.src = "misc/intro";
  const dismissIntro = () => {
    introEl.classList.add("hide");
    setTimeout(() => introEl.remove(), 800);
  };
  introEl.addEventListener("click", dismissIntro);
  setTimeout(dismissIntro, 3500);
}

killBtn.addEventListener("click", () => {
  if (!confirm("Stop the BookCricket server? This ends the game for anyone connected.")) return;
  killBtn.disabled = true;
  killBtn.textContent = "Stopping…";
  appendLine("Server is shutting down…", "fore-lightred_ex");
  fetch("shutdown", { method: "POST" }).catch(() => {});
});

declareBtn.addEventListener("click", () => {
  socket.emit("declare_request");
  // the engine confirms at the next over boundary; freeze the button until
  // the next scorecard push so it can't be spammed meanwhile
  declareBtn.disabled = true;
  declareBtn.textContent = "🏳️ Declaring at over end…";
});

function updateDeclareButton(state) {
  if (state.declareEligible) {
    declareBtn.style.display = "";
    declareBtn.disabled = false;
    declareBtn.textContent = "🏳️ Declare";
  } else {
    declareBtn.style.display = "none";
  }
}

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
  // startsWith, not includes: prompts like "Pick next bowler: ... [Press
  // Enter to auto-select]" also mention "press enter" as a fallback hint
  // but need a real text field, not a bare Continue button.
  const p = prompt.trim().toLowerCase();
  return p.startsWith("continue") || p.startsWith("press enter") || p.startsWith("press any key");
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
  // handshake: the server replies with this browser's start menu
  socket.emit("hello", { clientId: clientId });
});

// the stop-server button only makes sense when you own the server (local
// play); on a public deployment the server says so and the button stays away
socket.on("server_config", (config) => {
  killBtn.style.display = config && config.allowShutdown ? "" : "none";
});

// start menu: New game, or resume one of this browser's saved games, or
// upload a save file. The game thread only begins once we emit "start_game".
socket.on("start_menu", (data) => {
  if (gameStarted) return;
  renderStartMenu(data || {});
});

function beginGame(payload) {
  if (gameStarted) return;
  gameStarted = true;
  clearControls();
  socket.emit("start_game", payload);
}

function renderStartMenu(data) {
  const saves = data.saves || [];
  const tournaments = data.tournaments || [];
  const canUpload = !!data.canUpload;
  const canSeries = !!data.canSeries;
  clearControls();
  const wrap = document.createElement("div");
  wrap.className = "start-menu";

  const heading = document.createElement("div");
  heading.className = "start-title";
  heading.textContent = "Welcome to BookCricket";
  wrap.appendChild(heading);

  const newBtn = document.createElement("button");
  newBtn.className = "choice-btn start-new";
  newBtn.textContent = "🏏 New game";
  newBtn.addEventListener("click", () => beginGame({ mode: "new" }));
  wrap.appendChild(newBtn);

  if (canSeries) {
    const seriesBtn = document.createElement("button");
    seriesBtn.className = "choice-btn start-series";
    seriesBtn.textContent = "🏆 New series / tournament";
    seriesBtn.addEventListener("click", () => beginGame({ mode: "series" }));
    wrap.appendChild(seriesBtn);
  }

  if (tournaments.length) {
    const title = document.createElement("div");
    title.className = "start-saves-title";
    title.textContent = "Resume a saved series";
    wrap.appendChild(title);
    const list = document.createElement("div");
    list.className = "start-saves";
    tournaments.forEach((s) => {
      const row = document.createElement("button");
      row.className = "choice-btn save-row";
      row.innerHTML = describeSeries(s);
      row.addEventListener("click", () => beginGame({ mode: "resume_series", id: s.id }));
      list.appendChild(row);
    });
    wrap.appendChild(list);
  }

  if (saves.length) {
    const title = document.createElement("div");
    title.className = "start-saves-title";
    title.textContent = "Resume a saved game";
    wrap.appendChild(title);

    const list = document.createElement("div");
    list.className = "start-saves";
    saves.forEach((s) => {
      const row = document.createElement("button");
      row.className = "choice-btn save-row";
      row.innerHTML = describeSave(s);
      row.addEventListener("click", () => beginGame({ mode: "resume", id: s.id }));
      list.appendChild(row);
    });
    wrap.appendChild(list);
  }

  if (canUpload) {
    const label = document.createElement("label");
    label.className = "choice-btn upload-btn";
    label.textContent = "📂 Upload a save file";
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".pkl,application/octet-stream";
    input.style.display = "none";
    input.addEventListener("change", () => {
      if (input.files && input.files[0]) uploadSave(input.files[0]);
    });
    label.appendChild(input);
    wrap.appendChild(label);
  }

  controlsEl.appendChild(wrap);
}

function describeSave(s) {
  const score = (s.score != null ? s.score : 0) + "/" + (s.wickets != null ? s.wickets : 0);
  const main = escapeHtml((s.team1 || "?") + " v " + (s.team2 || "?")) +
    "  ·  " + escapeHtml(s.match_type || s.format || "");
  const sub = escapeHtml((s.battingTeam || s.batting_team || "") + " " + score +
    "  ·  " + (s.situation || ""));
  return '<span class="save-main">' + main + '</span>' +
    '<span class="save-sub">' + sub + '</span>';
}

function describeSeries(s) {
  const teams = s.teams || [];
  const who = teams.length === 2 ? teams.join(" v ") : teams.length + " teams";
  const main = escapeHtml(who) + "  ·  " + escapeHtml(s.match_type || s.format || "");
  const sub = escapeHtml(s.situation || "");
  return '<span class="save-main">' + main + '</span>' +
    '<span class="save-sub">' + sub + '</span>';
}

function uploadSave(file) {
  const fd = new FormData();
  fd.append("file", file);
  fd.append("clientId", clientId);
  appendLine("Uploading save…", null);
  fetch("upload_save", { method: "POST", body: fd })
    .then((r) => r.json().then((j) => ({ ok: r.ok, j })))
    .then(({ ok, j }) => {
      if (!ok) {
        appendLine("Upload failed: " + (j.error || "unknown error"), "fore-lightred_ex");
        return;
      }
      beginGame({ mode: "resume", id: j.id });
    })
    .catch((e) => appendLine("Upload failed: " + e, "fore-lightred_ex"));
}

socket.on("disconnect", () => {
  statusEl.textContent = "disconnected";
  statusEl.className = "status err";
  // a reconnect gets a fresh server session and start menu, so allow the
  // menu to show again (the auto-saved game can be resumed from it)
  gameStarted = false;
  hideSimOverlay();
  clearControls();
  const p = document.createElement("p");
  p.className = "hint";
  p.textContent = "Connection lost. Reconnecting…";
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
  } else if (data.type === "event") {
    // the server blocks until this event is acked. If the event put up any
    // full-screen takeover frames, the ack rides on the last of them and
    // fires when it leaves the screen; otherwise (docked pop-up, hold-open
    // frame, or nothing shown) ack right away so play continues.
    dispatchPushedItems = [];
    renderEvent(data.kind, data.data);
    let claimant = null;
    for (const it of dispatchPushedItems) {
      if (it.holdMs && it.paneClass && it.paneClass.indexOf("takeover") !== -1) {
        claimant = it;
      }
    }
    dispatchPushedItems = null;
    if (data.eid != null) {
      if (claimant) claimant.eid = data.eid;
      else socket.emit("event_ack", data.eid);
    }
  } else if (data.type === "highlights") {
    renderMatchHighlights(data.data);
  } else if (data.type === "xi") {
    renderPlayingXI(data.data);
  } else if (data.type === "reset") {
    resetSidePane();
  } else if (data.type === "trivia") {
    renderTrivia(data.data);
  }
});

// clear the side pane between matches so a replay doesn't show the previous
// match's scorecard, innings summaries or run-rate graph
function resetSidePane() {
  liveScorecardEl.innerHTML =
    '<p class="hint">Scorecard will appear after the first over.</p>';
  inningsSummariesEl.innerHTML = "";
  currentLiveInningsBlockEl = null;
  runRateGraphEl.style.display = "none";
  runRateLegendEl.innerHTML = "";
  runRateSvgEl.innerHTML = "";
  if (nextBatsmenCardEl) nextBatsmenCardEl.style.display = "none";
  if (nextBatsmenListEl) nextBatsmenListEl.innerHTML = "";
  if (triviaHideTimer) {
    clearTimeout(triviaHideTimer);
    triviaHideTimer = null;
  }
  if (triviaPanelEl) {
    triviaPanelEl.classList.remove("visible");
    triviaPanelEl.innerHTML = "";
  }
}

// bottom-right "did you know?" card: a short Wikipedia snippet about a
// team/player/venue/umpire or general cricket, pushed every 30-55s while a
// match is live (see functions/Trivia.py). Best-effort/decorative only - no
// data means the server couldn't reach Wikipedia this round, so the panel
// just quietly keeps showing whatever it last had (or stays hidden).
const TRIVIA_LABELS = {
  team: "🏏 About the team",
  player: "🧢 About the player",
  venue: "🏟️ About the venue",
  umpire: "🤍 About the umpire",
  general: "💡 Did you know?",
};

const TRIVIA_SHOW_MS = 5000; // flash briefly, then hide until the next one arrives
let triviaHideTimer = null;

function renderTrivia(data) {
  if (!triviaPanelEl || !data || !data.text) return;
  const label = TRIVIA_LABELS[data.category] || TRIVIA_LABELS.general;
  const subject = data.subject ? escapeHtml(String(data.subject)) : "";
  triviaPanelEl.innerHTML =
    '<div class="trivia-label">' + label + "</div>" +
    (subject ? '<div class="trivia-subject">' + subject + "</div>" : "") +
    '<div class="trivia-text">' + escapeHtml(String(data.text)) + "</div>";
  triviaPanelEl.classList.add("visible");

  if (triviaHideTimer) clearTimeout(triviaHideTimer);
  triviaHideTimer = setTimeout(() => {
    triviaPanelEl.classList.remove("visible");
    triviaHideTimer = null;
  }, TRIVIA_SHOW_MS);
}

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
  const oversLine = state.isTest
    ? "Day " + state.day + "/" + state.maxDays + "  ·  Session " + state.session + "/" + state.sessionsPerDay +
      "  ·  Overs: " + Number(state.overs).toFixed(1)
    : "Overs: " + Number(state.overs).toFixed(1) + "/" + state.totalOvers;
  parts.push(
    '<div class="sub-line">' + oversLine + "  ·  CRR: " + Number(state.crr).toFixed(2) + "</div>"
  );

  if (state.resultMessage) {
    parts.push('<div class="target-line">' + escapeHtml(state.resultMessage) + "</div>");
  } else if (state.target !== null && state.target !== undefined) {
    const need = Math.max(state.target - state.score, 0);
    // limited-overs chases count down the balls; a Test chase has no ball limit
    const balls = state.ballsRemaining;
    const from =
      balls === null || balls === undefined
        ? " more"
        : " from " + balls + " ball" + (balls === 1 ? "" : "s");
    let targetLine = "Need " + need + from + " vs " + escapeHtml(state.bowlingTeam);
    if (state.wicketsInHand !== null && state.wicketsInHand !== undefined) {
      targetLine += "  ·  " + state.wicketsInHand + " wkt" + (state.wicketsInHand === 1 ? "" : "s") + " in hand";
    }
    if (state.requiredRunRate !== null && state.requiredRunRate !== undefined) {
      targetLine += "  ·  RRR: " + Number(state.requiredRunRate).toFixed(2);
    }
    parts.push('<div class="target-line">' + targetLine + "</div>");
  } else if (state.leadTrail) {
    let leadLine;
    if (state.leadTrail.team) {
      // always the batting team's perspective: "lead by" / "trail by"
      const verb = state.leadTrail.status === "trail" ? "trail by" : "lead by";
      leadLine = escapeHtml(state.leadTrail.team) + " " + verb + " " + state.leadTrail.diff +
        (state.leadTrail.diff === 1 ? " run" : " runs");
    } else {
      leadLine = "Scores level";
    }
    parts.push('<div class="target-line">' + leadLine + "</div>");
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
  renderRunRateGraph(state);
  renderNextBatsmen(state);
  updateDeclareButton(state);
}

function renderNextBatsmen(state) {
  if (!nextBatsmenCardEl || !nextBatsmenListEl) return;
  const upcoming = state.nextBatsmen || [];
  if (!upcoming.length) {
    nextBatsmenCardEl.style.display = "none";
    return;
  }
  nextBatsmenCardEl.style.display = "";
  nextBatsmenListEl.innerHTML = upcoming
    .map((p) => "<li>" + escapeHtml(p.name) + "</li>")
    .join("");
}

const RUN_RATE_COLOR_CURRENT = "#7fe3a3";
const RUN_RATE_COLOR_FIRST_INNINGS = "#f2d16b";

function buildWormPath(series, maxOver, maxScore, width, height) {
  if (!series.length) return { line: "", dots: [] };
  const x = (over) => (over / maxOver) * width;
  const y = (score) => height - (score / maxScore) * height;
  const points = [{ x: x(0), y: y(0) }].concat(
    series.map((pt) => ({ x: x(pt.over + 1), y: y(pt.score) }))
  );
  const line = points.map((p) => p.x.toFixed(1) + "," + p.y.toFixed(1)).join(" ");
  const dots = series
    .filter((pt) => pt.wickets > 0)
    .map((pt) => ({ x: x(pt.over + 1), y: y(pt.score) }));
  return { line, dots };
}

function renderRunRateGraph(state) {
  if (state.isTest || !state.overHistory || !state.overHistory.length) {
    runRateGraphEl.style.display = "none";
    return;
  }
  runRateGraphEl.style.display = "";

  const width = 260;
  const height = 150;
  const maxOver = state.totalOvers || Math.max(...state.overHistory.map((p) => p.over + 1));
  const allSeries = state.firstInningsOverHistory
    ? state.overHistory.concat(state.firstInningsOverHistory)
    : state.overHistory;
  const maxScore = Math.max(10, ...allSeries.map((p) => p.score)) * 1.1;

  const current = buildWormPath(state.overHistory, maxOver, maxScore, width, height);
  const parts = [];

  // gridlines
  for (let i = 1; i < 4; i++) {
    const gy = (height / 4) * i;
    parts.push(
      '<line x1="0" y1="' + gy.toFixed(1) + '" x2="' + width + '" y2="' + gy.toFixed(1) +
      '" stroke="#1e4530" stroke-width="1"/>'
    );
  }

  if (state.firstInningsOverHistory) {
    const first = buildWormPath(state.firstInningsOverHistory, maxOver, maxScore, width, height);
    parts.push(
      '<polyline points="' + first.line + '" fill="none" stroke="' + RUN_RATE_COLOR_FIRST_INNINGS +
      '" stroke-width="2" opacity="0.85"/>'
    );
    first.dots.forEach((d) => {
      parts.push(
        '<circle cx="' + d.x.toFixed(1) + '" cy="' + d.y.toFixed(1) + '" r="2.5" fill="' +
        RUN_RATE_COLOR_FIRST_INNINGS + '"/>'
      );
    });
  }

  parts.push(
    '<polyline points="' + current.line + '" fill="none" stroke="' + RUN_RATE_COLOR_CURRENT +
    '" stroke-width="2.5"/>'
  );
  current.dots.forEach((d) => {
    parts.push(
      '<circle cx="' + d.x.toFixed(1) + '" cy="' + d.y.toFixed(1) + '" r="2.5" fill="' +
      RUN_RATE_COLOR_CURRENT + '"/>'
    );
  });

  runRateSvgEl.setAttribute("viewBox", "0 0 " + width + " " + height);
  runRateSvgEl.innerHTML = parts.join("");

  const legendParts = [
    '<div class="legend-item"><span class="legend-swatch" style="background:' + RUN_RATE_COLOR_CURRENT +
    '"></span>' + escapeHtml(state.battingTeam) + "</div>",
  ];
  if (state.firstInningsOverHistory) {
    legendParts.push(
      '<div class="legend-item"><span class="legend-swatch" style="background:' +
      RUN_RATE_COLOR_FIRST_INNINGS + '"></span>' + escapeHtml(state.firstInningsTeam) + "</div>"
    );
  }
  runRateLegendEl.innerHTML = legendParts.join("");
}

// the innings-summary block currently being refreshed in place (every 5
// overs / every session, inProgress: true); cleared once that innings'
// final (inProgress: false) push locks it in as permanent history, so the
// next innings starts a fresh block instead of continuing to update this one
let currentLiveInningsBlockEl = null;

function buildInningsCardHtml(innings) {
  const parts = [];
  parts.push(
    '<div class="team-line"><span>' + escapeHtml(innings.battingTeam) + " innings" +
    (innings.inProgress ? ' <span class="live-badge">LIVE</span>' : "") + "</span>" +
    '<span class="score">' + innings.score + "/" + innings.wickets + (innings.declared ? "d" : "") +
    " (" + Number(innings.overs).toFixed(1) + ")</span></div>"
  );
  parts.push('<div class="sub-line">Extras: ' + innings.extras + "</div>");

  parts.push("<h3>Batting</h3><table>");
  (innings.battingCard || []).forEach((b) => {
    let name = b.name;
    if (b.captain) name += " (c)";
    if (b.keeper) name += " (wk)";
    // a batsman who did not bat has no score to show
    const dnb = b.dismissal === "DNB";
    const num = dnb ? "" : b.runs + " (" + b.balls + ")";
    parts.push(
      '<tr><td class="name">' + escapeHtml(name) + "</td>" +
      '<td class="dismissal">' + escapeHtml(b.dismissal) + "</td>" +
      '<td class="num">' + num + "</td></tr>"
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

  return parts.join("");
}

function renderInningsSummary(innings) {
  if (currentLiveInningsBlockEl) {
    // refresh the block already showing this in-progress innings
    currentLiveInningsBlockEl.innerHTML = buildInningsCardHtml(innings);
  } else {
    const wrapper = document.createElement("div");
    wrapper.className = "innings-summary";
    wrapper.innerHTML = buildInningsCardHtml(innings);
    inningsSummariesEl.appendChild(wrapper);
    currentLiveInningsBlockEl = wrapper;
  }

  if (!innings.inProgress) {
    // innings is genuinely done - lock this block in as permanent history
    currentLiveInningsBlockEl = null;
  }
}

// simplified inline stumps icon - no external image assets
const STUMPS_SVG =
  '<svg width="52" height="52" viewBox="0 0 60 60">' +
  '<line x1="14" y1="14" x2="14" y2="52" stroke="#e6f2ea" stroke-width="5" stroke-linecap="round"/>' +
  '<line x1="30" y1="9" x2="30" y2="52" stroke="#e6f2ea" stroke-width="5" stroke-linecap="round"/>' +
  '<line x1="46" y1="14" x2="46" y2="52" stroke="#e6f2ea" stroke-width="5" stroke-linecap="round"/>' +
  '<line x1="14" y1="14" x2="30" y2="9" stroke="#f2d16b" stroke-width="4" stroke-linecap="round"/>' +
  '<line x1="30" y1="9" x2="46" y2="14" stroke="#f2d16b" stroke-width="4" stroke-linecap="round"/>' +
  "</svg>";

function buildFlagCard(teamName) {
  const card = document.createElement("div");
  card.className = "event-player";

  const img = document.createElement("img");
  img.className = "event-flag-pic";
  img.alt = teamName;
  // server resolves the raw team name to resources/teams/flags/<slug>.<ext>
  img.src = "teams/flags/" + encodeURIComponent(teamName);
  img.addEventListener("error", () => {
    const fallback = document.createElement("span");
    fallback.className = "event-flag-fallback";
    fallback.textContent = teamName.slice(0, 3).toUpperCase();
    img.replaceWith(fallback);
  });

  const label = document.createElement("div");
  label.className = "event-player-name";
  label.textContent = teamName;

  card.appendChild(img);
  card.appendChild(label);
  return card;
}

// match won: the winning team's flag over the result line
function buildVictoryCard(teamName, resultStr) {
  const card = buildFlagCard(teamName);
  const nameEl = card.querySelector(".event-player-name");
  if (nameEl) nameEl.remove(); // the result line already names the winner
  const badge = document.createElement("div");
  badge.className = "event-achievement-badge";
  badge.textContent = "🏆 " + resultStr;
  card.appendChild(badge);
  return card;
}

// caption + image fetched from srcPath (misc/<kind>, venues/<name>, ...),
// with an emoji stand-in when no image has been saved there
function buildMiscCard(srcPath, fallbackEmoji, caption, subtitle) {
  const card = document.createElement("div");
  card.className = "event-player";

  const img = document.createElement("img");
  img.className = "event-misc-pic";
  img.alt = caption;
  img.src = srcPath;
  img.addEventListener("error", () => {
    const fallback = document.createElement("span");
    fallback.className = "event-misc-fallback";
    fallback.textContent = fallbackEmoji;
    img.replaceWith(fallback);
  });
  card.appendChild(img);

  const label = document.createElement("div");
  label.className = "event-player-name";
  label.textContent = caption;
  card.appendChild(label);

  if (subtitle) {
    const sub = document.createElement("div");
    sub.className = "event-player-role";
    sub.textContent = subtitle;
    card.appendChild(sub);
  }
  return card;
}

// partnership milestone: a badge over both batsmen's photos
function buildPartnershipCard(names, runs) {
  const wrap = document.createElement("div");
  wrap.className = "event-player";

  const badge = document.createElement("div");
  badge.className = "event-achievement-badge";
  badge.textContent = "🤝 " + runs + " run partnership";
  wrap.appendChild(badge);

  const row = document.createElement("div");
  row.className = "event-openers";
  names.forEach((n) => row.appendChild(buildPlayerCard(String(n))));
  wrap.appendChild(row);
  return wrap;
}

// team total milestone: big score number with team name and wickets
function buildTeamScoreCard(team, score, wickets) {
  const card = document.createElement("div");
  card.className = "event-player";

  const num = document.createElement("div");
  num.className = "event-countdown-num";
  num.textContent = String(score);
  card.appendChild(num);

  const label = document.createElement("div");
  label.className = "event-player-name";
  label.textContent = team;
  card.appendChild(label);

  const sub = document.createElement("div");
  sub.className = "event-player-role";
  sub.textContent = score + "/" + wickets + " · team milestone";
  card.appendChild(sub);
  return card;
}

// umpire giving a decision (LBW / run out): umpire photo, a "wickets hit"
// stumps symbol, and the decision label
function buildUmpireDecisionCard(umpireName, label) {
  const card = buildPlayerCard(umpireName || "Umpire", label, "umpires/");
  const nameEl = card.querySelector(".event-player-name");
  if (nameEl) nameEl.remove(); // show only the umpire's photo, not the name
  const stumps = document.createElement("div");
  stumps.className = "event-decision-stumps";
  stumps.innerHTML = STUMPS_SVG;
  card.insertBefore(stumps, card.firstChild); // wickets symbol above the umpire
  return card;
}

function buildCountdownCard(name, number) {
  const card = buildPlayerCard(name);
  const nameEl = card.querySelector(".event-player-name");
  if (nameEl) nameEl.remove(); // countdown shows just the photo + number
  const num = document.createElement("div");
  num.className = "event-countdown-num";
  num.textContent = String(number);
  card.insertBefore(num, card.firstChild); // big number above the photo
  return card;
}

const GAME_ON_PHRASES = [
  "GAME ON!",
  "LET'S GO!",
  "BRING IT ON!",
  "IT'S SHOWTIME!",
  "CHALLENGE ACCEPTED!",
  "GO TIME!",
];

function buildGameOnCard(name) {
  const card = buildPlayerCard(name);
  const nameEl = card.querySelector(".event-player-name");
  if (nameEl) nameEl.remove();
  const go = document.createElement("div");
  go.className = "event-gameon-text";
  go.textContent = GAME_ON_PHRASES[Math.floor(Math.random() * GAME_ON_PHRASES.length)];
  card.insertBefore(go, card.firstChild);
  return card;
}

// Events can arrive back-to-back with no user interaction in between (the
// openers card followed instantly by the opening bowler's card at innings
// start), so queue them: each pop-up gets its full hold time instead of the
// last writer clobbering the ones before it.
const eventQueue = [];
let eventTimer = null;

// A hold-open frame (holdMs 0, e.g. the DRS "decision pending" lights) waits
// to be replaced by the event that resolves it. It still needs a timer: with
// none at all, a frame already queued behind it would never be drained and
// the pane would stick on screen forever.
const HOLD_OPEN_MIN_MS = 1200; // brief look-at-it time when the next frame is already waiting
const HOLD_OPEN_MAX_MS = 15000; // safety net if the resolving event never arrives

let holdingOpen = false; // the visible frame is waiting to be replaced

// game-sync ack plumbing: the server blocks in WebChannel.event() until the
// pop-up for the event it just sent is done. While an event is being
// dispatched, every frame it pushes is collected in dispatchPushedItems;
// the dispatcher then pins the event's eid on the last takeover frame, and
// finishEventFrame acks it once that frame leaves the screen. Frames only
// hold the game while actually timed and full-screen: hold-open frames
// (holdMs 0) wait to be *replaced* by the server's next event, which a
// blocked server could never send.
let dispatchPushedItems = null;
let currentEventItem = null; // the frame currently visible in the pane

function finishEventFrame() {
  if (currentEventItem && currentEventItem.eid != null) {
    socket.emit("event_ack", currentEventItem.eid);
  }
  currentEventItem = null;
}

function showEventPane(content, holdMs, paneClass) {
  const item = { content: content, holdMs: holdMs, paneClass: paneClass, eid: null };
  if (dispatchPushedItems) dispatchPushedItems.push(item);
  eventQueue.push(item);
  // a hold-open frame is meant to give way the moment its result lands
  if (holdingOpen && eventTimer) {
    clearTimeout(eventTimer);
    eventTimer = null;
  }
  if (!eventTimer) drainEventQueue();
}

function drainEventQueue() {
  const item = eventQueue.shift();
  if (!item) return;
  // moving on to a new frame: the one on screen (if any) is done - let the
  // server know if it was holding the game
  finishEventFrame();
  currentEventItem = item;

  if (typeof item.content === "string") {
    eventPaneEl.innerHTML = item.content;
  } else {
    eventPaneEl.innerHTML = "";
    eventPaneEl.appendChild(item.content);
  }
  // rebuild the class list from scratch (dropping "visible") so the pop/flip
  // animations restart even if the pane is already showing a previous event
  eventPaneEl.className = "event-pane" + (item.paneClass ? " " + item.paneClass : "");
  void eventPaneEl.offsetWidth; // force reflow
  eventPaneEl.classList.add("visible");

  holdingOpen = !item.holdMs;
  const hold =
    item.holdMs || (eventQueue.length ? HOLD_OPEN_MIN_MS : HOLD_OPEN_MAX_MS);
  eventTimer = setTimeout(() => {
    eventTimer = null;
    if (eventQueue.length) {
      drainEventQueue();
    } else {
      eventPaneEl.classList.remove("visible");
      holdingOpen = false;
      finishEventFrame();
    }
  }, hold);
}

function initialsOf(name) {
  return name
    .split(/\s+/)
    .map((w) => w[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

function buildPlayerCard(name, role, srcPath) {
  const initials = initialsOf(name);

  const card = document.createElement("div");
  card.className = "event-player";

  const img = document.createElement("img");
  img.className = "event-player-pic";
  img.alt = name;
  // server resolves the raw name to a <slug>.<ext> file under the resource
  // dir (players/pics by default, umpires/ for umpire cards); a 404 (no pic
  // saved for this person) swaps in the initials avatar
  img.src = (srcPath || "players/pics/") + encodeURIComponent(name);
  img.addEventListener("error", () => {
    const fallback = document.createElement("span");
    fallback.className = "event-player-fallback";
    fallback.textContent = initials || "🏏";
    img.replaceWith(fallback);
  });

  const label = document.createElement("div");
  label.className = "event-player-name";
  label.textContent = name;

  card.appendChild(img);
  card.appendChild(label);
  if (role) {
    const roleEl = document.createElement("div");
    roleEl.className = "event-player-role";
    roleEl.textContent = role;
    card.appendChild(roleEl);
  }
  return card;
}

function renderEvent(kind, data) {
  if (kind === "toss") {
    showEventPane('<span class="event-coin">🪙</span>', 2500, "takeover");
  } else if (kind === "wicket") {
    showEventPane('<span class="event-stumps">' + STUMPS_SVG + "</span>", 2500);
  } else if (kind === "four") {
    showEventPane('<span class="event-digit four">4!</span>', 1500);
  } else if (kind === "six") {
    showEventPane('<span class="event-digit six">6!</span>', 1500);
  } else if (kind === "new_bowler" && data && data.opening) {
    // opening bowler at innings start: full screen with a flavour caption
    const name = data.name ? String(data.name) : "";
    if (name) {
      const card = buildPlayerCard(name);
      const nameEl = card.querySelector(".event-player-name");
      if (nameEl) nameEl.remove(); // the caption names them, no need to repeat
      const cap = document.createElement("div");
      cap.className = "event-achievement-badge";
      cap.textContent = data.caption ? String(data.caption) : "Opening bowler";
      card.appendChild(cap); // caption below the photo
      showEventPane(card, 3500, "takeover");
    }
  } else if (kind === "new_batsman" || kind === "new_bowler") {
    const name = data && data.name ? String(data.name) : "";
    const role = kind === "new_bowler" ? "New bowler" : "New batsman";
    if (name) showEventPane(buildPlayerCard(name, role), 3000, "player");
  } else if (kind === "openers") {
    const names = ((data && data.names) || []).map(String).filter(Boolean);
    if (names.length) {
      // the opening batting pair, full screen, with a flavour caption
      const wrap = document.createElement("div");
      wrap.className = "event-player";
      if (data && data.caption) {
        const cap = document.createElement("div");
        cap.className = "event-achievement-badge";
        cap.textContent = String(data.caption);
        wrap.appendChild(cap);
      }
      const row = document.createElement("div");
      row.className = "event-openers";
      names.forEach((n) => {
        const c = buildPlayerCard(n);
        const nameEl = c.querySelector(".event-player-name");
        if (nameEl) nameEl.remove(); // the caption names them, no need to repeat
        row.appendChild(c);
      });
      wrap.appendChild(row);
      showEventPane(wrap, 4000, "takeover roster");
    }
  } else if (kind === "teams_selected") {
    const names = ((data && data.names) || []).map(String).filter(Boolean);
    if (names.length) {
      const row = document.createElement("div");
      row.className = "event-openers";
      names.forEach((n, i) => {
        if (i > 0) {
          const vs = document.createElement("span");
          vs.className = "event-vs";
          vs.textContent = "vs";
          row.appendChild(vs);
        }
        row.appendChild(buildFlagCard(n));
      });
      showEventPane(row, 4000, "takeover roster");
    }
  } else if (kind === "session_break") {
    const isLunch = data && data.interval === "Lunch";
    showEventPane(
      isLunch
        ? buildMiscCard("misc/lunch", "🍽️", "Lunch break")
        : buildMiscCard("misc/tea", "☕", "Tea break"),
      3500,
      "takeover"
    );
  } else if (kind === "innings_over") {
    const card = buildMiscCard("misc/innings_over", "🏏", "Innings over", "");
    if (data && data.team) {
      const score = document.createElement("div");
      score.className = "event-innings-score";
      score.textContent =
        data.team + "  " + data.score + "/" + data.wickets +
        (data.overs != null ? " (" + Number(data.overs).toFixed(1) + ")" : "");
      card.appendChild(score);
    }
    if (data && data.topBatter) {
      const tb = document.createElement("div");
      tb.className = "event-innings-sub";
      tb.textContent =
        "🏏 Top scorer: " + data.topBatter.name + " " +
        data.topBatter.runs + " (" + data.topBatter.balls + ")";
      card.appendChild(tb);
    }
    if (data && data.topBowler) {
      const tw = document.createElement("div");
      tw.className = "event-innings-sub";
      tw.textContent =
        "⚾ Best bowler: " + data.topBowler.name + " " +
        data.topBowler.wickets + "/" + data.topBowler.runs;
      card.appendChild(tw);
    }
    showEventPane(card, 4500, "takeover");
  } else if (kind === "match_decided") {
    // the instant, punchy "victory moment" popup - right after the ball
    // that decided the chase, well before the later factual result/trophy
    // card ("victory", below) that follows the scorecards and summaries
    const team = data && data.team ? String(data.team) : "";
    const text = data && data.text ? String(data.text) : "";
    showEventPane(
      team ? buildVictoryCard(team, text) : buildMiscCard("misc/victory", "🏆", text),
      4200,
      "takeover"
    );
  } else if (kind === "victory") {
    const caption = data && data.result ? String(data.result) : "Victory!";
    const team = data && data.team ? String(data.team) : "";
    showEventPane(
      team ? buildVictoryCard(team, caption) : buildMiscCard("misc/victory", "🏆", caption),
      5000,
      "takeover"
    );
  } else if (kind === "declare") {
    const sub = data && data.team ? data.score + "/" + data.wickets : "";
    const cap = data && data.team ? data.team + " declared" : "Declared";
    showEventPane(buildMiscCard("misc/declare", "✋", cap, sub), 4000, "takeover");
  } else if (kind === "follow_on") {
    const sub = data && data.opponent ? data.opponent + " to bat again" : "";
    showEventPane(buildMiscCard("misc/follow_on", "🔁", "Follow-on enforced!", sub), 4000, "takeover");
  } else if (kind === "partnership_milestone") {
    const names = ((data && data.names) || []).map(String).filter(Boolean);
    const runs = data && data.runs;
    if (names.length && runs) {
      showEventPane(buildPartnershipCard(names, runs), 4000, "takeover roster");
    }
  } else if (kind === "team_score") {
    if (data && data.score) {
      showEventPane(
        buildTeamScoreCard(String(data.team), data.score, data.wickets),
        4000,
        "takeover"
      );
    }
  } else if (kind === "super_over") {
    const stage = data && data.stage;
    if (stage === "start") {
      showEventPane(
        buildMiscCard("misc/super_over", "⚡", "SUPER OVER!", "the scores are level!"),
        3500,
        "takeover"
      );
    } else if (stage === "innings") {
      showEventPane(
        buildMiscCard(
          "misc/super_over", "⚡",
          data.team + " " + data.runs + "/" + data.wickets,
          "super over"
        ),
        3000,
        "takeover"
      );
    } else if (stage === "result") {
      showEventPane(
        data.team
          ? buildVictoryCard(String(data.team), "won the Super Over!")
          : buildMiscCard("misc/super_over", "⚡", "Super Over tied!", "honours shared"),
        4500,
        "takeover"
      );
    }
  } else if (kind === "first_ball_wicket") {
    const batter = data && data.batter ? String(data.batter) : "";
    const bowler = data && data.bowler ? String(data.bowler) : "";
    const text = data && data.text ? String(data.text) : "";
    if (batter && bowler) {
      const wrap = document.createElement("div");
      wrap.className = "event-player";
      const badge = document.createElement("div");
      badge.className = "event-achievement-badge";
      badge.textContent = "🎯 " + (text || "First-ball wicket!");
      wrap.appendChild(badge);
      const row = document.createElement("div");
      row.className = "event-openers";
      row.appendChild(buildPlayerCard(bowler, "Bowler")); // took the wicket
      row.appendChild(buildPlayerCard(batter, "Out")); // departing batsman
      wrap.appendChild(row);
      showEventPane(wrap, 4000, "takeover roster");
    }
  } else if (kind === "approaching") {
    const name = data && data.name ? String(data.name) : "";
    const text = data && data.text ? String(data.text) : "";
    if (name) {
      const card = buildPlayerCard(name); // photo + full name
      const badge = document.createElement("div");
      badge.className = "event-achievement-badge";
      badge.textContent = "🔥 " + text;
      // cool line between the photo and the name
      card.insertBefore(badge, card.lastChild);
      if (data && data.milestone) {
        const sub = document.createElement("div");
        sub.className = "event-player-role";
        sub.textContent = "one short of a " + data.milestone;
        card.appendChild(sub);
      }
      showEventPane(card, 3500, "takeover");
    }
  } else if (kind === "boundary_streak") {
    const name = data && data.name ? String(data.name) : "";
    const text = data && data.text ? String(data.text) : "";
    if (name && text) {
      const card = buildPlayerCard(name);
      const badge = document.createElement("div");
      badge.className = "event-achievement-badge";
      badge.textContent = "🔥 " + text;
      // badge sits between the photo and the name
      card.insertBefore(badge, card.lastChild);
      showEventPane(card, 3000, "takeover");
    }
  } else if (kind === "tension") {
    const text = data && data.text ? String(data.text) : "";
    const isFinal = !!(data && data.final);
    if (text) {
      const card = document.createElement("div");
      card.className = "event-player";
      const line = document.createElement("div");
      line.className = "event-tension-text" + (isFinal ? " final" : "");
      line.textContent = text;
      card.appendChild(line);
      // the equation on every slide: N runs needed from M balls
      const runs = data && data.runsToWin;
      const balls = data && data.ballsLeft;
      if (runs != null && balls != null && runs > 0) {
        const eq = document.createElement("div");
        eq.className = "event-tension-eq";
        eq.textContent =
          runs + (runs === 1 ? " run" : " runs") + " from " +
          balls + (balls === 1 ? " ball!" : " balls!");
        card.appendChild(eq);
      }
      // kept short so the pop-ups keep pace with the balls being bowled
      showEventPane(card, isFinal ? 2600 : 1600, "takeover");
    }
  } else if (kind === "rain") {
    const cfg = {
      clouds: ["misc/rain_clouds", "🌥️", "Rain clouds gathering", ""],
      cloudy: ["misc/rain_cloudy", "🌥️", "It's getting cloudy", ""],
      drizzle: ["misc/rain_drizzle", "🌦️", "It's drizzling", "umpires might stop play soon"],
      heavy: ["misc/rain_heavy", "🌧️", "Heavy rain!", ""],
      stopped: ["misc/rain_stopped", "☔", "Rain stopped play", (data && data.resume) || ""],
    }[data && data.stage];
    if (cfg) showEventPane(buildMiscCard(cfg[0], cfg[1], cfg[2], cfg[3]), 3500, "takeover");
  } else if (kind === "target") {
    const team = data && data.team ? String(data.team) : "";
    let caption, sub;
    if (data && data.status) {
      // Test non-chase innings: lead / trail on aggregate
      const verb = data.status === "trail" ? "trail by" : "lead by";
      caption = team + " " + verb + " " + data.diff + (data.diff === 1 ? " run" : " runs");
      sub = "";
    } else {
      // chasing: the run target
      const runs = data && data.runsToWin;
      caption = team + " need " + runs + (runs === 1 ? " run to win" : " runs to win");
      sub = data && data.overs
        ? "from " + data.overs + (data.overs === 1 ? " over" : " overs")
        : "in the final innings";
      if (data && data.dls) sub += " · D/L revised target";
    }
    showEventPane(buildMiscCard("misc/target", "🎯", caption, sub), 4000, "takeover");
  } else if (kind === "weather") {
    const w = data && data.weather;
    const cfg = {
      sunny: ["misc/weather_sunny", "☀️", "Sunny"],
      overcast: ["misc/weather_overcast", "☁️", "Overcast"],
      rainy: ["misc/weather_rainy", "🌧️", "Rain about"],
      cloudy: ["misc/weather_cloudy", "⛅", "Cloudy"],
      humid: ["misc/weather_humid", "🥵", "Humid"],
    }[w] || ["misc/weather_" + (w || "unknown"), "🌤️", w || "Weather"];
    showEventPane(
      buildMiscCard(cfg[0], cfg[1], cfg[2], (data && data.text) || ""),
      3500,
      "takeover"
    );
  } else if (kind === "resume") {
    const bt = data && data.battingTeam ? String(data.battingTeam) : "";
    const score = data ? (data.score + "/" + data.wickets) : "";
    showEventPane(
      buildMiscCard("misc/resume", "⏮️", "Resuming your game",
        bt ? (bt + " " + score) : ""),
      3000,
      "takeover"
    );
  } else if (kind === "series") {
    const stage = data && data.stage;
    // any series beat other than "simulating" means the sim (if any) is done
    if (stage !== "simulating") hideSimOverlay();
    if (stage === "simulating") {
      showSimOverlay(
        (data && data.label) || "Match",
        ((data && data.home) || "") + "  v  " + ((data && data.away) || "")
      );
    } else if (stage === "tie") {
      showEventPane(
        buildMiscCard("misc/super_over", "⚡", "Match tied!",
          "Super Over: " + (data.home || "") + " v " + (data.away || "")),
        3000, "takeover");
    } else if (stage === "final_set") {
      showEventPane(
        buildMiscCard("misc/series_final", "🏆", "Final set!",
          (data.teamA || "") + " vs " + (data.teamB || "")),
        3500, "takeover");
    } else if (stage === "match_result") {
      const w = data && data.winner;
      showEventPane(
        buildMiscCard("misc/series_result", "📋", w ? (w + " win") : "No result",
          (data.home || "") + " v " + (data.away || "")),
        2600, "takeover");
    } else if (stage === "champion") {
      showEventPane(
        buildMiscCard("misc/champion", "🏆", "Champions!",
          (data && data.summary) || (data && data.champion) || ""),
        5000, "takeover");
    }
    // standings/stats/match_start stages are rendered as text in the log
  } else if (kind === "validating_teams") {
    // small centered pop-up so the pause between the playing XI and the
    // toss doesn't look like a hang (not a takeover: it must not hold up
    // the very validation it announces)
    showEventPane(
      buildMiscCard("misc/validating_teams", "🔍", "Validating teams…", "just a moment"),
      2500,
      "popup"
    );
  } else if (kind === "free_hit") {
    const ump = data && data.umpire ? String(data.umpire) : "Umpire";
    // umpire signalling the free hit: photo + big "FREE HIT!" badge
    const card = buildPlayerCard(ump, "", "umpires/");
    const nameEl = card.querySelector(".event-player-name");
    if (nameEl) nameEl.remove();
    const badge = document.createElement("div");
    badge.className = "event-gameon-text";
    badge.textContent = "FREE HIT!";
    card.insertBefore(badge, card.firstChild);
    showEventPane(card, 3000, "takeover");
  } else if (kind === "runout") {
    const ump = data && data.umpire ? String(data.umpire) : "";
    showEventPane(buildUmpireDecisionCard(ump, "RUN OUT"), 3000, "takeover");
  } else if (kind === "lbw") {
    const ump = data && data.umpire ? String(data.umpire) : "";
    showEventPane(buildUmpireDecisionCard(ump, "LBW"), 3000, "takeover");
  } else if (kind === "achievement") {
    const name = data && data.name ? String(data.name) : "";
    const text = data && data.text ? String(data.text) : "";
    // no dedicated cricket-ball emoji exists, baseball is the stand-in
    const emoji =
      {
        batting: "🏏", bowling: "⚾", fielding: "🧤",
        hattrick: "🎩",            // the hat-trick itself (3 in 3)
        hattrick_building: "⏳",   // tension: 2 down, 1 more for the hat-trick
        hattrick_streak: "🔥",     // the streak keeps going beyond 3 (4-in-4, 5-in-5, ...)
      }[data && data.type] || "🌟";
    if (name && text) {
      const card = buildPlayerCard(name);
      const badge = document.createElement("div");
      badge.className = "event-achievement-badge";
      badge.textContent = emoji + " " + text;
      // badge sits between the photo and the name
      card.insertBefore(badge, card.lastChild);
      // the "on a hat-trick" tension card is shorter (a beat, not a
      // celebration) - the actual milestone popups linger longer
      const holdMs = (data && data.type) === "hattrick_building" ? 2200 : 4000;
      showEventPane(card, holdMs, "takeover");
    }
  } else if (kind === "umpires") {
    const names = ((data && data.names) || []).map(String).filter(Boolean);
    if (names.length) {
      const row = document.createElement("div");
      row.className = "event-openers";
      names.forEach((n) => row.appendChild(buildPlayerCard(n, "Umpire", "umpires/")));
      showEventPane(row, 2500, "takeover roster");
    }
  } else if (kind === "lineup_countdown") {
    const players = (data && data.players) || [];
    const frameMs = (data && data.frameMs) || 900;
    const gameOnMs = (data && data.gameOnMs) || 2200;
    players.forEach((p) => {
      showEventPane(buildCountdownCard(String(p.name), p.count), frameMs, "takeover countdown");
    });
    if (data && data.gameOn && data.gameOn.name) {
      showEventPane(buildGameOnCard(String(data.gameOn.name)), gameOnMs, "takeover countdown");
    }
  } else if (kind === "commentators") {
    const names = ((data && data.names) || []).map(String).filter(Boolean);
    if (names.length) {
      const row = document.createElement("div");
      row.className = "event-openers";
      names.forEach((n) => row.appendChild(buildPlayerCard(n, "Commentator", "commentators/")));
      showEventPane(row, 2500, "takeover roster");
    }
  } else if (kind === "venue_selected") {
    const name = data && data.name ? String(data.name) : "";
    if (name) {
      showEventPane(
        buildMiscCard("venues/" + encodeURIComponent(name), "🏟️", name),
        4000,
        "takeover venue"
      );
    }
  } else if (kind === "third_umpire") {
    if (data && data.stage === "referred") {
      showEventPane(
        buildMiscCard("misc/third_umpire", "📺", "Third umpire", "checking the replay…"),
        3000,
        "takeover"
      );
    } else {
      // given out on the spot by the on-field umpire
      const label = data && data.kind === "stumped" ? "STUMPED" : "RUN OUT";
      showEventPane(buildUmpireDecisionCard(data && data.umpire, label), 3000, "takeover");
    }
  } else if (kind === "drs_pending") {
    showEventPane(
      '<div class="drs-lights blinking"><span class="drs-bulb red"></span><span class="drs-bulb green"></span></div>',
      0,
      "takeover"
    );
  } else if (kind === "drs_result") {
    const out = !!(data && data.out);
    showEventPane(
      '<div class="drs-lights decided ' + (out ? "out" : "not-out") + '">' +
        '<span class="drs-bulb red"></span><span class="drs-bulb green"></span></div>',
      3000,
      "takeover"
    );
  }
}

function renderPlayingXI(xi) {
  const card = document.createElement("div");
  card.className = "playing-xi";

  (xi.teams || []).forEach((team) => {
    const col = document.createElement("div");
    col.className = "xi-col";

    const heading = document.createElement("h4");
    heading.textContent = team.name;
    col.appendChild(heading);

    (team.players || []).forEach((p) => {
      const row = document.createElement("div");
      row.className = "xi-row";

      const img = document.createElement("img");
      img.className = "xi-pic";
      img.alt = p.name;
      img.src = "players/pics/" + encodeURIComponent(p.name);
      img.addEventListener("error", () => {
        const fallback = document.createElement("span");
        fallback.className = "xi-pic xi-fallback";
        fallback.textContent = initialsOf(p.name);
        img.replaceWith(fallback);
      });

      const label = document.createElement("span");
      let name = p.name;
      if (p.captain) name += " (c)";
      if (p.keeper) name += " (wk)";
      label.textContent = name;

      row.appendChild(img);
      row.appendChild(label);
      col.appendChild(row);
    });
    card.appendChild(col);
  });

  logEl.appendChild(card);
  logEl.scrollTop = logEl.scrollHeight;
}

// small circular player thumbnail for the highlights card; the initials
// fallback is wired up after the card's innerHTML is set (see below)
function mhThumb(name) {
  return (
    '<img class="mh-pic" alt="" src="players/pics/' + encodeURIComponent(name) +
    '" data-name="' + escapeHtml(name) + '">'
  );
}

function renderMatchHighlights(highlights) {
  const parts = [];
  parts.push("<h2>🏆 Match Highlights</h2>");
  parts.push('<div class="result-line">' + escapeHtml(highlights.resultStr) + "</div>");

  (highlights.teams || []).forEach((t) => {
    parts.push(
      '<div class="team-score-line"><strong>' + escapeHtml(t.name) + "</strong>: " +
      t.scoreLines.map(escapeHtml).join(" &amp; ") + "</div>"
    );
  });

  (highlights.innings || []).forEach((inn) => {
    parts.push(
      '<h4>Innings ' + inn.no + " · " + escapeHtml(inn.battingTeam) + " " +
      inn.score + "/" + inn.wickets + (inn.declared ? "d" : "") +
      " (" + Number(inn.overs).toFixed(1) + ")</h4>"
    );
    parts.push('<div class="mh-inn">');

    parts.push('<div class="mh-inn-col"><div class="mh-sub">Batting</div><ul class="mh-list">');
    (inn.topBatters || []).forEach((b) => {
      parts.push(
        "<li>" + mhThumb(b.name) + "<span>" + escapeHtml(b.name) + " " +
        b.runs + " (" + b.balls + ")</span></li>"
      );
    });
    parts.push("</ul></div>");

    parts.push('<div class="mh-inn-col"><div class="mh-sub">Bowling</div><ul class="mh-list">');
    (inn.topBowlers || []).forEach((b) => {
      parts.push(
        "<li>" + mhThumb(b.name) + "<span>" + escapeHtml(b.name) + " " +
        b.wickets + "/" + b.runs + " (" + Number(b.overs).toFixed(1) + ")</span></li>"
      );
    });
    parts.push("</ul></div>");

    parts.push("</div>");
  });

  if ((highlights.topBatters || []).length) {
    parts.push('<h4>Top Scorers</h4><ul class="mh-list">');
    highlights.topBatters.forEach((b) => {
      parts.push(
        "<li>" + mhThumb(b.name) + "<span>" + escapeHtml(b.name) + " (" +
        escapeHtml(b.team) + ") - " + b.runs + " (" + b.balls + ")</span></li>"
      );
    });
    parts.push("</ul>");
  }

  if ((highlights.topBowlers || []).length) {
    parts.push('<h4>Top Wicket-Takers</h4><ul class="mh-list">');
    highlights.topBowlers.forEach((b) => {
      parts.push(
        "<li>" + mhThumb(b.name) + "<span>" + escapeHtml(b.name) + " (" +
        escapeHtml(b.team) + ") - " + b.wickets + "/" + b.runs + "</span></li>"
      );
    });
    parts.push("</ul>");
  }

  if (highlights.playerOfMatch) {
    parts.push(
      '<div class="mom-line">' + mhThumb(highlights.playerOfMatch.name) +
      "<span>Player of the Match: <strong>" +
      escapeHtml(highlights.playerOfMatch.name) + "</strong> (" +
      escapeHtml(highlights.playerOfMatch.stat) + ")</span></div>"
    );
  }

  const card = document.createElement("div");
  card.className = "match-highlights";
  card.innerHTML = parts.join("");
  // swap in an initials avatar for any thumbnail whose photo is missing
  card.querySelectorAll("img.mh-pic").forEach((img) => {
    img.addEventListener("error", () => {
      const fb = document.createElement("span");
      fb.className = "mh-pic mh-fallback";
      fb.textContent = initialsOf(img.dataset.name || "");
      img.replaceWith(fb);
    }, { once: true });
  });
  logEl.appendChild(card);
  logEl.scrollTop = logEl.scrollHeight;

  // celebrate the Man of the Match in the event pane too (queued after the
  // victory card, since highlights always arrive after the result)
  if (highlights.playerOfMatch && highlights.playerOfMatch.name) {
    const mom = buildPlayerCard(
      String(highlights.playerOfMatch.name),
      highlights.playerOfMatch.stat ? String(highlights.playerOfMatch.stat) : ""
    );
    const badge = document.createElement("div");
    badge.className = "event-achievement-badge";
    badge.textContent = "🏅 Man of the Match";
    // badge sits between the photo and the name
    mom.insertBefore(badge, mom.children[1]);
    showEventPane(mom, 6000, "takeover");
  }
}
