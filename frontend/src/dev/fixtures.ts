// Synthetic demo data: every company, investor and number here is invented. It feeds the
// dev-only fake API (VITE_FAKE_API=1) and the frontend tests, never the real backend.
import type {
  Candidate,
  ChatMessage,
  ExploredGraph,
  Fact,
  HiddenLink,
  LinkNode,
  NewsItem,
  Profile,
  ProfileChange,
  Report,
  Source,
  WalkSummary,
} from "../api/types";

const registry = (date: string, precision: Source["date_precision"] = "year"): Source => ({
  name: "Finnish Trade Register",
  url: "https://example.com/registry",
  date,
  date_precision: precision,
  rank: "filing",
});
const press = (name: string, date: string): Source => ({
  name,
  url: "https://example.com/press",
  date,
  date_precision: "day",
  rank: "press",
});
const company: Source = {
  name: "Company website",
  url: "https://example.com",
  date: null,
  date_precision: null,
  rank: "primary",
};
const database: Source = {
  name: "Funding database",
  url: null,
  date: null,
  date_precision: null,
  rank: "aggregator",
};

const fact = (value: Fact["value"], source: Source, unit?: string): Fact => ({
  value,
  unit: unit ?? null,
  trust: source.rank,
  sources: [source],
});
const absent: Fact = { value: null, unit: null, trust: "not_published", sources: [] };

/** A Cala news row: a date at its precision, no per-item source link. */
const newsItem = (
  title: string,
  summary: string,
  date: string | null,
  precision: Source["date_precision"],
  entities: NewsItem["entities"],
): NewsItem => ({
  title,
  summary,
  date: date
    ? {
        value: date,
        unit: null,
        trust: "cala_news",
        sources: [
          {
            name: "Cala knowledge query",
            url: null,
            date: precision === "month" ? `${date}-01` : date,
            date_precision: precision,
            rank: "cala_news",
          },
        ],
      }
    : absent,
  entities,
  trust: "cala_news",
});

const node = (entity_id: string, name: string, entity_type = "Organization"): LinkNode => ({
  entity_id,
  name,
  entity_type,
});
const took = (source: string, target: string, role: string) => ({
  source,
  target,
  relationship: "PARTICIPATES_IN_FUNDING_ROUND",
  role,
});

/** Fjordline Angels, in Northwind's seed, sat next to North Star Capital in three rounds. */
const fjordlineWithNorthStar: HiddenLink = {
  kind: "trusted_co_investor",
  label: "co-invested 3× with North Star Capital",
  explanation:
    "Fjordline Angels, who joined a round of Northwind Labs, invested alongside North Star Capital in 3 other rounds: Pinecone Grid, Tundra Health, Brightwave.",
  via_entity_id: "i-fjordline",
  target: node("i-northstar", "North Star Capital"),
  count: 3,
  trust: "press",
  nodes: [
    node("c-northwind", "Northwind Labs", "Company"),
    node("r-northwind-seed", "Northwind Labs seed round", "FundingRound"),
    node("i-fjordline", "Fjordline Angels"),
    node("r-pinecone-seed", "Seed", "FundingRound"),
    node("i-northstar", "North Star Capital"),
    node("c-pinecone", "Pinecone Grid", "Company"),
    node("r-tundra-seed", "Seed", "FundingRound"),
    node("c-tundra", "Tundra Health", "Company"),
    node("r-brightwave-pre", "Pre-Seed", "FundingRound"),
    node("c-brightwave", "Brightwave", "Company"),
  ],
  edges: [
    took("c-northwind", "r-northwind-seed", "ISSUER"),
    took("i-fjordline", "r-northwind-seed", "INVESTOR"),
    took("i-fjordline", "r-pinecone-seed", "INVESTOR"),
    took("i-northstar", "r-pinecone-seed", "is_lead"),
    took("c-pinecone", "r-pinecone-seed", "ISSUER"),
    took("i-fjordline", "r-tundra-seed", "INVESTOR"),
    took("i-northstar", "r-tundra-seed", "INVESTOR"),
    took("c-tundra", "r-tundra-seed", "ISSUER"),
    took("i-fjordline", "r-brightwave-pre", "INVESTOR"),
    took("i-northstar", "r-brightwave-pre", "is_lead"),
    took("c-brightwave", "r-brightwave-pre", "ISSUER"),
  ],
  facts: [
    fact("Pinecone Grid · Seed", press("Arctic Startup Daily", "2023-03-02")),
    fact("Tundra Health · Seed", press("Nordic Finance Wire", "2024-01-15")),
    fact("Brightwave · Pre-Seed", database),
  ],
};

