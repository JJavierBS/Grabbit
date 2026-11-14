import { render, screen } from "@testing-library/react";
import { reportV2 } from "../../dev/fixtures";
import { cssFile, declarations } from "../../test/css";
import { ReportOutline } from "./ReportOutline";

const css = cssFile("features/report/ReportOutline.module.css");

describe("ReportOutline", () => {
  it("shows date and size, and leaves the profile version to What changed", () => {
    render(<ReportOutline report={reportV2} open={false} rewritten={false} onOpen={() => {}} />);
    expect(screen.getByText(/4 startups/)).toBeInTheDocument();
    expect(screen.queryByText(/Profile version/)).not.toBeInTheDocument();
  });

  it("lifts slightly on hover with a short transition, and stays put under reduced motion", () => {
    const hover = declarations(css, ".card:hover");
    expect(hover.transform).toBe("translateY(var(--lift-hover))");
    expect(declarations(css, ".card").transition).toMatch(/transform var\(--duration-fast\)/);
    const reduced = css.slice(css.indexOf("prefers-reduced-motion"));
    expect(reduced).toMatch(/\.card:hover\s*\{\s*transform: none;/);
  });
});
