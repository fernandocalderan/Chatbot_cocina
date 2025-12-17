function buildHeaders(widgetToken) {
  if (!widgetToken) return {};
  return { Authorization: `Bearer ${widgetToken}` };
}

export async function fetchWidgetRuntime(apiUrl, widgetToken) {
  const res = await fetch(`${apiUrl}/v1/widget/runtime`, {
    headers: {
      ...buildHeaders(widgetToken),
    },
  });
  if (!res.ok) return null;
  return res.json();
}

export async function createWidgetSession(apiUrl, widgetToken, tenantId) {
  const res = await fetch(`${apiUrl}/v1/widget/session`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildHeaders(widgetToken),
    },
    body: JSON.stringify({ tenant_id: tenantId }),
  });
  if (!res.ok) return null;
  return res.json();
}

export async function sendWidgetMessage(apiUrl, widgetToken, sessionId, type, value) {
  const res = await fetch(`${apiUrl}/v1/widget/message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildHeaders(widgetToken),
    },
    body: JSON.stringify({
      session_id: sessionId,
      type,
      payload: { value },
    }),
  });
  if (!res.ok) return null;
  return res.json();
}

export async function fetchAgendaSlots(apiUrl, widgetToken, sessionId) {
  const url = new URL(`${apiUrl}/v1/widget/agenda/slots`);
  url.searchParams.set("session_id", sessionId);
  const res = await fetch(url.toString(), { headers: buildHeaders(widgetToken) });
  if (!res.ok) return null;
  return res.json();
}

export async function confirmAgendaSlot(apiUrl, widgetToken, sessionId, slotStart) {
  const res = await fetch(`${apiUrl}/v1/widget/agenda/confirm`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildHeaders(widgetToken),
    },
    body: JSON.stringify({ session_id: sessionId, slot_start: slotStart }),
  });
  if (!res.ok) return null;
  return res.json();
}
