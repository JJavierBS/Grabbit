/// <reference types="node" />
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const SRC = join(dirname(fileURLToPath(import.meta.url)), "..");

// Vitest runs with `css: false` (vite.config), which stubs CSS imports, even `?raw` ones,
// and jsdom does not lay CSS out. Tests that pin a visual rule read the file from disk.

/** A CSS file under `src/`, e.g. `cssFile("features/report/CalaPath.module.css")`. */
export function cssFile(fromSrc: string): string {
  return readFileSync(join(SRC, fromSrc), "utf8");
}

/** Declarations of the first rule whose selector list is exactly `selector`. */
export function declarations(css: string, selector: string): Record<string, string> {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const source = css.replace(/\/\*[\s\S]*?\*\//g, "");
  const match = source.match(new RegExp(`(?:^|\\})\\s*${escaped}\\s*\\{([^}]*)\\}`, "m"));
  if (!match) throw new Error(`No rule for ${selector}`);
  const out: Record<string, string> = {};
  for (const line of match[1].split(";")) {
    const i = line.indexOf(":");
    if (i > 0)
      out[line.slice(0, i).trim()] = line
        .slice(i + 1)
        .trim()
        .replace(/\s+/g, " ");
  }
  return out;
}

/** Every `font-size` in px the file sets. */
export function fontSizesPx(css: string): number[] {
  return [...css.matchAll(/font-size:\s*(\d+(?:\.\d+)?)px/g)].map((m) => Number(m[1]));
}
