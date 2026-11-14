import type { ProfileChange } from "../../api/types";

// The note starts the text, a sentence or a line (Gemini often puts it after a blank line),
// and ends at the end of its sentence: a dot inside a name such as "Maki.vc" does not end it.
const NOTE = /(?:^|(?<=[.!?]\s)|(?<=\n))From now on:(?:[^.!?\n]|[.!?](?![\s]|$))*[.!?]?/;

/** Pulls the agent's one-line "From now on: ..." note out of its reply text. */
export function splitChangeNote(text: string): { note: string | null; rest: string } {
  const match = NOTE.exec(text);
  if (!match) return { note: null, rest: text };
  // Keep line breaks: the rest is Markdown (paragraphs, "-" lists of questions).
  const rest = (text.slice(0, match.index) + text.slice(match.index + match[0].length))
    .replace(/[ \t]+/g, " ")
    .replace(/ *\n */g, "\n")
    .replace(/\n{3,}/g, "\n\n")
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
    // One turn changes several fields with the same reason; say each reason once.
    note: `From now on: ${[...new Set(changes.map((c) => c.reason.replace(/\.+$/, "")))].join("; ")}.`,
    rest: text,
  };
}

/** Undo applies to the newest change only: the message whose changes hold the live version. */
export const isUndoable = (changes: ProfileChange[], profileVersion: number | undefined) =>
  profileVersion !== undefined && changes.some((c) => c.version === profileVersion);
