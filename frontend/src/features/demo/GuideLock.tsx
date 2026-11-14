import type { ReactNode } from "react";
import { useDemo, useGuideLocked } from "./DemoRoot";
import styles from "./GuideLock.module.css";
import type { DemoTarget } from "./steps";

/**
 * Disables every control inside it while the guided demo's current step does not use them.
 * A native `fieldset disabled` covers buttons and fields; links and SVG buttons are held by
 * the demo's click guard in App. Outside the demo it renders its children unwrapped.
 */
export function GuideLock({ target, children }: { target?: DemoTarget; children: ReactNode }) {
  const demo = useDemo();
  const locked = useGuideLocked(target);
  if (!demo?.active) return children;
  return (
    <fieldset className={styles.lock} disabled={locked} data-guide-locked={locked || undefined}>
      {children}
    </fieldset>
  );
}
