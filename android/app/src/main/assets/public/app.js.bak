// ── GLOBAL STATE ──
const API_BASE = "";
let currentSessionId = null;
let bloqueado = false;
let typingAnimationId = null;
let AUTH_PIN = sessionStorage.getItem("shio_pin") || "";
let particleCanvas, particleCtx, particles = [];

// ── MARKED & HIGHLIGHT.JS ──
const renderer = new marked.Renderer();
renderer.link = function(href, title, text) {
  if (typeof href === "object") { title = href.title || ""; text = href.text || ""; href = href.href || ""; }
  const t = title ? ` title="${title}"` : "";
  return `<a href="${href}"${t} target="_blank" rel="noopener noreferrer">${text}</a>`;
};
marked.setOptions({
  renderer, highlight: (code, lang) => {
    const language = hljs.getLanguage(lang) ? lang : "plaintext";
    return hljs.highlight(code, { language }).value;
  },
  langPrefix: "hljs language-", breaks: true, gfm: true,
});
const _origParse = marked.parse;
marked.parse = function(text, opts, cb) {
  let html = _origParse(text, opts, cb);
  if (window.renderMathInElement) {
    const tmp = document.createElement("div");
    tmp.innerHTML = html;
    renderMathInElement(tmp, {
      delimiters: [
        { left: "$$", right: "$$", display: true },
        { left: "$", right: "$", display: false },
        { left: "\\(", right: "\\)", display: false },
        { left: "\\[", right: "\\]", display: true },
      ],
      throwOnError: false,
    });
    return tmp.innerHTML;
  }
  return html;
};

// ── AUTH ──
function authHeaders() {
  return { "Content-Type": "application/json", Authorization: "Bearer " + AUTH_PIN };
}

async function tryLogin() {
  const input = document.getElementById("pinInput");
  const pin = input.value.trim();
  if (!pin) return;
  try {
    const r = await fetch(`${API_BASE}/auth`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pin }),
    });
    if (r.ok) {
      AUTH_PIN = pin;
      sessionStorage.setItem("shio_pin", pin);
      document.getElementById("loginScreen").style.display = "none";
      initApp();
    } else {
      showToast("PIN incorrecto", "error");
      input.value = ""; input.focus();
    }
  } catch (e) { showToast("Sin conexión al servidor", "error"); }
}

async function checkAuth() {
  if (!AUTH_PIN) { document.getElementById("loginScreen").style.display = "flex"; return; }
  try {
    const r = await fetch(`${API_BASE}/health`, { headers: { Authorization: "Bearer " + AUTH_PIN } });
    if (r.ok) { document.getElementById("loginScreen").style.display = "none"; initApp(); }
    else document.getElementById("loginScreen").style.display = "flex";
  } catch { document.getElementById("loginScreen").style.display = "flex"; }
}

// ── TOAST ──
function showToast(msg, type = "info") {
  const c = document.getElementById("toastContainer");
  const t = document.createElement("div");
  t.className = `toast toast-${type}`;
  t.textContent = msg;
  c.appendChild(t);
  requestAnimationFrame(() => t.classList.add("show"));
  setTimeout(() => { t.classList.remove("show"); setTimeout(() => t.remove(), 300); }, 3000);
}

// ── THEMES ──
const THEMES = [
  { name: "Oscuro",     key: "dark",       bg: "#0f0f13", panel: "#16161d", text: "#e8e8ed", accent: "#7c6af7" },
  { name: "Claro",      key: "light",      bg: "#f0f2f8", panel: "#ffffff", text: "#1a1a2e", accent: "#7c6af7" },
  { name: "Solarized",  key: "solarized",  bg: "#002b36", panel: "#073642", text: "#839496", accent: "#268bd2" },
  { name: "Midnight",   key: "midnight",   bg: "#090918", panel: "#10102a", text: "#c8c8e8", accent: "#818cf8" },
  { name: "Forest",     key: "forest",     bg: "#0d1a0d", panel: "#142014", text: "#c8e0c8", accent: "#34d399" },
  { name: "Dracula",    key: "dracula",    bg: "#282a36", panel: "#44475a", text: "#f8f8f2", accent: "#bd93f9" },
  { name: "Nord",       key: "nord",       bg: "#2e3440", panel: "#3b4252", text: "#eceff4", accent: "#88c0d0" },
  { name: "Catppuccin", key: "catppuccin", bg: "#1e1e2e", panel: "#313244", text: "#cdd6f4", accent: "#cba6f7" },
  { name: "Gruvbox",    key: "gruvbox",    bg: "#282828", panel: "#3c3836", text: "#ebdbb2", accent: "#fabd2f" },
  { name: "Tokyo",      key: "tokyo",      bg: "#1a1b26", panel: "#24283b", text: "#c0caf5", accent: "#7aa2f7" },
];

