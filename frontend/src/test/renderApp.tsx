import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactElement } from "react";
import { setTransport } from "../api/client";
import { ToastProvider } from "../components/Toast";
import { installTestStreams } from "./fakeEvents";

export type Route = (body: unknown) => unknown;
export type Routes = Record<string, Route | { status: number; body: unknown }>;

/** Serves `routes` keyed by "METHOD /path" instead of the network. */
export function mockApi(routes: Routes) {
  const calls: { key: string; body: unknown }[] = [];
  const streams = installTestStreams();
  setTransport(async (request) => {
    const key = `${request.method} ${new URL(request.url).pathname}`;
    const text = await request.text();
    const body = text ? JSON.parse(text) : undefined;
    calls.push({ key, body });
    const route = routes[key];
    if (!route)
      return new Response(JSON.stringify({ error: { code: "not_found", message: key } }), {
        status: 404,
      });
    if (typeof route === "function")
      return new Response(JSON.stringify(route(body)), { status: 200 });
    return new Response(JSON.stringify(route.body), { status: route.status });
  });
  return Object.assign(calls, { streams });
}

export function renderWithClient(ui: ReactElement) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <ToastProvider>{ui}</ToastProvider>
    </QueryClientProvider>,
  );
}
