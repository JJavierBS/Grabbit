import {
  type ForwardedRef,
  forwardRef,
  type InputHTMLAttributes,
  type TextareaHTMLAttributes,
  useCallback,
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
} from "react";
import styles from "./Input.module.css";

interface FieldProps {
  label: string;
  /** Keeps the label for screen readers only, e.g. a chat composer. */
  hideLabel?: boolean;
  hint?: string;
  error?: string;
}

type InputProps = FieldProps & InputHTMLAttributes<HTMLInputElement>;
type TextAreaProps = FieldProps & TextareaHTMLAttributes<HTMLTextAreaElement>;

function useFieldIds(id: string | undefined, hint?: string, error?: string) {
  const auto = useId();
  const fieldId = id ?? auto;
  const describedBy =
    [error ? `${fieldId}-error` : null, hint ? `${fieldId}-hint` : null]
      .filter(Boolean)
      .join(" ") || undefined;
  return { fieldId, describedBy };
}

function FieldFrame({
  fieldId,
  label,
  hideLabel,
  hint,
  error,
  children,
}: FieldProps & { fieldId: string; children: React.ReactNode }) {
  return (
    <div className={styles.field}>
      <label htmlFor={fieldId} className={hideLabel ? "visually-hidden" : styles.label}>
        {label}
      </label>
      {children}
      {hint && !error && (
        <p id={`${fieldId}-hint`} className={styles.hint}>
          {hint}
        </p>
      )}
      {error && (
        <p id={`${fieldId}-error`} className={styles.error} role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

// The field takes its height from its text, or from its placeholder while empty, in JS:
// `field-sizing: content` is missing before Safari 26.2 and from 26.2 on still clips a
// wrapped placeholder, so the one-row composer scrolled inside itself on iPhone (#218).
function useAutoGrow(
  forwarded: ForwardedRef<HTMLTextAreaElement>,
  value: TextAreaProps["value"],
  placeholder: string | undefined,
) {
  const own = useRef<HTMLTextAreaElement | null>(null);
  const ref = useCallback(
    (node: HTMLTextAreaElement | null) => {
      own.current = node;
      if (typeof forwarded === "function") forwarded(node);
      else if (forwarded) forwarded.current = node;
    },
    [forwarded],
  );
  const grow = useCallback(() => {
    const el = own.current;
    if (!el) return;
    const empty = el.value === "";
    if (empty) el.value = el.placeholder;
    el.style.height = "auto";
    const { borderTopWidth, borderBottomWidth } = getComputedStyle(el);
    const borders = (parseFloat(borderTopWidth) || 0) + (parseFloat(borderBottomWidth) || 0);
    el.style.height = `${el.scrollHeight + borders}px`;
    if (empty) el.value = "";
  }, []);
  // biome-ignore lint/correctness/useExhaustiveDependencies: re-measure when the text or placeholder changes.
  useLayoutEffect(grow, [grow, value, placeholder]);
  // A new width (web font loaded, rotation, sidebar) re-wraps the text.
  useEffect(() => {
    const el = own.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    let width = el.clientWidth;
    const observer = new ResizeObserver(() => {
      if (el.clientWidth === width) return;
      width = el.clientWidth;
      grow();
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, [grow]);
  return { ref, grow };
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, hideLabel, hint, error, id, className, ...rest },
  ref,
) {
  const { fieldId, describedBy } = useFieldIds(id, hint, error);
  return (
    <FieldFrame fieldId={fieldId} label={label} hideLabel={hideLabel} hint={hint} error={error}>
      <input
        ref={ref}
        id={fieldId}
        className={[styles.control, className].filter(Boolean).join(" ")}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        {...rest}
      />
    </FieldFrame>
  );
});

export const TextArea = forwardRef<HTMLTextAreaElement, TextAreaProps>(function TextArea(
  { label, hideLabel, hint, error, id, className, onInput, ...rest },
  forwarded,
) {
  const { fieldId, describedBy } = useFieldIds(id, hint, error);
  const { ref, grow } = useAutoGrow(forwarded, rest.value, rest.placeholder);
  return (
    <FieldFrame fieldId={fieldId} label={label} hideLabel={hideLabel} hint={hint} error={error}>
      <textarea
        ref={ref}
        onInput={(e) => {
          grow();
          onInput?.(e);
        }}
        id={fieldId}
        className={[styles.control, styles.multiline, className].filter(Boolean).join(" ")}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        {...rest}
      />
    </FieldFrame>
  );
});
