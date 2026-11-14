import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "./App";
import { renderWithQuery, stubApi } from "./test/render";

describe("App", () => {
  it("shows the API modes from /api/health", async () => {
    stubApi({
      "/api/health": {
        body: { status: "ok", cala_mode: "replay", llm_mode: "fake", demo_mode: true },
      },
    });

    renderWithQuery(<App />);

    expect(await screen.findByText(/Cala replay · LLM fake · demo mode/)).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "Chat" })).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "Report" })).toBeInTheDocument();
  });

  it("says so when the API is down instead of rendering blank", async () => {
    stubApi({
      "/api/health": {
        status: 500,
        body: { error: { code: "internal_error", message: "Something went wrong" } },
      },
    });

    renderWithQuery(<App />);

    expect(await screen.findByRole("alert")).toHaveTextContent("Something went wrong");
  });
});
