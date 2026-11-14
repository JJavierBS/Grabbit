import { beforeEach, describe, expect, it } from "vitest";
import { stubApi } from "../test/render";
import { ApiError, api, unwrap } from "./client";
import { withWorkspace } from "./workspace";

function sentWorkspace(fetchMock: ReturnType<typeof stubApi>, call: number): string | null {
  const request = fetchMock.mock.calls[call][0] as Request;
  return request.headers.get("X-Workspace");
}

describe("api client", () => {
  it("returns data on success", async () => {
    stubApi({ "/api/alerts": { body: [] } });

    await expect(unwrap(api.GET("/api/alerts"))).resolves.toEqual([]);
  });

  it("throws ApiError with the backend error code", async () => {
    stubApi({
      "/api/demo/simulate-event": {
        status: 403,
        body: { error: { code: "demo_mode_disabled", message: "Set DEMO_MODE=1" } },
      },
    });

    const call = unwrap(api.POST("/api/demo/simulate-event", { body: { fixture: "x" } }));

    await expect(call).rejects.toMatchObject({
      name: "ApiError",
      status: 403,
      code: "demo_mode_disabled",
    });
    await expect(call).rejects.toBeInstanceOf(ApiError);
  });
});

describe("anonymous workspace", () => {
  beforeEach(() => localStorage.clear());

  it("sends the same workspace on every call and keeps it for the next visit", async () => {
    const fetchMock = stubApi({ "/api/alerts": { body: [] } });

    await unwrap(api.GET("/api/alerts"));
    await unwrap(api.GET("/api/alerts"));

    const first = sentWorkspace(fetchMock, 0);
    expect(first).toMatch(/^[A-Za-z0-9_-]{1,64}$/);
    expect(sentWorkspace(fetchMock, 1)).toBe(first);
    expect(localStorage.getItem("grabbit.workspace")).toBe(first);
  });

  it("reuses the workspace stored by an earlier visit", async () => {
    localStorage.setItem("grabbit.workspace", "visitor-a");
    const fetchMock = stubApi({ "/api/alerts": { body: [] } });

    await unwrap(api.GET("/api/alerts"));

    expect(sentWorkspace(fetchMock, 0)).toBe("visitor-a");
  });

  it("names the workspace in the event stream URL", () => {
    localStorage.setItem("grabbit.workspace", "visitor-a");

    expect(withWorkspace("/api/events")).toBe("/api/events?workspace=visitor-a");
    expect(withWorkspace("/api/events?x=1")).toBe("/api/events?x=1&workspace=visitor-a");
  });
});
