import type { Report } from "../../api/types";

export type ChangeMark = "added" | "moved" | "changed";

export interface ReportDiff {
  summaryChanged: boolean;
  /** Section title -> mark; sections that did not change are absent. */
  sections: Record<string, ChangeMark>;
  removedSections: string[];
  /** Candidate entity id -> mark; unchanged candidates are absent. */
  candidates: Record<string, ChangeMark>;
  removedCandidates: { entity_id: string; name: string }[];
  /** Whole percent the text got shorter by, or null if it did not get at least 5% shorter. */
  shorterBy: number | null;
}

/** Candidates in reading order: first appearance in a section, then any left over. */
export function candidateOrder(report: Report): string[] {
  const seen = new Set<string>();
  for (const section of report.sections) for (const id of section.candidate_ids) seen.add(id);
  for (const c of report.candidates) seen.add(c.entity_id);
  return [...seen];
}

/** Marks items whose position among the items present in both lists changed. */
function moved(before: string[], after: string[]): Set<string> {
  const common = new Set(before.filter((x) => after.includes(x)));
  const a = before.filter((x) => common.has(x));
  const b = after.filter((x) => common.has(x));
  return new Set(b.filter((x, i) => a[i] !== x));
}

const textLength = (r: Report) =>
  r.summary.length + r.sections.reduce((n, s) => n + s.body_md.length, 0);

/**
 * What changed between two reports, for the highlight after a correction.
 * Returns null when there is no previous report or it is the same report.
 */
export function diffReports(prev: Report | undefined, next: Report): ReportDiff | null {
  if (!prev || prev.id === next.id) return null;

  const prevTitles = prev.sections.map((s) => s.title);
  const nextTitles = next.sections.map((s) => s.title);
  const prevBodies = new Map(prev.sections.map((s) => [s.title, s.body_md]));
  const movedTitles = moved(prevTitles, nextTitles);
  const sections: Record<string, ChangeMark> = {};
  for (const s of next.sections) {
    if (!prevBodies.has(s.title)) sections[s.title] = "added";
    else if (movedTitles.has(s.title)) sections[s.title] = "moved";
    else if (prevBodies.get(s.title) !== s.body_md) sections[s.title] = "changed";
  }

  const prevIds = candidateOrder(prev);
  const nextIds = candidateOrder(next);
  const movedIds = moved(prevIds, nextIds);
  const candidates: Record<string, ChangeMark> = {};
  for (const id of nextIds) {
    if (!prevIds.includes(id)) candidates[id] = "added";
    else if (movedIds.has(id)) candidates[id] = "moved";
  }
  const names = new Map(prev.candidates.map((c) => [c.entity_id, c.name]));
  const removedCandidates = prevIds
    .filter((id) => !nextIds.includes(id))
    .map((id) => ({ entity_id: id, name: names.get(id) ?? id }));

  const before = textLength(prev);
  const after = textLength(next);
  const shrink = before > 0 ? Math.round(((before - after) / before) * 100) : 0;

  return {
    summaryChanged: prev.summary !== next.summary,
    sections,
    removedSections: prevTitles.filter((t) => !nextTitles.includes(t)),
    candidates,
    removedCandidates,
    shorterBy: shrink >= 5 ? shrink : null,
  };
}

const plural = (n: number, one: string, many: string) => `${n} ${n === 1 ? one : many}`;

/** One short line per kind of change, for the "rewritten" banner. */
export function describeDiff(diff: ReportDiff): string[] {
  const marks = Object.values(diff.sections);
  const count = (m: ChangeMark) => marks.filter((x) => x === m).length;
  const startups = Object.values(diff.candidates).filter((m) => m === "added").length;
  return [
    count("moved") && `${plural(count("moved"), "section", "sections")} moved`,
    count("added") && `${plural(count("added"), "section", "sections")} added`,
    count("changed") && `${plural(count("changed"), "section", "sections")} rewritten`,
    diff.removedSections.length &&
      `${plural(diff.removedSections.length, "section", "sections")} removed`,
    startups && `${plural(startups, "startup", "startups")} added`,
    diff.removedCandidates.length &&
      `${plural(diff.removedCandidates.length, "startup", "startups")} removed`,
    diff.shorterBy && `${diff.shorterBy}% shorter`,
  ].filter((x): x is string => Boolean(x));
}

export const hasChanges = (diff: ReportDiff) =>
  diff.summaryChanged || describeDiff(diff).length > 0 || Object.keys(diff.candidates).length > 0;
