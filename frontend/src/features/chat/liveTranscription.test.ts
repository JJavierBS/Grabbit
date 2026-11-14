import { mockApi } from "../../test/renderApp";
import { startLiveTranscription } from "./liveTranscription";

const encoder = new TextEncoder();

class FakeSocket {
  static OPEN = 1;
  static last: FakeSocket | undefined;
  readyState = 0;
  binaryType = "blob";
  sent: Record<string, unknown>[] = [];
  onopen: (() => void) | null = null;
  onerror: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onmessage: ((e: { data: unknown }) => void) | null = null;
  readonly url: string;
  constructor(url: string) {
    this.url = url;
    FakeSocket.last = this;
    queueMicrotask(() => {
      this.readyState = 1;
      this.onopen?.();
    });
  }
  send(data: string) {
    this.sent.push(JSON.parse(data));
  }
  close() {
    this.readyState = 3;
  }
  /** Gemini answers in binary frames. */
  receive(message: unknown) {
    this.onmessage?.({ data: encoder.encode(JSON.stringify(message)).buffer });
  }
}

let worklet: { port: { onmessage: ((e: { data: ArrayBuffer }) => void) | null } };

class FakeContext {
  audioWorklet = { addModule: vi.fn(async () => {}) };
  destination = {};
  createMediaStreamSource() {
    return { connect: (next: unknown) => next, disconnect: vi.fn() };
  }
  createGain() {
    return { gain: { value: 1 }, connect: (next: unknown) => next };
  }
  close = vi.fn(async () => {});
}

beforeEach(() => {
  FakeSocket.last = undefined;
  vi.stubGlobal("WebSocket", FakeSocket);
  vi.stubGlobal("AudioContext", FakeContext);
  vi.stubGlobal(
    "AudioWorkletNode",
    class {
      port = { onmessage: null };
      constructor() {
        worklet = this as typeof worklet;
      }
      connect(next: unknown) {
        return next;
      }
    },
  );
  URL.createObjectURL = vi.fn(() => "blob:worklet");
  URL.revokeObjectURL = vi.fn();
  mockApi({
    "POST /api/transcribe/token": () => ({
      url: "wss://live.example/Constrained",
      token: "auth_tokens/a b",
      model: "gemini-3.5-transcribe-live",
      expires_at: "2026-11-14T20:00:00Z",
    }),
  });
});

afterEach(() => vi.unstubAllGlobals());

async function open(onText = vi.fn()) {
  const started = startLiveTranscription({} as MediaStream, onText);
  await vi.waitFor(() => expect(FakeSocket.last?.sent.length).toBe(1));
  const socket = FakeSocket.last as FakeSocket;
  socket.receive({ setupComplete: {} });
  return { session: await started, socket, onText };
}

describe("startLiveTranscription", () => {
  it("connects with the token and sets up the model", async () => {
    const { socket } = await open();
    expect(socket.url).toBe("wss://live.example/Constrained?access_token=auth_tokens%2Fa%20b");
    expect(socket.sent[0]).toEqual({ setup: { model: "models/gemini-3.5-transcribe-live" } });
  });

  it("streams the mic as base64 16 kHz PCM", async () => {
    const { socket } = await open();
    worklet.port.onmessage?.({ data: new Int16Array([1, -1]).buffer });
    expect(socket.sent[1]).toEqual({
      realtimeInput: { audio: { data: "AQD//w==", mimeType: "audio/pcm;rate=16000" } },
    });
  });

  it("sends the words spoken while connecting once the session is ready", async () => {
    const started = startLiveTranscription({} as MediaStream, vi.fn());
    await vi.waitFor(() => expect(FakeSocket.last?.sent.length).toBe(1));
    const socket = FakeSocket.last as FakeSocket;
    worklet.port.onmessage?.({ data: new Int16Array([1, -1]).buffer });
    expect(socket.sent).toHaveLength(1);

    socket.receive({ setupComplete: {} });
    await started;
    worklet.port.onmessage?.({ data: new Int16Array([2]).buffer });

    expect(socket.sent.slice(1).map((m) => JSON.stringify(m))).toEqual([
      JSON.stringify({
        realtimeInput: { audio: { data: "AQD//w==", mimeType: "audio/pcm;rate=16000" } },
      }),
      JSON.stringify({
        realtimeInput: { audio: { data: "AgA=", mimeType: "audio/pcm;rate=16000" } },
      }),
    ]);
  });

  it("shows final sentences plus the one being spoken", async () => {
    const { socket, onText } = await open();
    socket.receive({ serverContent: { interimInputTranscription: { text: "Busco" } } });
    socket.receive({ serverContent: { inputTranscription: { text: "Busco startups." } } });
    socket.receive({ serverContent: { interimInputTranscription: { text: "Me fío" } } });
    expect(onText.mock.calls.map(([t]) => t)).toEqual([
      "Busco",
      "Busco startups.",
      "Busco startups. Me fío",
    ]);
  });

  it("ends the audio and waits for the last sentence before returning the transcript", async () => {
    const { session, socket } = await open();
    socket.receive({ serverContent: { inputTranscription: { text: "Busco startups." } } });
    socket.receive({ serverContent: { interimInputTranscription: { text: "Me fío de" } } });

    const finished = session.finish();
    expect(socket.sent.at(-1)).toEqual({ realtimeInput: { audioStreamEnd: true } });
    socket.receive({ serverContent: { inputTranscription: { text: "Me fío de Y Combinator." } } });

    expect(await finished).toBe("Busco startups. Me fío de Y Combinator.");
    expect(socket.readyState).toBe(3);
  });

  it("keeps the interim text when no final one comes in time", async () => {
    vi.useFakeTimers({ toFake: ["setTimeout", "clearTimeout"] });
    try {
      const { session, socket } = await open();
      socket.receive({ serverContent: { interimInputTranscription: { text: "Me fío de" } } });
      const finished = session.finish();
      await vi.advanceTimersByTimeAsync(3000);
      expect(await finished).toBe("Me fío de");
    } finally {
      vi.useRealTimers();
    }
  });

  it("rejects finish when the socket dropped, so the recording is used instead", async () => {
    const { session, socket } = await open();
    socket.onclose?.();
    await expect(session.finish()).rejects.toThrow();
  });

  it("rejects when the backend has no live transcription", async () => {
    mockApi({
      "POST /api/transcribe/token": {
        status: 503,
        body: { error: { code: "live_transcription_unavailable", message: "x" } },
      },
    });
    await expect(startLiveTranscription({} as MediaStream, vi.fn())).rejects.toThrow();
  });
});
