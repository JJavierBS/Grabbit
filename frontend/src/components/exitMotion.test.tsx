import { act, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { App } from "../App";
import { historyV2, profileV2, reportV1 } from "../dev/fixtures";
import { mockApi, renderWithClient } from "../test/renderApp";
import { ToastProvider, useToast } from "./Toast";
import { EXIT_FALLBACK_MS } from "./usePresence";

// jsdom runs no CSS animations. Pretend every element has one that never reports finishing,
// so the exits must hold the element in its leaving state and fall back to the timeout.
function withRunningAnimations() {
  const never = { finished: new Promise<Animation>(() => {}) } as unknown as Animation;
  Object.defineProperty(Element.prototype, "getAnimations", {
    configurable: true,
    value: () => [never],
  });
}

function withoutAnimations() {
  Reflect.deleteProperty(Element.prototype, "getAnimations");
}

function Fire() {
  const { toast } = useToast();
  return (
    <button type="button" onClick={() => toast({ title: "GREÏ raised", duration: null })}>
      fire
    </button>
  );
}

describe("exit motion", () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    withRunningAnimations();
  });
  afterEach(() => {
    withoutAnimations();
    vi.useRealTimers();
  });

  it("lets a dismissed toast play its exit before it leaves the list", async () => {
    render(
      <ToastProvider>
        <Fire />
      </ToastProvider>,
    );
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    await user.click(screen.getByRole("button", { name: "fire" }));
    const card = screen.getByText("GREÏ raised").closest("li") as HTMLElement;

    await user.click(screen.getByRole("button", { name: "Dismiss: GREÏ raised" }));
    expect(card).toHaveAttribute("data-state", "leaving");
    expect(card).toBeInTheDocument();

    act(() => vi.advanceTimersByTime(EXIT_FALLBACK_MS));
    expect(card).not.toBeInTheDocument();
  });

  it("slides the side panel out before unmounting it", async () => {
    mockApi({
      "GET /api/profile": () => profileV2,
      "GET /api/profile/history": () => historyV2,
      "GET /api/chat": () => [],
      "GET /api/alerts": () => [],
      "GET /api/reports": () => [],
      "GET /api/reports/latest": () => reportV1,
    });
    renderWithClient(<App />);
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    await user.click(await screen.findByRole("button", { name: "Open report" }));
    const panel = document.getElementById("report-panel") as HTMLElement;
    expect(within(panel).getByRole("heading", { name: "Slush 2026 prep report" })).toBeVisible();

    await user.click(screen.getByRole("button", { name: "Close panel" }));
    expect(panel).toHaveAttribute("data-state", "leaving");
    expect(panel).toBeInTheDocument();

    act(() => vi.advanceTimersByTime(EXIT_FALLBACK_MS));
    expect(document.getElementById("report-panel")).toBeNull();
  });
});
