import { QueryClient, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, unwrap } from "./client";
import type { ReportKind } from "./types";

export const queryKeys = {
  health: ["health"],
  profile: ["profile"],
  profileHistory: ["profile", "history"],
  chat: ["chat"],
  latestReport: ["reports", "latest"],
  alerts: ["alerts"],
} as const;

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
  });
}

export const useHealth = () =>
  useQuery({ queryKey: queryKeys.health, queryFn: () => unwrap(api.GET("/api/health")) });

export const useProfile = () =>
  useQuery({ queryKey: queryKeys.profile, queryFn: () => unwrap(api.GET("/api/profile")) });

export const useProfileHistory = () =>
  useQuery({
    queryKey: queryKeys.profileHistory,
    queryFn: () => unwrap(api.GET("/api/profile/history")),
  });

export const useChat = () =>
  useQuery({ queryKey: queryKeys.chat, queryFn: () => unwrap(api.GET("/api/chat")) });

export const useLatestReport = () =>
  useQuery({
    queryKey: queryKeys.latestReport,
    queryFn: () => unwrap(api.GET("/api/reports/latest")),
  });

export const useAlerts = () =>
  useQuery({ queryKey: queryKeys.alerts, queryFn: () => unwrap(api.GET("/api/alerts")) });

export function useSendChat() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (text: string) => unwrap(api.POST("/api/chat", { body: { text } })),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.chat }),
  });
}

export function useRunReport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (kind: ReportKind) => unwrap(api.POST("/api/reports/run", { body: { kind } })),
    onSuccess: (report) => queryClient.setQueryData(queryKeys.latestReport, report),
  });
}
