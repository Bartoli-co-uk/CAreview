import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Gauge } from "../components/charts/Gauge";

describe("Gauge", () => {
  it.each([
    [0, "Poor"],
    [49, "Poor"],
    [50, "Needs improvement"],
    [79, "Needs improvement"],
    [80, "Good"],
    [100, "Good"],
  ])("renders an accessible label for score %i (%s band)", (score, band) => {
    render(<Gauge score={score} />);
    const el = screen.getByRole("img", { name: new RegExp(`${score} out of 100, ${band}`) });
    expect(el).toBeInTheDocument();
  });

  it("clamps out-of-range scores instead of rendering an invalid arc", () => {
    render(<Gauge score={150} />);
    expect(screen.getByRole("img", { name: /100 out of 100/ })).toBeInTheDocument();
  });

  it("renders the numeric value as visible text, not only in the SVG", () => {
    render(<Gauge score={72} />);
    expect(screen.getByText("72")).toBeInTheDocument();
  });
});
