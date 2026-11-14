import { useEffect, useRef, useState } from "react";
import { api, unwrap } from "../../api/client";
import { type LiveSession, startLiveTranscription } from "./liveTranscription";

type State = "idle" | "listening" | "transcribing";

/** Text that grows the draft: what the user typed, then what they said. */
export type DraftUpdate = (draft: string) => string;

export const MIC_BLOCKED =
  "Grabbit cannot use the microphone. Allow it in the browser, then press Talk again.";
export const NOTHING_HEARD = "Grabbit did not hear anything. Press Talk and try again.";
export const NOT_TRANSCRIBED = "Grabbit could not write that down. Press Talk and try again.";

const canRecord = () =>
  typeof MediaRecorder !== "undefined" && Boolean(globalThis.navigator?.mediaDevices?.getUserMedia);

const release = (stream: MediaStream) => {
  for (const track of stream.getTracks()) track.stop();
};

const join = (base: string, text: string) => (base && text ? `${base} ${text}` : base || text);

/**
 * Press to talk, press to stop. The words appear in the message box while the user speaks:
 * the mic streams straight to Gemini's Live API (#185). A recording runs alongside, so if the
 * live session cannot start or drops, Stop sends it to POST /api/transcribe instead (#161).
 * Either way the user reads the text and sends it, so a misheard word never reaches the agent
 * unseen.
 */
export function useDictation(onText: (update: DraftUpdate) => void) {
  const [state, setState] = useState<State>("idle");
  const [error, setError] = useState<string | null>(null);
  const recorder = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);
  const live = useRef<Promise<LiveSession | null> | null>(null);
  // What the user had typed when Talk started; the transcript goes after it.
  const base = useRef("");
  const starting = useRef(false);
  const supported = canRecord();

  const drop = () => {
    discard(recorder.current);
    recorder.current = null;
    void live.current?.then((session) => session?.cancel());
    live.current = null;
  };

  // Leaving the chat drops the recording instead of sending it.
  // biome-ignore lint/correctness/useExhaustiveDependencies: cleanup on unmount only.
  useEffect(() => drop, []);

  const done = (text: string) => {
    onText(() => join(base.current, text));
    if (!text) setError(NOTHING_HEARD);
    setState("idle");
  };

  const transcribe = async (audio: Blob) => {
    try {
      const { text } = await unwrap(
        api.POST("/api/transcribe", {
          // The contract types an audio body as a string; the browser sends the Blob as is.
          body: audio as unknown as string,
          bodySerializer: (body) => body,
          headers: { "Content-Type": audio.type },
        }),
      );
      done(text);
    } catch {
      onText(() => base.current);
      setError(NOT_TRANSCRIBED);
      setState("idle");
    }
  };

  const start = async () => {
    starting.current = true;
    setError(null);
    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      setError(MIC_BLOCKED);
      return;
    } finally {
      starting.current = false;
    }
    const r = new MediaRecorder(stream);
    chunks.current = [];
    r.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.current.push(e.data);
    };
    recorder.current = r;
    r.start();
    setState("listening");
    onText((draft) => {
      base.current = draft.trim();
      return draft;
    });
    live.current = startLiveTranscription(stream, (text) =>
      onText(() => join(base.current, text)),
    ).catch(() => null);
  };

  const stop = async () => {
    setState("transcribing");
    const r = recorder.current;
    recorder.current = null;
    const session = await live.current;
    live.current = null;
    if (session) {
      try {
        const text = await session.finish();
        discard(r);
        done(text);
        return;
      } catch {
        // The live session dropped: the recording still has every word.
      }
    }
    if (!r) return;
    const stopped = new Promise<void>((resolve) => {
      r.onstop = () => resolve();
    });
    if (r.state !== "inactive") r.stop();
    await stopped;
    release(r.stream);
    // Safari records audio/mp4, Chrome and Firefox audio/webm; the backend takes either.
    await transcribe(new Blob(chunks.current, { type: r.mimeType || "audio/webm" }));
  };

  const toggle = () => {
    if (starting.current || state === "transcribing") return;
    if (recorder.current) void stop();
    else void start();
  };

  /** Stops without transcribing, e.g. when the message is sent while still recording. */
  const cancel = () => {
    drop();
    setState("idle");
  };

  return {
    supported,
    listening: state === "listening",
    transcribing: state === "transcribing",
    error,
    toggle,
    cancel,
  };
}

function discard(r: MediaRecorder | null) {
  if (!r) return;
  r.onstop = null;
  if (r.state !== "inactive") r.stop();
  release(r.stream);
}