interface LinkEnd {
  id: string;
  name: string;
  round: string;
  roundName: string;
}

const auroraAlsoBacks = (from: LinkEnd, to: LinkEnd, lead: boolean): HiddenLink => ({
  kind: "shared_investor",
  label: `also backs ${to.name}`,
  explanation: `Aurora Ventures backs ${from.name} and also ${to.name}, another startup on your list.`,
  via_entity_id: "i-aurora",
  target: node(to.id, to.name, "Company"),
  count: 1,
  trust: "press",
  nodes: [
    node(from.id, from.name, "Company"),
    node(from.round, from.roundName, "FundingRound"),
    node("i-aurora", "Aurora Ventures"),
    node(to.round, to.roundName, "FundingRound"),
    node(to.id, to.name, "Company"),
  ],
  edges: [
    took(from.id, from.round, "ISSUER"),
    took("i-aurora", from.round, "INVESTOR"),
    took("i-aurora", to.round, lead ? "is_lead" : "INVESTOR"),
    took(to.id, to.round, "ISSUER"),
  ],
  facts: [fact(`${to.name} · ${to.roundName}`, press("Nordic Finance Wire", "2023-05-03"))],
});
const northwindEnd: LinkEnd = {
  id: "c-northwind",
  name: "Northwind Labs",
  round: "r-northwind-seed",
  roundName: "Northwind Labs seed round",
};
const lumenEnd: LinkEnd = {
  id: "c-lumen",
  name: "Lumen Ledger",
  round: "r-lumen-a",
  roundName: "Lumen Ledger Series A",
};

/** Baltic Seed Fund, Kettle's lead, sat next to Aurora Ventures in one other round. */
const balticWithAurora: HiddenLink = {
  kind: "trusted_co_investor",
  label: "co-invested 1× with Aurora Ventures",
  explanation:
    "Baltic Seed Fund, who led a round of Kettle Robotics, invested alongside Aurora Ventures in 1 other round: Pinecone Grid.",
  via_entity_id: "i-baltic",
  target: node("i-aurora", "Aurora Ventures"),
  count: 1,
  trust: "aggregator",
  nodes: [
    node("c-kettle", "Kettle Robotics", "Company"),
    node("r-kettle-pre", "Kettle Robotics pre-seed", "FundingRound"),
    node("i-baltic", "Baltic Seed Fund"),
    node("r-pinecone-seed", "Seed", "FundingRound"),
    node("i-aurora", "Aurora Ventures"),
    node("c-pinecone", "Pinecone Grid", "Company"),
  ],
  edges: [
    took("c-kettle", "r-kettle-pre", "ISSUER"),
    took("i-baltic", "r-kettle-pre", "is_lead"),
    took("i-baltic", "r-pinecone-seed", "INVESTOR"),
    took("i-aurora", "r-pinecone-seed", "INVESTOR"),
    took("c-pinecone", "r-pinecone-seed", "ISSUER"),
  ],
  facts: [fact("Pinecone Grid · Seed", database)],
};

