import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, fireEvent, screen, waitFor } from "@testing-library/react";
import FloatingButton from "../components/FloatingButton";

describe("Chat widget smoke test", () => {
  const runtime = {
    tenant: { id: "tenant-1", display_name: "Estudio Martínez" },
    visual: { primary_color: "#3A4F7A", position: "bottom-right", size: "medium", logo_url: null },
    messages: { welcome: "Hola 👋", language: "es", errors: { offline: "Offline" } },
    automation: { ai_level: "medium", saving_mode: false, human_fallback: true },
    flow_id: "cocinas_v3",
  };

  beforeEach(() => {
    vi.restoreAllMocks();
    const store = {};
    vi.stubGlobal("localStorage", {
      getItem: (k) => (k in store ? store[k] : null),
      setItem: (k, v) => {
        store[k] = String(v);
      },
      removeItem: (k) => {
        delete store[k];
      },
      clear: () => {
        Object.keys(store).forEach((k) => delete store[k]);
      },
    });
    vi.stubGlobal("fetch", vi.fn((url) => {
      const u = String(url);
      if (u.includes("/v1/widget/session")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ session_id: "sess-1", state: "INICIADA" }) });
      }
      if (u.includes("/v1/widget/message")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ messages: [{ type: "text", content: "Respuesta de prueba" }], state: "EN_CONVERSACION" }),
        });
      }
      if (u.includes("/v1/widget/agenda/slots")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ slots: [] }) });
      }
      return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
    }));
    globalThis.localStorage.clear();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("abre la ventana, envía un mensaje y muestra respuesta del bot", async () => {
    render(<FloatingButton apiUrl="http://localhost:9000" widgetToken="token" runtime={runtime} strings={{ sendLabel: "Enviar" }} />);

    const openBtn = screen.getByRole("button");
    fireEvent.click(openBtn);

    const input = await screen.findByPlaceholderText("Escribe un mensaje...");
    fireEvent.change(input, { target: { value: "hola" } });
    fireEvent.click(screen.getByText("Enviar"));

    await waitFor(() => {
      expect(screen.getByText("Respuesta de prueba")).toBeTruthy();
    });

    expect(global.fetch).toHaveBeenCalled();
  });
});
