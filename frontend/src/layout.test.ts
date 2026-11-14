/// <reference types="node" />
import { readFileSync } from "node:fs";

// Read from disk: with `css: false`, Vitest stubs CSS imports, even `?raw` ones.
const read = (path: string) => readFileSync(new URL(path, import.meta.url), "utf8");
const appCss = read("./App.module.css");
const chatCss = read("./features/chat/ChatPanel.module.css");

// jsdom does not lay out CSS (vite.config `css: false`), so these tests pin the layout rules
// that broke in the browser: a collapsed sidebar squeezing the chat into ~700px, and visually
// hidden labels escaping the scroll areas until the whole document scrolled 10,695px.

/** Declarations of the first top-level rule whose selector list is exactly `selector`. */
function declarations(css: string, selector: string): Record<string, string> {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const source = css.replace(/\/\*[\s\S]*?\*\//g, "");
  const match = source.match(new RegExp(`(?:^|\\})\\s*${escaped}\\s*\\{([^}]*)\\}`, "m"));
  if (!match) throw new Error(`No rule for ${selector}`);
  const body = match[1];
  const out: Record<string, string> = {};
  for (const line of body.split(";")) {
    const i = line.indexOf(":");
    if (i > 0)
      out[line.slice(0, i).trim()] = line
        .slice(i + 1)
        .trim()
        .replace(/\s+/g, " ");
  }
  return out;
}

describe("app layout", () => {
  it("keeps the workspace in its own column, so a collapsed sidebar cannot squeeze it", () => {
    expect(declarations(appCss, ".workspace")["grid-column"]).toBe("2");
    expect(declarations(appCss, '.app[data-sidebar="closed"]')["grid-template-columns"]).toBe(
      "0 minmax(0, 1fr)",
    );
  });

  it("folds the sidebar instead of removing it from the grid, and animates the fold", () => {
    expect(declarations(appCss, '.app[data-sidebar="closed"] .sidebar').display).toBeUndefined();
    expect(declarations(appCss, '.app[data-sidebar="closed"] .sidebar').visibility).toBe("hidden");
    expect(declarations(appCss, ".app").transition).toContain("grid-template-columns");
  });

  it("never lets the document scroll: the shell clips and each scroll area is positioned", () => {
    const app = declarations(appCss, ".app");
    expect(app.overflow).toBe("clip");
    expect(app.position).toBe("relative");
    expect(declarations(appCss, ".panel").position).toBe("relative");
    expect(declarations(chatCss, ".log").position).toBe("relative");
  });

  it("scrolls the chat across the full width and centres the conversation inside", () => {
    const log = declarations(chatCss, ".log");
    expect(log["overflow-y"]).toBe("auto");
    expect(log["max-width"]).toBeUndefined();
    expect(declarations(chatCss, ".column")["max-width"]).toBe("var(--chat-width)");
  });
});
