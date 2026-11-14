import { useEffect, useRef, useState } from "react";
import type { Report } from "../../api/types";
import { diffReports, hasChanges, type ReportDiff } from "./reportDiff";

/** How long the "changed" marks stay before they fade (the fade is --duration-slow). */
export const CHANGED_HOLD_MS = 4000;

/**
 * Remembers the report on screen; when a different report replaces it, returns the diff
 * for CHANGED_HOLD_MS, then null again.
 */
export function useReportChanges(report: Report | undefined): ReportDiff | null {
  const previous = useRef<Report | undefined>(undefined);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const [diff, setDiff] = useState<ReportDiff | null>(null);

  useEffect(() => () => clearTimeout(timer.current), []);

  useEffect(() => {
    if (!report) return;
    const next = diffReports(previous.current, report);
    previous.current = report;
    // A refetch of the same report returns null here and leaves a running fade alone.
    if (!next || !hasChanges(next)) return;
    clearTimeout(timer.current);
    setDiff(next);
    timer.current = setTimeout(() => setDiff(null), CHANGED_HOLD_MS);
  }, [report]);

  return diff;
}
