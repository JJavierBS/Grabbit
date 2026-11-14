import type { ExploredGraph, GraphEdge, GraphNode } from "../../../api/types";
import { humanize } from "../../../lib/humanize";

/** One box of the explored subgraph: a Cala entity, or a fold of the ones left out. */
export interface WalkNode {
  id: string;
  kind: "root" | "round" | "entity" | "more";
  label: string;
  sub?: string;
  entityId?: string;
  lead?: boolean;
  trusted?: boolean;
  depth: number;
  x: number;
  y: number;
  /** Width in the tall layout; the wide one uses NODE_W. */
  w?: number;
}

export interface WalkEdge {
  from: string;
  to: string;
  /** What the line says: the edge's role, `is_lead`, or the Cala relationship name. */
  label: string;
  /** The Cala relationship and its attributes, for the tooltip. */
  title: string;
  /** On the way from the root to an investor you trust. */
  strong?: boolean;
  /** A second link between drawn nodes, outside the tree (e.g. one investor in two rounds). */
  cross?: boolean;
}

export interface WalkLayout {
  nodes: WalkNode[];
  edges: WalkEdge[];
  width: number;
  height: number;
  tall?: boolean;
}

export const NODE_W = 152;
export const PITCH = 248;
export const ROW = 46;
export const MAX_DEPTH = 3;
export const MAX_CHILDREN = 5;
const INDENT = 22;

const ROUND_TYPES = new Set(["FundingRound", "PrivateCompanyFundingRound", "CorporateEvent"]);
const TYPE_LABEL: Record<string, string> = {
  FundingRound: "Funding round",
  PrivateCompanyFundingRound: "Funding round (filing)",
  CorporateEvent: "Corporate event",
};

export function typeLabel(entityType: string): string {
  return TYPE_LABEL[entityType] ?? entityType.replace(/([a-z])([A-Z])/g, "$1 $2");
}

function edgeLabel(e: GraphEdge): string {
  if (e.is_lead) return humanize("is_lead");
  return humanize(e.role ?? e.relationship);
}

function edgeTitle(e: GraphEdge): string {
  return [
    humanize(e.relationship),
    e.role && `as ${humanize(e.role)}`,
    e.is_lead && "lead investor",
  ]
    .filter(Boolean)
    .join(" · ");
}

// The node's own word that an edge word already says.
const ALSO_SAID: Record<string, string> = {
  [humanize("is_lead")]: "lead investor",
  [humanize("INVESTOR")]: "investor",
};

function saysAgain(edge: string, part: string): boolean {
  const word = part.toLowerCase();
  return word === edge.toLowerCase() || word === ALSO_SAID[edge];
}

interface Link {
  other: string;
  edge: GraphEdge;
}

/**
 * The walk the agent did in Cala's graph, as a tidy tree read left to right: the root,
 * then each hop one column further. Each node hangs under the first node that reached it;
 * investors you trust and leads come first, the rest of a long list folds into "+N more".
 */
