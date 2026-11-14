import { act } from '@testing-library/react';
import { type EventStream, setEventStreamFactory } from '../api/client';

/** A controllable EventSource for tests: open, push events, drop the connection. */
export class TestStream implements EventStream {
  readyState = 0;
  onopen: ((ev: Event) => unknown) | null = null;
  onerror: ((ev: Event) => unknown) | null = null;
  closed = false;
  private listeners = new Map<string, ((ev: MessageEvent) => void)[]>();

  constructor(readonly url: string) {}

  addEventListener(type: string, listener: (ev: MessageEvent) => void) {
    this.listeners.set(type, [...(this.listeners.get(type) ?? []), listener]);
  }

  close() {
    this.closed = true;
    this.readyState = 2;
  }

  open() {
    act(() => {
      this.readyState = 1;
      this.onopen?.(new Event('open'));
    });
  }

  push(type: string, data: unknown) {
    act(() => {
      const ev = new MessageEvent(type, { data: JSON.stringify(data) });
      for (const l of this.listeners.get(type) ?? []) l(ev);
    });
  }

  /** The server went away and the browser gave up (readyState CLOSED). */
  drop() {
    act(() => {
      this.readyState = 2;
      this.onerror?.(new Event('error'));
    });
  }
}

/** Routes every new stream to a list the test can inspect. */
export function installTestStreams(): TestStream[] {
  const streams: TestStream[] = [];
  setEventStreamFactory((url) => {
    const s = new TestStream(url);
    streams.push(s);
    return s;
  });
  return streams;
}
