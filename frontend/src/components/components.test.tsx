import { render, screen } from "@testing-library/react";
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
