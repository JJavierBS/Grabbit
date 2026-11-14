import { act, renderHook, waitFor } from "@testing-library/react";
import { mockApi } from "../../test/renderApp";
import type { LiveSession } from "./liveTranscription";
import { NOTHING_HEARD, useDictation } from "./useDictation";

const live = vi.hoisted(() => ({ start: vi.fn() }));
vi.mock("./liveTranscription", () => ({ startLiveTranscription: live.start }));

function stubMic() {
  const stream = { getTracks: () => [{ stop: vi.fn() }] };
  class FakeRecorder {
    state = "inactive";
    mimeType = "audio/webm";
    stream = stream;
    ondataavailable: ((e: { data: Blob }) => void) | null = null;
    onstop: (() => void) | null = null;
    start() {
      this.state = "recording";
    }
    stop() {
      this.state = "inactive";
      this.ondataavailable?.({ data: new Blob(["opus"], { type: this.mimeType }) });
      this.onstop?.();
    }
  }
  vi.stubGlobal("MediaRecorder", FakeRecorder);
  Object.defineProperty(navigator, "mediaDevices", {
    configurable: true,
    value: { getUserMedia: vi.fn(() => Promise.resolve(stream)) },
  });
}

/** The hook driving a draft that starts as `typed`. */
function setup(typed = "") {
  let draft = typed;
  const hook = renderHook(() =>
    useDictation((update) => {
      draft = update(draft);
    }),
  );
  return { hook, draft: () => draft };
}

beforeEach(() => {
  stubMic();
  live.start.mockReset();
});

afterEach(() => {
  vi.unstubAllGlobals();
  Reflect.deleteProperty(navigator, "mediaDevices");
});

describe("useDictation", () => {
  it("writes the words into the draft while the user speaks, after what they typed", async () => {
    let speak: (text: string) => void = () => {};
    const session: LiveSession = {
      finish: vi.fn(async () => "drop consumer health"),
      cancel: vi.fn(),
    };
    live.start.mockImplementation(async (_stream, onText) => {
      speak = onText;
      return session;
    });
    const calls = mockApi({});
    const { hook, draft } = setup("Shorter,");

    await act(async () => hook.result.current.toggle());
    expect(hook.result.current.listening).toBe(true);
    act(() => speak("drop consumer"));
    expect(draft()).toBe("Shorter, drop consumer");

    await act(async () => hook.result.current.toggle());
    expect(draft()).toBe("Shorter, drop consumer health");
    expect(hook.result.current.listening).toBe(false);
    expect(calls.some((c) => c.key === "POST /api/transcribe")).toBe(false);
  });

  it("sends the recording to the backend when the live session cannot start", async () => {
    live.start.mockRejectedValue(new Error("no token"));
    mockApi({ "POST /api/transcribe": () => ({ text: "drop consumer health" }) });
    const { hook, draft } = setup();

    await act(async () => hook.result.current.toggle());
    await act(async () => hook.result.current.toggle());

    await waitFor(() => expect(draft()).toBe("drop consumer health"));
  });

  it("falls back to the recording when the live session drops, replacing its partial text", async () => {
    let speak: (text: string) => void = () => {};
    live.start.mockImplementation(async (_stream, onText) => {
      speak = onText;
      return { finish: vi.fn(async () => Promise.reject(new Error("closed"))), cancel: vi.fn() };
    });
    mockApi({ "POST /api/transcribe": () => ({ text: "drop consumer health" }) });
    const { hook, draft } = setup();

    await act(async () => hook.result.current.toggle());
    act(() => speak("drop cons"));
    await act(async () => hook.result.current.toggle());

    await waitFor(() => expect(draft()).toBe("drop consumer health"));
  });

  it("says nothing was heard when the live session hears nothing", async () => {
    live.start.mockResolvedValue({ finish: vi.fn(async () => ""), cancel: vi.fn() });
    const { hook, draft } = setup("typed");

    await act(async () => hook.result.current.toggle());
    await act(async () => hook.result.current.toggle());

    expect(draft()).toBe("typed");
    expect(hook.result.current.error).toBe(NOTHING_HEARD);
  });

  it("cancels the live session when the message is sent mid-sentence", async () => {
    const session = { finish: vi.fn(), cancel: vi.fn() };
    live.start.mockResolvedValue(session);
    const { hook } = setup();

    await act(async () => hook.result.current.toggle());
    await act(async () => hook.result.current.cancel());

    expect(session.cancel).toHaveBeenCalledOnce();
    expect(session.finish).not.toHaveBeenCalled();
  });
});
