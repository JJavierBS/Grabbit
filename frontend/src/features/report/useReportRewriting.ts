import { useEffect, useState } from "react";
import type { Profile, Report } from "../../api/types";

export const REWRITING_TEXT = "Rewriting the report for your latest change…";

/** A rebuild that has not landed by now is treated as failed: the line stops waiting. */
export const REWRITE_WAIT_MS = 120_000;

/**
 * True while the backend is rewriting the report for a newer profile: every profile change
 * schedules a rebuild (backend `schedule_rebuild`), which lands after the chat turn ends.
 */
export function isRewriting(
  profile: Pick<Profile, "version" | "updated_at"> | undefined,
  report: Pick<Report, "profile_version"> | null | undefined,
  now: number,
): boolean {
  if (!profile || !report) return false;
  if (profile.version <= report.profile_version) return false;
  return now - Date.parse(profile.updated_at) < REWRITE_WAIT_MS;
}

/** `isRewriting` that also turns itself off when the wait runs out. */
export function useReportRewriting(
  profile: Profile | undefined,
  report: Report | null | undefined,
): boolean {
  const [now, setNow] = useState(() => Date.now());
  const rewriting = isRewriting(profile, report, now);

  useEffect(() => {
    if (!rewriting || !profile) return;
    const left = Date.parse(profile.updated_at) + REWRITE_WAIT_MS - Date.now();
    const timer = window.setTimeout(() => setNow(Date.now()), Math.max(0, left) + 50);
    return () => window.clearTimeout(timer);
  }, [rewriting, profile]);

  // A fresh profile restarts the clock.
  // biome-ignore lint/correctness/useExhaustiveDependencies: only a new profile version matters.
  useEffect(() => setNow(Date.now()), [profile?.version]);

  return rewriting;
}
