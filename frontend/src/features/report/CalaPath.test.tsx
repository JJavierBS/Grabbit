import { fireEvent, render, screen } from "@testing-library/react";
import { candidates } from "../../dev/fixtures";
import { cssFile, declarations, fontSizesPx } from "../../test/css";
import { CalaPath } from "./CalaPath";

const css = cssFile("features/report/CalaPath.module.css");
const northwind = (() => {
  const found = candidates.find((c) => c.entity_id === "c-northwind");
  if (!found) throw new Error("fixture changed");
  return found;
})();
const LONG = "Northwind Atmospheric Carbon Removal Systems";

function draw() {
  return render(
    <CalaPath candidate={{ ...northwind, name: LONG }} trusted={new Set(["i-aurora"])} />,
  );
}

describe("CalaPath legibility", () => {
  it("draws at its own size instead of scaling the text down", () => {
    const { container } = draw();
    const svg = container.querySelector("svg") as SVGSVGElement;
    const [, , vbWidth] = (svg.getAttribute("viewBox") ?? "").split(" ").map(Number);
    expect(Number(svg.getAttribute("width"))).toBe(vbWidth);
    expect(declarations(css, ".svg").width).toBeUndefined();
    expect(Math.min(...fontSizesPx(css))).toBeGreaterThanOrEqual(12);
  });

  it("puts every edge label on a plate and colours only the strong ones violet", () => {
    const { container } = draw();
    const labels = container.querySelectorAll("[data-edge-label]");
    expect(labels.length).toBeGreaterThan(0);
    for (const label of labels) expect(label.querySelector("rect + text")).not.toBeNull();
    expect(declarations(css, ".edgeLabel").fill).toBe("var(--color-text-muted)");
    expect(declarations(css, ".edgeStrong .edgeLabel").fill).toBe("var(--color-violet-light)");
  });

  it("keeps source badges in the caption at least 24px tall", () => {
    expect(declarations(css, ".caption [data-trust]")["min-height"]).toBe("24px");
  });

  it("shows a clipped node's full name on focus", () => {
    const { container } = draw();
    const node = screen.getByRole("button", { name: `Company ${LONG}` });
    expect(node.querySelector("text")?.textContent).toMatch(/…$/);
    fireEvent.focus(node);
    expect(container.querySelector("[data-overlay] text")?.textContent).toBe(LONG);
    fireEvent.blur(node);
    expect(container.querySelector("[data-overlay]")).toBeNull();
  });
});