function renderThemes() {
  const el = document.getElementById("themeOptions");
  if (!el) return;
  el.innerHTML = "";
  THEMES.forEach(theme => {
    const btn = document.createElement("button");
    btn.className = "themeOption";
    btn.innerHTML = `<div style="width:100%;height:32px;background:${theme.bg};border-radius:8px;border:1px solid rgba(255,255,255,0.08);"></div><span>${theme.name}</span>`;
    btn.onclick = () => { applyTheme(theme.key); localStorage.setItem("theme", theme.key); };
    el.appendChild(btn);
  });
}

function applyTheme(key) {
  const theme = THEMES.find(t => t.key === key);
  if (!theme) return;
  const r = document.documentElement.style;
  r.setProperty("--bg", theme.bg);
  r.setProperty("--panel", theme.panel);
  r.setProperty("--text", theme.text);
  r.setProperty("--accent", theme.accent);
}

// ── PARTICLES ──
function initParticles() {
  particleCanvas = document.getElementById("particleCanvas");
  if (!particleCanvas) return;
  particleCtx = particleCanvas.getContext("2d");
  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);
  for (let i = 0; i < 35; i++) {
    particles.push({ x: Math.random() * particleCanvas.width, y: Math.random() * particleCanvas.height,
      vx: (Math.random() - .5) * .28, vy: (Math.random() - .5) * .28, r: Math.random() * 1.8 + .4, a: Math.random() * .25 + .04 });
  }
  animateParticles();
}
function resizeCanvas() {
  const chatEl = document.getElementById("chat");
  if (!particleCanvas || !chatEl) return;
  particleCanvas.width = chatEl.offsetWidth;
  particleCanvas.height = chatEl.offsetHeight;
}
function animateParticles() {
  if (!particleCtx || !particleCanvas) return;
  particleCtx.clearRect(0, 0, particleCanvas.width, particleCanvas.height);
  const accent = getComputedStyle(document.documentElement).getPropertyValue("--accent").trim() || "#7c6af7";
  particles.forEach(p => {
    p.x += p.vx; p.y += p.vy;
    if (p.x < 0 || p.x > particleCanvas.width) p.vx *= -1;
    if (p.y < 0 || p.y > particleCanvas.height) p.vy *= -1;
    particleCtx.beginPath();
    particleCtx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    particleCtx.fillStyle = accent;
    particleCtx.globalAlpha = p.a;
    particleCtx.fill();
  });
  particleCtx.globalAlpha = 1;
  requestAnimationFrame(animateParticles);
}

// ── CONNECTION ──
async function checkConnection() {
  const dot = document.getElementById("statusDot");
  const label = document.getElementById("statusLabel");
  try {
    const r = await fetch(`${API_BASE}/health`, { headers: { Authorization: "Bearer " + AUTH_PIN }, signal: AbortSignal.timeout(5000) });
    if (r.ok) {
      dot.className = "status-dot online";
      label.className = "status-label online";
      label.textContent = "Conectado";
    } else throw 0;
  } catch {
    dot.className = "status-dot offline";
    label.className = "status-label";
    label.textContent = "Desconectado";
  }
}

