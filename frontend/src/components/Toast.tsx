import { X } from "lucide-react";
import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import styles from "./Toast.module.css";
import { afterExit } from "./usePresence";

export interface ToastInput {
  title: string;
  description?: string;
  tone?: "default" | "alert";
  /** Extra label row, e.g. the "Simulated event" badge. */
  meta?: ReactNode;
  action?: { label: string; onClick: () => void };
  /** Milliseconds before it closes on its own; null keeps it until dismissed. */
  duration?: number | null;
}

interface ToastItem extends ToastInput {
  id: number;
  /** Dismissed: it plays its exit, then leaves the list. */
  leaving?: boolean;
}

interface ToastApi {
  toast: (input: ToastInput) => number;
  dismiss: (id: number) => void;
}

const ToastContext = createContext<ToastApi | null>(null);
const DEFAULT_DURATION = 8000;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);
  const nextId = useRef(1);

  const dismiss = useCallback((id: number) => {
    setItems((list) => list.map((t) => (t.id === id ? { ...t, leaving: true } : t)));
  }, []);

  const remove = useCallback((id: number) => {
    setItems((list) => list.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback((input: ToastInput) => {
    const id = nextId.current++;
    setItems((list) => [...list, { ...input, id }]);
    return id;
  }, []);

  const api = useMemo(() => ({ toast, dismiss }), [toast, dismiss]);

  return (
    <ToastContext.Provider value={api}>
      {children}
      <section className={styles.region} aria-label="Notifications">
        <ol className={styles.list}>
          {items.map((item) => (
            <ToastCard key={item.id} item={item} onDismiss={dismiss} onGone={remove} />
          ))}
        </ol>
      </section>
    </ToastContext.Provider>
  );
}

interface ToastCardProps {
  item: ToastItem;
  onDismiss: (id: number) => void;
  onGone: (id: number) => void;
}

function ToastCard({ item, onDismiss, onGone }: ToastCardProps) {
  const duration = item.duration === undefined ? DEFAULT_DURATION : item.duration;
  const ref = useRef<HTMLLIElement>(null);

  useEffect(() => {
    if (duration === null || item.leaving) return;
    const timer = setTimeout(() => onDismiss(item.id), duration);
    return () => clearTimeout(timer);
  }, [duration, item.id, item.leaving, onDismiss]);

  // A dismissed toast slides away before it leaves the list.
  useEffect(() => {
    if (!item.leaving) return;
    return afterExit(ref.current, () => onGone(item.id));
  }, [item.leaving, item.id, onGone]);

  const tone = item.tone ?? "default";
  return (
    <li
      ref={ref}
      className={`${styles.toast} ${styles[tone]}`}
      data-state={item.leaving ? "leaving" : undefined}
      aria-hidden={item.leaving || undefined}
    >
      <div
        className={styles.body}
        role={tone === "alert" ? "alert" : "status"}
        aria-live={tone === "alert" ? "assertive" : "polite"}
      >
        {item.meta && <div className={styles.meta}>{item.meta}</div>}
        <p className={styles.title}>{item.title}</p>
        {item.description && <p className={styles.description}>{item.description}</p>}
        {item.action && (
          <button
            type="button"
            className={styles.action}
            onClick={() => {
              item.action?.onClick();
              onDismiss(item.id);
            }}
          >
            {item.action.label}
          </button>
        )}
      </div>
      <button
        type="button"
        className={styles.close}
        aria-label={`Dismiss: ${item.title}`}
        onClick={() => onDismiss(item.id)}
      >
        <X aria-hidden="true" />
      </button>
    </li>
  );
}

export function useToast(): ToastApi {
  const api = useContext(ToastContext);
  if (!api) throw new Error("useToast must be used inside <ToastProvider>");
  return api;
}
