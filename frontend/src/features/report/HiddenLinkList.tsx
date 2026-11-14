import type { HiddenLink } from "../../api/types";
import { FactValue } from "../../components/FactValue";
import { TrustBadge } from "../../components/TrustBadge";
import styles from "./HiddenLinkList.module.css";

/** "FIRSTPICK co-invested 2× with 500 Global": the investor it branches from, then the link. */
export function linkTitle(link: HiddenLink): string {
  const via = link.nodes.find((n) => n.entity_id === link.via_entity_id);
  return via ? `${via.name} ${link.label}` : link.label;
}

/** Each hidden link with its explanation, the rounds that prove it and their trust. */
export function HiddenLinkList({ links }: { links: HiddenLink[] }) {
  return (
    <ul className={styles.list}>
      {links.map((link) => (
        <li
          key={`${link.kind}:${link.via_entity_id}:${link.target.entity_id}`}
          className={styles.item}
        >
          <div className={styles.head}>
            <span className={styles.title}>{linkTitle(link)}</span>
            <TrustBadge level={link.trust} />
          </div>
          <p className={styles.explanation}>{link.explanation}</p>
          {link.facts.length > 0 && (
            <p className={styles.facts}>
              {link.facts.map((f, i) => (
                // biome-ignore lint/suspicious/noArrayIndexKey: facts have no id and never reorder here.
                <FactValue key={i} inline fact={f} />
              ))}
            </p>
          )}
        </li>
      ))}
    </ul>
  );
}