// ── HISTORY ──
async function loadHistory() {
  const list = document.getElementById("historyList");
  if (!list) return;
  try {
    const r = await fetch(`${API_BASE}/history`, { headers: authHeaders() });
    const data = await r.json();
    list.innerHTML = "";
    data.forEach(conv => {
      const item = document.createElement("div");
      item.className = "history-item" + (conv.id === currentSessionId ? " active" : "");
      item.innerHTML = `<span class="history-item-text" title="${escapeHTML(conv.title)}">💬 ${escapeHTML(conv.title)}</span><span class="history-delete" title="Eliminar">×</span>`;
      item.onclick = e => { if (e.target.closest(".history-delete")) return; loadConversation(conv.id); };
      item.ondblclick = e => { if (e.target.closest(".history-delete")) return; e.stopPropagation(); startRename(item, conv.id, conv.title); };
      item.querySelector(".history-delete").onclick = async e => {
        e.stopPropagation();
        await fetch(`${API_BASE}/history/${conv.id}`, { method: "DELETE", headers: authHeaders() });
        if (currentSessionId === conv.id) { currentSessionId = null; document.getElementById("chat").innerHTML = ""; showWelcome(); }
        loadHistory();
      };
      list.appendChild(item);
    });
  } catch {
    list.innerHTML = '<div style="padding:8px;font-size:12px;color:var(--muted2);">Sin conexión</div>';
  }
}

function startRename(item, id, oldTitle) {
  let saved = false;
  const textEl = item.querySelector(".history-item-text");
  const input = document.createElement("input");
  input.type = "text"; input.value = oldTitle;
  input.style.cssText = "width:100%;padding:4px 6px;border-radius:6px;border:1px solid var(--accent);background:var(--input-bg);color:var(--text);font-size:12px;font-family:Inter,sans-serif;outline:none;";
  textEl.replaceWith(input);
  input.focus(); input.select();
  const save = async () => {
    if (saved) return; saved = true;
    const newTitle = input.value.trim() || oldTitle;
    await fetch(`${API_BASE}/history/${id}`, { method: "PATCH", headers: authHeaders(), body: JSON.stringify({ title: newTitle }) });
    loadHistory();
  };
  input.onblur = save;
  input.onkeydown = e => { if (e.key === "Enter") { e.preventDefault(); save(); } if (e.key === "Escape") loadHistory(); };
}

async function loadConversation(id) {
  try {
    const r = await fetch(`${API_BASE}/history/${id}`, { headers: authHeaders() });
    const conv = await r.json();
    if (conv.error) return;
    currentSessionId = id;
    const chat = document.getElementById("chat");
    chat.innerHTML = ""; hideWelcome();
    conv.messages.forEach(m => { if (m.role === "system") return; addMessageToChat(m.role === "user" ? "user" : "bot", m.content, m.role !== "user"); });
    addCopyButtons(); scrollFinal(); loadHistory();
    if (window.innerWidth <= 768) {
      document.getElementById("sidebar").classList.remove("mobile-open");
      document.getElementById("sidebarOverlay").classList.remove("show");
    }
  } catch (e) { console.error("Error cargando conversación", e); }
}

// ── WELCOME ──
function showWelcome() {
  let w = document.getElementById("welcomeScreen");
  if (w) { w.style.display = "flex"; return; }
  w = document.createElement("div");
  w.id = "welcomeScreen";
  w.innerHTML = `
    <div class="welcome-logo">✦</div>
    <h2 class="welcome-title">Hola, soy Shio</h2>
    <p class="welcome-sub">¿En qué puedo ayudarte hoy?</p>
    <div class="welcome-suggestions">
      <div class="suggestion" data-msg="Hola Shio, ¿qué puedes hacer?">💬 ¿Qué puedes hacer?</div>
      <div class="suggestion" data-msg="busca Python FastAPI tutorial">🔍 Buscar en la web</div>
      <div class="suggestion" data-msg="noticias">📰 Noticias de hoy</div>
      <div class="suggestion" data-msg="yt tutoriales de cocina">📺 Buscar videos</div>
      <div class="suggestion" data-msg="imagenes de paisajes cyberpunk">🖼️ Buscar imágenes</div>
    </div>`;
  document.getElementById("chat").appendChild(w);
  w.querySelectorAll(".suggestion").forEach(s => {
    s.onclick = () => { document.getElementById("msg").value = s.dataset.msg; enviar(); };
  });
}
function hideWelcome() {
  const w = document.getElementById("welcomeScreen");
  if (w) w.style.display = "none";
}

