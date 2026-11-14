import { act, screen } from "@testing-library/react";
import { profileV2, reportV1, reportV2 } from "../../dev/fixtures";
import { SETTLE_MS } from "../../lib/useSettled";
import { cssFile, declarations } from "../../test/css";
import { renderWithQuery, stubApi } from "../../test/render";
import { ReportView } from "./ReportView";
import { diffReports } from "./reportDiff";

const css = cssFile("features/report/ReportView.module.css");

function show(props: Partial<Parameters<typeof ReportView>[0]> = {}) {
  stubApi({ "/api/profile": { body: profileV2 } });
  return renderWithQuery(
    <ReportView
      report={reportV2}
      isPending={false}
      error={null}
      onRetry={() => {}}
      diff={null}
      {...props}
    />,
  );
}

describe("ReportView, calm surfaces", () => {
  afterEach(() => vi.useRealTimers());

  it("tints what changed for about four seconds, then lets the tint fade", () => {
    vi.useFakeTimers();
    const diff = diffReports(reportV1, reportV2);
    expect(diff).not.toBeNull();
    const { container } = show({ diff });
    const changed = container.querySelectorAll("[data-changed]");
    expect(changed.length).toBeGreaterThan(0);
    for (const el of changed) expect(el).not.toHaveAttribute("data-settled");

    act(() => vi.advanceTimersByTime(SETTLE_MS));
    for (const el of container.querySelectorAll("[data-changed]")) {
      expect(el).toHaveAttribute("data-settled");
    }
    // The tint only applies while not settled, and fades with a transition.
    expect(css).toMatch(/\.section\[data-changed\]:not\(\[data-settled\]\)/);
    expect(declarations(css, ".section").transition).toContain("background-color");
  });

  it("uses a soft violet banner with violet text for a rewrite", () => {
    show({ diff: diffReports(reportV1, reportV2) });
    expect(screen.getByRole("status")).toHaveTextContent("Rewritten for you.");
    const banner = declarations(css, ".banner");
    expect(banner.background).toBe("var(--color-marker-soft)");
    expect(banner.color).toBe("var(--color-violet-light)");
  });

  it("does not show the profile version in the report header", () => {
    show();
    expect(screen.queryByText(/Profile version/)).not.toBeInTheDocument();
  });

  it("shows an empty report as a calm note, not as an error", () => {
    const { container } = show({ report: { ...reportV2, sections: [], candidates: [] } });
    expect(screen.getByText("No startup matches yet")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(container.querySelector('[data-state="empty"]')).not.toBeNull();
  });

  it("shows a missing report as a calm note, and only a failed load as an error", () => {
    show({ report: undefined });
    expect(screen.getByText("No report yet")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("keeps a failed load as an error with a retry", () => {
    show({ report: undefined, error: new Error("Cala is down") });
    expect(screen.getByRole("alert")).toHaveTextContent("Cala is down");
  });
});