export const candidates: Candidate[] = [
  {
    entity_id: "c-northwind",
    name: "Northwind Labs",
    website: "https://example.com/northwind",
    description: "Carbon accounting for Nordic logistics fleets.",
    founding_date: fact("2021-01-01", registry("2021-01-01")),
    funding_stage: fact("Seed", database),
    headcount: fact(18, company, "people"),
    total_funding: fact(3_100_000, press("Arctic Startup Daily", "2024-09-12"), "EUR"),
    hq: fact("Helsinki, Finland", registry("2021-01-01")),
    industries: ["Climate software", "Logistics"],
    rounds: [
      {
        entity_id: "r-northwind-seed",
        label: "Seed",
        name: "Northwind Labs seed round",
        amount: fact(2_500_000, press("Arctic Startup Daily", "2024-09-12"), "EUR"),
        date: fact("2024-09-12", press("Arctic Startup Daily", "2024-09-12")),
        investors: [
          { entity_id: "i-aurora", name: "Aurora Ventures", is_lead: true, role: "investor" },
          { entity_id: "i-fjordline", name: "Fjordline Angels", is_lead: false, role: "investor" },
        ],
      },
    ],
    signals: [
      {
        kind: "co_invest",
        label: "Co-invest with who you trust",
        value: ["Aurora Ventures led the seed round, Sep 2024"],
        explanation: "Aurora Ventures, one of your reference investors, led the seed round.",
        facts: [],
      },
      {
        kind: "likely_to_raise",
        label: "Likely to raise soon",
        value: true,
        explanation:
          "2 of 3 checks pass: 14 months since the seed round; headcount grew from 11 to 18 in 12 months. Lead follow-on: not enough data.",
        facts: [fact(18, company, "people")],
      },
    ],
    news: [
      newsItem(
        "Northwind Labs opens a pilot with a Baltic ferry operator",
        "Northwind Labs will measure fuel use and emissions across a ferry fleet for six months, its first customer outside road logistics, with reporting shared with the port authority.",
        "2026-11-03",
        "day",
        [
          { entity_id: "e-baltic-ferries", name: "Baltic Ferries", entity_type: "Company" },
          { entity_id: "e-tallinn", name: "Tallinn", entity_type: "Municipality" },
        ],
      ),
      newsItem("Hiring a head of sales for Germany", "Two open roles in Hamburg.", null, null, []),
    ],
    links: [fjordlineWithNorthStar, auroraAlsoBacks(northwindEnd, lumenEnd, false)],
  },
  {
    entity_id: "c-lumen",
    name: "Lumen Ledger",
    website: "https://example.com/lumen",
    description: "Treasury automation for small Nordic exporters.",
    founding_date: fact("2020-03-01", registry("2020-03-01", "month")),
    funding_stage: fact("Series A", database),
    headcount: fact(42, company, "people"),
    total_funding: fact(9_400_000, database, "EUR"),
    hq: fact("Stockholm, Sweden", company),
    industries: ["Fintech", "B2B software"],
    rounds: [
      {
        entity_id: "r-lumen-a",
        label: "Series A",
        name: "Lumen Ledger Series A",
        amount: fact(8_000_000, press("Nordic Finance Wire", "2023-05-03"), "EUR"),
        date: fact("2023-05-03", press("Nordic Finance Wire", "2023-05-03")),
        investors: [
          { entity_id: "i-northstar", name: "North Star Capital", is_lead: true, role: "investor" },
          { entity_id: "i-aurora", name: "Aurora Ventures", is_lead: false, role: "investor" },
        ],
      },
    ],
    signals: [
      {
        kind: "co_invest",
        label: "Co-invest with who you trust",
        value: [
          "North Star Capital led the Series A, May 2023",
          "Aurora Ventures joined the Series A, May 2023",
        ],
        explanation:
          "Both of your reference investors are in the Series A; North Star Capital led it.",
        facts: [],
      },
      {
        kind: "lead_follow_on",
        label: "Lead follows on",
        value: 0.4,
        explanation:
          "North Star Capital joined a later round in 2 of its 5 other portfolio companies.",
        facts: [],
      },
    ],
    news: [
      newsItem(
        "Lumen Ledger adds invoice financing for exporters",
        "The company said small exporters can now finance open invoices inside its treasury app, starting with Swedish and Finnish banks.",
        "2026-10",
        "month",
        [{ entity_id: "e-nordbank", name: "Nordbank", entity_type: "Company" }],
      ),
    ],
    links: [auroraAlsoBacks(lumenEnd, northwindEnd, true)],
  },
  {
    entity_id: "c-kettle",
    name: "Kettle Robotics",
    website: "https://example.com/kettle",
    description: "Autonomous picking arms for food warehouses.",
    founding_date: fact("2023-01-01", registry("2023-01-01")),
    funding_stage: fact("Pre-seed", database),
    headcount: fact(9, company, "people"),
    total_funding: absent,
    hq: fact("Tallinn, Estonia", company),
    industries: ["Robotics", "Logistics"],
    rounds: [
      {
        entity_id: "r-kettle-pre",
        label: "Pre-seed",
        name: "Kettle Robotics pre-seed",
        amount: absent,
        date: fact("2025-02-01", database),
        investors: [
          { entity_id: "i-baltic", name: "Baltic Seed Fund", is_lead: true, role: "investor" },
        ],
      },
    ],
    signals: [
      {
        kind: "likely_to_raise",
        label: "Likely to raise soon",
        value: null,
        explanation:
          "Only one check has data (9 months since the pre-seed round), so there is not enough data.",
        facts: [],
      },
    ],
    news: [],
    links: [balticWithAurora],
  },
  {
    entity_id: "c-saltmarsh",
    name: "Saltmarsh Bio",
    website: "https://example.com/saltmarsh",
    description: "At-home gut health test kits.",
    founding_date: fact("2022-01-01", registry("2022-01-01")),
    funding_stage: fact("Seed", database),
    headcount: fact(
      14,
      {
        name: "Founder interview, unverified",
        url: null,
        date: null,
        date_precision: null,
        rank: "web_unverified",
      },
      "people",
    ),
    total_funding: fact(1_200_000, database, "EUR"),
    hq: fact("Copenhagen, Denmark", company),
    industries: ["Health", "Consumer"],
    rounds: [],
    signals: [],
    news: [],
    links: [],
  },
];

