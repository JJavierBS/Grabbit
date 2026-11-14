import { ArrowDown, MicVocal, RefreshCw, SendHorizontal, Square } from "lucide-react";
import {
  type FormEvent,
  Fragment,
  type KeyboardEvent,
  type ReactNode,
  type RefObject,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  useChat,
  useLatestReport,
  useProfile,
  useSendMessage,
  useTurnProgress,
  useUndo,
  useWalkTrace,
} from "../../api/hooks/queries";
import type { ChatMessage } from "../../api/types";
import { Button } from "../../components/Button";
import { TextArea } from "../../components/Input";
import { Logo } from "../../components/Logo";
import { Markdown } from "../../components/Markdown";
import { Skeleton } from "../../components/Skeleton";
import { DemoLauncher } from "../demo/DemoLauncher";
import { useDemo } from "../demo/DemoRoot";
import { GuideLock } from "../demo/GuideLock";
import { AgentQuestions } from "./AgentQuestions";
import { ChangeNote } from "./ChangeNote";
import styles from "./ChatPanel.module.css";
import { readDraft, saveDraft } from "./draft";
import { HowIFound } from "./HowIFound";
import { LiveWalk } from "./LiveWalk";
import { changeNoteText, isUndoable } from "./noteText";
import { VisualAnswer } from "./openui/VisualAnswer";
import { ReplySources } from "./ReplySources";
import { useComposerFocus } from "./useComposerFocus";
import { useDictation } from "./useDictation";
import { useFollowLog } from "./useFollowLog";
import { WorkingLine } from "./WorkingLine";

/** Corrections to try once a report exists. */
export const CORRECTIONS = ["Shorter, co-investors first", "Drop consumer health"];

/** First-run examples: a thesis can be this vague, and Grabbit asks the rest. */
export const THESIS_EXAMPLES = [
  "AI startups at pre-seed and seed",
  "Nordic climate tech at seed",
  "Fintech backed by Y Combinator",
];

export const PLACEHOLDER_FIRST = "Describe your thesis: sector, stage, investors you trust";
export const PLACEHOLDER_REPORT = "Correct the report or ask a question";

interface ChatPanelProps {
  /** Items with no place in the conversation yet, rendered after the messages. */
  footer?: ReactNode;
  /** Items anchored to a message, e.g. the report outline after the turn that wrote it. */
  renderAfter?: (message: ChatMessage) => ReactNode;
  /** Changes when the anchored or footer items change, so the log can follow them. */
  followKey?: string;
  /** The guided demo's card, docked on the composer (#184); it sends through this composer. */
  coach?: (send: (text: string) => void, busy: boolean) => ReactNode;
  /** The message box, for the layout to give focus back to it. */
  composerRef?: RefObject<HTMLTextAreaElement>;
}

