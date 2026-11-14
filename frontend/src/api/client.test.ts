import { describe, expect, it } from "vitest";
import { stubApi } from "../test/render";
import { ApiError, api, unwrap } from "./client";

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
