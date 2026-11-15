import styles from "./TranslationNote.module.css";

const names = new Intl.DisplayNames(["en"], { type: "language" });

export function languageName(code: string): string {
  try {
    return names.of(code) ?? code;
  } catch {
    return code;
  }
}

interface TranslationNoteProps {
  /** ISO 639-1 code of the text as its source wrote it. */
  language: string;
  showingOriginal: boolean;
  onToggle: () => void;
}

/** Says a third-party text was translated into the profile language, and shows the source text on demand. */
export function TranslationNote({ language, showingOriginal, onToggle }: TranslationNoteProps) {
  return (
    <p className={styles.note}>
      <span>Translated from {languageName(language)}</span>
      <button
        type="button"
        className={styles.toggle}
        aria-pressed={showingOriginal}
        onClick={onToggle}
      >
        {showingOriginal ? "Show translation" : "Show original"}
      </button>
    </p>
  );
}
