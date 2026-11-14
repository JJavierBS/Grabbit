import { render, screen } from "@testing-library/react";
import type { TrustLevel } from "../api/types";
import { TRUST_LABELS, TrustBadge } from "./TrustBadge";

const cases: [TrustLevel, string][] = [
  ["filing", "Official filing"],
  ["primary", "Company or investor"],
  ["press", "Press"],
  ["aggregator", "Database"],
  ["cala_news", "Cala news"],
  ["web_unverified", "Web, unverified"],
  ["not_published", "Not published"],
];

describe("TrustBadge", () => {
  it.each(cases)("shows the agent.md label for %s", (level, label) => {
    render(<TrustBadge level={level} />);
    const badge = screen.getByText(label).closest("[data-trust]");
    expect(badge).toHaveAttribute("data-trust", level);
    expect(TRUST_LABELS[level]).toBe(label);
  });

  it("names the source in the accessible description when given", () => {
    render(<TrustBadge level="filing" sourceName="Companies House" />);
    expect(screen.getByTitle("Official filing: Companies House")).toBeInTheDocument();
  });

  it("links to the source when a url is given", () => {
    render(<TrustBadge level="press" sourceName="TechCrunch" href="https://example.com/a" />);
    const link = screen.getByRole("link", { name: /press/i });
    expect(link).toHaveAttribute("href", "https://example.com/a");
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", expect.stringContaining("noopener"));
  });

  it("never renders a link for not published facts", () => {
    render(<TrustBadge level="not_published" href="https://example.com" />);
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
  });
});
