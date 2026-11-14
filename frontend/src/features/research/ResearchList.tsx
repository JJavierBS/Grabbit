import { SquarePen } from "lucide-react";
import type { Research } from "../../api/workspace";
import { Button } from "../../components/Button";
import { dayLabel } from "../report/ReportSidebar";
import styles from "../report/ReportSidebar.module.css";
import own from "./ResearchList.module.css";

export const UNTITLED = "New research";

interface Props {
  current: string;
  list: Research[];
  onNew: () => void;
  onOpen: (id: string) => void;
}

/**
 * "New research" and this browser's researches (#145): each one a thesis with its own chat,
 * profile, reports and alerts. Shown above the current research's reports.
 */
export function ResearchList({ current, list, onNew, onOpen }: Props) {
  return (
    <>
      <Button
        variant="secondary"
        size="sm"
        className={own.new}
        icon={<SquarePen aria-hidden="true" />}
        onClick={onNew}
      >
        New research
      </Button>
      {list.length > 1 && (
        <nav className={own.research} aria-labelledby="research-title">
          <h2 id="research-title" className={styles.heading}>
            Research
          </h2>
          <ul className={styles.list}>
            {list.map((r) => (
              <li key={r.id}>
                <button
                  type="button"
                  className={styles.item}
                  aria-current={r.id === current ? "true" : undefined}
                  title={r.title ?? UNTITLED}
                  onClick={() => onOpen(r.id)}
                >
                  <span className={styles.summary}>{r.title ?? UNTITLED}</span>
                  <span className={styles.meta}>{dayLabel(r.created_at)}</span>
                </button>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </>
  );
}
