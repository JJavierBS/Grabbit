import { CirclePlay } from "lucide-react";
import styles from "./DemoLauncher.module.css";
import { useDemo } from "./DemoRoot";

interface DemoLauncherProps {
  /** Under the first-run welcome, or as the sidebar's last row. */
  place: "welcome" | "sidebar";
}

/** Starts the guided demo; hidden inside the demo and where the app runs without it. */
export function DemoLauncher({ place }: DemoLauncherProps) {
  const demo = useDemo();
  if (!demo || demo.active) return null;
  return (
    <button type="button" className={styles.launcher} data-place={place} onClick={demo.start}>
      <CirclePlay aria-hidden="true" />
      <span>{place === "welcome" ? "See how it works" : "How Grabbit works"}</span>
      {place === "welcome" && <span className={styles.length}>1 min</span>}
      {place === "welcome" && !demo.seen && <span className={styles.fresh} aria-hidden="true" />}
    </button>
  );
}
