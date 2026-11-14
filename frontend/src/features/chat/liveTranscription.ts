import { api, unwrap } from "../../api/client";

/** Live Talk: the browser streams the mic straight to Gemini's Live API (#185). */
export interface LiveSession {
  /** Ends the audio, waits briefly for the last words and returns the whole transcript. */
  finish(): Promise<string>;
  /** Drops the session without waiting for anything. */
  cancel(): void;
}

const SETUP_TIMEOUT_MS = 5000;
// The final text came 0.4 s after the end of audio in the 14 Nov spike.
const FINAL_TIMEOUT_MS = 3000;

// Downsamples the mic to 16 kHz mono 16-bit PCM and posts 100 ms chunks (1,600 samples), the
// format the Live API takes. `sampleRate` is the AudioContext's, a global of the worklet scope.
const WORKLET = `
class Pcm16 extends AudioWorkletProcessor {
  constructor() {
    super();
    this.step = sampleRate / 16000;
    this.pos = 0; this.sum = 0; this.count = 0;
    this.chunk = new Int16Array(1600); this.n = 0;
  }
  process(inputs) {
    const samples = inputs[0][0];
    if (!samples) return true;
    for (let i = 0; i < samples.length; i++) {
      this.sum += samples[i]; this.count++; this.pos++;
      if (this.pos < this.step) continue;
      this.pos -= this.step;
      const v = Math.max(-1, Math.min(1, this.sum / this.count));
      this.sum = 0; this.count = 0;
      this.chunk[this.n++] = v < 0 ? v * 0x8000 : v * 0x7fff;
      if (this.n === this.chunk.length) {
        this.port.postMessage(this.chunk.buffer, [this.chunk.buffer]);
        this.chunk = new Int16Array(1600); this.n = 0;
      }
    }
    return true;
  }
}
registerProcessor("grabbit-pcm16", Pcm16);
`;

interface ServerMessage {
  setupComplete?: unknown;
  serverContent?: {
    interimInputTranscription?: { text?: string };
    inputTranscription?: { text?: string };
  };
}

const decoder = new TextDecoder();

function parse(data: unknown): ServerMessage {
  // Gemini sends JSON in binary frames.
  const text = typeof data === "string" ? data : decoder.decode(data as ArrayBuffer);
  try {
    return JSON.parse(text) as ServerMessage;
  } catch {
    return {};
  }
}

function base64(buffer: ArrayBuffer): string {
  let binary = "";
  for (const byte of new Uint8Array(buffer)) binary += String.fromCharCode(byte);
  return btoa(binary);
}

/**
 * Opens a live transcription session for `stream`. `onText` gets the whole transcript so far,
 * final sentences plus the one still being spoken, each time it changes. Rejects when the
 * session cannot start, so Talk can fall back to recording.
 */
export async function startLiveTranscription(
  stream: MediaStream,
  onText: (text: string) => void,
): Promise<LiveSession> {
  // Capture starts at once and queues while the session connects, so the first words,
  // spoken before Gemini answers, are not lost.
  const queued: string[] = [];
  let open: WebSocket | null = null;
  const audio = await captureAudio(stream, (chunk) => {
    const message = JSON.stringify({
      realtimeInput: { audio: { data: base64(chunk), mimeType: "audio/pcm;rate=16000" } },
    });
    if (open) open.send(message);
    else queued.push(message);
  });
  let ws: WebSocket;
  try {
    ws = await connect();
  } catch (error) {
    audio.stop();
    throw error;
  }
  for (const message of queued.splice(0)) ws.send(message);
  open = ws;

  const finals: string[] = [];
  let interim = "";
  let onFinal: (() => void) | null = null;
  const transcript = () => [...finals, interim].filter(Boolean).join(" ");

  let failed = false;
  ws.onerror = () => {
    failed = true;
  };
  ws.onclose = () => {
    failed = true;
    onFinal?.();
  };
  ws.onmessage = (e) => {
    const content = parse(e.data).serverContent;
    if (!content) return;
    if (content.inputTranscription) {
      const text = content.inputTranscription.text?.trim();
      if (text) finals.push(text);
      interim = "";
      onText(transcript());
      onFinal?.();
    } else if (content.interimInputTranscription) {
      interim = content.interimInputTranscription.text?.trim() ?? "";
      onText(transcript());
    }
  };
  return {
    async finish() {
      audio.stop();
      if (failed) {
        ws.close();
        throw new Error("live socket closed early");
      }
      // Wait for the sentence still being spoken, or for any words at all; keep the interim
      // text if no final one comes. With every sentence final there is nothing to wait for.
      if ((interim || finals.length === 0) && ws.readyState === WebSocket.OPEN) {
        await new Promise<void>((resolve) => {
          const timer = setTimeout(resolve, FINAL_TIMEOUT_MS);
          onFinal = () => {
            clearTimeout(timer);
            resolve();
          };
          ws.send(JSON.stringify({ realtimeInput: { audioStreamEnd: true } }));
        });
      }
      onFinal = null;
      ws.close();
      return transcript();
    },
    cancel() {
      audio.stop();
      onFinal = null;
      ws.close();
    },
  };
}

/** A Live API session set up for Talk's model, with a single-use token from the backend. */
async function connect(): Promise<WebSocket> {
  const live = await unwrap(api.POST("/api/transcribe/token"));
  const ws = new WebSocket(`${live.url}?access_token=${encodeURIComponent(live.token)}`);
  ws.binaryType = "arraybuffer";
  try {
    await new Promise<void>((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error("live setup timed out")), SETUP_TIMEOUT_MS);
      ws.onopen = () => ws.send(JSON.stringify({ setup: { model: `models/${live.model}` } }));
      ws.onerror = () => reject(new Error("live socket failed"));
      ws.onclose = () => reject(new Error("live socket closed"));
      ws.onmessage = (e) => {
        if (parse(e.data).setupComplete === undefined) return;
        clearTimeout(timer);
        resolve();
      };
    });
  } catch (error) {
    ws.close();
    throw error;
  }
  return ws;
}

/** Mic to 16 kHz PCM chunks through the worklet; `stop` releases the audio graph. */
async function captureAudio(stream: MediaStream, onChunk: (chunk: ArrayBuffer) => void) {
  const context = new AudioContext();
  const module = URL.createObjectURL(new Blob([WORKLET], { type: "text/javascript" }));
  try {
    await context.audioWorklet.addModule(module);
  } catch (error) {
    void context.close();
    throw error;
  } finally {
    URL.revokeObjectURL(module);
  }
  const source = context.createMediaStreamSource(stream);
  const pcm = new AudioWorkletNode(context, "grabbit-pcm16");
  // A worklet only runs while connected to the output; a muted gain keeps it silent.
  const mute = context.createGain();
  mute.gain.value = 0;
  source.connect(pcm).connect(mute).connect(context.destination);
  pcm.port.onmessage = (e: MessageEvent<ArrayBuffer>) => onChunk(e.data);
  return {
    stop() {
      pcm.port.onmessage = null;
      source.disconnect();
      void context.close();
    },
  };
}
