import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import App from "./App.jsx";

globalThis.URL.createObjectURL = () => "blob:preview";
globalThis.URL.revokeObjectURL = () => {};
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

function upload(container) {
  const input = container.querySelector("input[type=file]");
  fireEvent.change(input, { target: { files: [new File(["x"], "clip.mp4", { type: "video/mp4" })] } });
}

test("shows the verdict and timeline returned by the API", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue({
    ok: true,
    json: async () => ({
      violent: true, decided_by: "video", audio_probability: 0.2, violent_clip_share: 0.75,
      seconds: 3.2, note: "",
      clips: [0.9, 0.8, 0.95, 0.1].map((p, i) => ({ start: i * 0.64, end: (i + 1) * 0.64, probability: p })),
    }),
  });
  const { container } = render(<App />);
  upload(container);
  fireEvent.click(screen.getByText("Detect violence"));
  await waitFor(() => screen.getByText("Violent content detected"));
  expect(screen.getByText("75% of 4")).toBeTruthy();
  expect(container.querySelectorAll("rect.hot")).toHaveLength(3);
});

test("shows the server's error message", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue({ ok: false, status: 415, json: async () => ({ error: "unsupported file type" }) });
  const { container } = render(<App />);
  upload(container);
  fireEvent.click(screen.getByText("Detect violence"));
  await waitFor(() => screen.getByRole("alert"));
  expect(screen.getByRole("alert").textContent).toBe("unsupported file type");
});

test("button is disabled until a file is chosen", () => {
  render(<App />);
  expect(screen.getByText("Detect violence").disabled).toBe(true);
});
