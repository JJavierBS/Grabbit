import { act, render, renderHook, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import type { Alert } from "../../api/types";
import { ToastProvider } from "../../components/Toast";
import { AlertCard } from "./AlertCard";
import { askNotificationPermission, notificationText } from "./notify";
import { useAlertDelivery } from "./useAlertDelivery";

const alert = (simulated: boolean): Alert => ({
  id: "al-1",
  created_at: "2026-11-14T10:00:00Z",
  entity_id: "c-northwind",
  entity_name: "Northwind Labs",
  kind: "new_round",
  title: "Northwind Labs is raising a Series A",
  why_it_matters: "Aurora Ventures leads it.",
  importance: 0.9,
  facts: [
    {
      value: 8_000_000,
      unit: "EUR",
      trust: "press",
      sources: [
        {
          name: "Arctic Startup Daily",
          url: "https://example.com",
          date: null,
          date_precision: null,
          rank: "press",
        },
      ],
    },
  ],
  simulated,
});

class FakeNotification {
  static permission: NotificationPermission = "granted";
  static requestPermission = vi.fn(async () => FakeNotification.permission);
  static created: FakeNotification[] = [];
  onclick: (() => void) | null = null;
  readonly title: string;
  readonly options: NotificationOptions;
  constructor(title: string, options: NotificationOptions) {
    this.title = title;
    this.options = options;
    FakeNotification.created.push(this);
  }
  close() {}
}

function setVisibility(state: DocumentVisibilityState) {
  Object.defineProperty(document, "visibilityState", { configurable: true, get: () => state });
}

describe("alerts", () => {
  beforeEach(() => {
    FakeNotification.created = [];
    FakeNotification.permission = "granted";
    FakeNotification.requestPermission.mockClear();
    vi.stubGlobal("Notification", FakeNotification);
  });
  afterEach(() => {
    vi.unstubAllGlobals();
    setVisibility("visible");
  });

  const wrapper = ({ children }: { children: ReactNode }) => (
    <ToastProvider>{children}</ToastProvider>
  );

  it("shows a toast with the simulated label and opens the alert from it", async () => {
    const onOpen = vi.fn();
    const { result } = renderHook(() => useAlertDelivery(onOpen), { wrapper });
    act(() => result.current(alert(true)));
    expect(screen.getByRole("alert")).toHaveTextContent("Northwind Labs is raising a Series A");
    expect(screen.getByText("Simulated event")).toBeInTheDocument();
    expect(FakeNotification.created).toHaveLength(0);
    await userEvent.click(screen.getByRole("button", { name: "Open in chat" }));
    expect(onOpen).toHaveBeenCalledWith(alert(true));
  });

  it("has no simulated label for a real alert", () => {
    const { result } = renderHook(() => useAlertDelivery(vi.fn()), { wrapper });
    act(() => result.current(alert(false)));
    expect(screen.queryByText("Simulated event")).not.toBeInTheDocument();
  });

  it("sends a desktop notification when the tab is hidden, and clicking it opens the alert", () => {
    setVisibility("hidden");
    const focus = vi.spyOn(window, "focus").mockImplementation(() => undefined);
    const onOpen = vi.fn();
    const { result } = renderHook(() => useAlertDelivery(onOpen), { wrapper });
    act(() => result.current(alert(true)));
    expect(FakeNotification.created).toHaveLength(1);
    const n = FakeNotification.created[0];
    expect(n.title).toBe("Simulated event: Northwind Labs is raising a Series A");
    expect(n.options.tag).toBe("al-1");
    act(() => n.onclick?.());
    expect(focus).toHaveBeenCalled();
    expect(onOpen).toHaveBeenCalledWith(alert(true));
  });

  it("sends no desktop notification without permission", () => {
    setVisibility("hidden");
    FakeNotification.permission = "denied";
    const { result } = renderHook(() => useAlertDelivery(vi.fn()), { wrapper });
    act(() => result.current(alert(false)));
    expect(FakeNotification.created).toHaveLength(0);
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });

  it("asks for permission only while it is undecided", async () => {
    FakeNotification.permission = "default";
    await askNotificationPermission();
    expect(FakeNotification.requestPermission).toHaveBeenCalledOnce();
    FakeNotification.permission = "denied";
    expect(await askNotificationPermission()).toBe("denied");
    expect(FakeNotification.requestPermission).toHaveBeenCalledOnce();
  });

  it("keeps the title plain for a real alert", () => {
    expect(notificationText(alert(false)).title).toBe("Northwind Labs is raising a Series A");
  });

  it("shows the alert card with why it matters, facts, badges and the simulated label", () => {
    render(<AlertCard alert={alert(true)} />);
    expect(
      screen.getByRole("heading", { name: "Northwind Labs is raising a Series A" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Aurora Ventures leads it.")).toBeInTheDocument();
    expect(screen.getByText("€8M")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /press/i })).toBeInTheDocument();
    expect(screen.getByText("Simulated event")).toBeInTheDocument();
  });

  it("spells out each fact's source badge instead of a bare icon", () => {
    render(<AlertCard alert={alert(false)} />);
    expect(screen.getByText("Press")).not.toHaveClass("visually-hidden");
  });
});
