import { act, render, screen, within } from "@testing-library/react";
import { ELAPSED_AFTER_MS, WorkingLine, workingText } from "./WorkingLine";

describe("WorkingLine", () => {
  afterEach(() => vi.useRealTimers());

  it("says Grabbit is walking Cala while there is no report yet", () => {
    render(<WorkingLine hasReport={false} />);
    expect(screen.getByRole("status")).toHaveTextContent(
      "Reading your thesis and walking the Slush attendees in Cala…",
    );
  });

  it("says Grabbit is checking the report once one exists", () => {
    render(<WorkingLine hasReport />);
    expect(screen.getByRole("status")).toHaveTextContent(workingText(true));
    expect(workingText(true)).toBe("Reading your message and checking the report…");
  });

  it("counts the seconds only after 10 s, hidden from screen readers", () => {
    vi.useFakeTimers();
    render(<WorkingLine hasReport={false} />);
    const status = screen.getByRole("status");
    act(() => vi.advanceTimersByTime(ELAPSED_AFTER_MS - 1000));
    expect(status).not.toHaveTextContent(/· \d+ s/);

    act(() => vi.advanceTimersByTime(3000));
    const count = within(status).getByText("· 12 s");
    expect(count).toHaveAttribute("aria-hidden", "true");
  });
});
