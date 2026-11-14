import { forwardRef, type InputHTMLAttributes, type TextareaHTMLAttributes, useId } from "react";
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
  { label, hideLabel, hint, error, id, className, ...rest },
  ref,
) {
  const { fieldId, describedBy } = useFieldIds(id, hint, error);
  return (
    <FieldFrame fieldId={fieldId} label={label} hideLabel={hideLabel} hint={hint} error={error}>
      <textarea
        ref={ref}
        id={fieldId}
        className={[styles.control, styles.multiline, className].filter(Boolean).join(" ")}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        {...rest}
      />
    </FieldFrame>
  );
});
