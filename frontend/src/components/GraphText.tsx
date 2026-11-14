/**
 * Text inside Grabbit's SVG graphs (the explored walk and the report's Cala path). The SVGs
 * draw at 1 unit = 1 CSS px and scroll instead of shrinking, so these sizes are what the
 * reader sees: never below 12px (#116).
 */

export const NODE_H = 36;
export const LABEL_PX = 13;
export const SUB_PX = 12;
export const EDGE_PX = 12;
/** Inner padding of a node box, left and right. */
export const NODE_PAD = 10;

// Average advance of Hanken Grotesk, as a share of the font size (semibold label, regular
// sub and edge text). Generous on purpose: an estimate that runs long only clips earlier.
const ADVANCE = { label: 0.6, text: 0.56 };

/** Width the text takes at `px`, estimated without layout (jsdom has none). */
export function textWidth(text: string, px: number, bold = false): number {
  return Math.ceil(text.length * px * (bold ? ADVANCE.label : ADVANCE.text));
}

/** Characters that fit in `width` at `px`. */
export function fits(width: number, px: number, bold = false): number {
  return Math.max(4, Math.floor(width / (px * (bold ? ADVANCE.label : ADVANCE.text))));
}

/** A node's sub line starts with a capital, whatever word comes first ("You trust · lead"). */
export function subLine(text: string): string {
  return text.replace(/^\p{Ll}/u, (c) => c.toUpperCase());
}

export function clip(text: string, max: number): string {
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

/** Width a node needs to show its whole label and sub line. */
export function fullNodeWidth(label: string, sub?: string): number {
  const inner = Math.max(textWidth(label, LABEL_PX, true), sub ? textWidth(sub, SUB_PX) : 0);
  return inner + 2 * NODE_PAD;
}

interface EdgeLabelProps {
  x: number;
  /** Baseline of the text. */
  y: number;
  anchor: "start" | "middle" | "end";
  text: string;
  className?: string;
  backgroundClassName?: string;
}

/** An edge's word on a plate of the graph's own background, so lines never run through it. */
export function EdgeLabel({ x, y, anchor, text, className, backgroundClassName }: EdgeLabelProps) {
  const w = textWidth(text, EDGE_PX) + 8;
  const h = EDGE_PX + 6;
  const left = anchor === "start" ? x - 4 : anchor === "middle" ? x - w / 2 : x - w + 4;
  return (
    <g data-edge-label="">
      <rect
        className={backgroundClassName}
        x={left}
        y={y - EDGE_PX + 1 - 3}
        width={w}
        height={h}
        rx={4}
      />
      <text x={x} y={y} textAnchor={anchor} className={className}>
        {text}
      </text>
    </g>
  );
}