// ── MESSAGES ──
function addMessageToChat(type, content, parseMarkdown = false) {
  const div = document.createElement("div");
  div.className = "message " + type;
  if (parseMarkdown) { div.innerHTML = marked.parse(content || ""); }
  else { div.textContent = content; }
  const ts = document.createElement("div");
  ts.className = "msg-timestamp";
  ts.textContent = new Date().toLocaleTimeString("es-ES", { hour: "2-digit", minute: "2-digit" });
  div.appendChild(ts);
  document.getElementById("chat").appendChild(div);
  return div;
}

function escapeHTML(str) {
  return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#039;");
}

// ── TYPING ANIMATION ──
function getTypingSpeed(len) { return len < 200 ? 18 : len < 500 ? 10 : len < 1000 ? 5 : 2; }

function typeWriter(element, fullText, onComplete) {
  const speed = getTypingSpeed(fullText.length);
  let i = 0, skipped = false;
  const cursor = document.createElement("span");
  cursor.className = "typing-cursor";
  element.appendChild(cursor);
  element.style.cursor = "pointer";
  const skip = () => { skipped = true; element.style.cursor = ""; element.removeEventListener("click", skip); };
  element.addEventListener("click", skip);
  function type() {
    if (skipped || i >= fullText.length) {
      cursor.remove();
      const ts = element.querySelector(".msg-timestamp");
      element.innerHTML = marked.parse(fullText);
      if (ts) element.appendChild(ts);
      element.style.cursor = "";
      element.removeEventListener("click", skip);
      typingAnimationId = null;
      if (onComplete) onComplete();
      return;
    }
    const chunk = speed <= 3 ? 4 : speed <= 8 ? 2 : 1;
    element.insertBefore(document.createTextNode(fullText.slice(i, i + chunk)), cursor);
    i += chunk;
    scrollFinal();
    typingAnimationId = setTimeout(type, speed);
  }
  type();
}

// ── SEND ──
async function enviar() {
  const input = document.getElementById("msg");
  const msg = input.value.trim();
  if (await checkImagenesComando(msg)) { bloqueado = false; return; }
  if (bloqueado) return;
  if (!msg && !attachedFiles.length) return;
  bloqueado = true;
  hideWelcome();

  if (!currentSessionId) {
    try {
      const r = await fetch(`${API_BASE}/history/new`, { method: "POST", headers: authHeaders() });
      currentSessionId = (await r.json()).session_id;
    } catch { currentSessionId = Date.now().toString(); }
  }

  let displayMsg = msg;
  if (attachedFiles.length) {
    const fileList = attachedFiles.map(f => `📎 **${f.name}**`).join("\n");
    displayMsg = fileList + "\n\n" + msg;
  }
  addMessageToChat("user", displayMsg, true);

  const combinedContext = attachedFiles.map(f => `### [ARCHIVO: ${f.name}]\n${f.text}\n### [FIN ARCHIVO]`).join("\n\n");
  attachedFiles = []; updateFilePreviews();
  input.value = ""; input.style.height = "auto";
  scrollFinal();
  document.getElementById("typing").style.display = "flex";

  try {
    const payload = {
      msg, session_id: currentSessionId,
      file_context: combinedContext || null,
      model: currentModel || null,
      temperature: currentTemp ?? 0.2,
    };
    const r = await fetch(`${API_BASE}/chat`, { method: "POST", headers: authHeaders(), body: JSON.stringify(payload) });
    if (r.status === 429) { showToast("Demasiadas peticiones. Espera un momento.", "error"); document.getElementById("typing").style.display = "none"; bloqueado = false; return; }
    if (r.status === 401) { showToast("Sesión expirada", "error"); document.getElementById("typing").style.display = "none"; bloqueado = false; return; }
    const data = await r.json();
    document.getElementById("typing").style.display = "none";
    if (data.session_id) currentSessionId = data.session_id;

    const botMsg = addMessageToChat("bot", "");
    const responseText = data.text || "_Sin respuesta del modelo_";
    typeWriter(botMsg, responseText, () => {
      addCopyButtons(); scrollFinal();
      if (data.imagenes && data.imagenes.length) {
        const c = document.createElement("div"); c.className = "images-container";
        data.imagenes.slice(0, 10).forEach(url => {
          const img = document.createElement("img"); img.src = url; img.onclick = () => window.open(url, "_blank"); c.appendChild(img);
        });
        botMsg.appendChild(c); scrollFinal();
      }
      if (data.videos && data.videos.length) {
        const c = document.createElement("div"); c.className = "videos-container";
        data.videos.forEach(v => {
          const card = document.createElement("div"); card.className = "video-card";
          card.innerHTML = `<img src="${v.thumbnail}" alt="Thumbnail"><div class="video-info">${v.title}</div>`;
          card.onclick = () => window.open(v.url, "_blank"); c.appendChild(card);
        });
        botMsg.appendChild(c); scrollFinal();
      }
      loadHistory();
    });
  } catch {
    document.getElementById("typing").style.display = "none";
    addMessageToChat("bot", "Error conectando al servidor", true);
    scrollFinal();
  } finally { bloqueado = false; }
}

