import { act, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { mockApi, renderWithClient } from "../../test/renderApp";
import { ALERT_DELAY_MS, DemoAlertButton } from "./DemoAlertButton";

describe("DemoAlertButton", () => {
  beforeEach(() => vi.useFakeTimers({ shouldAdvanceTime: true }));
  afterEach(() => vi.useRealTimers());

  it("counts the seconds down while the alert is on its way", async () => {
    mockApi({ "POST /api/demo/simulate-event": () => ({}) });
    renderWithClient(<DemoAlertButton fixture="grei_seed_round" />);
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

    await user.click(screen.getByRole("button", { name: "Alerts" }));
    const button = screen.getByRole("button", { name: "Alert in 30 s" });
    expect(button).toBeDisabled();

    act(() => vi.advanceTimersByTime(10_000));
    expect(button).toHaveAccessibleName("Alert in 20 s");

    act(() => vi.advanceTimersByTime(ALERT_DELAY_MS - 10_000));
    await waitFor(() => expect(screen.getByRole("button", { name: "Alerts" })).toBeEnabled());
  });

  it("says why when the simulation fails, instead of re-enabling silently", async () => {
    mockApi({
      "POST /api/demo/simulate-event": {
        status: 404,
        body: { error: { code: "fixture_not_found", message: "No demo event 'nope'." } },
      },
    });
    renderWithClient(<DemoAlertButton fixture="nope" />);
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

    await user.click(screen.getByRole("button", { name: "Alerts" }));
    act(() => vi.advanceTimersByTime(ALERT_DELAY_MS));

    expect(await screen.findByText("The demo alert did not fire")).toBeInTheDocument();
    expect(screen.getByText("No demo event 'nope'.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Alerts" })).toBeEnabled();
  });
});
