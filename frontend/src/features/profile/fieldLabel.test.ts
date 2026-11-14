import { describe, expect, it } from "vitest";
import { fieldLabel } from "./ProfileHistory";

describe("fieldLabel", () => {
  it("names every profile field the agent can change", () => {
    expect(fieldLabel("instructions")).toBe("Its own report instructions");
    expect(fieldLabel("sources")).toBe("News sources");
    expect(fieldLabel("filters.sectors_out")).toBe("Sectors to leave out");
  });

  it("falls back to a readable name for unknown fields", () => {
    expect(fieldLabel("style.language")).toMatch(/language/i);
  });
});
