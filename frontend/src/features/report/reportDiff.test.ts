import { act, renderHook } from "@testing-library/react";
import type { Report } from "../../api/types";
import { reportV1, reportV2, reportV3 } from "../../dev/fixtures";
import { candidateOrder, describeDiff, diffReports } from "./reportDiff";
import { CHANGED_HOLD_MS, useReportChanges } from "./useReportChanges";

describe("diffReports", () => {
  it("returns null without a previous report or for the same report", () => {
    expect(diffReports(undefined, reportV1)).toBeNull();
    expect(diffReports(reportV1, { ...reportV1 })).toBeNull();
  });

  it("finds moved, rewritten and removed sections and the shrink", () => {
    const diff = diffReports(reportV1, reportV2);
    expect(diff).not.toBeNull();
    expect(diff?.sections).toEqual({
      "Co-investors you trust": "moved",
      Shortlist: "moved",
      "Likely to raise soon": "changed",
    });
    expect(diff?.removedSections).toEqual(["Rounds and leads"]);
    expect(diff?.summaryChanged).toBe(true);
    expect(diff?.shorterBy).toBeGreaterThan(50);
  });

  it("finds removed and added startups by entity id", () => {
    const diff = diffReports(reportV2, reportV3);
    expect(diff?.removedCandidates).toEqual([{ entity_id: "c-saltmarsh", name: "Saltmarsh Bio" }]);
    const back = diffReports(reportV3, { ...reportV2, id: "rep-4" });
    expect(back?.candidates["c-saltmarsh"]).toBe("added");
  });

  it("marks a startup as moved when the reading order changes", () => {
    expect(candidateOrder(reportV1).slice(0, 2)).toEqual(["c-northwind", "c-lumen"]);
    const swapped: Report = {
      ...reportV1,
      id: "rep-x",
      sections: [
        {
          ...reportV1.sections[0],
          candidate_ids: ["c-lumen", "c-northwind", "c-kettle", "c-saltmarsh"],
        },
      ],
    };
    const diff = diffReports(reportV1, swapped);
    expect(diff?.candidates).toMatchObject({ "c-lumen": "moved", "c-northwind": "moved" });
    expect(diff?.candidates["c-kettle"]).toBeUndefined();
  });

  it("does not call a longer report shorter", () => {
    expect(diffReports(reportV2, { ...reportV1, id: "rep-5" })?.shorterBy).toBeNull();
  });
});

describe("describeDiff", () => {
  it("writes one plain line per kind of change", () => {
    const lines = describeDiff(
      diffReports(reportV1, reportV2) as NonNullable<ReturnType<typeof diffReports>>,
    );
    expect(lines).toContain("2 sections moved");
    expect(lines).toContain("1 section rewritten");
    expect(lines).toContain("1 section removed");
    expect(lines.at(-1)).toMatch(/^\d+% shorter$/);
  });

  it("counts removed startups", () => {
    const lines = describeDiff(
      diffReports(reportV2, reportV3) as NonNullable<ReturnType<typeof diffReports>>,
    );
    expect(lines).toContain("1 startup removed");
  });
});

describe("useReportChanges", () => {
  afterEach(() => vi.useRealTimers());

  it("holds the diff for a few seconds after a new report, then clears it", () => {
    vi.useFakeTimers();
    const { result, rerender } = renderHook(({ report }) => useReportChanges(report), {
      initialProps: { report: reportV1 },
    });
    expect(result.current).toBeNull();
    rerender({ report: reportV2 });
    expect(result.current?.removedSections).toEqual(["Rounds and leads"]);
    act(() => vi.advanceTimersByTime(CHANGED_HOLD_MS + 1));
    expect(result.current).toBeNull();
  });

  it("keeps the fade running when the same report is fetched again", () => {
    vi.useFakeTimers();
    const { result, rerender } = renderHook(({ report }) => useReportChanges(report), {
      initialProps: { report: reportV1 },
    });
    rerender({ report: reportV2 });
    rerender({ report: { ...reportV2 } });
    act(() => vi.advanceTimersByTime(CHANGED_HOLD_MS + 1));
    expect(result.current).toBeNull();
  });
});
