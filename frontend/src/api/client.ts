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

/** The single API client. Same origin: Vite proxies `/api` locally, FastAPI serves it deployed. */
export const api = createClient<paths>({
  baseUrl: globalThis.location?.origin ?? "",
  // Resolved per call so tests can stub `fetch` after import.
  fetch: (request) => globalThis.fetch(request),
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
    throw new ApiError(response.status, "http_error", `Request failed (${response.status})`);
  }
  return data;
}