const ids = candidates.map((c) => c.entity_id);

export const reportV1: Report = {
  id: "rep-1",
  kind: "prep",
  created_at: "2026-11-14T09:30:00Z",
  profile_version: 2,
  summary:
    "Four Slush 2026 attendees match your thesis of Nordic B2B climate and fintech software at pre-seed and seed. Northwind Labs is the strongest fit: Aurora Ventures led its seed round 14 months ago and the team is growing, so a new round may come soon. Lumen Ledger is later stage but both of your reference investors are on its cap table.",
  sections: [
    {
      title: "Shortlist",
      body_md:
        "These startups attend Slush 2026 and match your stage and sectors. Each fact shows where it comes from; **not published** means Cala has no value for it.",
      candidate_ids: ids,
    },
    {
      title: "Rounds and leads",
      body_md:
        "Who led the last round matters more than its size at this stage.\n\n- Northwind Labs: seed, led by Aurora Ventures.\n- Lumen Ledger: Series A, led by North Star Capital.\n- Kettle Robotics: pre-seed, led by Baltic Seed Fund; the amount is not published.",
      candidate_ids: ["c-northwind", "c-lumen", "c-kettle"],
    },
    {
      title: "Co-investors you trust",
      body_md:
        "Your reference investors appear in two rounds. Aurora Ventures led Northwind Labs and followed North Star Capital into Lumen Ledger.",
      candidate_ids: ["c-northwind", "c-lumen"],
    },
    {
      title: "Likely to raise soon",
      body_md: "A hint, not a recommendation. Northwind Labs passes 2 of 3 checks.",
      candidate_ids: ["c-northwind"],
    },
  ],
  candidates,
};

