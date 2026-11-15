import raw from "../vercel.json?raw";

type Rewrite = { source: string; destination: string };
const config = JSON.parse(raw) as {
  framework: string;
  outputDirectory: string;
  rewrites: Rewrite[];
};

describe("Vercel deploy config", () => {
  it("builds the Vite app into dist", () => {
    expect(config.framework).toBe("vite");
    expect(config.outputDirectory).toBe("dist");
  });

  // The client calls /api on its own origin (client.ts), so Vercel must proxy it to Aiven.
  it("proxies every /api path to the Aiven API over HTTPS, keeping the path", () => {
    const api = config.rewrites.find((r) => r.source === "/api/:path*");
    expect(api).toBeDefined();
    const target = new URL(api?.destination ?? "");
    expect(target.protocol).toBe("https:");
    expect(target.hostname).toMatch(/\.aiven\.app$/);
    expect(target.pathname).toBe("/api/:path*");
  });
});
