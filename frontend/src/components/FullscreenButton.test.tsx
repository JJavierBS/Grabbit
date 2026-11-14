import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { FullscreenButton } from "./FullscreenButton";

let fullscreenElement: Element | null = null;

function setFullscreen(element: Element | null) {
  fullscreenElement = element;
  document.dispatchEvent(new Event("fullscreenchange"));
}

function stubFullscreen(enabled: boolean) {
  Object.defineProperty(document, "fullscreenEnabled", { configurable: true, value: enabled });
  Object.defineProperty(document, "fullscreenElement", {
    configurable: true,
    get: () => fullscreenElement,
  });
  const request = vi.fn(() => {
    setFullscreen(document.documentElement);
    return Promise.resolve();
  });
  const exit = vi.fn(() => {
    setFullscreen(null);
    return Promise.resolve();
  });
  document.documentElement.requestFullscreen = request;
  document.exitFullscreen = exit;
  return { request, exit };
}

afterEach(() => {
  fullscreenElement = null;
  Reflect.deleteProperty(document, "fullscreenEnabled");
  Reflect.deleteProperty(document, "fullscreenElement");
});

describe("FullscreenButton", () => {
  it("puts the page in full screen and takes it out again", async () => {
    const { request, exit } = stubFullscreen(true);
    render(<FullscreenButton />);

    await userEvent.click(screen.getByRole("button", { name: "Full screen" }));
    expect(request).toHaveBeenCalledOnce();
    const exitButton = screen.getByRole("button", { name: "Exit full screen" });
    expect(exitButton).toHaveAttribute("aria-pressed", "true");

    await userEvent.click(exitButton);
    expect(exit).toHaveBeenCalledOnce();
    expect(screen.getByRole("button", { name: "Full screen" })).toBeInTheDocument();
  });

  it("follows full screen left with Esc or the back gesture", () => {
    stubFullscreen(true);
    render(<FullscreenButton />);
    act(() => setFullscreen(document.documentElement));
    expect(screen.getByRole("button", { name: "Exit full screen" })).toBeInTheDocument();
    act(() => setFullscreen(null));
    expect(screen.getByRole("button", { name: "Full screen" })).toBeInTheDocument();
  });

  it("is hidden where the browser cannot go full screen", () => {
    stubFullscreen(false);
    render(<FullscreenButton />);
    expect(screen.queryByRole("button", { name: /full screen/i })).not.toBeInTheDocument();
  });
});