/** The same report after "shorter, co-investors first". */
export const reportV2: Report = {
  ...reportV1,
  id: "rep-2",
  created_at: "2026-11-14T09:34:00Z",
  profile_version: 3,
  summary:
    "Four matches. Aurora Ventures led Northwind Labs; both your reference investors back Lumen Ledger.",
  sections: [
    {
      title: "Co-investors you trust",
      body_md: "Aurora Ventures led Northwind Labs and joined North Star Capital in Lumen Ledger.",
      candidate_ids: ["c-northwind", "c-lumen"],
    },
    {
      title: "Shortlist",
      body_md: "Attending Slush 2026, matching stage and sectors.",
      candidate_ids: ids,
    },
    {
      title: "Likely to raise soon",
      body_md: "Northwind Labs: 2 of 3 checks pass.",
      candidate_ids: ["c-northwind"],
    },
  ],
};

/** After "drop consumer health": Saltmarsh Bio is gone. */
export const reportV3: Report = {
  ...reportV2,
  id: "rep-3",
  created_at: "2026-11-14T09:36:00Z",
  profile_version: 4,
  summary:
    "Three matches. Aurora Ventures led Northwind Labs; both your reference investors back Lumen Ledger.",
  sections: reportV2.sections.map((s) => ({
    ...s,
    candidate_ids: s.candidate_ids.filter((id) => id !== "c-saltmarsh"),
  })),
  candidates: candidates.filter((c) => c.entity_id !== "c-saltmarsh"),
};

export const profileV2: Profile = {
  version: 2,
  event_id: "e-slush-2026",
  thesis: "Nordic B2B climate and fintech software, pre-seed to seed, tickets around 25k EUR.",
  filters: {
    stages: ["pre_seed", "seed"],
    sectors_in: ["Climate software", "Fintech"],
    sectors_out: [],
    countries: ["FI", "SE", "EE", "DK", "NO"],
    headcount_max: 50,
    ticket: { value: 25_000, unit: "EUR", trust: "primary", sources: [] },
  },
  reference_investors: [
    { entity_id: "i-aurora", name: "Aurora Ventures" },
    { entity_id: "i-northstar", name: "North Star Capital" },
  ],
  sources: [],
  style: { length: "medium", detail: "plain", language: "en", sections: [] },
  cadence: "event",
  alert_threshold: "medium",
  instructions: "Plain language. One paragraph per startup. Lead with the round and who led it.",
  updated_at: "2026-11-14T09:29:00Z",
};

export const historyV2: ProfileChange[] = [
  {
    version: 2,
    field: "reference_investors",
    before: [],
    after: ["Aurora Ventures", "North Star Capital"],
    reason: "You said you trust these two investors.",
    by: "agent",
  },
  {
    version: 1,
    field: "filters.stages",
    before: [],
    after: ["pre_seed", "seed"],
    reason: "You chose pre-seed and seed when asked about stage.",
    by: "agent",
  },
];

export const chatV2: ChatMessage[] = [
  {
    id: "m1",
    role: "agent",
    report_id: null,
    ui: null,
    graph: null,
    walk: null,
    sources: [],
    text: "Hi, I am Grabbit. Tell me what you look for at Slush 2026, however vague.",
    created_at: "2026-11-14T09:20:00Z",
    profile_changes: [],
  },
  {
    id: "m2",
    role: "user",
    report_id: null,
    ui: null,
    graph: null,
    walk: null,
    sources: [],
    text: "Nordic B2B software, climate or fintech. Small tickets, around 25k.",
    created_at: "2026-11-14T09:21:00Z",
    profile_changes: [],
  },
  {
    id: "m3",
    role: "agent",
    report_id: null,
    ui: null,
    graph: null,
    walk: null,
    sources: [],
    text: "Of the 64 attendees that match, 41 are pre-seed or seed and 23 are Series A or later. Which stage do you want?",
    created_at: "2026-11-14T09:21:30Z",
    profile_changes: [],
  },
  {
    id: "m4",
    role: "user",
    report_id: null,
    ui: null,
    graph: null,
    walk: null,
    sources: [],
    text: "Pre-seed and seed. I trust Aurora Ventures and North Star Capital.",
    created_at: "2026-11-14T09:23:00Z",
    profile_changes: [],
  },
  {
    id: "m5",
    role: "agent",
    text: "From now on: pre-seed and seed only, and Aurora Ventures and North Star Capital are your reference investors. Your Slush prep report is ready.",
    created_at: "2026-11-14T09:30:00Z",
    profile_changes: historyV2.slice().reverse(),
    report_id: "rep-1",
    ui: null,
    graph: null,
    walk: null,
    sources: [],
  },
];

