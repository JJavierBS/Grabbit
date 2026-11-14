import { useEffect, useRef, useState } from "react";
import type { ExploredGraph } from "../../../api/types";
import { FactValue } from "../../../components/FactValue";
import {
  clip,
  EDGE_PX,
  EdgeLabel,
  fits,
  fullNodeWidth,
  LABEL_PX,
  NODE_H,
  NODE_PAD,
  SUB_PX,
  subLine,
} from "../../../components/GraphText";
import styles from "./ExploredGraphView.module.css";
import { layoutWalk, NODE_W, ROW, toTallWalk, typeLabel, type WalkNode } from "./exploredGraph";
import { factKind, factLabel } from "./facts";

const PAD = 8;
/**
 * The wide drawing is never scaled down (#116), so when it does not fit the frame the tree
 * is drawn instead; the frame still scrolls if anything runs wider.
 */
const TALL_BELOW = 1;

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

interface Props {
  graph: ExploredGraph;
  rootId: string;
  trusted: Set<string>;
  /** Still growing: new entities and edges fade in as the agent reaches them (#134). */
  live?: boolean;
}

/** What the agent walked in Cala's graph for this answer: each box an entity, each line an edge. */
export function ExploredGraphView({ graph, rootId, trusted, live = false }: Props) {
  const frame = useRef<HTMLElement>(null);
  const wide = layoutWalk(graph, rootId, trusted);
  const width = useWidth(frame);
  const layout =
    width !== null && width < wide.width * TALL_BELOW
      ? toTallWalk(wide, width - 2 * PAD - 18)
      : wide;
  const [picked, setPicked] = useState<string | null>(null);
  // The node under the pointer or keyboard focus shows its whole name in an overlay drawn
  // on top. The node itself stays put: moving a focused element in the DOM would blur it.
  const [active, setActive] = useState<string | null>(null);
  const byId = new Map(layout.nodes.map((n) => [n.id, n]));
  const activeNode = active ? byId.get(active) : undefined;
  const pickedNode = graph.nodes.find((n) => n.entity_id === picked);
  const root = layout.nodes.find((n) => n.kind === "root");
  const w = layout.width + PAD * 2;
  const h = layout.height - ROW + NODE_H + PAD * 2;
  const pick = (n: WalkNode) => setPicked(n.kind === "more" ? null : (n.entityId ?? null));

  return (
    <figure
      ref={frame}
      className={styles.figure}
      data-tall={layout.tall || undefined}
      data-live={live || undefined}
    >
      <div className={styles.scroll}>
        <svg
          className={styles.svg}
          width={w}
          height={h}
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
                  <EdgeLabel
                    x={x2 - 8}
                    y={b.y - 6}
                    anchor="end"
                    text={clip(e.label, fits(x2 - x1 - 16, EDGE_PX))}
                    className={styles.edgeLabel}
                    backgroundClassName={styles.edgeLabelBg}
                  />
                )}
              </g>
            );
          })}
          {layout.nodes.map((n) => {
            const inner = (n.w ?? NODE_W) - 2 * NODE_PAD;
            return (
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
                data-active={n.id === active || undefined}
                transform={`translate(${n.x},${n.y - NODE_H / 2})`}
                onClick={() => pick(n)}
                onPointerEnter={() => setActive(n.id)}
                onPointerLeave={() => setActive((a) => (a === n.id ? null : a))}
                onFocus={() => setActive(n.id)}
                onBlur={() => setActive((a) => (a === n.id ? null : a))}
                onKeyDown={(ev) => {
                  if (ev.key === "Enter" || ev.key === " ") {
                    ev.preventDefault();
                    pick(n);
                  }
                }}
              >
                <title>{n.label}</title>
                <rect width={n.w ?? NODE_W} height={NODE_H} rx={8} />
                <text x={NODE_PAD} y={n.sub ? 15 : 23} className={styles.nodeLabel}>
                  {clip(n.label, fits(inner, LABEL_PX, true))}
                </text>
                {n.sub && (
                  <text x={NODE_PAD} y={30} className={styles.nodeSub}>
                    {clip(subLine(n.sub), fits(inner, SUB_PX))}
                  </text>
                )}
              </g>
            );
          })}
          {activeNode && <FullName node={activeNode} />}
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
        ) : live ? (
          "Growing as Grabbit walks Cala's entity graph. Each box is a Cala entity, each line an edge."
        ) : (
          "What Grabbit walked in Cala's entity graph to answer. Each box is a Cala entity, each line an edge. Select one."
        )}
      </figcaption>
    </figure>
  );
}

/** The active node again, unclipped and wider when it needs to be; decoration only. */
function FullName({ node }: { node: WalkNode }) {
  const width = Math.max(node.w ?? NODE_W, fullNodeWidth(node.label, node.sub));
  return (
    // biome-ignore lint/a11y/noAriaHiddenOnFocusable: an SVG <g> without tabIndex is not focusable; the name it repeats is already the node's label.
    <g
      aria-hidden="true"
      className={styles.node}
      data-overlay=""
      data-kind={node.kind}
      data-trusted={node.trusted || undefined}
      transform={`translate(${node.x},${node.y - NODE_H / 2})`}
    >
      <rect width={width} height={NODE_H} rx={8} className={styles.overlayBase} />
      <rect width={width} height={NODE_H} rx={8} />
      <text x={NODE_PAD} y={node.sub ? 15 : 23} className={styles.nodeLabel}>
        {node.label}
      </text>
      {node.sub && (
        <text x={NODE_PAD} y={30} className={styles.nodeSub}>
          {subLine(node.sub)}
        </text>
      )}
    </g>
  );
}
