const locales = {
  es: {
    headerTitle: "Asistente virtual",
    headerSubtitle: "Resolvemos tus dudas",
    status: { label: "En linea" },
    openLabel: "Abrir chat",
    closeLabel: "Cerrar chat",
    messagePlaceholder: "Escribe un mensaje...",
    sendLabel: "Enviar",
    errorMessage: "No pude responder. Intenta de nuevo.",
  },
  en: {
    headerTitle: "Virtual assistant",
    headerSubtitle: "We can help you",
    status: { label: "Online" },
    openLabel: "Open chat",
    closeLabel: "Close chat",
    messagePlaceholder: "Type a message...",
    sendLabel: "Send",
    errorMessage: "I could not reply. Please try again.",
  },
};

export function resolveLanguage(language) {
  const normalized = (language || "").toLowerCase();
  if (normalized.startsWith("en")) return "en";
  if (normalized.startsWith("es")) return "es";
  return "es";
}

export function getStrings(language) {
  const key = resolveLanguage(language);
  return locales[key] || locales.es;
}
