import { dayLabel, shortTitle } from "./ReportSidebar";

describe("dayLabel", () => {
  const now = new Date(2026, 10, 14, 10, 0);

  it("names today and yesterday, and dates anything older", () => {
    expect(dayLabel(new Date(2026, 10, 14, 0, 5).toISOString(), now)).toBe("Today");
    expect(dayLabel(new Date(2026, 10, 13, 23, 50).toISOString(), now)).toBe("Yesterday");
    expect(dayLabel("2026-11-02T09:00:00Z", now)).toBe("2 Nov 2026");
  });
});

describe("shortTitle", () => {
  const withIndustries = (...sets: string[][]) => ({
    candidates: sets.map((industries) => ({ industries })) as never,
  });

  it("names the shared industry when at least half of the startups have it", () => {
    expect(shortTitle(withIndustries(["ai"], ["AI", "fintech"], ["climate"], ["ai"]))).toBe(
      "4 AI startups",
    );
    expect(shortTitle(withIndustries(["FINTECH"], ["fintech"]))).toBe("2 fintech startups");
    expect(shortTitle(withIndustries(["SOFTWARE_AND_SERVICES"]))).toBe(
      "1 software and services startup",
    );
  });

  it("falls back to the count when no industry dominates", () => {
    expect(shortTitle(withIndustries(["ai"], ["climate"], ["health"]))).toBe("3 startups");
    expect(shortTitle(withIndustries())).toBe("0 startups");
  });
});
