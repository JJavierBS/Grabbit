import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./styles/base.css";
import { App, Grabbit } from "./App";
import { setEventStreamFactory, setTransport } from "./api/client";
import { ToastProvider } from "./components/Toast";
import { Gallery } from "./design/Gallery";
import { DemoRoot } from "./features/demo/DemoRoot";

if (import.meta.env.VITE_FAKE_API === "1") {
  const fake = (await import("./dev/fakeApi")).devFakeApi();
  setTransport(fake.transport);
  setEventStreamFactory(fake.openStream);
}

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
});

const root = document.getElementById("root");
if (!root) throw new Error("Missing #root element");

createRoot(root).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        {new URLSearchParams(location.search).has("gallery") ? (
          <Gallery />
        ) : (
          <DemoRoot demo={<App />}>
            <Grabbit />
          </DemoRoot>
        )}
      </ToastProvider>
    </QueryClientProvider>
  </StrictMode>,
);
