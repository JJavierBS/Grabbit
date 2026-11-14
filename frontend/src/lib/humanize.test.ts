import { humanize, humanizeEnum } from "./humanize";

describe("humanize", () => {
  it.each([
    ["PRE_SEED", "Pre-seed"],
    ["SEED", "Seed"],
    ["SERIES_A", "Series A"],
    ["series_b", "Series B"],
    ["SOFTWARE_AND_SERVICES", "Software and services"],
    ["ai", "AI"],
    ["AI_AND_ML", "AI and ML"],
    ["b2b_software", "B2B software"],
  ])("names the stage or sector %s as %s", (raw, readable) => {
    expect(humanize(raw)).toBe(readable);
  });

  it.each([
    ["is_lead", "led"],
    ["ISSUER", "raised"],
    ["GRANTOR", "granted"],
    ["ATTENDEE", "attends"],
    ["INVESTOR", "invested"],
  ])("writes the graph edge %s as %s", (raw, readable) => {
    expect(humanize(raw)).toBe(readable);
  });

  it("falls back to sentence case for values it does not know", () => {
    expect(humanize("CLIMATE_TECH_HARDWARE")).toBe("Climate tech hardware");
    expect(humanize("OPERATES_IN_INDUSTRY")).toBe("Operates in industry");
    expect(humanize("deep_tech")).toBe("Deep tech");
  });

  it("keeps someone's own mixed-case spelling", () => {
    expect(humanize("Series A extension")).toBe("Series A extension");
  });
});

describe("humanizeEnum", () => {
  it("rewrites enum-looking values only", () => {
    expect(humanizeEnum("PRE_SEED")).toBe("Pre-seed");
    expect(humanizeEnum("SEED")).toBe("Seed");
    expect(humanizeEnum("software_and_services")).toBe("Software and services");
    expect(humanizeEnum("Helsinki")).toBe("Helsinki");
    expect(humanizeEnum("HQ in Oslo")).toBe("HQ in Oslo");
    expect(humanizeEnum("EUR")).toBe("EUR");
    expect(humanizeEnum("ACTIVE")).toBe("Active");
    expect(humanizeEnum("EQUITY")).toBe("Equity");
  });
});
