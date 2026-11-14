import { ArrowRight, FlaskConical, Play, RotateCcw, X } from "lucide-react";
import { type KeyboardEvent, useEffect, useRef, useState } from "react";
import { Button } from "../../components/Button";
import styles from "./CoachCard.module.css";
import { useDemo } from "./DemoRoot";
import { DEMO_STEPS, type DemoActions, type DemoSignals } from "./steps";

interface CoachCardProps {
  signals: DemoSignals;
  actions: DemoActions;
  /** A turn is running: "Show me" waits for it. */
  busy: boolean;
  /** The report panel covers the chat (narrow screens): the card floats above it. */
  floating?: boolean;
}

/**
 * The guided demo's narrator (#184): one step at a time, what to do, then what happened.
 * "Show me" makes the move for the visitor; making it themselves works the same.
 */
export function CoachCard({ signals, actions, busy, floating = false }: CoachCardProps) {
  const demo = useDemo();
  const [index, setIndex] = useState(0);
  const ref = useRef<HTMLElement>(null);
  const finished = index >= DEMO_STEPS.length;
  const step = DEMO_STEPS[index];
  const done = !finished && step.done(signals);

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

  const title = finished ? "That's the loop. Your turn." : step.title;
  const text = finished
    ? "Now describe your own thesis. Nothing from this demo stays in your research."
    : done
      ? step.outcome
      : step.prompt;

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
      <p key={`${index}-${done}`} className={styles.text}>
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
        ) : done ? (
          <Button
            size="sm"
            icon={<ArrowRight aria-hidden="true" />}
            onClick={() => setIndex((i) => i + 1)}
          >
            {index === DEMO_STEPS.length - 1 ? "Finish" : "Next"}
          </Button>
        ) : (
          <Button
            size="sm"
            icon={<Play aria-hidden="true" />}
            loading={busy}
            onClick={() => step.act(actions)}
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
