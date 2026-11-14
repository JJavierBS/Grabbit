import type { ProfileChange } from '../../api/types';

const NOTE = /(?:^|(?<=[.!?]\s))From now on:[^.!?]*[.!?]?/;

/** Pulls the agent's one-line "From now on: ..." note out of its reply text. */
export function splitChangeNote(text: string): { note: string | null; rest: string } {
  const match = NOTE.exec(text);
  if (!match) return { note: null, rest: text };
  const rest = (text.slice(0, match.index) + text.slice(match.index + match[0].length))
    .replace(/\s+/g, ' ')
    .trim();
  return { note: match[0].trim(), rest };
}

/** The note to show: the agent's own line, else one built from the change reasons. */
export function changeNoteText(
  text: string,
  changes: ProfileChange[],
): { note: string | null; rest: string } {
  const split = splitChangeNote(text);
  if (split.note || changes.length === 0) return split;
  return {
    note: `From now on: ${changes.map((c) => c.reason.replace(/\.$/, '')).join('; ')}.`,
    rest: text,
  };
}

/** Undo applies to the newest change only: the message whose changes hold the live version. */
export const isUndoable = (changes: ProfileChange[], profileVersion: number | undefined) =>
  profileVersion !== undefined && changes.some((c) => c.version === profileVersion);
