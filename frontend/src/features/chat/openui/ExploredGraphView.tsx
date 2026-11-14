import { useEffect, useRef, useState } from "react";
import type { ExploredGraph } from "../../../api/types";
import { FactValue } from "../../../components/FactValue";
import styles from "./ExploredGraphView.module.css";
import {
  layoutWalk,
  NODE_W,
  ROW,
  toTallWalk,
  typeLabel,
  type WalkNode,
} from "./exploredGraph";
import { factKind, factLabel } from "./facts";

const NODE_H = 34;
const PAD = 8;
/** Below this width the wide drawing would need scrolling; draw the tree instead. */
const TALL_BELOW = 560;

/** The frame's width, or null until measured (and in tests, which draw the wide layout). */
function useWidth(ref: React.RefObject<HTMLElement | null>): number | null {
  const [width, setWidth] = useState<number | null>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(([entry]) => setWidth(Math.round(entry.contentRect.width)));
    observer.observe(el);
    return () => observer.disconnect();
  }, [ref]);
  return width;
}

function clip(text: string, max: number): string {
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

interface Props {
  graph: ExploredGraph;
  rootId: string;
  trusted: Set<string>;
}

/** What the agent walked in Cala's graph for this answer: each box an entity, each line an edge. */
export function ExploredGraphView({ graph, rootId, trusted }: Props) {
  const frame = useRef<HTMLElement>(null);
  const wide = layoutWalk(graph, rootId, trusted);
  const width = useWidth(frame);
  const layout =
    width !== null && width < TALL_BELOW ? toTallWalk(wide, width - 2 * PAD - 18) : wide;
  const [picked, setPicked] = useState<string | null>(null);
  const byId = new Map(layout.nodes.map((n) => [n.id, n]));
  const pickedNode = graph.nodes.find((n) => n.entity_id === picked);
  const root = layout.nodes.find((n) => n.kind === "root");
  const w = layout.width + PAD * 2;
  const h = layout.height - ROW + NODE_H + PAD * 2;
  const pick = (n: WalkNode) => setPicked(n.kind === "more" ? null : (n.entityId ?? null));

  return (
    <figure ref={frame} className={styles.figure} data-tall={layout.tall || undefined}>
      <div className={styles.scroll}>
        <svg
          className={styles.svg}
          viewBox={`${-PAD} ${-PAD - NODE_H / 2} ${w} ${h}`}
          role="img"
          aria-label={`Entities and edges Grabbit walked in Cala's graph from ${root?.label ?? "the question"}`}
        >
          {layout.edges.map((e) => {
            const a = byId.get(e.from);
            const b = byId.get(e.to);
            if (!a || !b) return null;
            const cls = [styles.edge, e.strong && styles.strong, e.cross && styles.cross]
              .filter(Boolean)
              .join(" ");
            if (layout.tall) {
              const x = a.x + 11;
              return (
                <g key={`${e.from}-${e.to}`} className={cls}>
                  <path d={`M${x},${a.y + NODE_H / 2} V${b.y} H${b.x}`} />
                </g>
              );
            }
            const x1 = a.x + NODE_W;
            const x2 = b.x;
            const mx = (x1 + x2) / 2;
            return (
              <g key={`${e.from}-${e.to}`} className={cls}>
                {e.title && <title>{e.title}</title>}
                <path d={`M${x1},${a.y} C${mx},${a.y} ${mx},${b.y} ${x2},${b.y}`} />
                {e.label && (
                  <text
                    x={x2 - 6}
                    y={b.y - 5}
                    textAnchor="end"
                    className={styles.edgeLabel}
                  >
                    {clip(e.label, 18)}
                  </text>
                )}
              </g>
            );
          })}
          {layout.nodes.map((n) => (
            // biome-ignore lint/a11y/useSemanticElements: an SVG group cannot be a <button>.
            <g
              key={n.id}
              role="button"
              tabIndex={n.kind === "more" ? -1 : 0}
              aria-label={`${n.kind === "more" ? "" : `${typeLabel(graph.nodes.find((g) => g.entity_id === n.entityId)?.entity_type ?? "")} `}${n.label}`}
              aria-pressed={n.kind === "more" ? undefined : picked === n.entityId}
              className={styles.node}
              data-kind={n.kind}
              data-trusted={n.trusted || undefined}
              data-lead={n.lead || undefined}
              data-picked={(picked && picked === n.entityId) || undefined}
              transform={`translate(${n.x},${n.y - NODE_H / 2})`}
              onClick={() => pick(n)}
              onKeyDown={(ev) => {
                if (ev.key === "Enter" || ev.key === " ") {
                  ev.preventDefault();
                  pick(n);
                }
              }}
            >
              <title>{n.label}</title>
              <rect width={n.w ?? NODE_W} height={NODE_H} rx={8} />
              <text x={10} y={n.sub ? 14 : 21} className={styles.nodeLabel}>
                {clip(n.label, Math.floor(((n.w ?? NODE_W) - 20) / 7))}
              </text>
              {n.sub && (
                <text x={10} y={27} className={styles.nodeSub}>
                  {clip(n.sub, Math.floor(((n.w ?? NODE_W) - 20) / 5.6))}
                </text>
              )}
            </g>
          ))}
        </svg>
      </div>
      <figcaption className={styles.caption} aria-live="polite">
        {pickedNode ? (
          <>
            <span>
              <strong>{pickedNode.name}</strong> · {typeLabel(pickedNode.entity_type)} · Cala entity{" "}
              <code>{pickedNode.entity_id.slice(0, 8)}</code>
            </span>
            {Object.keys(pickedNode.facts).length > 0 && (
              <dl className={styles.facts}>
                {Object.entries(pickedNode.facts).map(([k, f]) => (
                  <FactValue key={k} label={factLabel(k)} kind={factKind(k)} fact={f} />
                ))}
              </dl>
            )}
          </>
        ) : (
          "What Grabbit walked in Cala's entity graph to answer. Each box is a Cala entity, each line an edge. Select one."
        )}
      </figcaption>
    </figure>
  );
}
