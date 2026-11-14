import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { type ToastInput, ToastProvider, useToast } from "./Toast";

function Trigger({ input }: { input: ToastInput }) {
  const { toast } = useToast();
  return (
    <button type="button" onClick={() => toast(input)}>
      fire
    </button>
  );
}

function setup(input: ToastInput) {
  render(
    <ToastProvider>
      <Trigger input={input} />
    </ToastProvider>,
  );
  return screen.getByRole("button", { name: "fire" });
}

describe("Toast", () => {
  afterEach(() => vi.useRealTimers());

  it("shows title, description and meta", async () => {
    await userEvent.click(
      setup({ title: "New round", description: "Seed, 2M EUR", meta: "Simulated event" }),
    );
    expect(screen.getByText("New round")).toBeInTheDocument();
    expect(screen.getByText("Seed, 2M EUR")).toBeInTheDocument();
    expect(screen.getByText("Simulated event")).toBeInTheDocument();
  });

  it("uses an assertive alert role for alert tone", async () => {
    await userEvent.click(setup({ title: "Exec left", tone: "alert" }));
    expect(screen.getByRole("alert")).toHaveTextContent("Exec left");
  });

  it("runs the action and closes", async () => {
    const onClick = vi.fn();
    await userEvent.click(setup({ title: "Open me", action: { label: "Open", onClick } }));
    await userEvent.click(screen.getByRole("button", { name: "Open" }));
    expect(onClick).toHaveBeenCalledOnce();
    expect(screen.queryByText("Open me")).not.toBeInTheDocument();
  });

  it("closes on dismiss", async () => {
    await userEvent.click(setup({ title: "Bye" }));
    await userEvent.click(screen.getByRole("button", { name: "Dismiss: Bye" }));
    expect(screen.queryByText("Bye")).not.toBeInTheDocument();
  });

  it("closes after its duration, and stays when duration is null", () => {
    vi.useFakeTimers();
    render(
      <ToastProvider>
        <Trigger input={{ title: "Short", duration: 1000 }} />
      </ToastProvider>,
    );
    act(() => screen.getByRole("button", { name: "fire" }).click());
    expect(screen.getByText("Short")).toBeInTheDocument();
    act(() => vi.advanceTimersByTime(1001));
    expect(screen.queryByText("Short")).not.toBeInTheDocument();
  });

  it("keeps a sticky toast open", () => {
    vi.useFakeTimers();
    render(
      <ToastProvider>
        <Trigger input={{ title: "Sticky", duration: null }} />
      </ToastProvider>,
    );
    act(() => screen.getByRole("button", { name: "fire" }).click());
    act(() => vi.advanceTimersByTime(60_000));
    expect(screen.getByText("Sticky")).toBeInTheDocument();
  });
});
