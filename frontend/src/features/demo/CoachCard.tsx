import { ArrowRight, FlaskConical, Play, RotateCcw, X } from "lucide-react";
import { type KeyboardEvent, useEffect, useRef, useState } from "react";
import { Button } from "../../components/Button";
import styles from "./CoachCard.module.css";
import { useDemo } from "./DemoRoot";
import { DEMO_END, DEMO_STEPS, type DemoActions, type DemoSignals } from "./steps";

interface CoachCardProps {
  signals: DemoSignals;
  actions: DemoActions;
  /** A turn is running: "Show me" waits for it. */
  busy: boolean;
  /** The report panel covers the chat (narrow screens): the card floats above it. */
  floating?: boolean;
}

/**
 * The guided demo's narrator (#184): one step at a time. "Show me" makes the move, the only
 * control the demo leaves enabled besides leaving it. Once the result is on screen the guide
 * moves on by itself; the next step's text says what just happened.
 */
export function CoachCard({ signals, actions, busy, floating = false }: CoachCardProps) {
  const demo = useDemo();
  // The step whose move was made: its button waits for the result, e.g. the alert.
  const [acted, setActed] = useState(-1);
  const ref = useRef<HTMLElement>(null);
  const index = demo?.step ?? 0;
  const finished = index >= DEMO_STEPS.length;
  const step = DEMO_STEPS[index];
  const done = !finished && step.done(signals);
  const advanceMs = demo?.advanceMs ?? 0;
  const next = demo?.next;

  // A beat to see the result land, then the next step.
  useEffect(() => {
    if (!done || !next) return;
    const timer = setTimeout(next, advanceMs);
    return () => clearTimeout(timer);
  }, [done, advanceMs, next]);

  // The demo opens on the card, so a keyboard reader starts where the guide speaks.
  useEffect(() => {
    ref.current?.focus({ focusVisible: false } as FocusOptions);
  }, []);

  if (!demo) return null;

  const onKeyDown = (e: KeyboardEvent) => {
    if (e.key !== "Escape") return;
    e.stopPropagation();
    demo.exit();
  };

  const title = finished ? DEMO_END.title : step.title;
  const text = finished ? DEMO_END.text : step.prompt;

  return (
    <section
      ref={ref}
      className={styles.card}
      aria-labelledby="coach-title"
      data-floating={floating || undefined}
      tabIndex={-1}
      onKeyDown={onKeyDown}
    >
      <ol className={styles.progress} aria-hidden="true">
        {DEMO_STEPS.map((s, i) => (
          <li
            key={s.title}
            data-state={i < index || finished ? "done" : i === index ? "now" : undefined}
          />
        ))}
      </ol>
      <div className={styles.head}>
        <h3 id="coach-title" className={styles.title} aria-live="polite">
          {title}
        </h3>
        <Button
          variant="ghost"
          size="sm"
          className={styles.exit}
          aria-label="Exit the demo"
          icon={<X aria-hidden="true" />}
          onClick={demo.exit}
        />
      </div>
      <p key={index} className={styles.text}>
        {text}
      </p>
      <div className={styles.foot}>
        {finished ? (
          <>
            <Button size="sm" icon={<ArrowRight aria-hidden="true" />} onClick={demo.exit}>
              Try it yourself
            </Button>
            <Button
              variant="ghost"
              size="sm"
              icon={<RotateCcw aria-hidden="true" />}
              onClick={demo.start}
            >
              Replay
            </Button>
          </>
        ) : (
          <Button
            size="sm"
            icon={<Play aria-hidden="true" />}
            loading={busy || (acted === index && !done)}
            disabled={done}
            onClick={() => {
              setActed(index);
              step.act(actions);
            }}
          >
            Show me
          </Button>
        )}
        <p className={styles.meta}>
          <FlaskConical aria-hidden="true" />
          <span>Sample data, nothing is saved</span>
          {!finished && (
            <span className={styles.count}>
              {index + 1} of {DEMO_STEPS.length}
            </span>
          )}
        </p>
      </div>
    </section>
  );
}
