import { fireEvent, render, screen } from "@testing-library/react";
import { Badge } from "./Badge";
import { Button } from "./Button";
import { Input, TextArea } from "./Input";
import { Skeleton } from "./Skeleton";

describe("Button", () => {
  it("is a non-submitting button by default", () => {
    render(<Button>Run now</Button>);
    expect(screen.getByRole("button", { name: "Run now" })).toHaveAttribute("type", "button");
  });

  it("is disabled and busy while loading", () => {
    render(<Button loading>Save</Button>);
    const button = screen.getByRole("button", { name: "Save" });
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute("aria-busy", "true");
  });
});

describe("Input", () => {
  it("links label, hint and error to the control", () => {
    render(<Input label="Thesis" hint="One sentence" error="Required" />);
    const input = screen.getByLabelText("Thesis");
    expect(input).toHaveAttribute("aria-invalid", "true");
    expect(input).toHaveAccessibleDescription("Required");
    expect(screen.getByRole("alert")).toHaveTextContent("Required");
  });

  it("keeps a hidden label in the accessible name", () => {
    render(<TextArea label="Message Grabbit" hideLabel />);
    expect(screen.getByRole("textbox", { name: "Message Grabbit" })).toBeInTheDocument();
  });
});

describe("TextArea height without field-sizing (iOS Safari, #218)", () => {
  const LINE = 24;
  const PADDING = 16;
  const CHARS_PER_LINE = 20;

  // jsdom has no layout: the stubbed scroll height wraps the current value every 20 characters.
  beforeEach(() => {
    Object.defineProperty(HTMLTextAreaElement.prototype, "scrollHeight", {
      configurable: true,
      get(this: HTMLTextAreaElement) {
        return Math.max(1, Math.ceil(this.value.length / CHARS_PER_LINE)) * LINE + PADDING;
      },
    });
  });
  afterEach(() => {
    delete (HTMLTextAreaElement.prototype as { scrollHeight?: number }).scrollHeight;
  });

  const height = (lines: number) => `${lines * LINE + PADDING}px`;
  const supportFieldSizing = (supported: boolean) =>
    vi.stubGlobal("CSS", { supports: () => supported });

  it("fits a placeholder that wraps while the field is empty", () => {
    supportFieldSizing(false);
    const placeholder = "Describe your thesis: sector, stage, investors you trust";
    render(
      <TextArea
        label="Message"
        hideLabel
        rows={1}
        value=""
        onChange={() => {}}
        placeholder={placeholder}
      />,
    );
    const field = screen.getByRole("textbox", { name: "Message" }) as HTMLTextAreaElement;
    expect(field.style.height).toBe(height(3));
    expect(field.value).toBe("");
  });

  it("grows with a controlled value", () => {
    supportFieldSizing(false);
    const { rerender } = render(
      <TextArea label="Message" hideLabel rows={1} value="short" onChange={() => {}} />,
    );
    const field = screen.getByRole("textbox", { name: "Message" });
    expect(field.style.height).toBe(height(1));
    rerender(
      <TextArea label="Message" hideLabel rows={1} value={"x".repeat(50)} onChange={() => {}} />,
    );
    expect(field.style.height).toBe(height(3));
  });

  it("grows as an uncontrolled field is typed in", () => {
    supportFieldSizing(false);
    render(<TextArea label="Message" hideLabel rows={1} />);
    const field = screen.getByRole("textbox", { name: "Message" });
    fireEvent.input(field, { target: { value: "y".repeat(41) } });
    expect(field.style.height).toBe(height(3));
  });

  it("leaves the height to CSS where field-sizing is supported", () => {
    supportFieldSizing(true);
    render(
      <TextArea label="Message" hideLabel rows={1} value={"x".repeat(50)} onChange={() => {}} />,
    );
    expect(screen.getByRole("textbox", { name: "Message" }).style.height).toBe("");
  });
});

describe("Badge and Skeleton", () => {
  it("renders badge text", () => {
    render(<Badge tone="warning">Simulated event</Badge>);
    expect(screen.getByText("Simulated event")).toBeInTheDocument();
  });

  it("announces loading", () => {
    render(<Skeleton label="Loading report" />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading report");
  });
});
