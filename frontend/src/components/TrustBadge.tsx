import { Building2, CircleDashed, Database, Globe, Landmark, Newspaper } from 'lucide-react';
import type { TrustLevel } from '../api/types';
import styles from './TrustBadge.module.css';

export const TRUST_LABELS: Record<TrustLevel, string> = {
  filing: 'Official filing',
  primary: 'Company or investor',
  press: 'Press',
  aggregator: 'Database',
  web_unverified: 'Web, unverified',
  not_published: 'Not published',
};

const ICONS = {
  filing: Landmark,
  primary: Building2,
  press: Newspaper,
  aggregator: Database,
  web_unverified: Globe,
  not_published: CircleDashed,
} satisfies Record<TrustLevel, unknown>;

interface TrustBadgeProps {
  level: TrustLevel;
  sourceName?: string;
  /** Opens the source in a new tab. Ignored for `not_published`. */
  href?: string | null;
  /** Hides the text label on dense rows; the label stays in the accessible name. */
  compact?: boolean;
}

export function TrustBadge({ level, sourceName, href, compact = false }: TrustBadgeProps) {
  const Icon = ICONS[level];
  const label = TRUST_LABELS[level];
  const title = sourceName ? `${label}: ${sourceName}` : label;
  const content = (
    <>
      <Icon className={styles.icon} aria-hidden="true" strokeWidth={2} />
      <span className={compact ? 'visually-hidden' : undefined}>{label}</span>
    </>
  );
  const className = `${styles.badge} ${styles[level]}`;

  if (href && level !== 'not_published') {
    return (
      <a
        className={`${className} ${styles.link}`}
        data-trust={level}
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        title={title}
      >
        {content}
      </a>
    );
  }
  return (
    <span className={className} data-trust={level} title={title}>
      {content}
    </span>
  );
}
