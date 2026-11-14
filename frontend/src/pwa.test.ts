import indexHtml from "../index.html?raw";
import manifestText from "../public/manifest.webmanifest?raw";

const publicFiles = Object.keys(import.meta.glob("../public/*")).map((path) =>
  path.replace("../public", ""),
);
const inPublic = (src: string) => publicFiles.includes(src);

interface ManifestIcon {
  src: string;
  sizes: string;
  type: string;
  purpose?: string;
}

const manifest = JSON.parse(manifestText) as {
  name: string;
  short_name: string;
  start_url: string;
  scope: string;
  display: string;
  theme_color: string;
  background_color: string;
  icons: ManifestIcon[];
};

describe("PWA manifest", () => {
  it("has the fields browsers need to offer installing the app", () => {
    expect(manifest).toMatchObject({
      name: "Grabbit",
      short_name: "Grabbit",
      start_url: "/",
      scope: "/",
      display: "standalone",
    });
    expect(manifest.theme_color).toMatch(/^#[0-9a-f]{6}$/i);
    expect(manifest.background_color).toMatch(/^#[0-9a-f]{6}$/i);
  });

  it("lists 192 and 512 px icons and a maskable one, all present in public/", () => {
    const has = (sizes: string, purpose: string) =>
      manifest.icons.some((i) => i.sizes === sizes && (i.purpose ?? "any") === purpose);
    expect(has("192x192", "any")).toBe(true);
    expect(has("512x512", "any")).toBe(true);
    expect(has("512x512", "maskable")).toBe(true);
    for (const icon of manifest.icons) expect(inPublic(icon.src)).toBe(true);
  });

  it("is linked from index.html with an Apple touch icon", () => {
    expect(indexHtml).toContain('<link rel="manifest" href="/manifest.webmanifest" />');
    expect(indexHtml).toMatch(/<link rel="apple-touch-icon" href="\/apple-touch-icon.png" \/>/);
    expect(inPublic("/apple-touch-icon.png")).toBe(true);
  });
});
