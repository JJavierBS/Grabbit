import { Fragment, type ReactNode } from "react";
import type { TrustLevel } from "../api/types";
import { formatDate } from "./FactValue";
import styles from "./Markdown.module.css";
import { TRUST_LABELS, TrustBadge } from "./TrustBadge";

// shortcut: covers the subset report bodies use (paragraphs, "-" lists, **bold**, *italic*,
// [links](url)); switch to a real Markdown library if Gemini starts writing tables or headings.
const INLINE = /(\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]+\]\([^)\s]+\))/g;

// Agents sometimes write a fact's trust level as "[Database]" or "(Press)"; the UI draws
// those as badges. Names are the badge labels plus the short forms the prompts used.
const TRUST_NAMES = new Map<string, TrustLevel>([
  ...Object.entries(TRUST_LABELS).map(([level, label]) => [label, level as TrustLevel] as const),
  ["Filing", "filing"],
  ["Web unverified", "web_unverified"],
]);
const NAMES = [...TRUST_NAMES.keys()].map((n) => n.replace(/ /g, "\\s+")).join("|");
const TRUST_TAG = new RegExp(`\\s*(?:\\[(${NAMES})\\]|\\((${NAMES})\\))`, "gi");
const ISO_DATE = /\b\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])\b/g;
const TOKEN = new RegExp(`${TRUST_TAG.source}|${ISO_DATE.source}`, "gi");

function trustLevel(name: string): TrustLevel | undefined {
  const wanted = name.replace(/\s+/g, " ").toLowerCase();
  for (const [label, level] of TRUST_NAMES) {
    if (label.toLowerCase() === wanted) return level;
  }
  return undefined;
}

/** Plain text with trust tags drawn as badges and ISO dates written out ("10 Jun 2026"). */
function plain(text: string, key: string): ReactNode[] {
  const out: ReactNode[] = [];
  let last = 0;
  for (const m of text.matchAll(TOKEN)) {
    const at = m.index ?? 0;
    if (at > last) out.push(text.slice(last, at));
    const level = m[1] || m[2] ? trustLevel(m[1] ?? m[2]) : undefined;
    out.push(
      level ? (
        <Fragment key={`${key}-${at}`}>
          {at > 0 && " "}
          {/* An absent value is content, not a source: it keeps its words. */}
          <TrustBadge level={level} compact={level !== "not_published"} />
        </Fragment>
      ) : (
        formatDate(m[0], "day")
      ),
    );
    last = at + m[0].length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}

function safeHref(url: string): string | undefined {
  return /^(https?:|mailto:)/i.test(url) ? url : undefined;
}

function inline(text: string): ReactNode[] {
  return text.split(INLINE).map((part, i) => {
    const key = `${i}-${part.slice(0, 8)}`;
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
      return <strong key={key}>{plain(part.slice(2, -2), key)}</strong>;
    }
    const link = /^\[([^\]]+)\]\(([^)\s]+)\)$/.exec(part);
    if (link) {
      const href = safeHref(link[2]);
      return href ? (
        <a key={key} href={href} target="_blank" rel="noopener noreferrer">
          {plain(link[1], key)}
        </a>
      ) : (
        <Fragment key={key}>{plain(link[1], key)}</Fragment>
      );
    }
    if (part.startsWith("*") && part.endsWith("*") && part.length > 2) {
      return <em key={key}>{plain(part.slice(1, -1), key)}</em>;
    }
    return <Fragment key={key}>{plain(part, key)}</Fragment>;
  });
}

export function Markdown({ source }: { source: string }) {
  const blocks = source.trim().split(/\n\s*\n/);
  return (
    <div className={styles.prose}>
      {blocks.map((block, i) => {
        const lines = block.split("\n").filter((l) => l.trim());
        const key = `${i}-${block.slice(0, 12)}`;
        if (lines.length && lines.every((l) => /^\s*[-*]\s+/.test(l))) {
          return (
            <ul key={key}>
              {lines.map((l, j) => (
                // biome-ignore lint/suspicious/noArrayIndexKey: list lines are static text from one render.
                <li key={`${j}-${l.slice(0, 12)}`}>{inline(l.replace(/^\s*[-*]\s+/, ""))}</li>
              ))}
            </ul>
          );
        }
        return <p key={key}>{inline(lines.join(" "))}</p>;
      })}
    </div>
  );
}
