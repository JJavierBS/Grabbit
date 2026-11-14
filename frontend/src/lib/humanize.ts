/**
 * Readable words for Cala's enums: stages, sectors and graph edges. One place, so no raw
 * `PRE_SEED`, `SOFTWARE_AND_SERVICES` or `is_lead` reaches the screen.
 */

const WORDS: Record<string, string> = {
  // Stages
  pre_seed: "Pre-seed",
  seed: "Seed",
  angel: "Angel",
  series_unknown: "Series unknown",
  ipo: "IPO",
  // Sectors
  ai: "AI",
  artificial_intelligence: "Artificial intelligence",
  saas: "SaaS",
  // Graph edges, written as what the startup or investor did.
  is_lead: "led",
  lead: "led",
  issuer: "raised",
  grantor: "granted",
  attendee: "attends",
  participates_in_event: "attends",
  investor: "invested",
  founded: "founded",
  founder: "founded",
};

const ACRONYMS = new Set([
  "ai",
  "api",
  "ar",
  "b2b",
  "b2c",
  "esg",
  "eu",
  "ev",
  "hr",
  "iot",
  "ipo",
  "it",
  "ml",
  "uk",
  "us",
  "vr",
]);

/** Always readable: mapped words first, otherwise sentence case with known acronyms. */
export function humanize(value: string): string {
  const key = value
    .trim()
    .toLowerCase()
    .replace(/[\s-]+/g, "_");
  const known = WORDS[key];
  if (known) return known;
  const series = /^series_([a-z])$/.exec(key);
  if (series) return `Series ${series[1].toUpperCase()}`;
  const spaced = value.trim().replace(/_+/g, " ");
  // Mixed case is someone's own spelling ("Series A extension", "Kiln"): keep it.
  const flat = spaced === spaced.toUpperCase() || spaced === spaced.toLowerCase();
  const words = (flat ? spaced.toLowerCase() : spaced).split(" ");
  const text = words.map((w) => (ACRONYMS.has(w.toLowerCase()) ? w.toUpperCase() : w)).join(" ");
  return text.replace(/^\p{Ll}/u, (c) => c.toUpperCase());
}

/** Readable only when the value looks like an enum (`PRE_SEED`, `ai`); other text is kept. */
export function humanizeEnum(value: string): string {
  const key = value.trim().toLowerCase();
  const snake = /^[A-Z0-9]+(?:_[A-Z0-9]+)+$|^[a-z0-9]+(?:_[a-z0-9]+)+$/.test(value);
  // A lone capitalised word of four letters or more (`ACTIVE`, `EQUITY`); three-letter
  // codes such as `EUR` stay as written.
  const shouted = /^[A-Z]{4,}$/.test(value);
  return key in WORDS || snake || shouted ? humanize(value) : value;
}
