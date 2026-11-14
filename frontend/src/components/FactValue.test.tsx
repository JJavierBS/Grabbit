import { render, screen } from "@testing-library/react";
import type { Fact } from "../api/types";
import { FactValue, formatFact } from "./FactValue";

const src = (date_precision: "day" | "month" | "year" | null = null) => ({
  name: "Companies House",
  rank: "filing" as const,
  url: "https://example.com/filing",
  date: "2019-01-01",
  date_precision,
});

describe("formatFact", () => {
  it("shows a year-precision date as the year only", () => {
    const fact: Fact = { value: "2019-01-01", unit: null, trust: "filing", sources: [src("year")] };
    expect(formatFact(fact, "date")).toBe("2019");
  });

  it("shows month and day precision", () => {
    expect(
      formatFact(
        { value: "2024-03-01", unit: null, trust: "press", sources: [src("month")] },
        "date",
      ),
    ).toBe("Mar 2024");
    expect(
      formatFact(
        { value: "2024-03-14", unit: null, trust: "press", sources: [src("day")] },
        "date",
      ),
    ).toBe("14 Mar 2024");
  });

  it("does not shift a date across time zones", () => {
    expect(
      formatFact(
        { value: "2024-01-01", unit: null, trust: "press", sources: [src("day")] },
        "date",
      ),
    ).toBe("1 Jan 2024");
  });

  it("formats money with its currency, compact", () => {
    expect(formatFact({ value: 2_500_000, unit: "EUR", trust: "primary", sources: [] })).toBe(
      "€2.5M",
    );
  });

  it("keeps a sourced zero as zero", () => {
    expect(formatFact({ value: 0, unit: "people", trust: "filing", sources: [src()] })).toBe(
      "0 people",
    );
  });

  it("returns null when the value is absent", () => {
    expect(formatFact({ value: null, unit: null, trust: "not_published", sources: [] })).toBeNull();
  });

  it("joins lists and reads booleans", () => {
    expect(
      formatFact({ value: ["Fintech", "SaaS"], unit: null, trust: "aggregator", sources: [] }),
    ).toBe("Fintech, SaaS");
    expect(formatFact({ value: true, unit: null, trust: "aggregator", sources: [] })).toBe("Yes");
  });
});

describe("FactValue", () => {
  it('reads "Not published" with its badge when Cala has no value, never 0', () => {
    render(
      <FactValue
        label="Total funding"
        fact={{ value: null, unit: null, trust: "not_published", sources: [] }}
      />,
    );
    expect(screen.getAllByText("Not published").length).toBeGreaterThan(0);
    expect(screen.queryByText(/0/)).not.toBeInTheDocument();
  });

  it("treats a null value as not published even with another trust level", () => {
    const { container } = render(
      <FactValue label="HQ" fact={{ value: null, unit: null, trust: "press", sources: [] }} />,
    );
    expect(container.querySelector('[data-trust="press"]')).toBeNull();
    expect(container.querySelector('[data-trust="not_published"]')).not.toBeNull();
  });

  it("shows the value with the strongest source badge and link", () => {
    render(
      <FactValue
        label="Founded"
        kind="date"
        fact={{ value: "2019-06-01", unit: null, trust: "filing", sources: [src("year")] }}
      />,
    );
    expect(screen.getByText("2019")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /official filing/i })).toHaveAttribute(
      "href",
      "https://example.com/filing",
    );
    expect(screen.getByText("Founded")).toBeInTheDocument();
  });
});
