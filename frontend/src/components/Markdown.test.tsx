import { render, screen, within } from "@testing-library/react";
import { Markdown } from "./Markdown";

describe("Markdown", () => {
  it("renders paragraphs, lists, bold, italic and links", () => {
    const { container } = render(
      <Markdown
        source={"Intro with **bold** and *soft*.\n\n- one\n- [two](https://example.com)"}
      />,
    );
    expect(container.querySelectorAll("p")).toHaveLength(1);
    expect(screen.getByText("bold").tagName).toBe("STRONG");
    expect(screen.getByText("soft").tagName).toBe("EM");
    expect(screen.getAllByRole("listitem")).toHaveLength(2);
    expect(screen.getByRole("link", { name: "two" })).toHaveAttribute(
      "href",
      "https://example.com",
    );
  });

  it("never renders raw HTML or unsafe links", () => {
    const { container } = render(
      <Markdown source={"<img src=x onerror=alert(1)> [x](javascript:alert(1))"} />,
    );
    expect(container.querySelector("img")).toBeNull();
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
    expect(container.textContent).toContain("<img src=x onerror=alert(1)>");
  });

  it.each([
    ["[Filing]", "filing"],
    ["[Official filing]", "filing"],
    ["[Company or investor]", "primary"],
    ["[Press]", "press"],
    ["[Database]", "aggregator"],
    ["[Web, unverified]", "web_unverified"],
    ["[Not published]", "not_published"],
    ["(database)", "aggregator"],
    ["(PRESS)", "press"],
    ["[web unverified]", "web_unverified"],
  ])("draws %s as a %s trust badge instead of text", (tag, level) => {
    const { container } = render(<Markdown source={`Raised €1.2M ${tag} last year.`} />);
    const badge = container.querySelector(`[data-trust="${level}"]`);
    expect(badge).not.toBeNull();
    expect(container.textContent).not.toContain(tag);
    expect(container.querySelector("p")?.textContent).toMatch(/^Raised €1\.2M .+ last year\.$/);
  });

  it("gives an inline badge its trust label as accessible name", () => {
    render(<Markdown source="Kiln raised €2M [Database]." />);
    const badge = screen.getByTitle("Database");
    expect(within(badge).getByText("Database")).toHaveClass("visually-hidden");
  });

  it("spells out Not published instead of an icon-only badge", () => {
    render(<Markdown source="Revenue [Not published]" />);
    expect(screen.getByText("Not published")).not.toHaveClass("visually-hidden");
  });

  it("keeps badges inside their list item", () => {
    render(<Markdown source={"- Seed €1M [Press]\n- Lead Inventure (Filing)"} />);
    const items = screen.getAllByRole("listitem");
    expect(items).toHaveLength(2);
    expect(items[0].querySelector('[data-trust="press"]')).not.toBeNull();
    expect(items[1].querySelector('[data-trust="filing"]')).not.toBeNull();
  });

  it("draws tags inside bold text and keeps links whose text is a label", () => {
    const { container } = render(
      <Markdown source="**€3M [Database]** per [Press](https://example.com/a)" />,
    );
    expect(container.querySelector('strong [data-trust="aggregator"]')).not.toBeNull();
    expect(screen.getByRole("link", { name: "Press" })).toHaveAttribute(
      "href",
      "https://example.com/a",
    );
  });

  it("leaves other bracketed text as text", () => {
    const { container } = render(
      <Markdown source="Notes [draft] and (press release) and [Database, Press]." />,
    );
    expect(container.querySelector("[data-trust]")).toBeNull();
    expect(container.textContent).toBe("Notes [draft] and (press release) and [Database, Press].");
  });

  it("writes ISO dates as day, month and year", () => {
    const { container } = render(
      <Markdown source="Closed on 2026-06-10, announced 2025-01-03. Ref 2026-13-01." />,
    );
    expect(container.textContent).toBe(
      "Closed on 10 Jun 2026, announced 3 Jan 2025. Ref 2026-13-01.",
    );
  });
});
