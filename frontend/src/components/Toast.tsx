import { X } from 'lucide-react';
import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import styles from './Toast.module.css';

export interface ToastInput {
  title: string;
  description?: string;
  tone?: 'default' | 'alert';
  /** Extra label row, e.g. the "Simulated event" badge. */
  meta?: ReactNode;
  action?: { label: string; onClick: () => void };
  /** Milliseconds before it closes on its own; null keeps it until dismissed. */
  duration?: number | null;
}

interface ToastItem extends ToastInput {
  id: number;
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
            <ToastCard key={item.id} item={item} onDismiss={dismiss} />
          ))}
        </ol>
      </section>
    </ToastContext.Provider>
  );
}

function ToastCard({ item, onDismiss }: { item: ToastItem; onDismiss: (id: number) => void }) {
  const duration = item.duration === undefined ? DEFAULT_DURATION : item.duration;

  useEffect(() => {
    if (duration === null) return;
    const timer = setTimeout(() => onDismiss(item.id), duration);
    return () => clearTimeout(timer);
  }, [duration, item.id, onDismiss]);

  const tone = item.tone ?? 'default';
  return (
    <li
      className={`${styles.toast} ${styles[tone]}`}
      role={tone === 'alert' ? 'alert' : 'status'}
      aria-live={tone === 'alert' ? 'assertive' : 'polite'}
    >
      <div className={styles.body}>
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
  if (!api) throw new Error('useToast must be used inside <ToastProvider>');
  return api;
}