export function ChatPanel({ footer, renderAfter, followKey, coach, composerRef }: ChatPanelProps) {
  const chat = useChat();
  const profile = useProfile();
  const report = useLatestReport();
  const progress = useTurnProgress();
  const trace = useWalkTrace().data;
  const demo = useDemo();
  const sandbox = demo?.active ?? false;
  const send = useSendMessage({ sandbox });
  const undo = useUndo();
  // The guided demo never reads or writes the visitor's draft.
  const [draft, setDraft] = useState(() => (sandbox ? "" : readDraft()));
  const ownField = useRef<HTMLTextAreaElement>(null);
  const field = composerRef ?? ownField;
  const focusComposer = useComposerFocus(field, !sandbox);
  const dictation = useDictation(setDraft);
  const messages = chat.data ?? [];
  const hasReport = Boolean(report.data);
  const firstRun = chat.isSuccess && messages.length === 0;
  // Corrections need a report; examples help only before the first message.
  const suggestions = hasReport ? CORRECTIONS : firstRun ? THESIS_EXAMPLES : [];
  // The live walk grows under the working line; follow it like a new message.
  const growth = trace ? `${trace.steps.length}|${trace.nodes}|${trace.answer?.length ?? 0}` : "";
  const follow = useFollowLog(messages, chat.isSuccess, `${followKey}|${send.isPending}|${growth}`);

  // Back from the guided demo: the visitor's own research starts at the composer.
  const returning = demo?.returning;
  useEffect(() => {
    if (returning) focusComposer();
  }, [returning, focusComposer]);

  useEffect(() => {
    if (!sandbox) saveDraft(draft);
  }, [draft, sandbox]);

  // Each reply hands the turn back: the next message starts in the box, unless the reader
  // is typing in another field.
  const working = send.isPending;
  const wasWorking = useRef(false);
  useEffect(() => {
    const active = document.activeElement;
    const elsewhere = active !== field.current && active?.matches("input, textarea, select");
    if (wasWorking.current && !working && !elsewhere) focusComposer();
    wasWorking.current = working;
  }, [working, focusComposer, field]);

  // Talk ends with the words in the box: read them, then Enter sends.
  const dictating = dictation.listening || dictation.transcribing;
  const wasDictating = useRef(false);
  useEffect(() => {
    if (wasDictating.current && !dictating) focusComposer();
    wasDictating.current = dictating;
  }, [dictating, focusComposer]);

  const submit = (text: string) => {
    const value = text.trim();
    if (!value || send.isPending) return;
    dictation.cancel();
    // The message leaves the composer at once; if it is not sent, it comes back to edit.
    setDraft("");
    // Sent from a suggestion, an answer or the Send button: the next message starts here.
    focusComposer();
    send.mutate(value, { onError: () => setDraft((current) => current || value) });
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    submit(draft);
  };

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      submit(draft);
    }
  };

  return (
    <section
      className={styles.panel}
      aria-labelledby="chat-title"
      data-working={send.isPending || undefined}
      data-listening={dictation.listening || undefined}
    >
      <h2 id="chat-title" className="visually-hidden">
        Chat with Grabbit
      </h2>
      <div
        ref={follow.logRef}
        className={styles.log}
        role="log"
        aria-live="polite"
        aria-busy={chat.isPending}
        onScroll={follow.onScroll}
      >
        <div className={styles.column} data-loaded={chat.isSuccess || undefined}>
          {chat.isPending && <Skeleton lines={4} label="Loading the conversation" />}
          {chat.isError && (
            <div className={styles.error} role="alert">
              <p>{chat.error.message}</p>
              <Button
                variant="secondary"
                size="sm"
                icon={<RefreshCw aria-hidden="true" />}
                onClick={() => chat.refetch()}
              >
                Try again
              </Button>
            </div>
          )}
          {firstRun && (
            <div className={styles.welcome}>
              <Logo stacked className={styles.welcomeLogo} />
              <p className={styles.welcomeLead}>Tell me what you look for at Slush 2026.</p>
              <p className={styles.welcomeHint}>
                <span>A sector, a stage, investors you trust:</span>{" "}
                <span>however vague, I ask the rest.</span>
              </p>
              <DemoLauncher place="welcome" />
            </div>
          )}
          {messages.map((m) => (
            <Fragment key={m.id}>
              <Message
                message={m}
                entering={follow.isNew(m)}
                canUndo={isUndoable(m.profile_changes, profile.data?.version)}
                undoing={undo.isPending}
                onUndo={() => undo.mutate()}
                onAnswer={m.id === messages.at(-1)?.id ? submit : undefined}
                busy={send.isPending}
                showSteps={demo?.active}
              />
              {renderAfter?.(m)}
            </Fragment>
          ))}
          {footer}
          {/* The working line is always the last thing in the log, under any card. */}
          {send.isPending && <WorkingLine hasReport={hasReport} phase={progress.data?.label} />}
          {send.isPending && trace && trace.steps.length > 0 && <LiveWalk trace={trace} />}
        </div>
      </div>

      <form className={styles.composer} onSubmit={onSubmit}>
        {coach?.(submit, send.isPending)}
        {follow.behind && (
          <Button
            variant="secondary"
            size="sm"
            className={styles.jump}
            icon={<ArrowDown aria-hidden="true" />}
            onClick={follow.jumpToLatest}
          >
            Jump to latest
          </Button>
        )}
        {send.isError && (
          <p className={styles.sendError} role="alert">
            Your message was not sent: {send.error.message}
          </p>
        )}
        {undo.isError && (
          <p className={styles.sendError} role="alert">
            Undo failed: {undo.error.message}
          </p>
        )}
        {dictation.error && (
          <p className={styles.sendError} role="alert">
            {dictation.error}
          </p>
        )}
        {suggestions.length > 0 && (
          <GuideLock>
            <div className={styles.suggestions}>
              {suggestions.map((s) => (
                <Button
                  key={s}
                  variant="secondary"
                  size="sm"
                  disabled={send.isPending}
                  onClick={() => submit(s)}
                >
                  {s}
                </Button>
              ))}
            </div>
          </GuideLock>
        )}
        <GuideLock>
          <div className={styles.inputRow}>
            <TextArea
              label="Message Grabbit"
              hideLabel
              placeholder={
                dictation.listening
                  ? "Listening… press Stop when you are done"
                  : dictation.transcribing
                    ? "Writing down what you said…"
                    : hasReport
                      ? PLACEHOLDER_REPORT
                      : PLACEHOLDER_FIRST
              }
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={onKeyDown}
              rows={1}
              ref={field}
            />
            {dictation.supported && (
              <Button
                variant={dictation.listening ? "primary" : "ghost"}
                aria-label={dictation.listening ? "Stop talking" : "Talk"}
                aria-pressed={dictation.listening}
                className={styles.talk}
                loading={dictation.transcribing}
                onClick={dictation.toggle}
                icon={
                  dictation.listening ? (
                    <Square aria-hidden="true" />
                  ) : (
                    <MicVocal aria-hidden="true" />
                  )
                }
              />
            )}
            <Button
              type="submit"
              aria-label="Send"
              className={styles.send}
              loading={send.isPending}
              disabled={!draft.trim()}
              icon={<SendHorizontal aria-hidden="true" />}
            />
          </div>
        </GuideLock>
      </form>
    </section>
  );
}

