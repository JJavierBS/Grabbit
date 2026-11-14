import { act, renderHook } from "@testing-library/react";
import { SETTLE_MS, useSettled } from "./useSettled";

describe("useSettled", () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it("holds for about four seconds after a change, then settles", () => {
    const first = {};
    const { result, rerender } = renderHook(({ key }) => useSettled(key), {
      initialProps: { key: first as object | null },
    });
    expect(SETTLE_MS).toBe(4000);
    expect(result.current).toBe(false);
    act(() => vi.advanceTimersByTime(SETTLE_MS - 1));
    expect(result.current).toBe(false);
    act(() => vi.advanceTimersByTime(1));
    expect(result.current).toBe(true);

    rerender({ key: {} });
    expect(result.current).toBe(false);
    act(() => vi.advanceTimersByTime(SETTLE_MS));
    expect(result.current).toBe(true);
  });

  it("reads as settled when nothing changed", () => {
    const { result } = renderHook(() => useSettled(null));
    expect(result.current).toBe(true);
  });
});
