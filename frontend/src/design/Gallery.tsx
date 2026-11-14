import { Bell, Send } from "lucide-react";
import type { TrustLevel } from "../api/types";
import { Badge } from "../components/Badge";
import { Button } from "../components/Button";
import { Card } from "../components/Card";
import { Input, TextArea } from "../components/Input";
import { Skeleton } from "../components/Skeleton";
import { useToast } from "../components/Toast";
import { TrustBadge } from "../components/TrustBadge";
import styles from "./Gallery.module.css";

const LEVELS: TrustLevel[] = [
  "filing",
  "primary",
  "press",
  "aggregator",
  "web_unverified",
  "not_published",
];

/** Living reference of the base components, at /?gallery once the app exists. */
export function Gallery() {
  const { toast } = useToast();
  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Grabbit design system</h1>
        <p className={styles.lead}>
          Base components in the warm, sourced tone of the event. Every fact carries its trust.
        </p>
      </header>

      <Card as="section" padding="lg" className={styles.section}>
        <h2 className={styles.h2}>Trust scale</h2>
        <div className={styles.row}>
          {LEVELS.map((level) => (
            <TrustBadge key={level} level={level} sourceName="Example source" />
          ))}
        </div>
        <div className={styles.row}>
          {LEVELS.map((level) => (
            <TrustBadge key={level} level={level} compact />
          ))}
        </div>
      </Card>

      <Card as="section" padding="lg" className={styles.section}>
        <h2 className={styles.h2}>Actions</h2>
        <div className={styles.row}>
          <Button icon={<Send aria-hidden="true" />}>Send</Button>
          <Button variant="secondary">Undo last change</Button>
          <Button variant="ghost">Profile history</Button>
          <Button loading>Rewriting</Button>
          <Button disabled>Disabled</Button>
          <Button size="sm" variant="secondary">
            Small
          </Button>
        </div>
        <div className={styles.row}>
          <Badge>Seed</Badge>
          <Badge tone="ink">Lead</Badge>
          <Badge tone="info">Likely to raise</Badge>
          <Badge tone="warning">Simulated event</Badge>
          <Badge tone="danger">Error</Badge>
        </div>
      </Card>

      <Card as="section" padding="lg" className={styles.section}>
        <h2 className={styles.h2}>Fields</h2>
        <div className={styles.grid}>
          <Input
            label="Thesis"
            placeholder="Nordic B2B climate software, pre-seed"
            hint="One sentence is enough."
          />
          <Input label="Ticket" defaultValue="abc" error="Use a number, for example 25000." />
          <TextArea label="Message" placeholder="Shorter, co-investors first" />
        </div>
      </Card>

      <Card as="section" padding="lg" className={styles.section}>
        <h2 className={styles.h2}>Feedback</h2>
        <div className={styles.row}>
          <Button
            variant="secondary"
            onClick={() =>
              toast({ title: "Report rewritten", description: "Co-investors now lead." })
            }
          >
            Show toast
          </Button>
          <Button
            icon={<Bell aria-hidden="true" />}
            onClick={() =>
              toast({
                tone: "alert",
                title: "Northwind Labs raised a seed round",
                description: "Led by an investor you trust.",
                meta: <Badge tone="warning">Simulated event</Badge>,
                action: { label: "Open in chat", onClick: () => undefined },
                duration: null,
              })
            }
          >
            Show alert
          </Button>
        </div>
        <div className={styles.grid}>
          <Skeleton block="title" />
          <Skeleton lines={3} />
          <Skeleton block="card" />
        </div>
      </Card>
    </main>
  );
}
