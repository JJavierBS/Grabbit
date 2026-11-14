import { answerLibrary, PROMPT_OPTIONS } from "./library";

// The backend sends this file to Gemini. After a component change: npx vitest run -u
it("the backend prompt matches the component library", async () => {
  await expect(answerLibrary.prompt(PROMPT_OPTIONS)).toMatchFileSnapshot(
    "../../../../../backend/app/agent/openui_prompt.txt",
  );
});
