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

export interface DemoStep {
  title: string;
  /** What to do, before the step is done. */
  prompt: string;
  /** What just happened and why it matters, once it is done. */
  outcome: string;
  act: (actions: DemoActions) => void;
  done: (signals: DemoSignals) => boolean;
}

export const DEMO_THESIS = "Nordic climate and fintech at seed";
export const DEMO_ANSWER = "I trust Aurora Ventures and North Star Capital.";
export const DEMO_CORRECTION = "Shorter, co-investors first";

export const DEMO_STEPS: DemoStep[] = [
  {
    title: "Start vague",
    prompt: "Say what you look for in your own words. A sector and a stage are enough.",
    outcome: "Grabbit walked the Slush attendees and came back with one question.",
    act: ({ send }) => send(DEMO_THESIS),
    done: (s) => s.agentReplies >= 1,
  },
  {
    title: "Answer, see how it got there",
    prompt: "It asks only what the data can't settle. Pick the investors you trust.",
    outcome:
      "The graph is the path Grabbit walked. The steps under it say what it did, and which part came from your report instead of Cala.",
    act: ({ send }) => send(DEMO_ANSWER),
    done: (s) => s.hasReport,
  },
  {
    title: "Every fact shows its source",
    prompt: "The shortlist is ready. Open the report.",
    outcome:
      "Each figure carries a badge, from official filing down to not published, so you know how far to trust it.",
    act: ({ openReport }) => openReport(),
    done: (s) => s.reportOpened,
  },
  {
    title: "Correct it in plain words",
    prompt: "There is no settings screen. Tell Grabbit what to change.",
    outcome:
      "Grabbit rewrote its own instructions, then the report. What changed keeps each edit and the reason.",
    act: ({ send }) => send(DEMO_CORRECTION),
    // The answer brings the profile to version 2; any correction moves it on.
    done: (s) => s.profileVersion > 2,
  },
  {
    title: "It comes to you",
    prompt: "Confirm the report and Grabbit keeps watching your shortlist.",
    outcome:
      "A startup on your shortlist is raising. For real, this arrives as a desktop notification, even with the tab in the background.",
    act: ({ confirm }) => confirm(),
    done: (s) => s.alerts >= 1,
  },
];

const SEEN_KEY = "grabbit.demo.seen:v1";

/** Seen or dismissed in this browser; storage may be blocked, then the invitation stays. */
export function readDemoSeen(): boolean {
  try {
    return localStorage.getItem(SEEN_KEY) === "1";
  } catch {
    return false;
  }
}

export function saveDemoSeen() {
  try {
    localStorage.setItem(SEEN_KEY, "1");
  } catch {
    // Blocked storage: the invitation shows again next time, nothing else depends on it.
  }
}
