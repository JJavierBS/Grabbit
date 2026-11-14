import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactElement } from "react";
import { vi } from "vitest";

export function renderWithQuery(ui: ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>);
}

/** Stubs `fetch` so each `/api` path answers with the given JSON body and status. */
export function stubApi(routes: Record<string, { status?: number; body: unknown }>) {
  const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
    const url = new URL(input instanceof Request ? input.url : String(input));
    const route = routes[url.pathname];
    if (!route)
      return Response.json(
        { error: { code: "not_found", message: url.pathname } },
        { status: 404 },
      );
    return Response.json(route.body, { status: route.status ?? 200 });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}
