import {
  nameResearch,
  researches,
  researchSnapshot,
  startResearch,
  switchResearch,
  TITLE_CHARS,
  workspaceId,
} from "./workspace";

beforeEach(() => localStorage.clear());

describe("researches (#145)", () => {
  it("knows the current workspace even from before research lists existed", () => {
    localStorage.setItem("grabbit.workspace", "old-ws");
    expect(researches().map((r) => r.id)).toEqual(["old-ws"]);
    expect(researches()[0].title).toBeNull();
  });

  it("starts a new research only once the current one has a message", () => {
    const first = workspaceId();
    expect(startResearch()).toBe(first);
    expect(researches()).toHaveLength(1);

    nameResearch("AI at seed");
    const second = startResearch();
    expect(second).not.toBe(first);
    expect(workspaceId()).toBe(second);
    expect(researches().map((r) => [r.id, r.title])).toEqual([
      [second, null],
      [first, "AI at seed"],
    ]);
  });

  it("is named once, by its first message, on one short line", () => {
    nameResearch(`  Nordic\nclimate   tech ${"x".repeat(200)}`);
    nameResearch("Shorter, co-investors first");
    const title = researches()[0].title ?? "";
    expect(title.startsWith("Nordic climate tech x")).toBe(true);
    expect(title).toHaveLength(TITLE_CHARS);
  });

  it("switches only to a research it knows", () => {
    const first = workspaceId();
    nameResearch("AI at seed");
    startResearch();
    switchResearch("someone-elses-id");
    expect(workspaceId()).not.toBe(first);
    switchResearch(first);
    expect(workspaceId()).toBe(first);
    expect(researchSnapshot().current).toBe(first);
  });

  it("keeps working for the page when storage is blocked", () => {
    const blocked = {
      getItem: () => {
        throw new Error("blocked");
      },
      setItem: () => {
        throw new Error("blocked");
      },
    };
    vi.stubGlobal("localStorage", blocked);
    const first = workspaceId();
    nameResearch("AI at seed");
    const second = startResearch();
    expect(second).not.toBe(first);
    expect(workspaceId()).toBe(second);
    expect(researches().map((r) => r.id)).toEqual([second, first]);
  });
});
