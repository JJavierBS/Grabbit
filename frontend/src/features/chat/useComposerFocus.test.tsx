import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useRef, useState } from "react";
import { useComposerFocus } from "./useComposerFocus";

function Harness({ enabled = true }: { enabled?: boolean }) {
  const field = useRef<HTMLTextAreaElement>(null);
  const [shown, setShown] = useState(true);
  useComposerFocus(field, enabled);
  return (
    <>
      <textarea aria-label="Message" ref={field} />
      {shown && (
        <button type="button" onClick={() => setShown(false)}>
          Close alert
        </button>
      )}
      <button type="button">Stays</button>
      <button type="button" disabled={!shown} onClick={() => setShown(false)}>
        Confirm
      </button>
    </>
  );
}

const box = () => screen.getByRole("textbox", { name: "Message" });

describe("useComposerFocus (#188)", () => {
  it("takes focus back when the focused control leaves the page", async () => {
    render(<Harness />);
    await userEvent.click(screen.getByRole("button", { name: "Close alert" }));
    await vi.waitFor(() => expect(box()).toHaveFocus());
  });

  it("takes focus back when the focused control turns disabled", async () => {
    render(<Harness />);
    await userEvent.click(screen.getByRole("button", { name: "Confirm" }));
    await vi.waitFor(() => expect(box()).toHaveFocus());
  });

  it("leaves focus alone on a control that is still there", async () => {
    render(<Harness />);
    await userEvent.click(screen.getByRole("button", { name: "Stays" }));
    expect(screen.getByRole("button", { name: "Stays" })).toHaveFocus();
  });

  it("does nothing on a touch screen", () => {
    vi.stubGlobal("matchMedia", (q: string) => ({ matches: q === "(pointer: coarse)" }));
    render(<Harness />);
    expect(box()).not.toHaveFocus();
  });

  it("does nothing while disabled, as in the guided demo", async () => {
    render(<Harness enabled={false} />);
    expect(box()).not.toHaveFocus();
    act(() => screen.getByRole("button", { name: "Stays" }).focus());
    await userEvent.keyboard("a");
    expect(box()).not.toHaveFocus();
  });
});
