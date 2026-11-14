import { fireEvent, render, screen } from "@testing-library/react";
import { NODE_H } from "../../../components/GraphText";
import { exploredAurora } from "../../../dev/fixtures";
import { cssFile, declarations, fontSizesPx } from "../../../test/css";
import { ExploredGraphView } from "./ExploredGraphView";

const css = cssFile("features/chat/openui/ExploredGraphView.module.css");
const LONG = "Northern Lights Climate Opportunities Fund";
const graph = {
  ...exploredAurora,
  nodes: exploredAurora.nodes.map((n) => (n.entity_id === "c-fjord" ? { ...n, name: LONG } : n)),
};

function draw() {
  return render(<ExploredGraphView graph={graph} rootId="i-aurora" trusted={new Set()} />);
}

describe("ExploredGraphView legibility", () => {
  it("draws at its own size instead of scaling the text down", () => {
    const { container } = draw();
    const svg = container.querySelector("svg") as SVGSVGElement;
    const [, , vbWidth, vbHeight] = (svg.getAttribute("viewBox") ?? "").split(" ").map(Number);
    expect(Number(svg.getAttribute("width"))).toBe(vbWidth);
    expect(Number(svg.getAttribute("height"))).toBe(vbHeight);
    const rule = declarations(css, ".svg");
    expect(rule.width).toBeUndefined();
    expect(rule["max-width"]).toBe("none");
    expect(declarations(css, ".scroll")["overflow-x"]).toBe("auto");
  });

  it("never sets graph text below 12px", () => {
    expect(Math.min(...fontSizesPx(css))).toBeGreaterThanOrEqual(12);
  });

  it("puts every edge label on a background plate", () => {
    const { container } = draw();
    const labels = container.querySelectorAll("[data-edge-label]");
    expect(labels.length).toBeGreaterThan(0);
    for (const label of labels) expect(label.querySelector("rect + text")).not.toBeNull();
    expect(declarations(css, ".edgeLabelBg").fill).toBe("var(--color-panel)");
  });

  it("keeps nodes and source badges at least 24px tall", () => {
    expect(NODE_H).toBeGreaterThanOrEqual(24);
    const { container } = draw();
    for (const rect of container.querySelectorAll('g[role="button"] > rect')) {
      expect(Number(rect.getAttribute("height"))).toBeGreaterThanOrEqual(24);
    }
    expect(declarations(css, ".caption [data-trust]")["min-height"]).toBe("24px");
  });

  it("shows a clipped node's full name on focus and on hover", () => {
    const { container } = draw();
    const node = screen.getByRole("button", { name: new RegExp(LONG) });
    expect(node.querySelector("text")?.textContent).toMatch(/…$/);
    expect(container.querySelector("[data-overlay]")).toBeNull();

    fireEvent.focus(node);
    expect(container.querySelector("[data-overlay] text")?.textContent).toBe(LONG);
    fireEvent.blur(node);
    expect(container.querySelector("[data-overlay]")).toBeNull();

    fireEvent.pointerEnter(node);
    expect(container.querySelector("[data-overlay] text")?.textContent).toBe(LONG);
    fireEvent.pointerLeave(node);
    expect(container.querySelector("[data-overlay]")).toBeNull();
  });
});
