import { createLibrary, defineComponent } from "@openuidev/react-lang";
import { createContext, useContext } from "react";
import { z } from "zod/v4";
import type { Candidate } from "../../../api/types";
import { FactValue } from "../../../components/FactValue";
import { Markdown } from "../../../components/Markdown";
import { CalaPath } from "../../report/CalaPath";
import styles from "./library.module.css";

/**
 * Spike: components the model may place in a chat answer. They take Cala entity ids and
 * draw values from the report, never from the model, so an answer cannot invent a fact.
 */
export interface AnswerData {
  candidates: Map<string, Candidate>;
  trusted: Set<string>;
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

const Answer = defineComponent({
  name: "Answer",
  description: "The whole reply, top to bottom.",
  props: z.object({
    children: z.array(z.union([Text.ref, CompanyGraph.ref, FactGrid.ref, Compare.ref])),
  }),
  component: ({ props, renderNode }) => (
    <div className={styles.answer}>{renderNode(props.children)}</div>
  ),
});

export const answerLibrary = createLibrary({
  root: "Answer",
  components: [Answer, Text, CompanyGraph, FactGrid, Compare],
});

/** Options of the prompt in `backend/app/agent/openui_prompt.txt` (prompt.test.ts keeps them in sync). */
export const PROMPT_OPTIONS = {
  preamble:
    "You answer a business angel's questions about their Slush shortlist. Facts come from Cala and are drawn by the components; you only pick which startup ids and fields to show.",
  additionalRules: [
    "Use only entity ids listed in the context.",
    "Never write a number, amount or date in Text; show it with FactGrid or Compare.",
    "To explain why a startup is on the list, use CompanyGraph.",
    "Start with one Text that answers the question in one or two sentences; it replaces the text reply.",
    "Keep every Text to two sentences at most.",
  ],
};
