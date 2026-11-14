import { createLibrary, defineComponent } from "@openuidev/react-lang";
import { createContext, useContext } from "react";
import { z } from "zod/v4";
import type { Candidate, ExploredGraph, GraphNode } from "../../../api/types";
import { FactValue } from "../../../components/FactValue";
import { Markdown } from "../../../components/Markdown";
import { CalaNews } from "../../report/CalaNews";
import { CalaPath } from "../../report/CalaPath";
import { HiddenLinkList } from "../../report/HiddenLinkList";
import { ExploredGraphView } from "./ExploredGraphView";
import { EXPLORED_FIELDS, factKind, factLabel } from "./facts";
import styles from "./library.module.css";

/**
 * Spike: components the model may place in a chat answer. They take Cala entity ids and
 * draw values from the report, never from the model, so an answer cannot invent a fact.
 */
export interface AnswerData {
  candidates: Map<string, Candidate>;
  trusted: Set<string>;
  /** What the agent walked in Cala for this answer (`ChatMessage.graph`). */
  explored?: ExploredGraph | null;
}

export const AnswerContext = createContext<AnswerData>({
  candidates: new Map(),
  trusted: new Set(),
});

const FIELDS = ["founding_date", "funding_stage", "headcount", "total_funding", "hq"] as const;
type Field = (typeof FIELDS)[number];
const FIELD_LABEL: Record<Field, string> = {
  founding_date: "Founded",
  funding_stage: "Stage",
  headcount: "Team",
  total_funding: "Total raised",
  hq: "Headquarters",
};

function useCandidate(id: string): Candidate | undefined {
  return useContext(AnswerContext).candidates.get(id);
}

function Missing({ id }: { id: string }) {
  return <p className={styles.missing}>Not in this report ({id.slice(0, 8)}).</p>;
}

const Text = defineComponent({
  name: "Text",
  description: "One or two short sentences of plain prose. Never put numbers or dates here.",
  props: z.object({ text: z.string() }),
  component: ({ props }) => <Markdown source={props.text} />,
});

const CompanyGraph = defineComponent({
  name: "CompanyGraph",
  description:
    "Draws the path in Cala's graph that put a startup on the list: event, startup, rounds, " +
    "who led or joined, and which of them the investor trusts. Use it to explain why.",
  props: z.object({ entityId: z.string().describe("Cala entity id of the startup") }),
  component: function CompanyGraphView({ props }) {
    const c = useCandidate(props.entityId);
    const { trusted } = useContext(AnswerContext);
    if (!c) return <Missing id={props.entityId} />;
    return (
      <div className={styles.block}>
        <h6 className={styles.title}>{c.name} in Cala's graph</h6>
        <CalaPath candidate={c} trusted={trusted} />
      </div>
    );
  },
});

const HiddenLinks = defineComponent({
  name: "HiddenLinks",
  description:
    "Relationships two steps away in Cala's graph that the startup's own page does not show: " +
    "an investor in its rounds who co-invested with an investor the user trusts, or who also " +
    "backs another startup on the list. Each comes with the rounds that prove it.",
  props: z.object({ entityId: z.string().describe("Cala entity id of the startup") }),
  component: function HiddenLinksView({ props }) {
    const c = useCandidate(props.entityId);
    if (!c) return <Missing id={props.entityId} />;
    return (
      <div className={styles.block}>
        <h6 className={styles.title}>{c.name}: links two steps away</h6>
        {c.links.length > 0 ? (
          <HiddenLinkList links={c.links} />
        ) : (
          <p className={styles.missing}>No hidden link found in Cala's graph.</p>
        )}
      </div>
    );
  },
});

const FactGrid = defineComponent({
  name: "FactGrid",
  description: "Sourced facts of one startup, each with its trust badge from Cala.",
  props: z.object({
    entityId: z.string().describe("Cala entity id of the startup"),
    fields: z.array(z.enum(FIELDS)),
  }),
  component: function FactGridView({ props }) {
    const c = useCandidate(props.entityId);
    if (!c) return <Missing id={props.entityId} />;
    return (
      <div className={styles.block}>
        <h6 className={styles.title}>{c.name}</h6>
        <dl className={styles.facts}>
          {props.fields.map((f) => (
            <FactValue
              key={f}
              label={FIELD_LABEL[f]}
              kind={f === "founding_date" ? "date" : "auto"}
              fact={c[f]}
            />
          ))}
        </dl>
      </div>
    );
  },
});

