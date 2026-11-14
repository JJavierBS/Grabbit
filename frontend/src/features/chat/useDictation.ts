import { useEffect, useRef, useState } from "react";
import { api, unwrap } from "../../api/client";

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

/**
 * Press to talk, press to stop: the browser records and the backend writes down what was said
 * (POST /api/transcribe), so it works in every browser. The text lands in the message box for
 * the user to read and send, so a misheard word never reaches the agent unseen.
 */
export function useDictation(onText: (update: DraftUpdate) => void) {
  const [state, setState] = useState<State>("idle");
  const [error, setError] = useState<string | null>(null);
  const recorder = useRef<MediaRecorder | null>(null);
  const starting = useRef(false);
  const supported = canRecord();

  // Leaving the chat drops the recording instead of sending it.
  useEffect(() => () => discard(recorder.current), []);

  const transcribe = async (audio: Blob) => {
    setState("transcribing");
    try {
      const { text } = await unwrap(
        api.POST("/api/transcribe", {
          // The contract types an audio body as a string; the browser sends the Blob as is.
          body: audio as unknown as string,
          bodySerializer: (body) => body,
          headers: { "Content-Type": audio.type },
        }),
      );
      if (text) onText((draft) => (draft.trim() ? `${draft.trim()} ${text}` : text));
      else setError(NOTHING_HEARD);
    } catch {
      setError(NOT_TRANSCRIBED);
    } finally {
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
    const chunks: Blob[] = [];
    r.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };
    r.onstop = () => {
      release(stream);
      recorder.current = null;
      // Safari records audio/mp4, Chrome and Firefox audio/webm; the backend takes either.
      void transcribe(new Blob(chunks, { type: r.mimeType || "audio/webm" }));
    };
    recorder.current = r;
    r.start();
    setState("listening");
  };

  const toggle = () => {
    if (starting.current || state === "transcribing") return;
    if (recorder.current) recorder.current.stop();
    else void start();
  };

  /** Stops without transcribing, e.g. when the message is sent while still recording. */
  const cancel = () => {
    discard(recorder.current);
    recorder.current = null;
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
