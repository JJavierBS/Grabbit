import { FlaskConical } from "lucide-react";
import { useCallback } from "react";
import type { Alert } from "../../api/types";
import { Badge } from "../../components/Badge";
import { useToast } from "../../components/Toast";
import { SIMULATED_LABEL, showDesktopNotification } from "./notify";

export function SimulatedBadge() {
  return (
    <Badge tone="warning" icon={<FlaskConical aria-hidden="true" />}>
      {SIMULATED_LABEL}
    </Badge>
  );
}

/**
 * Delivers one alert: a desktop notification when the tab is hidden (and allowed), and
 * always a toast, so the alert is still on screen when the user comes back.
 */
export function useAlertDelivery(onOpen: (alert: Alert) => void) {
  const { toast } = useToast();
  return useCallback(
    (alert: Alert) => {
      if (document.visibilityState === "hidden")
        showDesktopNotification(alert, () => onOpen(alert));
      toast({
        tone: "alert",
        title: alert.title,
        description: `${alert.entity_name}. ${alert.why_it_matters}`,
        meta: alert.simulated ? <SimulatedBadge /> : undefined,
        action: { label: "Open in chat", onClick: () => onOpen(alert) },
        duration: null,
      });
    },
    [toast, onOpen],
  );
}