export function layoutWalk(graph: ExploredGraph, rootId: string, trusted: Set<string>): WalkLayout {
  const byId = new Map(graph.nodes.map((n) => [n.entity_id, n]));
  const root = byId.get(rootId) ?? graph.nodes[0];
  if (!root) return { nodes: [], edges: [], width: NODE_W, height: ROW };

  const links = new Map<string, Link[]>();
  const link = (a: string, b: string, edge: GraphEdge) =>
    links.set(a, [...(links.get(a) ?? []), { other: b, edge }]);
  for (const e of graph.edges) {
    if (!byId.has(e.source) || !byId.has(e.target) || e.source === e.target) continue;
    link(e.source, e.target, e);
    link(e.target, e.source, e);
  }
  const leads = new Set(graph.edges.filter((e) => e.is_lead).map((e) => e.source));
  const rank = (n: GraphNode) =>
    (trusted.has(n.entity_id) ? 0 : 2) + (leads.has(n.entity_id) ? 0 : 1);

  // Breadth first, so each node sits at its shortest distance from the root.
  const depth = new Map([[root.entity_id, 0]]);
  const children = new Map<string, Link[]>();
  const queue = [root.entity_id];
  while (queue.length) {
    const id = queue.shift() as string;
    const d = depth.get(id) as number;
    if (d >= MAX_DEPTH) continue;
    for (const l of links.get(id) ?? []) {
      if (depth.has(l.other)) continue;
      depth.set(l.other, d + 1);
      children.set(id, [...(children.get(id) ?? []), l]);
      queue.push(l.other);
    }
  }

  // An investor you trust anywhere below a node makes the whole way to it strong.
  const strong = new Set<string>();
  const markStrong = (id: string): boolean => {
    let hit = trusted.has(id) && id !== root.entity_id;
    for (const l of children.get(id) ?? []) if (markStrong(l.other)) hit = true;
    if (hit) strong.add(id);
    return hit;
  };
  markStrong(root.entity_id);

  const nodes: WalkNode[] = [];
  const edges: WalkEdge[] = [];
  let row = 0;
  const place = (n: GraphNode, d: number, via?: Link): number => {
    const kids = [...(children.get(n.entity_id) ?? [])].sort(
      (a, b) =>
        rank(byId.get(a.other) as GraphNode) - rank(byId.get(b.other) as GraphNode) ||
        (byId.get(a.other)?.name ?? "").localeCompare(byId.get(b.other)?.name ?? ""),
    );
    const shown = kids.slice(0, MAX_CHILDREN);
    const rows: number[] = [];
    for (const l of shown) {
      rows.push(place(byId.get(l.other) as GraphNode, d + 1, l));
      edges.push({
        from: n.entity_id,
        to: l.other,
        label: edgeLabel(l.edge),
        title: edgeTitle(l.edge),
        strong: strong.has(l.other),
      });
    }
    if (kids.length > shown.length) {
      const id = `more:${n.entity_id}`;
      rows.push(row);
      nodes.push({
        id,
        kind: "more",
        label: `+${kids.length - shown.length} more`,
        depth: d + 1,
        x: (d + 1) * PITCH,
        y: row * ROW,
      });
      edges.push({ from: n.entity_id, to: id, label: "", title: "" });
      row += 1;
    }
    let y: number;
    if (rows.length) {
      y = (rows[0] + rows[rows.length - 1]) / 2;
    } else {
      y = row;
      row += 1;
    }
    const isTrusted = trusted.has(n.entity_id);
    const isLead = leads.has(n.entity_id);
    const kind = d === 0 ? "root" : ROUND_TYPES.has(n.entity_type) ? "round" : "entity";
    const role = via?.edge.role === "INVESTOR" && via.edge.source === n.entity_id && "Investor";
    nodes.push({
      id: n.entity_id,
      kind,
      label: n.name,
      sub:
        [isTrusted && "you trust", isLead ? "Lead investor" : role || typeLabel(n.entity_type)]
          .filter(Boolean)
          .join(" · ") || undefined,
      entityId: n.entity_id,
      lead: isLead,
      trusted: isTrusted,
      depth: d,
      x: d * PITCH,
      y: y * ROW,
    });
    return y;
  };
  place(root, 0);

  // Links the tree left out, between nodes it drew in neighbouring columns.
  const drawn = new Map(nodes.map((n) => [n.id, n]));
  const inTree = new Set(edges.map((e) => [e.from, e.to].sort().join("|")));
  for (const e of graph.edges) {
    const key = [e.source, e.target].sort().join("|");
    const a = drawn.get(e.source);
    const b = drawn.get(e.target);
    if (!a || !b || inTree.has(key) || Math.abs(a.depth - b.depth) !== 1) continue;
    inTree.add(key);
    const [from, to] = a.depth < b.depth ? [a, b] : [b, a];
    edges.push({
      from: from.id,
      to: to.id,
      label: "",
      title: edgeTitle(e),
      cross: true,
      strong: trusted.has(e.source) || trusted.has(e.target),
    });
  }

  const maxDepth = Math.max(...nodes.map((n) => n.depth));
  return { nodes, edges, width: maxDepth * PITCH + NODE_W, height: Math.max(row, 1) * ROW };
}

/**
 * The same walk as an indented tree for narrow columns: one node per row, children under
 * their parent, the edge label moved into the sub line. Cross links are dropped.
 */
export function toTallWalk(wide: WalkLayout, width: number): WalkLayout {
  const tree = wide.edges.filter((e) => !e.cross);
  const kids = new Map<string, WalkEdge[]>();
  for (const e of tree) kids.set(e.from, [...(kids.get(e.from) ?? []), e]);
  const byId = new Map(wide.nodes.map((n) => [n.id, n]));
  const root = wide.nodes.find((n) => n.kind === "root");
  const nodes: WalkNode[] = [];
  const visit = (id: string, depth: number, via?: WalkEdge) => {
    const n = byId.get(id);
    if (!n) return;
    const x = depth * INDENT;
    // "invested · Investor" or "led · Lead investor" says it twice: keep the edge's word.
    const own = (n.sub ?? "").split(" · ").filter((p) => !(via && saysAgain(via.label, p)));
    const sub = [via?.label, ...own].filter(Boolean).join(" · ") || undefined;
    nodes.push({ ...n, sub, x, y: nodes.length * ROW, w: width - x });
    // Kids follow the wide layout's top-to-bottom order.
    const ordered = [...(kids.get(id) ?? [])].sort(
      (a, b) => (byId.get(a.to)?.y ?? 0) - (byId.get(b.to)?.y ?? 0),
    );
    for (const e of ordered) visit(e.to, depth + 1, e);
  };
  if (root) visit(root.id, 0);
  return { nodes, edges: tree, width, height: nodes.length * ROW, tall: true };
}
