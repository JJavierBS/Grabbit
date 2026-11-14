import { dayLabel } from "./ReportSidebar";

describe("dayLabel", () => {
  const now = new Date(2026, 10, 14, 10, 0);

  it("names today and yesterday, and dates anything older", () => {
    expect(dayLabel(new Date(2026, 10, 14, 0, 5).toISOString(), now)).toBe("Today");
    expect(dayLabel(new Date(2026, 10, 13, 23, 50).toISOString(), now)).toBe("Yesterday");
    expect(dayLabel("2026-11-02T09:00:00Z", now)).toBe("2 Nov 2026");
  });
});