function scrollFinal() { document.getElementById("chat").scrollTop = document.getElementById("chat").scrollHeight; }

function addCopyButtons() {
  document.querySelectorAll("pre").forEach(pre => {
    if (pre.parentElement.classList.contains("code-block")) return;
    const wrapper = document.createElement("div"); wrapper.className = "code-block";
    const header = document.createElement("div"); header.className = "code-header";
    const langClass = pre.querySelector("code")?.className?.match(/language-(\w+)/);
    header.textContent = langClass ? langClass[1] : "code";
    const btn = document.createElement("button"); btn.className = "copy-btn"; btn.textContent = "Copiar";
    btn.onclick = () => {
      navigator.clipboard.writeText(pre.innerText);
      btn.textContent = "✓ Copiado"; btn.classList.add("copied");
      setTimeout(() => { btn.textContent = "Copiar"; btn.classList.remove("copied"); }, 1500);
    };
    pre.parentNode.insertBefore(wrapper, pre);
    wrapper.appendChild(header); wrapper.appendChild(btn); wrapper.appendChild(pre);
  });
}

// ── VOICE ──
let mediaRecorder, chunks = [];
document.addEventListener("DOMContentLoaded", () => {
  const vozBtn = document.getElementById("vozBtn");
  if (vozBtn) vozBtn.onclick = async () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop(); vozBtn.classList.remove("grabando"); vozBtn.innerHTML = "🎙️"; return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream); chunks = [];
      mediaRecorder.ondataavailable = e => chunks.push(e.data);
      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunks, { type: "audio/wav" });
        const fd = new FormData(); fd.append("file", blob, "voz.wav");
        const r = await fetch(`${API_BASE}/stt`, { method: "POST", body: fd, headers: { Authorization: "Bearer " + AUTH_PIN } });
        document.getElementById("msg").value = (await r.json()).text;
        enviar();
      };
      mediaRecorder.start(); vozBtn.classList.add("grabando"); vozBtn.innerHTML = "⏺";
    } catch { showToast("Sin permiso de micrófono", "error"); }
  };
});

// ── FILE UPLOAD ──
let currentModel = localStorage.getItem("shio_model") || "qwen3-coder:480b-cloud";
let currentTemp = parseFloat(localStorage.getItem("shio_temp") ?? "0.2");
let attachedFiles = [];

function initFileUpload() {
  const chatEl = document.getElementById("chat");
  const dropOverlay = document.getElementById("dropOverlay");
  chatEl.addEventListener("dragover", e => { e.preventDefault(); dropOverlay.style.display = "flex"; });
  chatEl.addEventListener("dragleave", e => { if (!chatEl.contains(e.relatedTarget)) dropOverlay.style.display = "none"; });
  chatEl.addEventListener("drop", async e => {
    e.preventDefault(); dropOverlay.style.display = "none";
    if (e.dataTransfer.files.length) await handleFileUpload(e.dataTransfer.files[0]);
  });
  document.getElementById("fileBtn").onclick = () => document.getElementById("fileInput").click();
  document.getElementById("fileInput").onchange = async e => {
    if (e.target.files.length) await handleFileUpload(e.target.files[0]);
    e.target.value = "";
  };
}