const edge = (
  source: string,
  target: string,
  role: string,
  is_lead = false,
): ExploredGraph["edges"][number] => ({
  source,
  target,
  relationship: "PARTICIPATES_IN_FUNDING_ROUND",
  role,
  is_lead,
  facts: {},
});

/** What the agent walked in Cala for "What else has Aurora Ventures backed?" (#73). */
export const exploredAurora: ExploredGraph = {
  nodes: [
    {
      entity_id: "i-aurora",
      name: "Aurora Ventures",
      entity_type: "Organization",
      facts: { website: fact("aurora.example", database) },
    },
    {
      entity_id: "r-fjord-seed",
      name: "Seed",
      entity_type: "FundingRound",
      facts: {
        transaction_value: fact(1800000, press("Nordic Tech Wire", "2025-03-04"), "EUR"),
        event_date: fact("2025-03-01", registry("2025-03-01", "month")),
      },
    },
    { entity_id: "r-kelp-pre", name: "Pre-Seed", entity_type: "FundingRound", facts: {} },
    { entity_id: "c-fjord", name: "Fjordlight Robotics", entity_type: "Company", facts: {} },
    { entity_id: "c-kelp", name: "Kelpwise", entity_type: "Company", facts: {} },
    { entity_id: "i-northstar", name: "North Star Capital", entity_type: "Company", facts: {} },
    { entity_id: "i-birch", name: "Birch Angels", entity_type: "Organization", facts: {} },
    { entity_id: "p-lina", name: "Lina Korhonen", entity_type: "Person", facts: {} },
  ],
  edges: [
    edge("i-aurora", "r-fjord-seed", "INVESTOR", true),
    edge("i-aurora", "r-kelp-pre", "INVESTOR"),
    edge("c-fjord", "r-fjord-seed", "ISSUER"),
    edge("i-northstar", "r-fjord-seed", "INVESTOR"),
    edge("c-kelp", "r-kelp-pre", "ISSUER"),
    edge("i-birch", "r-kelp-pre", "INVESTOR", true),
    edge("i-northstar", "r-kelp-pre", "INVESTOR"),
    {
      source: "p-lina",
      target: "i-aurora",
      relationship: "FOUNDED",
      role: null,
      is_lead: false,
      facts: {},
    },
  ],
};

export const exploredAnswerUi = [
  "root = Answer([t, g, f])",
  't = Text("Aurora Ventures also led the seed of Fjordlight Robotics and joined Kelpwise, both with North Star Capital.")',
  'g = ExploredGraph("i-aurora")',
  'f = EntityFacts("r-fjord-seed")',
].join("\n");

/** How the agent walked Cala for the Aurora answer, as the chat keeps it (#138). */
export const exploredAuroraWalk: WalkSummary = {
  steps: [
    {
      id: 0,
      kind: "search",
      text: "Searching Cala for “Aurora Ventures”",
      result: "found Aurora Ventures",
      done: true,
    },
    {
      id: 1,
      kind: "expand",
      text: "Looking at Aurora Ventures’ funding rounds and people",
      result: "found 3 funding rounds",
      done: true,
    },
    {
      id: 2,
      kind: "expand",
      text: "Opening 3 funding rounds to see who raised and who invested",
      result: "found 3 startups and 2 investors",
      done: true,
    },
  ],
  checked: exploredAurora.nodes.length,
  seconds: 9.4,
};
