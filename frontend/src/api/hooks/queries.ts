import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, api, unwrap } from "../client";
import type { ChatMessage, Report } from "../types";

export const keys = {
  profile: ["profile"] as const,
  history: ["profile", "history"] as const,
  chat: ["chat"] as const,
  /** Prefix of every report query: invalidate it when a report may have changed. */
  reportsAll: ["reports"] as const,
  report: ["reports", "latest"] as const,
  reports: ["reports", "list"] as const,
  alerts: ["alerts"] as const,
};

export const useProfile = () =>
  useQuery({ queryKey: keys.profile, queryFn: () => unwrap(api.GET("/api/profile")) });

export const useProfileHistory = () =>
  useQuery({
    queryKey: keys.history,
    queryFn: () => unwrap(api.GET("/api/profile/history")),
  });

export const useChat = () =>
  useQuery({ queryKey: keys.chat, queryFn: () => unwrap(api.GET("/api/chat")) });

/** The latest report, or null before the first one exists (404 `no_report` is not an error). */
export const useLatestReport = () =>
  useQuery({
    queryKey: keys.report,
    queryFn: async (): Promise<Report | null> => {
      try {
        return await unwrap(api.GET("/api/reports/latest"));
      } catch (error) {
        if (error instanceof ApiError && error.code === "no_report") return null;
        throw error;
      }
    },
  });

/** Past reports, newest first (api.md `GET /api/reports`). */
export const useReports = () =>
  useQuery({ queryKey: keys.reports, queryFn: () => unwrap(api.GET("/api/reports")) });

export const useAlerts = () =>
  useQuery({ queryKey: keys.alerts, queryFn: () => unwrap(api.GET("/api/alerts")) });

/** A chat turn may rewrite the profile and the report, so refresh all three after it. */
function useRefreshAfterTurn() {
  const client = useQueryClient();
  return () =>
    Promise.all([
      client.invalidateQueries({ queryKey: keys.chat }),
      client.invalidateQueries({ queryKey: keys.profile }),
      client.invalidateQueries({ queryKey: keys.reportsAll }),
    ]);
}

export function useSendMessage() {
  const client = useQueryClient();
  const refresh = useRefreshAfterTurn();
  return useMutation({
    mutationFn: (text: string) => unwrap(api.POST("/api/chat", { body: { text } })),
    onMutate: async (text) => {
      await client.cancelQueries({ queryKey: keys.chat });
      const pending: ChatMessage = {
        id: `pending-${Date.now()}`,
        role: "user",
        report_id: null,
        ui: null,
        text,
        created_at: new Date().toISOString(),
        profile_changes: [],
      };
      client.setQueryData<ChatMessage[]>(keys.chat, (list = []) => [...list, pending]);
    },
    onSettled: refresh,
  });
}

export function useUndo() {
  const client = useQueryClient();
  const refresh = useRefreshAfterTurn();
  return useMutation({
    mutationFn: () => unwrap(api.POST("/api/profile/undo")),
    onSuccess: (profile) => client.setQueryData(keys.profile, profile),
    onSettled: refresh,
  });
}

export function useRunReport() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (kind: Report["kind"]) => unwrap(api.POST("/api/reports/run", { body: { kind } })),
    onSuccess: (report) => {
      client.setQueryData(keys.report, report);
      void client.invalidateQueries({ queryKey: keys.reports });
    },
  });
}

/** Demo trigger: a scripted change through the real watcher path (api.md, DEMO_MODE=1 only). */
export function useSimulateEvent() {
  return useMutation({
    mutationFn: (fixture: string) =>
      unwrap(api.POST("/api/demo/simulate-event", { body: { fixture } })),
  });
}
