import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  type EventStreamFactory,
  setEventStreamFactory,
  setTransport,
  type Transport,
} from "../../api/client";
import { useToast } from "../../components/Toast";
import type { FakeApi } from "../../dev/fakeApi";
import type { DemoTiming } from "./demoApi";
import { readDemoSeen, saveDemoSeen } from "./steps";

export interface DemoContextValue {
  /** True inside the guided demo, false in the visitor's own research. */
  active: boolean;
  /** The visitor started or dismissed the demo before; the invitation stops calling. */
  seen: boolean;
  start: () => void;
  exit: () => void;
  /** The visitor began their own research instead: the invitation counts as answered. */
  dismiss: () => void;
  /** Just back from the demo: the composer takes focus. */
  returning: boolean;
}

const DemoContext = createContext<DemoContextValue | null>(null);

/** The guided demo's controls, or null where the app runs without it (most tests). */
export const useDemo = () => useContext(DemoContext);

const TOUR_PARAM = "tour";

interface Run {
  id: number;
  api: FakeApi;
  client: QueryClient;
}

interface DemoRootProps {
  /** The visitor's own app. */
  children: ReactNode;
  /** The app to run inside the demo, on sample data. */
  demo: ReactNode;
  /** Tests run the demo without its pauses. */
  timing?: DemoTiming;
}

/**
 * Runs the guided demo (#184) in place of the visitor's app: a fresh fake backend, its own
 * query cache, and the real UI on top. Nothing reaches the server or the visitor's research;
 * leaving puts the real transport back and drops everything the demo made.
 */
export function DemoRoot({ children, demo, timing }: DemoRootProps) {
  const [run, setRun] = useState<Run | null>(null);
  const current = useRef<Run | null>(null);
  const [seen, setSeen] = useState(readDemoSeen);
  const [returning, setReturning] = useState(false);
  const saved = useRef<{ transport: Transport; stream: EventStreamFactory } | null>(null);
  const runs = useRef(0);
  const toasts = useToast();

  const start = useCallback(async () => {
    saveDemoSeen();
    setSeen(true);
    const { createDemoApi } = await import("./demoApi");
    const api = createDemoApi(timing);
    const transport = setTransport(api.transport);
    const stream = setEventStreamFactory(api.openStream);
    // A replay swaps one demo for another; the visitor's transport was saved by the first.
    saved.current ??= { transport, stream };
    toasts.clear();
    current.current?.api.dispose();
    runs.current += 1;
    current.current = {
      id: runs.current,
      api,
      client: new QueryClient({ defaultOptions: { queries: { refetchOnWindowFocus: false } } }),
    };
    setRun(current.current);
  }, [toasts, timing]);

  const exit = useCallback(() => {
    if (saved.current) {
      setTransport(saved.current.transport);
      setEventStreamFactory(saved.current.stream);
      saved.current = null;
    }
    toasts.clear();
    current.current?.api.dispose();
    current.current = null;
    setRun(null);
    setReturning(true);
    const url = new URL(location.href);
    if (url.searchParams.has(TOUR_PARAM)) {
      url.searchParams.delete(TOUR_PARAM);
      history.replaceState(history.state, "", url);
    }
  }, [toasts]);

  const dismiss = useCallback(() => {
    saveDemoSeen();
    setSeen(true);
  }, []);

  // Unmounted mid-demo (e.g. a hot reload): the visitor's app must never keep the fake API.
  useEffect(
    () => () => {
      if (saved.current) {
        setTransport(saved.current.transport);
        setEventStreamFactory(saved.current.stream);
        saved.current = null;
      }
      current.current?.api.dispose();
      current.current = null;
    },
    [],
  );

  // `?tour` opens straight on the demo, e.g. for the pitch.
  const startRef = useRef(start);
  startRef.current = start;
  useEffect(() => {
    if (new URLSearchParams(location.search).has(TOUR_PARAM)) void startRef.current();
  }, []);

  const value = useMemo<DemoContextValue>(
    () => ({
      active: run !== null,
      seen,
      start: () => void start(),
      exit,
      dismiss,
      returning: returning && run === null,
    }),
    [run, seen, start, exit, dismiss, returning],
  );

  return (
    <DemoContext.Provider value={value}>
      {run ? (
        <QueryClientProvider key={run.id} client={run.client}>
          {demo}
        </QueryClientProvider>
      ) : (
        children
      )}
    </DemoContext.Provider>
  );
}
