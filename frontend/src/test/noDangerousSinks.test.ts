import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, resolve } from "node:path";
import { describe, expect, it } from "vitest";

// Mechanical enforcement of the same safety property tests/test_ui_safety.py
// checked for the old vanilla UI: untrusted tenant strings must never become
// executable markup or code. JSX auto-escapes text content by default, so
// this holds structurally as long as none of these sinks are introduced.
// Vitest's CWD is the frontend/ package root.
const SRC_DIR = resolve(process.cwd(), "src");
const FORBIDDEN_PATTERNS = ["dangerouslySetInnerHTML", "eval(", "new Function(", "document.write"];
const FORBIDDEN_STORAGE = ["localStorage", "sessionStorage", "document.cookie"];

function collectSourceFiles(dir: string): string[] {
  const files: string[] = [];
  for (const entry of readdirSync(dir)) {
    if (entry === "test") continue; // don't scan the test files themselves for these literal strings
    const full = join(dir, entry);
    const stats = statSync(full);
    if (stats.isDirectory()) {
      files.push(...collectSourceFiles(full));
    } else if (/\.(ts|tsx)$/.test(entry)) {
      files.push(full);
    }
  }
  return files;
}

describe("no dangerous DOM/code sinks in frontend source", () => {
  const files = collectSourceFiles(SRC_DIR);

  it("scans at least the expected number of source files", () => {
    expect(files.length).toBeGreaterThan(10);
  });

  it.each(files)("%s has no dangerous sink", (file) => {
    const content = readFileSync(file, "utf-8");
    for (const pattern of FORBIDDEN_PATTERNS) {
      expect(content, `${file} must not use ${pattern}`).not.toContain(pattern);
    }
  });

  it.each(files)("%s never touches localStorage/sessionStorage/cookies", (file) => {
    const content = readFileSync(file, "utf-8");
    for (const pattern of FORBIDDEN_STORAGE) {
      expect(content, `${file} must not use ${pattern}`).not.toContain(pattern);
    }
  });
});
