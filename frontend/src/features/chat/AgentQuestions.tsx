import { Send } from "lucide-react";
import { type FormEvent, useId, useState } from "react";
import type { AgentQuestion } from "../../api/types";
import { Button } from "../../components/Button";
import styles from "./AgentQuestions.module.css";

/** The chosen answers as one message, in the order the questions were asked. */
export function composeAnswer(questions: AgentQuestion[], chosen: Record<string, string>): string {
  return questions
    .map((q) => chosen[q.key])
    .filter(Boolean)
    .join(" ");
}

interface Props {
  questions: AgentQuestion[];
  /** Sends the answers as the next message; without it the questions are read-only. */
  onAnswer?: (text: string) => void;
  /** A turn is running: choices stay, sending waits. */
  busy?: boolean;
}

/**
 * The agent's first questions with clickable answers (#153): one choice per question, all
 * optional, sent together as one plain message the agent applies like any typed answer.
 * Once the conversation moved on, they stay as a read-only record of what was asked.
 */
export function AgentQuestions({ questions, onAnswer, busy = false }: Props) {
  const id = useId();
  const [chosen, setChosen] = useState<Record<string, string>>({});
  const answer = composeAnswer(questions, chosen);

  if (!onAnswer) {
    return (
      <ul className={styles.asked} aria-label="Questions Grabbit asked">
        {questions.map((q) => (
          <li key={q.key}>{q.text}</li>
        ))}
      </ul>
    );
  }

  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (answer && !busy) onAnswer(answer);
  };

  return (
    <form className={styles.form} onSubmit={submit} aria-label="Answer Grabbit's questions">
      {questions.map((q) => (
        <fieldset key={q.key} className={styles.question}>
          <legend className={styles.text}>{q.text}</legend>
          <div className={styles.options}>
            {q.options.map((o) => (
              <label key={o.label} className={styles.option}>
                <input
                  type="radio"
                  name={`${id}-${q.key}`}
                  value={o.answer}
                  checked={chosen[q.key] === o.answer}
                  onChange={() => setChosen((c) => ({ ...c, [q.key]: o.answer }))}
                />
                <span>{o.label}</span>
              </label>
            ))}
          </div>
        </fieldset>
      ))}
      <div className={styles.actions}>
        <Button
          type="submit"
          size="sm"
          disabled={!answer || busy}
          icon={<Send aria-hidden="true" />}
        >
          Send answers
        </Button>
        <span className={styles.hint}>Skip any you like, or type your own below.</span>
      </div>
    </form>
  );
}
