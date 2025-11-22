const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:9000";

type Block = {
  id: string;
  type?: string;
  text?: string;
  options?: { id: string; [k: string]: string }[];
  slots?: string[];
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

const input = document.createElement("input");
input.style.width = "240px";
const sendBtn = document.createElement("button");
sendBtn.textContent = "Enviar";

let sessionId: string | null = null;
let currentBlock: Block | null = null;
let loading = false;

function renderMessage(sender: "Bot" | "Tú", text: string) {
  const row = document.createElement("div");
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
    btn.textContent = opt.label_es || opt.id;
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

async function sendPayload(message: string) {
  if (loading) return;
  loading = true;
  sendBtn.disabled = true;
  const res = await fetch(`${apiBase}/chat/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  });
  sendBtn.disabled = false;
  loading = false;
  if (!res.ok) {
    renderMessage("Bot", "Error al enviar");
    return;
  }
  const data = await res.json();
  sessionId = data.session_id;
  currentBlock = data.block;
  renderMessage("Bot", currentBlock.text || currentBlock.id);
  if (currentBlock.type === "options") {
    renderOptions(currentBlock);
  } else if (currentBlock.type === "appointment" && currentBlock.slots) {
    renderSlots(currentBlock);
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

app.appendChild(chatBox);
app.appendChild(input);
app.appendChild(sendBtn);

// Primer mensaje para iniciar (hola)
sendPayload("hola");