async function handleFileUpload(file) {
  const fd = new FormData(); fd.append("file", file);
  showToast(`Subiendo: ${file.name}…`, "info");
  try {
    const r = await fetch(`${API_BASE}/upload`, { method: "POST", body: fd, headers: { Authorization: "Bearer " + AUTH_PIN } });
    const data = await r.json();
    if (data.error) { showToast(data.error, "error"); return; }
    attachedFiles.push({ name: data.filename || file.name, text: data.text, size: file.size });
    updateFilePreviews();
    document.getElementById("msg").focus();
    showToast("Archivo listo para el chat", "success");
  } catch { showToast("Error subiendo archivo", "error"); }
}

function updateFilePreviews() {
  const c = document.getElementById("filePreviewContainer");
  if (!attachedFiles.length) { c.style.display = "none"; return; }
  c.style.display = "flex"; c.innerHTML = "";
  attachedFiles.forEach((file, index) => {
    const card = document.createElement("div"); card.className = "file-preview-card";
    const ext = file.name.split(".").pop().toUpperCase();
    card.innerHTML = `<span>[${ext}]</span> ${file.name}<div class="file-remove-btn" onclick="removeFile(${index})">✕</div>`;
    c.appendChild(card);
  });
}
function removeFile(index) { attachedFiles.splice(index, 1); updateFilePreviews(); }

// ── IMAGES COMMAND ──
async function checkImagenesComando(msg) {
  if (!msg.toLowerCase().startsWith("imagenes de ")) return false;
  const tema = msg.slice("imagenes de ".length).trim();
  addMessageToChat("user", msg);
  document.getElementById("msg").value = "";
  scrollFinal();
  try {
    const r = await fetch(`${API_BASE}/imagenes`, { method: "POST", headers: authHeaders(), body: JSON.stringify({ tema }) });
    const data = await r.json();
    if (data.imagenes && data.imagenes.length) {
      const botMsg = addMessageToChat("bot", `🖼️ Imágenes de: ${tema}`);
      const c = document.createElement("div"); c.className = "images-container";
      data.imagenes.slice(0, 20).forEach(url => {
        const img = document.createElement("img"); img.src = url; img.onclick = () => window.open(url, "_blank"); c.appendChild(img);
      });
      botMsg.appendChild(c); scrollFinal();
    }
  } catch { console.error("Error al buscar imágenes"); }
  return true;
}

// ── PROMPT EDITOR ──
async function openPromptEditor() {
  try {
    const r = await fetch(`${API_BASE}/prompt`, { headers: authHeaders() });
    const data = await r.json();
    document.getElementById("promptTextarea").value = data.prompt || "";
    document.getElementById("promptPanel").style.display = "flex";
  } catch { showToast("Error cargando prompt", "error"); }
}
async function savePrompt() {
  const text = document.getElementById("promptTextarea").value;
  try {
    await fetch(`${API_BASE}/prompt`, { method: "POST", headers: authHeaders(), body: JSON.stringify({ prompt: text }) });
    showToast("Prompt guardado ✓", "success");
    document.getElementById("promptPanel").style.display = "none";
  } catch { showToast("Error guardando prompt", "error"); }
}

// ── CONFIG (SYSTEM) ──
async function loadRuntimeConfig() {
  try {
    const r = await fetch(`${API_BASE}/config`, { headers: authHeaders() });
    const data = await r.json();
    const pin = document.getElementById("cfgPin");
    const mod = document.getElementById("modelSelect"); // reuse unified model select
    const host = document.getElementById("cfgHost");
    const key = document.getElementById("cfgApiKey");
    if (pin) pin.value = data.pin || "";
    if (mod && data.ollama_model) mod.value = data.ollama_model;
    if (host) host.value = data.ollama_host || "";
    if (key) key.value = data.cloud_api_key || "";
  } catch (e) { console.warn("No se pudo cargar config del servidor", e); }
}

