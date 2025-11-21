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

const input = document.createElement("input");
input.style.width = "240px";
const sendBtn = document.createElement("button");
sendBtn.textContent = "Enviar";

let sessionId: string | null = null;
let currentBlock: Block | null = null;

function renderMessage(sender: "Bot" | "Tú", text: string) {
  const row = document.createElement("div");
  row.innerHTML = `<strong>${sender}:</strong> ${text}`;
  chatBox.appendChild(row);
}

function renderOptions(block: Block) {
  const container = document.createElement("div");
  block.options?.forEach((opt) => {
    const btn = document.createElement("button");
    btn.textContent = opt.label_es || opt.id;
    btn.onclick = () => sendPayload(opt.id);
    container.appendChild(btn);
  });
  chatBox.appendChild(container);
}

async function sendPayload(message: string) {
  const res = await fetch(`${apiBase}/chat/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  });
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
    const slotRow = document.createElement("div");
    slotRow.textContent = `Slots: ${currentBlock.slots.join(", ")}`;
    chatBox.appendChild(slotRow);
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
