import { Renderer } from "@openuidev/react-lang";
import { useMemo } from "react";
import { useLatestReport, useProfile } from "../../../api/hooks/queries";
import { AnswerContext, type AnswerData, answerLibrary } from "./library";

/** The agent's answer drawn with Cala components, under its text. */
export function VisualAnswer({ ui }: { ui: string }) {
  const report = useLatestReport();
  const profile = useProfile();
  const data = useMemo<AnswerData>(
    () => ({
      candidates: new Map((report.data?.candidates ?? []).map((c) => [c.entity_id, c])),
      trusted: new Set((profile.data?.reference_investors ?? []).map((r) => r.entity_id)),
    }),
    [report.data, profile.data],
  );
  return (
    <AnswerContext.Provider value={data}>
      <Renderer response={ui} library={answerLibrary} />
    </AnswerContext.Provider>
  );
}
