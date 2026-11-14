import type { ApiErrorBody } from './types';

/** An error answer from the API, in the shape of api.md ("error": {code, message}). */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

type Transport = (path: string, init?: RequestInit) => Promise<Response>;

// The dev-only fake backend replaces fetch when VITE_FAKE_API=1 (see src/dev/fakeApi.ts).
let transport: Transport = (path, init) => fetch(path, init);

export function setTransport(next: Transport) {
  transport = next;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await transport(path, {
      ...init,
      headers: {
        Accept: 'application/json',
        ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
      },
    });
  } catch {
    throw new ApiError(
      0,
      'network_error',
      'Grabbit cannot reach its server. Check that it is running.',
    );
  }
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const error = (body as ApiErrorBody | null)?.error;
    throw new ApiError(
      response.status,
      error?.code ?? 'http_error',
      error?.message ?? `The server answered ${response.status}.`,
    );
  }
  return body as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, data?: unknown) =>
    request<T>(path, {
      method: 'POST',
      body: data === undefined ? undefined : JSON.stringify(data),
    }),
};
