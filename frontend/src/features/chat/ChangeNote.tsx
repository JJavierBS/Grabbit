import { FilePenLine, Undo2 } from "lucide-react";
import { Button } from "../../components/Button";
import styles from "./ChangeNote.module.css";

interface ChangeNoteProps {
  note: string;
  canUndo: boolean;
  undoing?: boolean;
  onUndo: () => void;
}

/** The agent's one-line note when it changed the profile, with undo for the newest change. */
export function ChangeNote({ note, canUndo, undoing = false, onUndo }: ChangeNoteProps) {
  return (
    <div className={styles.note}>
      <FilePenLine className={styles.icon} aria-hidden="true" />
      <p className={styles.text}>{note}</p>
      {canUndo && (
        <Button
          variant="secondary"
          size="sm"
          icon={<Undo2 aria-hidden="true" />}
          loading={undoing}
          onClick={onUndo}
        >
          Undo
        </Button>
      )}
    </div>
  );
}
