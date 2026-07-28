export interface DonutSlice {
  label: string;
  value: number;
  color: string;
}

interface DonutProps {
  slices: DonutSlice[];
  size?: number;
}

// Hand-rolled N-slice categorical donut (no charting library). Slices with
// zero total render an empty ring rather than dividing by zero.
export function Donut({ slices, size = 120 }: DonutProps) {
  const total = slices.reduce((sum, s) => sum + s.value, 0);
  const radius = size / 2 - 10;
  const circumference = 2 * Math.PI * radius;
  const center = size / 2;
  let offsetSoFar = 0;

  return (
    <div>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label="Policies by status">
        {total === 0 ? (
          <circle cx={center} cy={center} r={radius} fill="none" stroke="#f2f4f7" strokeWidth={12} />
        ) : (
          slices.map((slice) => {
            const fraction = slice.value / total;
            const dash = circumference * fraction;
            const dashArray = `${dash} ${circumference - dash}`;
            const dashOffset = -offsetSoFar * circumference;
            offsetSoFar += fraction;
            if (slice.value === 0) return null;
            return (
              <circle
                key={slice.label}
                cx={center}
                cy={center}
                r={radius}
                fill="none"
                stroke={slice.color}
                strokeWidth={12}
                strokeDasharray={dashArray}
                strokeDashoffset={dashOffset}
                transform={`rotate(-90 ${center} ${center})`}
              />
            );
          })
        )}
      </svg>
      <ul style={{ listStyle: "none", margin: "10px 0 0", padding: 0, fontSize: 13 }}>
        {slices.map((slice) => (
          <li key={slice.label} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
            <span
              className="badge-dot"
              style={{ background: slice.color }}
              aria-hidden="true"
            />
            <span style={{ color: slice.color, fontWeight: 600 }}>{slice.value}</span>
            <span>{slice.label}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
