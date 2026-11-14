import { useEffect, useRef, useState } from "react";
import type { Candidate } from "../../api/types";
import { TrustBadge } from "../../components/TrustBadge";
import styles from "./CalaPath.module.css";
import { layoutPath, NODE_W, type PathEdge, type PathNode, ROW, toTall } from "./calaPath";

const NODE_H = 34;
const PAD = 8;
/** Below this share of its natural width the wide path gets too small; draw the tree. */
const TALL_BELOW = 0.8;

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

function clip(text: string, max = 18): string {
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
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
  const hasLinks = layout.edges.some((e) => e.dashed);
  const byId = new Map(layout.nodes.map((n) => [n.id, n]));
  const w = layout.width + PAD * 2;
  const h = layout.height - ROW + NODE_H + PAD * 2;

  return (
    <figure ref={frame} className={styles.figure} data-tall={layout.tall || undefined}>
      <div className={styles.scroll}>
        <svg
          className={styles.svg}
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
                  <text
                    x={mx}
                    y={(a.y + b.y) / 2 - 4}
                    textAnchor="middle"
                    className={styles.edgeLabel}
                  >
                    {e.label}
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
              aria-label={`${KIND_LABEL[n.kind]} ${n.label}`}
              className={styles.node}
              data-kind={n.kind}
              data-trusted={n.trusted || undefined}
              data-lead={n.lead || undefined}
              data-link={n.kind === "link" || undefined}
              data-picked={picked?.id === n.id || undefined}
              transform={`translate(${n.x},${n.y - NODE_H / 2})`}
              onClick={() => setPicked(n.kind === "more" ? null : n)}
              onKeyDown={(ev) => {
                if (ev.key === "Enter" || ev.key === " ") setPicked(n);
              }}
            >
              <title>{n.label}</title>
              <rect width={n.w ?? NODE_W} height={NODE_H} rx={8} />
              <text x={10} y={n.sub ? 14 : 21} className={styles.nodeLabel}>
                {clip(n.label, n.w ? Math.floor((n.w - 20) / 7) : 18)}
              </text>
              {n.sub && (
                <text x={10} y={27} className={styles.nodeSub}>
                  {clip(n.sub, n.w ? Math.floor((n.w - 20) / 5.6) : 22)}
                </text>
              )}
            </g>
          ))}
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
