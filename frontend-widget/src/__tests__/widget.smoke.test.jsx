import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, fireEvent, screen, waitFor } from "@testing-library/react";
import FloatingButton from "../components/FloatingButton";

describe("Chat widget smoke test", () => {
  const mockResponse = {
    text: "Respuesta de prueba",
    session_id: "test-session",
    options: [],
  };

  beforeEach(() => {
    vi.restoreAllMocks();
    vi.stubGlobal("fetch", vi.fn(() => Promise.resolve({ json: () => Promise.resolve(mockResponse) })));
    vi.stubGlobal("crypto", { randomUUID: () => "test-session" });
    localStorage.clear();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("abre la ventana, envía un mensaje y muestra respuesta del bot", async () => {
    render(<FloatingButton apiUrl="http://localhost:9000" tenantTheme="blue" />);

    const openBtn = screen.getByRole("button");
    fireEvent.click(openBtn);

    const input = await screen.findByPlaceholderText("Escribe un mensaje…");
    fireEvent.change(input, { target: { value: "hola" } });
    fireEvent.click(screen.getByText("Enviar"));

    await waitFor(() => {
      expect(screen.getByText("Respuesta de prueba")).toBeTruthy();
    });

    expect(global.fetch).toHaveBeenCalled();
  });
});
