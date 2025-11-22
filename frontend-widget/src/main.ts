const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:9000";

type Block = {
  id: string;
  type?: string;
  text?: string;
  options?: { id: string; label?: string }[];
  slots?: string[];
  actions?: { type: string; [k: string]: any }[];
};

const app = document.getElementById("app") as HTMLDivElement;

const chatBox = document.createElement("div");
chatBox.style.maxWidth = "420px";
chatBox.style.border = "1px solid #ccc";
chatBox.style.padding = "12px";
chatBox.style.fontFamily = "Arial, sans-serif";
chatBox.style.fontSize = "14px";
chatBox.style.minHeight = "240px";
chatBox.style.background = "#f9f9f9";
chatBox.style.borderRadius = "12px";
chatBox.style.boxShadow = "0 4px 14px rgba(0,0,0,0.08)";

const input = document.createElement("input");
input.style.width = "240px";
input.style.borderRadius = "8px";
input.style.border = "1px solid #ccc";
input.style.padding = "6px 8px";
const sendBtn = document.createElement("button");
sendBtn.textContent = "Enviar";
sendBtn.style.marginLeft = "6px";
sendBtn.style.padding = "6px 12px";
sendBtn.style.borderRadius = "8px";
sendBtn.style.background = "#2563eb";
sendBtn.style.color = "#fff";
sendBtn.style.border = "none";

const langSelect = document.createElement("select");
["es", "ca", "pt", "en"].forEach((lng) => {
  const opt = document.createElement("option");
  opt.value = lng;
  opt.textContent = lng.toUpperCase();
  langSelect.appendChild(opt);
});
langSelect.style.marginBottom = "8px";

let sessionId: string | null = null;
let currentBlock: Block | null = null;
let loading = false;
let typingBubble: HTMLDivElement | null = null;

function renderMessage(sender: "Bot" | "Tú", text: string) {
  const row = document.createElement("div");
  row.style.marginTop = "6px";
  row.innerHTML = `<strong>${sender}:</strong> ${text}`;
  chatBox.appendChild(row);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function renderOptions(block: Block) {
  const container = document.createElement("div");
  container.style.marginTop = "6px";
  container.innerHTML = "<div>Elige una opción:</div>";
  block.options?.forEach((opt) => {
    const btn = document.createElement("button");
    btn.textContent = opt.label || opt.id;
    btn.style.marginRight = "6px";
    btn.onclick = () => {
      renderMessage("Tú", btn.textContent || "");
      sendPayload(opt.id);
      container.remove();
    };
    container.appendChild(btn);
  });
  chatBox.appendChild(container);
}

function renderSlots(block: Block) {
  const container = document.createElement("div");
  container.style.marginTop = "6px";
  const title = document.createElement("div");
  title.textContent = "Slots disponibles:";
  container.appendChild(title);
  block.slots?.forEach((s) => {
    const btn = document.createElement("button");
    btn.textContent = s;
    btn.style.marginRight = "6px";
    btn.onclick = () => {
      renderMessage("Tú", s);
      sendPayload(s);
      container.remove();
    };
    container.appendChild(btn);
  });
  chatBox.appendChild(container);
}

function renderAttachments(block: Block) {
  const hasAllow = (block.actions || []).some((a) => a.type === "allow_attachments");
  if (!hasAllow) return;
  const btn = document.createElement("button");
  btn.textContent = "Adjuntar foto";
  btn.style.marginTop = "6px";
  btn.onclick = () => {
    renderMessage("Tú", "[Adjunto enviado]");
    // Aquí iría la lógica real de subida y envío
  };
  chatBox.appendChild(btn);
}

function renderTyping(show: boolean) {
  if (show) {
    if (typingBubble) return;
    typingBubble = document.createElement("div");
    typingBubble.textContent = "Escribiendo…";
    typingBubble.style.fontStyle = "italic";
    typingBubble.style.color = "#555";
    chatBox.appendChild(typingBubble);
  } else if (typingBubble) {
    typingBubble.remove();
    typingBubble = null;
  }
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendPayload(message: string) {
  if (loading) return;
  loading = true;
  sendBtn.disabled = true;
  renderTyping(true);
  const res = await fetch(`${apiBase}/chat/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId, lang: langSelect.value }),
  });
  sendBtn.disabled = false;
  loading = false;
  renderTyping(false);
  if (!res.ok) {
    renderMessage("Bot", "Error al enviar");
    return;
  }
  const data = await res.json();
  sessionId = data.session_id;
  currentBlock = {
    id: data.block_id,
    type: data.type,
    text: data.text,
    options: data.options,
    actions: data.actions,
    slots: data.slots,
  };
  renderMessage("Bot", currentBlock.text || currentBlock.id);
  if (currentBlock.type === "options") {
    renderOptions(currentBlock);
  } else if (currentBlock.type === "appointment" && currentBlock.slots) {
    renderSlots(currentBlock);
  }
  renderAttachments(currentBlock);

  if (data.state_summary) {
    const summary = document.createElement("div");
    summary.style.marginTop = "8px";
    summary.style.padding = "8px";
    summary.style.background = "#eef2ff";
    summary.style.borderRadius = "8px";
    summary.innerHTML = `<strong>Estado:</strong> Score ${data.state_summary.lead_score || 0}, Proyecto: ${
      data.state_summary.project_type || "-"
    }, Presupuesto: ${data.state_summary.budget || "-"}, Urgencia: ${data.state_summary.urgency || "-"}`;
    chatBox.appendChild(summary);
  }
}

async function sendMessage() {
  const message = input.value.trim();
  if (!message) return;
  renderMessage("Tú", message);
  input.value = "";
  await sendPayload(message);
}

sendBtn.onclick = sendMessage;
input.onkeyup = (e) => {
  if (e.key === "Enter") sendMessage();
};

const controls = document.createElement("div");
controls.style.display = "flex";
controls.style.alignItems = "center";
controls.style.gap = "4px";
controls.appendChild(langSelect);
controls.appendChild(input);
controls.appendChild(sendBtn);

app.appendChild(chatBox);
app.appendChild(controls);

// Primer mensaje para iniciar (hola)
sendPayload("hola");
