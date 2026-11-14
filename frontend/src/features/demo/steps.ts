/** What the demo app knows about its own state, enough to tell when a step is done. */
export interface DemoSignals {
  agentReplies: number;
  hasReport: boolean;
  /** The visitor has opened the report at least once in this demo. */
  reportOpened: boolean;
  profileVersion: number;
  alerts: number;
}

/** The moves "Show me" makes for the visitor, through the same paths as their own clicks. */
export interface DemoActions {
  send: (text: string) => void;
  openReport: () => void;
  confirm: () => void;
}

/** The controls a step uses; inside the demo every other one is disabled. */
export type DemoTarget = "composer" | "answers" | "report" | "confirm";

export interface DemoStep {
  title: string;
  targets: DemoTarget[];
  /** What the last step just did, then what to do now; the card moves on by itself. */
  prompt: string;
  act: (actions: DemoActions) => void;
  done: (signals: DemoSignals) => boolean;
}

export const DEMO_THESIS = "Nordic climate and fintech at seed";
export const DEMO_ANSWER = "I trust Aurora Ventures and North Star Capital.";
export const DEMO_CORRECTION = "Shorter, co-investors first";

export const DEMO_STEPS: DemoStep[] = [
  {
    title: "Start vague",
    targets: ["composer"],
    prompt: "Say what you look for in your own words. A sector and a stage are enough.",
    act: ({ send }) => send(DEMO_THESIS),
    done: (s) => s.agentReplies >= 1,
  },
  {
    title: "Answer its question",
    targets: ["answers", "composer"],
    prompt:
      "Grabbit walked the Slush attendees and asks only what the data can't settle. Pick the investors you trust.",
    act: ({ send }) => send(DEMO_ANSWER),
    done: (s) => s.hasReport,
  },
  {
    title: "See how it got there",
    targets: ["report"],
    prompt:
      "Above: the path Grabbit walked, and under it every step it took, even the one read from your report. Now open the report.",
    act: ({ openReport }) => openReport(),
    done: (s) => s.reportOpened,
  },
  {
    title: "Correct it in plain words",
    targets: ["composer"],
    prompt:
      "Every figure carries a badge that says how far to trust it. There is no settings screen: tell Grabbit what to change.",
    act: ({ send }) => send(DEMO_CORRECTION),
    // The answer brings the profile to version 2; any correction moves it on.
    done: (s) => s.profileVersion > 2,
  },
  {
    title: "It comes to you",
    targets: ["confirm", "report"],
    prompt:
      "Grabbit rewrote its instructions and the report; What changed keeps why. Confirm, and it watches your shortlist.",
    act: ({ confirm }) => confirm(),
    done: (s) => s.alerts >= 1,
  },
];

/** The card after the last step, while the simulated alert is still on screen. */
export const DEMO_END = {
  title: "That's the loop. Your turn.",
  text: "A startup on your shortlist is raising. For real, that reaches you as a desktop notification. Nothing from this demo stays.",
};

/** Milliseconds the demo takes: long enough to read as real work, short enough to stay brisk. */
export interface DemoTiming {
  get: number;
  post: number;
  alert: number;
  /** How long a finished step stays on screen before the guide moves on. */
  advance: number;
}

export const DEMO_TIMING: DemoTiming = { get: 120, post: 700, alert: 2500, advance: 900 };

const SEEN_KEY = "grabbit.demo.seen:v1";

/**
 * Whether this browser has seen the demo; null when storage is blocked, since then it cannot
 * remember and the demo must not open by itself on every visit.
 */
export function readDemoSeen(): boolean | null {
  try {
    return localStorage.getItem(SEEN_KEY) === "1";
  } catch {
    return null;
  }
}

export function saveDemoSeen() {
  try {
    localStorage.setItem(SEEN_KEY, "1");
  } catch {
    // Blocked storage: readDemoSeen() reports it, so the demo does not reopen by itself.
  }
}