interface MessageProps {
  message: ChatMessage;
  /** Arrived during this visit: it enters with a short fade instead of popping in. */
  entering: boolean;
  canUndo: boolean;
  undoing: boolean;
  onUndo: () => void;
  /** Answers its questions with a click; only the latest reply's are still open (#153). */
  onAnswer?: (text: string) => void;
  busy: boolean;
  /** Opens "How I found this" instead of folding it. */
  showSteps?: boolean;
}

function Message({
  message,
  entering,
  canUndo,
  undoing,
  onUndo,
  onAnswer,
  busy,
  showSteps = false,
}: MessageProps) {
  const isAgent = message.role === "agent";
  const { note, rest } = isAgent
    ? changeNoteText(message.text, message.profile_changes)
    : { note: null, rest: message.text };
  return (
    <article
      className={`${styles.message} ${isAgent ? styles.agent : styles.user}`}
      data-message-id={message.id}
      data-enter={entering || undefined}
    >
      <p className="visually-hidden">{isAgent ? "Grabbit said:" : "You said:"}</p>
      {note && (
        <GuideLock>
          <ChangeNote note={note} canUndo={canUndo} undoing={undoing} onUndo={onUndo} />
        </GuideLock>
      )}
      {/* A visual answer opens with its own sentence; the text stays as the model's history. */}
      {message.ui ? (
        <div className={styles.visual}>
          <GuideLock>
            <VisualAnswer ui={message.ui} graph={message.graph} />
          </GuideLock>
          {message.walk && <HowIFound walk={message.walk} open={showSteps} />}
        </div>
      ) : (
        rest && (
          <div className={styles.bubble}>
            {isAgent ? <Markdown source={rest} /> : rest}
            {isAgent && message.sources.length > 0 && <ReplySources cited={message.sources} />}
          </div>
        )
      )}
      {isAgent && message.questions.length > 0 && (
        <GuideLock>
          <AgentQuestions questions={message.questions} onAnswer={onAnswer} busy={busy} />
        </GuideLock>
      )}
    </article>
  );
}
