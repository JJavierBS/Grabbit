import { useEffect, useRef, useState } from "react";
import type { Candidate } from "../../api/types";
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
} from "../../components/GraphText";
import { TrustBadge } from "../../components/TrustBadge";
import styles from "./CalaPath.module.css";
import { layoutPath, NODE_W, type PathEdge, type PathNode, ROW, toTall } from "./calaPath";

const PAD = 8;
/**
 * The wide drawing is never scaled down (#116), so when it does not fit the frame the tree
 * is drawn instead; the frame still scrolls if anything runs wider.
 */
const TALL_BELOW = 1;

const KIND_LABEL: Record<PathNode["kind"], string> = {
  event: "Event",
  startup: "Company",
  round: "Funding round",
  investor: "Investor",
  link: "Hidden link",
  more: "",
};

/** The frame's width, or null until measured (and in tests, which draw the wide path). */
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

function edgeClass(e: PathEdge): string {
  return [e.strong ? styles.edgeStrong : styles.edge, e.dashed && styles.edgeDashed]
    .filter(Boolean)
    .join(" ");
}

interface CalaPathProps {
  candidate: Candidate;
  trusted: Set<string>;
  eventName?: string;
}

/** Why this startup is on the list, drawn as the path Grabbit walked in Cala's graph. */
export function CalaPath({ candidate, trusted, eventName = "Slush 2026" }: CalaPathProps) {
  const frame = useRef<HTMLElement>(null);
  const wide = layoutPath(candidate, trusted, eventName);
  const width = useWidth(frame);
  // Tall: drawn at the frame's own width (padding and border aside), so text is not scaled.
  const layout =
    width !== null && width < wide.width * TALL_BELOW ? toTall(wide, width - 2 * PAD - 18) : wide;
  const [picked, setPicked] = useState<PathNode | null>(null);
  // The node under the pointer or keyboard focus shows its whole name in an overlay drawn
  // on top. The node itself stays put: moving a focused element in the DOM would blur it.
  const [active, setActive] = useState<string | null>(null);
  const hasLinks = layout.edges.some((e) => e.dashed);
  const byId = new Map(layout.nodes.map((n) => [n.id, n]));
  const activeNode = active ? byId.get(active) : undefined;
  const w = layout.width + PAD * 2;
  const h = layout.height - ROW + NODE_H + PAD * 2;

  return (
    <figure ref={frame} className={styles.figure} data-tall={layout.tall || undefined}>
      <div className={styles.scroll}>
        <svg
          className={styles.svg}
          width={w}
          height={h}
          viewBox={`${-PAD} ${-PAD - NODE_H / 2} ${w} ${h}`}
          role="img"
          aria-label={`Path in Cala's graph from ${eventName} to ${candidate.name} and its investors`}
        >
          {layout.edges.map((e) => {
            const a = byId.get(e.from);
            const b = byId.get(e.to);
            if (!a || !b) return null;
            if (layout.tall) {
              const x = a.x + 11;
              return (
                <g key={`${e.from}-${e.to}`} className={edgeClass(e)}>
                  <path d={`M${x},${a.y + NODE_H / 2} V${b.y} H${b.x}`} />
                </g>
              );
            }
            const x1 = a.x + NODE_W;
            const x2 = b.x;
            const mx = (x1 + x2) / 2;
            return (
              <g key={`${e.from}-${e.to}`} className={edgeClass(e)}>
                <path d={`M${x1},${a.y} C${mx},${a.y} ${mx},${b.y} ${x2},${b.y}`} />
                {e.label && (
                  <EdgeLabel
                    x={mx}
                    y={(a.y + b.y) / 2 + EDGE_PX / 2 - 1}
                    anchor="middle"
                    text={clip(e.label, fits(x2 - x1 - 4, EDGE_PX))}
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
                aria-label={`${KIND_LABEL[n.kind]} ${n.label}`}
                className={styles.node}
                data-kind={n.kind}
                data-trusted={n.trusted || undefined}
                data-lead={n.lead || undefined}
                data-link={n.kind === "link" || undefined}
                data-picked={picked?.id === n.id || undefined}
                data-active={n.id === active || undefined}
                transform={`translate(${n.x},${n.y - NODE_H / 2})`}
                onClick={() => setPicked(n.kind === "more" ? null : n)}
                onPointerEnter={() => setActive(n.id)}
                onPointerLeave={() => setActive((a) => (a === n.id ? null : a))}
                onFocus={() => setActive(n.id)}
                onBlur={() => setActive((a) => (a === n.id ? null : a))}
                onKeyDown={(ev) => {
                  if (ev.key === "Enter" || ev.key === " ") {
                    ev.preventDefault();
                    setPicked(n);
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
      <figcaption className={styles.caption}>
        {picked ? (
          <>
            <strong>{picked.label}</strong> · {KIND_LABEL[picked.kind]}
            {picked.entityId && (
              <>
                {" "}
                · Cala entity <code>{picked.entityId.slice(0, 8)}</code>
              </>
            )}
            {picked.detail && (
              <span className={styles.detail}>
                {picked.detail} {picked.trust && <TrustBadge level={picked.trust} />}
              </span>
            )}
          </>
        ) : (
          `Path in Cala's entity graph. Each box is a Cala entity, each line an edge${
            hasLinks ? "; dashed lines are links found two steps away" : ""
          }. Select one.`
        )}
      </figcaption>
    </figure>
  );
}

/** The active node again, unclipped and wider when it needs to be; decoration only. */
function FullName({ node }: { node: PathNode }) {
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