async function saveRuntimeConfig() {
  const pin = document.getElementById("cfgPin");
  const mod = document.getElementById("modelSelect");
  const host = document.getElementById("cfgHost");
  const key = document.getElementById("cfgApiKey");
  const data = {
    pin: pin?.value || "",
    ollama_model: mod?.value || currentModel,
    ollama_host: host?.value || "",
    cloud_api_key: key?.value || "",
  };
  try {
    await fetch(`${API_BASE}/config`, { method: "POST", headers: authHeaders(), body: JSON.stringify(data) });
    if (data.pin && data.pin !== AUTH_PIN) { AUTH_PIN = data.pin; sessionStorage.setItem("shio_pin", data.pin); }
    showToast("Configuración guardada ✓", "success");
    document.getElementById("settingsModal").style.display = "none";
  } catch { showToast("Error guardando configuración", "error"); }
}

// ── UNIFIED SETTINGS ──
function initSettingsPanel() {
  // Tab switching
  document.querySelectorAll(".stab").forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll(".stab").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".settings-tab-content").forEach(c => c.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`tab-${btn.dataset.tab}`)?.classList.add("active");
      // Load server config when switching to sistema tab
      if (btn.dataset.tab === "sistema") loadRuntimeConfig();
    };
  });

  // Model select
  const modelSelect = document.getElementById("modelSelect");
  if (modelSelect) {
    modelSelect.value = currentModel;
    modelSelect.onchange = e => {
      currentModel = e.target.value;
      localStorage.setItem("shio_model", currentModel);
      updateModelBadge();
    };
  }

  // Temperature
  const tempRange = document.getElementById("tempRange");
  const tempValue = document.getElementById("tempValue");
  if (tempRange) {
    tempRange.value = currentTemp;
    if (tempValue) tempValue.textContent = currentTemp.toFixed(2);
    tempRange.oninput = e => {
      currentTemp = parseFloat(e.target.value);
      if (tempValue) tempValue.textContent = currentTemp.toFixed(2);
      localStorage.setItem("shio_temp", currentTemp);
    };
  }

  // Save config button
  const saveConfigBtn = document.getElementById("saveConfigBtn");
  if (saveConfigBtn) saveConfigBtn.onclick = saveRuntimeConfig;

  // Clear memory
  const clearMemoryBtn = document.getElementById("clearMemoryBtn");
  if (clearMemoryBtn) clearMemoryBtn.onclick = () => {
    attachedFiles = []; updateFilePreviews();
    showToast("Contexto y archivos olvidados", "info");
  };

  updateModelBadge();
}

function updateModelBadge() {
  const badge = document.getElementById("modelBadge");
  if (!badge) return;
  const labels = {
    "qwen3-coder:480b-cloud": "🧑‍💻 qwen3-coder:480b",
    "qwen3.5:397b-cloud": "🧠 qwen3.5:397b",
    "qwen3-vl:235b-instruct-cloud": "👁 qwen3-vl:235b",
    "gpt-oss:120b-cloud": "⚡ gpt-oss:120b",
    "deepseek-v3.1:671b-cloud": "🔬 deepseek-v3.1:671b",
  };
  badge.textContent = labels[currentModel] || currentModel;
}

