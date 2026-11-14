import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ProfileChange } from "../../api/types";
import { ChangeNote } from "./ChangeNote";
import { changeNoteText, isUndoable, splitChangeNote } from "./noteText";

const change = (version: number, reason = "You asked for shorter reports."): ProfileChange => ({
  version,
  field: "instructions",
  before: "Long",
  after: "Short",
  reason,
  by: "agent",
});

describe("change note text", () => {
  it('pulls the "From now on" sentence out of the reply', () => {
    expect(splitChangeNote("From now on: co-investors first. I rewrote your report.")).toEqual({
      note: "From now on: co-investors first.",
      rest: "I rewrote your report.",
    });
  });

  it("finds the note in the middle of a reply", () => {
    expect(splitChangeNote("Got it. From now on: no B2C. Anything else?")).toEqual({
      note: "From now on: no B2C.",
      rest: "Got it. Anything else?",
    });
  });

  it("builds a note from the change reasons when the reply has none", () => {
    expect(changeNoteText("Done.", [change(3)]).note).toBe(
      "From now on: You asked for shorter reports.",
    );
  });

  it("finds the note after a blank line and keeps names with dots whole", () => {
    const text =
      "I updated your profile.\n\nFrom now on: trusting Maki.vc; AI only.\n\n- Raise soon?\n- Small teams?";
    expect(splitChangeNote(text)).toEqual({
      note: "From now on: trusting Maki.vc; AI only.",
      rest: "I updated your profile.\n\n- Raise soon?\n- Small teams?",
    });
  });

  it("says a reason shared by several changed fields once", () => {
    const changes = [change(2, "AI only"), change(2, "AI only"), change(2, "small teams")];
    expect(changeNoteText("Done.", changes).note).toBe("From now on: AI only; small teams.");
  });

  it("shows no note when nothing changed", () => {
    expect(changeNoteText("Hello.", [])).toEqual({ note: null, rest: "Hello." });
  });

  it("allows undo only for the change that holds the live profile version", () => {
    expect(isUndoable([change(3)], 3)).toBe(true);
    expect(isUndoable([change(2)], 3)).toBe(false);
    expect(isUndoable([change(3)], undefined)).toBe(false);
  });
});

describe("ChangeNote", () => {
  it("shows the note and calls undo", async () => {
    const onUndo = vi.fn();
    render(<ChangeNote note="From now on: co-investors first." canUndo onUndo={onUndo} />);
    expect(screen.getByText("From now on: co-investors first.")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Undo" }));
    expect(onUndo).toHaveBeenCalledOnce();
  });

  it("hides undo for older changes", () => {
    render(<ChangeNote note="From now on: no B2C." canUndo={false} onUndo={() => undefined} />);
    expect(screen.queryByRole("button", { name: "Undo" })).not.toBeInTheDocument();
  });
});
