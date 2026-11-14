import styles from "./Skeleton.module.css";

interface SkeletonProps {
  /** Number of text lines; the last one is shorter, like a paragraph. */
  lines?: number;
  /** A block placeholder (e.g. a card) instead of text lines. */
  block?: "card" | "badge" | "title";
  label?: string;
}

export function Skeleton({ lines = 3, block, label = "Loading" }: SkeletonProps) {
  return (
    <div className={styles.wrap} role="status" aria-live="polite">
      <span className="visually-hidden">{label}</span>
      {block ? (
        <span className={`${styles.bone} ${styles[block]}`} aria-hidden="true" />
      ) : (
        Array.from({ length: lines }, (_, i) => (
          <span
            // biome-ignore lint/suspicious/noArrayIndexKey: static placeholder lines never reorder.
            key={i}
            className={`${styles.bone} ${styles.line} ${i === lines - 1 && lines > 1 ? styles.short : ""}`}
            aria-hidden="true"
          />
        ))
      )}
    </div>
  );
}