// ── INIT ──
function initApp() {
  const chat = document.getElementById("chat");

  const setupBtn = (id, fn) => { const el = document.getElementById(id); if (el) el.onclick = fn; };

  setupBtn("menuNuevo", async () => {
    try {
      const r = await fetch(`${API_BASE}/history/new`, { method: "POST", headers: authHeaders() });
      currentSessionId = (await r.json()).session_id;
    } catch { currentSessionId = Date.now().toString(); }
    chat.innerHTML = ""; showWelcome(); loadHistory();
    if (window.innerWidth <= 768) {
      document.getElementById("sidebar").classList.remove("mobile-open");
      document.getElementById("sidebarOverlay").classList.remove("show");
    }
  });

  setupBtn("menuTemas", () => { document.getElementById("themePanel").style.display = "flex"; });
  setupBtn("themeClose", () => { document.getElementById("themePanel").style.display = "none"; });
  setupBtn("resetTheme", () => { localStorage.removeItem("theme"); applyTheme("dark"); });

  setupBtn("menuAjustes", () => {
    // Reset to IA tab
    document.querySelectorAll(".stab").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".settings-tab-content").forEach(c => c.classList.remove("active"));
    document.querySelector(".stab[data-tab='ia']")?.classList.add("active");
    document.getElementById("tab-ia")?.classList.add("active");
    document.getElementById("settingsModal").style.display = "flex";
  });
  setupBtn("settingsClose", () => { document.getElementById("settingsModal").style.display = "none"; });

  setupBtn("menuSistema", () => { document.getElementById("systemPanel").style.display = "flex"; });
  setupBtn("systemClose", () => { document.getElementById("systemPanel").style.display = "none"; });
  setupBtn("menuPrompt", openPromptEditor);
  setupBtn("promptClose", () => { document.getElementById("promptPanel").style.display = "none"; });
  setupBtn("savePromptBtn", savePrompt);

  // Close modals on overlay click
  document.querySelectorAll(".modal").forEach(modal => {
    modal.onclick = e => { if (e.target === modal) modal.style.display = "none"; };
  });

  // Textarea auto-grow + Enter to send
  const msgInput = document.getElementById("msg");
  if (msgInput) {
    msgInput.addEventListener("input", () => {
      msgInput.style.height = "auto";
      msgInput.style.height = Math.min(msgInput.scrollHeight, 120) + "px";
    });
    msgInput.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); enviar(); } });
  }

  // Sidebar collapse
  const sidebar = document.getElementById("sidebar");
  const collapseBtn = document.getElementById("collapseBtn");
  collapseBtn.onclick = () => {
    sidebar.classList.toggle("collapsed");
    collapseBtn.innerHTML = sidebar.classList.contains("collapsed") ? "&#8594;" : "&#8592;";
    localStorage.setItem("sidebarCollapsed", sidebar.classList.contains("collapsed"));
  };
  if (localStorage.getItem("sidebarCollapsed") === "true") { sidebar.classList.add("collapsed"); collapseBtn.innerHTML = "&#8594;"; }

  // Mobile
  const mobileMenuBtn = document.getElementById("mobileMenuBtn");
  const sidebarOverlay = document.getElementById("sidebarOverlay");
  mobileMenuBtn.onclick = () => { sidebar.classList.add("mobile-open"); sidebarOverlay.classList.add("show"); };
  sidebarOverlay.onclick = () => { sidebar.classList.remove("mobile-open"); sidebarOverlay.classList.remove("show"); };

  // Close sidebar on mobile menu click
  ["menuNuevo","menuTemas","menuAjustes","menuSistema","menuPrompt"].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      const orig = el.onclick;
      el.onclick = e => {
        if (orig) orig(e);
        if (window.innerWidth <= 768) { sidebar.classList.remove("mobile-open"); sidebarOverlay.classList.remove("show"); }
      };
    }
  });

  // Clock
  function updateClock() {
    const el = document.getElementById("hora");
    if (el) el.textContent = new Date().toLocaleDateString("es-ES", { weekday:"short", day:"numeric", month:"short" }) + "  ·  " + new Date().toLocaleTimeString("es-ES", { hour:"2-digit", minute:"2-digit" });
  }
  updateClock(); setInterval(updateClock, 30000);

  // Theme + particles + etc.
  renderThemes();
  applyTheme(localStorage.getItem("theme") || "dark");

  const safeInit = (name, fn) => { try { fn(); } catch (e) { console.error(`Error initializing ${name}:`, e); } };
  safeInit("Particles", initParticles);
  safeInit("FileUpload", initFileUpload);
  safeInit("Settings", initSettingsPanel);
  safeInit("History", loadHistory);
  safeInit("Welcome", showWelcome);
  safeInit("Connection", checkConnection);
  setInterval(() => safeInit("ConnectionCheck", checkConnection), 15000);
}

// ── BOOT ──
document.addEventListener("DOMContentLoaded", () => {
  const pinInput = document.getElementById("pinInput");
  if (pinInput) pinInput.addEventListener("keydown", e => { if (e.key === "Enter") tryLogin(); });
  checkAuth();
});
