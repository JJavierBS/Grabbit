import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { openEventStream } from "../client";
import type { Alert, Profile } from "../types";
import { keys } from "./queries";

export type StreamStatus = "connecting" | "open" | "retrying";

const CLOSED = 2;
const MAX_BACKOFF_MS = 15_000;

/** Delay before the n-th reconnect attempt (0-based): 1s, 2s, 4s ... capped at 15s. */
export const backoff = (attempt: number) => Math.min(1000 * 2 ** attempt, MAX_BACKOFF_MS);

/**
 * Listens to /api/events (api.md): `alert` adds to the alerts list and calls onAlert,
 * `report` refreshes the report, `profile` replaces the profile. The browser retries a
 * dropped stream itself; when it gives up (CLOSED) this hook opens a new one with backoff.
 */
export function useEvents(onAlert: (alert: Alert) => void): StreamStatus {
  const client = useQueryClient();
  const [status, setStatus] = useState<StreamStatus>("connecting");
  const onAlertRef = useRef(onAlert);
  onAlertRef.current = onAlert;

  useEffect(() => {
    let stream: ReturnType<typeof openEventStream> | null = null;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let attempt = 0;
    let stopped = false;

    const parse = <T>(ev: MessageEvent): T | null => {
      try {
        return JSON.parse(ev.data) as T;
      } catch {
        return null;
      }
    };

    const connect = () => {
      stream = openEventStream("/api/events");
      stream.onopen = () => {
        attempt = 0;
        setStatus("open");
      };
      stream.onerror = () => {
        if (stopped) return;
        setStatus("retrying");
        if (stream?.readyState === CLOSED) {
          stream.close();
          timer = setTimeout(connect, backoff(attempt++));
        }
      };
      stream.addEventListener("alert", (ev) => {
        const alert = parse<Alert>(ev);
        if (!alert) return;
        client.setQueryData<Alert[]>(keys.alerts, (list = []) =>
          list.some((a) => a.id === alert.id) ? list : [alert, ...list],
        );
        onAlertRef.current(alert);
      });
      stream.addEventListener("report", () => {
        client.invalidateQueries({ queryKey: keys.reportsAll });
      });
      stream.addEventListener("profile", (ev) => {
        const profile = parse<Profile>(ev);
        if (profile) client.setQueryData(keys.profile, profile);
        client.invalidateQueries({ queryKey: keys.history });
      });
    };

    connect();
    return () => {
      stopped = true;
      clearTimeout(timer);
      stream?.close();
    };
  }, [client]);

  return status;
}
