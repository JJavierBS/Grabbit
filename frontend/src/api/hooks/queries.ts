import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../client';
import type { Alert, ChatMessage, Profile, ProfileChange, Report } from '../types';

export const keys = {
  profile: ['profile'] as const,
  history: ['profile', 'history'] as const,
  chat: ['chat'] as const,
  /** Prefix of every report query: invalidate it when a report may have changed. */
  reportsAll: ['reports'] as const,
  report: ['reports', 'latest'] as const,
  reports: ['reports', 'list'] as const,
  alerts: ['alerts'] as const,
};

export const useProfile = () =>
  useQuery({ queryKey: keys.profile, queryFn: () => api.get<Profile>('/api/profile') });

export const useProfileHistory = () =>
  useQuery({
    queryKey: keys.history,
    queryFn: () => api.get<ProfileChange[]>('/api/profile/history'),
  });

export const useChat = () =>
  useQuery({ queryKey: keys.chat, queryFn: () => api.get<ChatMessage[]>('/api/chat') });

export const useLatestReport = () =>
  useQuery({ queryKey: keys.report, queryFn: () => api.get<Report>('/api/reports/latest') });

/** Past reports, newest first (api.md `GET /api/reports`). */
export const useReports = () =>
  useQuery({ queryKey: keys.reports, queryFn: () => api.get<Report[]>('/api/reports') });

export const useAlerts = () =>
  useQuery({ queryKey: keys.alerts, queryFn: () => api.get<Alert[]>('/api/alerts') });

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
    mutationFn: (text: string) => api.post<ChatMessage>('/api/chat', { text }),
    onMutate: async (text) => {
      await client.cancelQueries({ queryKey: keys.chat });
      const pending: ChatMessage = {
        id: `pending-${Date.now()}`,
        role: 'user',
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
    mutationFn: () => api.post<Profile>('/api/profile/undo'),
    onSuccess: (profile) => client.setQueryData(keys.profile, profile),
    onSettled: refresh,
  });
}

export function useRunReport() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (kind: Report['kind']) => api.post<Report>('/api/reports/run', { kind }),
    onSuccess: (report) => {
      client.setQueryData(keys.report, report);
      void client.invalidateQueries({ queryKey: keys.reports });
    },
  });
}

/** Demo trigger: a scripted change through the real watcher path (api.md, DEMO_MODE=1 only). */
export function useSimulateEvent() {
  return useMutation({
    mutationFn: (fixture: string) => api.post<Alert>('/api/demo/simulate-event', { fixture }),
  });
}
