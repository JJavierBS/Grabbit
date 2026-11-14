import type { ReactNode } from "react";
import { useGuideLocked } from "./DemoRoot";
import styles from "./GuideLock.module.css";

/**
 * Disables every control inside it while the guided demo runs. A native `fieldset disabled`
 * covers buttons and fields; links and SVG buttons are held by the demo's click guard in App.
 * Outside the demo it renders its children unwrapped.
 */
export function GuideLock({ children }: { children: ReactNode }) {
  if (!useGuideLocked()) return children;
  return (
    <fieldset className={styles.lock} disabled data-guide-locked>
      {children}
    </fieldset>
  );
}
