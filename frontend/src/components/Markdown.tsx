import { Fragment, type ReactNode } from "react";
import styles from "./Markdown.module.css";

// shortcut: covers the subset report bodies use (paragraphs, "-" lists, **bold**, *italic*,
// [links](url)); switch to a real Markdown library if Gemini starts writing tables or headings.
const INLINE = /(\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]+\]\([^)\s]+\))/g;

function safeHref(url: string): string | undefined {
  return /^(https?:|mailto:)/i.test(url) ? url : undefined;
}

function inline(text: string): ReactNode[] {
  return text.split(INLINE).map((part, i) => {
    const key = `${i}-${part.slice(0, 8)}`;
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
      return <strong key={key}>{part.slice(2, -2)}</strong>;
    }
    const link = /^\[([^\]]+)\]\(([^)\s]+)\)$/.exec(part);
    if (link) {
      const href = safeHref(link[2]);
      return href ? (
        <a key={key} href={href} target="_blank" rel="noopener noreferrer">
          {link[1]}
        </a>
      ) : (
        <Fragment key={key}>{link[1]}</Fragment>
      );
    }
    if (part.startsWith("*") && part.endsWith("*") && part.length > 2) {
      return <em key={key}>{part.slice(1, -1)}</em>;
    }
    return <Fragment key={key}>{part}</Fragment>;
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
