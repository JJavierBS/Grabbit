import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { act, renderHook } from '@testing-library/react';
import type { ReactNode } from 'react';
import { profileV2 } from '../../dev/fixtures';
import { installTestStreams } from '../../test/fakeEvents';
import type { Alert } from '../types';
import { keys } from './queries';
import { backoff, useEvents } from './useEvents';

const alert: Alert = {
  id: 'al-1',
  created_at: '2026-11-14T10:00:00Z',
  entity_id: 'c-northwind',
  entity_name: 'Northwind Labs',
  kind: 'new_round',
  title: 'Northwind Labs is raising',
  why_it_matters: 'A reference investor leads it.',
  importance: 0.9,
  facts: [],
  simulated: true,
};

function setup() {
  const streams = installTestStreams();
  const client = new QueryClient();
  const onAlert = vi.fn();
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  const hook = renderHook(() => useEvents(onAlert), { wrapper });
  return { streams, client, onAlert, hook };
}

describe('useEvents', () => {
  afterEach(() => vi.useRealTimers());

  it('opens /api/events and reports when it is live', () => {
    const { streams, hook } = setup();
    expect(streams[0].url).toBe('/api/events');
    expect(hook.result.current).toBe('connecting');
    streams[0].open();
    expect(hook.result.current).toBe('open');
  });

  it('adds an alert to the alerts list once and calls onAlert', () => {
    const { streams, client, onAlert } = setup();
    streams[0].push('alert', alert);
    streams[0].push('alert', alert);
    expect(client.getQueryData(keys.alerts)).toEqual([alert]);
    expect(onAlert).toHaveBeenCalledTimes(2);
    expect(onAlert).toHaveBeenCalledWith(alert);
  });

  it('refreshes the report and replaces the profile on their events', () => {
    const { streams, client } = setup();
    const spy = vi.spyOn(client, 'invalidateQueries');
    streams[0].push('report', { id: 'rep-9' });
    expect(spy).toHaveBeenCalledWith({ queryKey: keys.reportsAll });
    streams[0].push('profile', { ...profileV2, version: 7 });
    expect(client.getQueryData<{ version: number }>(keys.profile)?.version).toBe(7);
  });

  it('ignores a malformed event instead of crashing', () => {
    const { streams, onAlert } = setup();
    act(() => {
      // biome-ignore lint/suspicious/noExplicitAny: reach the private listener with bad data.
      (streams[0] as any).listeners.get('alert')[0](new MessageEvent('alert', { data: '{oops' }));
    });
    expect(onAlert).not.toHaveBeenCalled();
  });

  it('reconnects with backoff after the browser gives up', () => {
    vi.useFakeTimers();
    const { streams, hook } = setup();
    streams[0].open();
    streams[0].drop();
    expect(hook.result.current).toBe('retrying');
    expect(streams[0].closed).toBe(true);
    expect(streams).toHaveLength(1);
    act(() => vi.advanceTimersByTime(backoff(0)));
    expect(streams).toHaveLength(2);
    streams[1].open();
    expect(hook.result.current).toBe('open');
  });

  it('closes the stream on unmount', () => {
    const { streams, hook } = setup();
    hook.unmount();
    expect(streams[0].closed).toBe(true);
  });

  it('caps the backoff', () => {
    expect([0, 1, 2, 10].map(backoff)).toEqual([1000, 2000, 4000, 15000]);
  });
});
