import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { reportV1 } from "../dev/fixtures";
import { CalaNews } from "../features/report/CalaNews";
import { CandidateCard } from "../features/report/CandidateCard";
import { languageName } from "./TranslationNote";

const northwind = reportV1.candidates[0];
const GERMAN = "Northwind Labs startet ein Pilotprojekt mit einer baltischen Fähre";
const TRANSLATED = "Northwind Labs inicia un piloto con un ferry báltico";

describe("translated third-party text (#226)", () => {
  it("names the source language and swaps a news item to its original on request", async () => {
    const item = {
      ...northwind.news[0],
      title: TRANSLATED,
      title_original: { language: "de", text: GERMAN },
    };
    render(<CalaNews items={[item]} name={northwind.name} />);

    expect(screen.getByText("Translated from German")).toBeVisible();
    expect(screen.getByText(TRANSLATED)).toBeVisible();
    await userEvent.click(screen.getByRole("button", { name: "Show original" }));
    expect(screen.getByText(GERMAN)).toHaveAttribute("lang", "de");
    expect(screen.queryByText(TRANSLATED)).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Show translation" }));
    expect(screen.getByText(TRANSLATED)).toBeVisible();
  });

  it("keeps the original description of the startup one click away", async () => {
    const candidate = {
      ...northwind,
      description: "Contabilidad de carbono para flotas logísticas nórdicas.",
      description_original: { language: "sv", text: "Koldioxidredovisning för nordiska flottor." },
    };
    render(<CandidateCard candidate={candidate} trusted={new Set()} />);

    expect(screen.getByText("Translated from Swedish")).toBeVisible();
    await userEvent.click(screen.getByRole("button", { name: "Show original" }));
    expect(screen.getByText("Koldioxidredovisning för nordiska flottor.")).toHaveAttribute(
      "lang",
      "sv",
    );
  });

  it("says nothing about text that was not translated", () => {
    render(<CandidateCard candidate={northwind} trusted={new Set()} />);
    expect(screen.queryByText(/Translated from/)).not.toBeInTheDocument();
  });

  it("falls back to the code for a language it cannot name", () => {
    expect(languageName("not a code")).toBe("not a code");
  });
});