const Compare = defineComponent({
  name: "Compare",
  description: "Side-by-side table of two to four startups on the same sourced fields.",
  props: z.object({
    entityIds: z.array(z.string()).describe("Cala entity ids of the startups"),
    fields: z.array(z.enum(FIELDS)),
  }),
  component: function CompareView({ props }) {
    const { candidates } = useContext(AnswerContext);
    const rows = props.entityIds.map((id) => candidates.get(id)).filter((c): c is Candidate => !!c);
    return (
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th scope="col">Startup</th>
              {props.fields.map((f) => (
                <th key={f} scope="col">
                  {FIELD_LABEL[f]}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((c) => (
              <tr key={c.entity_id}>
                <th scope="row">{c.name}</th>
                {props.fields.map((f) => (
                  <td key={f}>
                    <FactValue inline kind={f === "founding_date" ? "date" : "auto"} fact={c[f]} />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  },
});

function useExplored(id: string): { graph?: ExploredGraph; node?: GraphNode } {
  const graph = useContext(AnswerContext).explored ?? undefined;
  return { graph, node: graph?.nodes.find((n) => n.entity_id === id) };
}

function NotExplored({ id }: { id: string }) {
  return <p className={styles.missing}>Not reached in Cala for this answer ({id.slice(0, 8)}).</p>;
}

const NOT_PUBLISHED = { value: null, unit: null, trust: "not_published", sources: [] } as const;

const ExploredGraphComponent = defineComponent({
  name: "ExploredGraph",
  description:
    "Draws the entities and edges you walked in Cala's graph with cala_search and " +
    "cala_neighbours, from rootId outwards, with Cala's edge names, leads and the investors " +
    "the angel trusts highlighted. Use it whenever you called the Cala tools.",
  props: z.object({
    rootId: z.string().describe("Cala entity id the question is about, from the tool results"),
  }),
  component: function ExploredGraphComponentView({ props }) {
    const { graph, node } = useExplored(props.rootId);
    const { trusted } = useContext(AnswerContext);
    if (!graph?.nodes.length) return <NotExplored id={props.rootId} />;
    const root = node ?? graph.nodes[0];
    return (
      <div className={styles.block}>
        <h6 className={styles.title}>Around {root.name} in Cala's graph</h6>
        <ExploredGraphView graph={graph} rootId={root.entity_id} trusted={trusted} />
      </div>
    );
  },
});

const EntityFacts = defineComponent({
  name: "EntityFacts",
  description:
    "Sourced facts of any entity you expanded with cala_neighbours (company, investor, " +
    "funding round), each with its trust badge. Omit fields to show all it has.",
  props: z.object({
    entityId: z.string().describe("Cala entity id from the tool results"),
    fields: z.array(z.enum(EXPLORED_FIELDS)).optional(),
  }),
  component: function EntityFactsView({ props }) {
    const { node } = useExplored(props.entityId);
    if (!node) return <NotExplored id={props.entityId} />;
    // People and unexpanded neighbours carry no facts; a block of "Not published" says nothing.
    if (Object.keys(node.facts).length === 0) return null;
    const keys = props.fields?.length ? props.fields : Object.keys(node.facts);
    return (
      <div className={styles.block}>
        <h6 className={styles.title}>{node.name}</h6>
        <dl className={styles.facts}>
          {keys.map((k) => (
            <FactValue
              key={k}
              label={factLabel(k)}
              kind={factKind(k)}
              fact={node.facts[k] ?? NOT_PUBLISHED}
            />
          ))}
        </dl>
      </div>
    );
  },
});

const News = defineComponent({
  name: "News",
  description:
    "Latest news about one startup from Cala (title, date, summary, who is mentioned). " +
    "Use it when the investor asks what is new or recent about a startup.",
  props: z.object({ entityId: z.string().describe("Cala entity id of the startup") }),
  component: function NewsView({ props }) {
    const c = useCandidate(props.entityId);
    if (!c) return <Missing id={props.entityId} />;
    return (
      <div className={styles.block}>
        <h6 className={styles.title}>{c.name}</h6>
        {c.news.length > 0 ? (
          <CalaNews items={c.news} name={c.name} heading="h6" />
        ) : (
          <p className={styles.missing}>No news about {c.name} in Cala yet.</p>
        )}
      </div>
    );
  },
});

const Answer = defineComponent({
  name: "Answer",
  description: "The whole reply, top to bottom.",
  props: z.object({
    children: z.array(
      z.union([
        Text.ref,
        CompanyGraph.ref,
        FactGrid.ref,
        Compare.ref,
        ExploredGraphComponent.ref,
        EntityFacts.ref,
        News.ref,
        HiddenLinks.ref,
      ]),
    ),
  }),
  component: ({ props, renderNode }) => (
    <div className={styles.answer}>{renderNode(props.children)}</div>
  ),
});

export const answerLibrary = createLibrary({
  root: "Answer",
  components: [
    Answer,
    Text,
    CompanyGraph,
    FactGrid,
    Compare,
    ExploredGraphComponent,
    EntityFacts,
    News,
    HiddenLinks,
  ],
});

/** Options of the prompt in `backend/app/agent/openui_prompt.txt` (prompt.test.ts keeps them in sync). */
export const PROMPT_OPTIONS = {
  preamble:
    "You answer a business angel's questions about their Slush shortlist and about anything in Cala's entity graph. Facts come from Cala and are drawn by the components; you only pick which entity ids and fields to show.",
  additionalRules: [
    "Use only entity ids listed in the context or returned by the Cala tools.",
    "FactGrid, Compare and CompanyGraph take startups in the report; ExploredGraph and EntityFacts take entities from the Cala tools.",
    "Never write a number, amount or date in Text; show it with FactGrid, Compare or EntityFacts.",
    "To explain why a startup is on the list, use CompanyGraph.",
    "For what is new about a startup, use News; never retell a headline in Text.",
    "For links an investor would not see on one company page (co-investors of trusted investors, shared investors), use HiddenLinks.",
    "Start with one Text that answers the question in one or two sentences; it replaces the text reply.",
    "Keep every Text to two sentences at most.",
  ],
};
