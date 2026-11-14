import { BellDot } from "lucide-react";
import { type CSSProperties, useEffect, useState } from "react";
import { useSimulateEvent } from "../../api/hooks/queries";
import { Button } from "../../components/Button";
import { useToast } from "../../components/Toast";
import styles from "./DemoAlertButton.module.css";

/** The demo alert arrives this long after the click, so it lands like a real one. */
export const ALERT_DELAY_MS = 30_000;

/** The staged alert the demo shows: GREÏ's seed round (decisions.md 2026-11-14 09:40). */
export const DEFAULT_DEMO_FIXTURE = "grei_seed_round";

interface DemoAlertButtonProps {
  fixture: string;
  /** Lets the top bar hide the words on phones; the button keeps them as its name. */
  labelClassName?: string;
}

/**
 * Queues the staged alert. While it waits, a ring drains around the bell and the button
 * says how many seconds are left; a simulation that fails says why instead of going quiet.
 */
export function DemoAlertButton({ fixture, labelClassName }: DemoAlertButtonProps) {
  const simulate = useSimulateEvent();
  const { toast } = useToast();
  const [endsAt, setEndsAt] = useState<number | null>(null);
  const [now, setNow] = useState(() => Date.now());

  // biome-ignore lint/correctness/useExhaustiveDependencies: one timer per queued alert.
  useEffect(() => {
    if (endsAt === null) return;
    const tick = window.setInterval(() => setNow(Date.now()), 1000);
    const fire = window.setTimeout(() => {
      window.clearInterval(tick);
      simulate.mutate(fixture, {
        onError: (error) =>
          toast({
            title: "The demo alert did not fire",
            description: error.message,
            duration: null,
          }),
        onSettled: () => setEndsAt(null),
      });
    }, endsAt - Date.now());
    return () => {
      window.clearInterval(tick);
      window.clearTimeout(fire);
    };
  }, [endsAt]);

  const queue = () => {
    const start = Date.now();
    setNow(start);
    setEndsAt(start + ALERT_DELAY_MS);
  };

  const queued = endsAt !== null;
  const secondsLeft = queued ? Math.max(0, Math.ceil((endsAt - now) / 1000)) : 0;
  const label = !queued
    ? "Alerts"
    : secondsLeft > 0
      ? `Alert in ${secondsLeft} s`
      : "Sending alert";

  return (
    <Button
      variant="ghost"
      size="sm"
      className={styles.button}
      data-queued={queued || undefined}
      disabled={queued}
      onClick={queue}
      icon={
        <span
          className={styles.bell}
          style={{ "--alert-delay": `${ALERT_DELAY_MS}ms` } as CSSProperties}
          aria-hidden="true"
        >
          {queued && (
            <svg className={styles.ring} viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="12" cy="12" r="10.5" pathLength={100} />
            </svg>
          )}
          <BellDot />
        </span>
      }
    >
      <span className={labelClassName}>{label}</span>
    </Button>
  );
}
