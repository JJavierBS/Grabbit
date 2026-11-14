import { ArrowUp, Mic, RefreshCw, Square } from 'lucide-react';
import {
  type FormEvent,
  type KeyboardEvent,
  type ReactNode,
  useEffect,
  useRef,
  useState,
} from 'react';
import { useChat, useProfile, useSendMessage, useUndo } from '../../api/hooks/queries';
import type { ChatMessage } from '../../api/types';
import { Button } from '../../components/Button';
import { TextArea } from '../../components/Input';
import { Skeleton } from '../../components/Skeleton';
import styles from './ChatPanel.module.css';
import { ChangeNote } from './ChangeNote';
import { changeNoteText, isUndoable } from './noteText';
import { useDictation } from './useDictation';

const SUGGESTIONS = ['Shorter, co-investors first', 'Drop consumer health'];

interface ChatPanelProps {
  /** Extra items rendered after the messages, e.g. an alert opened from a notification. */
  footer?: ReactNode;
}

export function ChatPanel({ footer }: ChatPanelProps) {
  const chat = useChat();
  const profile = useProfile();
  const send = useSendMessage();
  const undo = useUndo();
  const [draft, setDraft] = useState('');
  const dictation = useDictation(setDraft);
  const endRef = useRef<HTMLDivElement>(null);
  const messages = chat.data ?? [];

  // biome-ignore lint/correctness/useExhaustiveDependencies: scroll on every new message or footer.
  useEffect(() => {
    endRef.current?.scrollIntoView?.({ block: 'end' });
  }, [messages.length, send.isPending, footer]);

  const submit = (text: string) => {
    const value = text.trim();
    if (!value || send.isPending) return;
    if (dictation.listening) dictation.toggle('');
    send.mutate(value, { onSuccess: () => setDraft('') });
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    submit(draft);
  };

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
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
      <div className={styles.log} role="log" aria-live="polite" aria-busy={chat.isPending}>
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
        {chat.isSuccess && messages.length === 0 && (
          <p className={styles.empty}>
            Tell Grabbit what you look for at Slush 2026, however vague. It asks two or three
            questions backed by data, then writes your prep report.
          </p>
        )}
        {messages.map((m) => (
          <Message
            key={m.id}
            message={m}
            canUndo={isUndoable(m.profile_changes, profile.data?.version)}
            undoing={undo.isPending}
            onUndo={() => undo.mutate()}
          />
        ))}
        {send.isPending && (
          <p className={styles.thinking} role="status">
            Grabbit is reading your message and checking the report…
          </p>
        )}
        {footer}
        <div ref={endRef} />
      </div>

      <form className={styles.composer} onSubmit={onSubmit}>
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
        <div className={styles.suggestions}>
          {SUGGESTIONS.map((s) => (
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
        <div className={styles.inputRow}>
          <TextArea
            label="Message Grabbit"
            hideLabel
            placeholder={
              dictation.listening
                ? 'Listening… press Stop when you are done'
                : 'Correct the report or ask a question'
            }
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={onKeyDown}
            rows={1}
          />
          {dictation.supported && (
            <Button
              variant={dictation.listening ? 'primary' : 'ghost'}
              aria-label={dictation.listening ? 'Stop talking' : 'Talk'}
              aria-pressed={dictation.listening}
              className={styles.talk}
              onClick={() => dictation.toggle(draft)}
              icon={
                dictation.listening ? <Square aria-hidden="true" /> : <Mic aria-hidden="true" />
              }
            />
          )}
          <Button
            type="submit"
            aria-label="Send"
            className={styles.send}
            loading={send.isPending}
            disabled={!draft.trim()}
            icon={<ArrowUp aria-hidden="true" />}
          />
        </div>
      </form>
    </section>
  );
}

interface MessageProps {
  message: ChatMessage;
  canUndo: boolean;
  undoing: boolean;
  onUndo: () => void;
}

function Message({ message, canUndo, undoing, onUndo }: MessageProps) {
  const isAgent = message.role === 'agent';
  const { note, rest } = isAgent
    ? changeNoteText(message.text, message.profile_changes)
    : { note: null, rest: message.text };
  return (
    <article className={`${styles.message} ${isAgent ? styles.agent : styles.user}`}>
      <p className="visually-hidden">{isAgent ? 'Grabbit said:' : 'You said:'}</p>
      {note && <ChangeNote note={note} canUndo={canUndo} undoing={undoing} onUndo={onUndo} />}
      {rest && <p className={styles.bubble}>{rest}</p>}
    </article>
  );
}
