import { useId } from "react";
import styles from "./Logo.module.css";

/**
 * The Grabbit logo: violet speed lines, the rabbit whose head is a G, and the wordmark.
 * Redrawn as vector from the logo artwork, because the source PNG is a glow render on black.
 */
export function Logo({ className }: { className?: string }) {
  const cut = useId();
  return (
    <span className={[styles.logo, className].filter(Boolean).join(" ")}>
      <svg className={styles.mark} viewBox="115 290 410 370" aria-hidden="true">
        <mask id={cut}>
          <rect x="0" y="0" width="1000" height="1000" fill="#fff" />
          <circle cx="385" cy="545" r="48" />
          <rect x="385" y="478" width="140" height="19" />
          <circle cx="452" cy="452" r="9" />
        </mask>
        <g className={styles.speed}>
          <rect x="158" y="487" width="104" height="28" rx="14" />
          <rect x="122" y="537" width="128" height="29" rx="14.5" />
        </g>
        <g className={styles.rabbit} mask={`url(#${cut})`}>
          <circle cx="395" cy="535" r="120" />
          <ellipse cx="342" cy="395" rx="105" ry="34" transform="rotate(21 342 395)" />
          <ellipse cx="400" cy="362" rx="107" ry="33" transform="rotate(35 400 362)" />
        </g>
      </svg>
      <span className={styles.word}>Grabbit</span>
    </span>
  );
}
