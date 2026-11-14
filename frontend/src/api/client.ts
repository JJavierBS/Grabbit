import createClient from "openapi-fetch";
import type { components, paths } from "./schema";

type ErrorBody = components["schemas"]["ErrorResponse"];

/** Error from any `/api/*` call, with the backend's `{error: {code, message}}` shape. */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

/** Sends one request. The dev-only fake API and the tests swap it out (src/dev/fakeApi.ts). */
export type Transport = (request: Request) => Promise<Response>;

let transport: Transport = (request) => globalThis.fetch(request);

export function setTransport(next: Transport) {
  transport = next;
}

/** The single API client. Same origin: Vite proxies `/api` locally, FastAPI serves it deployed. */
export const api = createClient<paths>({
  baseUrl: globalThis.location?.origin ?? "",
  // Resolved per call so tests and the fake API can swap the transport after import.
  fetch: async (request) => {
    try {
      return await transport(request);
    } catch {
      throw new ApiError(
        0,
        "network_error",
        "Grabbit cannot reach its server. Check that it is running.",
      );
    }
  },
});

function isErrorBody(body: unknown): body is ErrorBody {
  return typeof body === "object" && body !== null && "error" in body;
}

/** Returns `data` or throws `ApiError`; use it inside query functions. */
export async function unwrap<T>(
  call: Promise<{ data?: T; error?: unknown; response: Response }>,
): Promise<T> {
  const { data, error, response } = await call;
  if (error !== undefined || data === undefined) {
    if (isErrorBody(error)) {
      throw new ApiError(response.status, error.error.code, error.error.message);
    }
    throw new ApiError(response.status, "http_error", `The server answered ${response.status}.`);
  }
  return data;
}

/**
 * GET for a path the generated schema does not have yet.
 * shortcut: untyped, only for `GET /api/reports` until the backend serves it (#54) and
 * `make gen-api` adds it to schema.ts; then switch the caller to `api.GET`.
 */
export async function getUntyped<T>(path: string): Promise<T> {
  const origin = globalThis.location?.origin ?? "http://localhost";
  return unwrap(
    (async () => {
      const response = await transport(new Request(new URL(path, origin)));
      const body = await response.json().catch(() => undefined);
      return response.ok ? { data: body as T, response } : { error: body, response };
    })(),
  );
}

/** The subset of EventSource the app uses, so tests and the fake API can stand in for it. */
export interface EventStream {
  readonly readyState: number;
  onopen: ((ev: Event) => unknown) | null;
  onerror: ((ev: Event) => unknown) | null;
  addEventListener(type: string, listener: (ev: MessageEvent) => void): void;
  close(): void;
}

let streamFactory: (url: string) => EventStream = (url) => new EventSource(url);

export function setEventStreamFactory(next: (url: string) => EventStream) {
  streamFactory = next;
}

export const openEventStream = (url: string) => streamFactory(url);
