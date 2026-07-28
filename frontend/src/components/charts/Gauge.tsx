import { scoreBand } from "../../lib/severity";

interface GaugeProps {
  score: number;
  max?: number;
  size?: number;
}

// Hand-rolled SVG arc gauge — no charting library dependency, so the bundle
// stays small and there is no third-party runtime to audit.
export function Gauge({ score, max = 100, size = 120 }: GaugeProps) {
  const clamped = Math.max(0, Math.min(max, score));
  const radius = size / 2 - 10;
  const circumference = 2 * Math.PI * radius;
  const fraction = clamped / max;
  const dashoffset = circumference * (1 - fraction);
  const band = scoreBand(clamped);
  const center = size / 2;

  return (
    <div
      role="img"
      aria-label={`Security score ${clamped} out of ${max}, ${band.label}`}
      style={{ position: "relative", width: size, height: size }}
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="#f2f4f7"
          strokeWidth={10}
        />
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={band.color}
          strokeWidth={10}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashoffset}
          transform={`rotate(-90 ${center} ${center})`}
        />
      </svg>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column",
        }}
      >
        <span style={{ fontSize: size * 0.28, fontWeight: 700, lineHeight: 1 }}>{clamped}</span>
        <span style={{ fontSize: size * 0.1, color: "#667085" }}>/{max}</span>
      </div>
    </div>
  );
}
