import { useEffect, useRef, useState } from "react";

// The Web Speech API is not in the TypeScript DOM lib; this is the part Grabbit uses.
interface Recognition {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  onresult: ((e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null;
  onerror: ((e: { error: string }) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}
type RecognitionCtor = new () => Recognition;

const getRecognition = (): RecognitionCtor | undefined => {
  const w = window as unknown as {
    SpeechRecognition?: RecognitionCtor;
    webkitSpeechRecognition?: RecognitionCtor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition;
};

/**
 * Press to talk: speech goes into the message box as the user speaks. The user reads it and
 * sends it, so a misheard word never reaches the agent unseen.
 */
export function useDictation(onText: (text: string) => void) {
  const [listening, setListening] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const recognition = useRef<Recognition | null>(null);
  const supported = getRecognition() !== undefined;

  useEffect(() => () => recognition.current?.abort(), []);

  const start = (base: string) => {
    const Ctor = getRecognition();
    if (!Ctor) return;
    const r = new Ctor();
    r.lang = navigator.language || "en-US";
    r.interimResults = true;
    r.continuous = true;
    r.onresult = (e) => {
      const spoken = Array.from(e.results, (res) => res[0].transcript)
        .join("")
        .trim();
      onText(base ? `${base} ${spoken}` : spoken);
    };
    r.onerror = (e) => {
      if (e.error === "aborted" || e.error === "no-speech") return;
      setError(
        e.error === "not-allowed" || e.error === "service-not-allowed"
          ? "Grabbit cannot use the microphone. Allow it in the browser, then press Talk again."
          : "Grabbit did not catch that. Press Talk and try again.",
      );
    };
    r.onend = () => {
      setListening(false);
      recognition.current = null;
    };
    recognition.current = r;
    setError(null);
    setListening(true);
    r.start();
  };

  const toggle = (base: string) => (listening ? recognition.current?.stop() : start(base.trim()));

  return { supported, listening, error, toggle };
}
