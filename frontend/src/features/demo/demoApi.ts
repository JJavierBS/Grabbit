import type { Profile } from "../../api/types";
import { change, createFakeApi, type FakeApi } from "../../dev/fakeApi";
import { historyV2, profileV2, reportV1, reportV2, reportV3 } from "../../dev/fixtures";
import { DEMO_ANSWER } from "./steps";

/** Milliseconds the demo backend takes: long enough to read as real work, short enough to stay brisk. */
export interface DemoTiming {
  get: number;
  post: number;
  alert: number;
}

export const DEMO_TIMING: DemoTiming = { get: 120, post: 700, alert: 2500 };

/** A new visitor's profile: nothing known yet. */
const blank: Profile = {
  ...profileV2,
  version: 0,
  thesis: "",
  filters: { ...profileV2.filters, stages: [], sectors_in: [], countries: [] },
  reference_investors: [],
};

/**
 * The guided demo's backend: a fresh, empty workspace on the synthetic fixtures. The first
 * message is the thesis and the second the answer, whatever their words; corrections and the
 * confirmation follow the same patterns as `npm run dev:fake`.
 */
export function createDemoApi(timing: DemoTiming = DEMO_TIMING): FakeApi {
  return createFakeApi({
    start: { profile: blank, report: null, history: [] },
    latency: { get: timing.get, post: timing.post },
    alertDelay: timing.alert,
    fallback:
      'This guided demo runs on sample data, so it only knows a few moves. Try "Shorter, co-investors first".',
    scripts: [
      {
        match: (_text, turn) => turn === 0,
        reply:
          "I checked the Slush 2026 attendees: 64 match Nordic climate and fintech software, 41 of them at pre-seed or seed. One question before I write your shortlist.",
        questions: [
          {
            key: "reference_investors",
            text: "Which investors do you trust? Startups they backed rank first.",
            options: [
              { label: "Aurora Ventures and North Star Capital", answer: DEMO_ANSWER },
              { label: "Only Aurora Ventures", answer: "I trust Aurora Ventures." },
            ],
          },
        ],
        next: (v) => {
          const next = change(
            v,
            "filters.stages",
            ["pre_seed", "seed"],
            "pre-seed and seed only, Nordic climate and fintech software",
            null,
            [],
          );
          return {
            ...next,
            profile: { ...next.profile, thesis: profileV2.thesis, filters: profileV2.filters },
          };
        },
      },
      {
        match: (_text, turn) => turn === 1,
        reply:
          "From now on: Aurora Ventures and North Star Capital are your reference investors. Your Slush prep report is ready.",
        next: (v) => ({
          profile: profileV2,
          report: reportV1,
          history: [historyV2[0], ...v.history],
        }),
      },
      {
        match: /short|co-?invest/i,
        reply: "From now on: shorter reports, co-investors first. I rewrote your report.",
        next: (v) =>
          change(
            v,
            "instructions",
            "Short. Co-investors first. Two lines per startup. Plain language.",
            "You asked for shorter reports with co-investors first.",
            reportV2,
          ),
      },
      {
        match: /health|consumer|b2c/i,
        reply: "From now on: no consumer health. Saltmarsh Bio is out of the report.",
        next: (v) =>
          change(
            v,
            "filters.sectors_out",
            ["Health", "Consumer"],
            "You asked to drop consumer health.",
            reportV3,
          ),
      },
      {
        match: /confirm|looks right|keep me posted/i,
        reply:
          "Done. During Slush week I will send a daily digest, and I will alert you at once when something changes on your shortlist.",
        alert: true,
      },
    ],
  });
}
