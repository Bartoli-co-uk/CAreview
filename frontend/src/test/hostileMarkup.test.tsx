import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { PolicyDetail } from "../components/PolicyDetail";
import type { Policy } from "../api/types";

// Frontend analogue of tests/test_ui_safety.py's SampleDataHostileFixtureTests:
// reuses the same committed sample-data.json hostile display name and proves
// JSX's default text-escaping renders it as inert text, never as markup.
// Vitest's CWD is the frontend/ package root, so resolve relative to that
// rather than import.meta.url (which Vite's transform doesn't guarantee is a
// plain file: URL).
const SAMPLE_DATA_PATH = resolve(process.cwd(), "../web/sample-data.json");
const HOSTILE_MARKER = "<img src=x onerror=alert(1)>";

describe("hostile markup rendering", () => {
  it("sample-data.json still contains the hostile-markup regression case", () => {
    const raw = readFileSync(SAMPLE_DATA_PATH, "utf-8");
    expect(raw).toContain(HOSTILE_MARKER);
  });

  it("renders a hostile display name as literal text with no injected <img>", () => {
    const raw = readFileSync(SAMPLE_DATA_PATH, "utf-8");
    const data = JSON.parse(raw) as { policies: Policy[] };
    const hostilePolicy = data.policies.find((p) => p.displayName.includes(HOSTILE_MARKER));
    expect(hostilePolicy).toBeDefined();

    const { container } = render(<PolicyDetail policy={hostilePolicy!} />);
    expect(screen.getByText(hostilePolicy!.displayName)).toBeInTheDocument();
    expect(container.querySelector("img")).toBeNull();
  });
});
