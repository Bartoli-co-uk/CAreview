import { describe, expect, it } from "vitest";
import { scoreBand, severityInfo, sortBySeverity } from "../lib/severity";

describe("severityInfo", () => {
  it("maps every known severity to a label, color, and order", () => {
    const critical = severityInfo("critical");
    const info = severityInfo("info");
    expect(critical.label).toBe("Critical");
    expect(info.label).toBe("Info");
    expect(critical.order).toBeLessThan(info.order);
  });

  it("falls back sanely for an unknown severity instead of throwing", () => {
    const result = severityInfo("mystery");
    expect(result.label).toBe("mystery");
    expect(result.order).toBe(99);
  });
});

describe("sortBySeverity", () => {
  it("orders items critical -> info", () => {
    const items = [{ severity: "low" }, { severity: "critical" }, { severity: "medium" }];
    expect(sortBySeverity(items).map((i) => i.severity)).toEqual(["critical", "medium", "low"]);
  });
});

describe("scoreBand", () => {
  it("bands boundary scores correctly", () => {
    expect(scoreBand(0).label).toBe("Poor");
    expect(scoreBand(49).label).toBe("Poor");
    expect(scoreBand(50).label).toBe("Needs improvement");
    expect(scoreBand(79).label).toBe("Needs improvement");
    expect(scoreBand(80).label).toBe("Good");
    expect(scoreBand(100).label).toBe("Good");
  });
});
