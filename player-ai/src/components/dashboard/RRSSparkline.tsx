'use client';

interface RRSSnapshot {
  date: string;
  overall: number;
}

interface RRSSparklineProps {
  snapshots: RRSSnapshot[];
}

export function RRSSparkline({ snapshots }: RRSSparklineProps) {
  if (!snapshots || snapshots.length < 2) return null;

  // 1. Sort snapshots by date ascending
  const sorted = [...snapshots].sort((a, b) => a.date.localeCompare(b.date));

  // 2. Take the last 4 (or fewer)
  const lastSnapshots = sorted.slice(-4);

  // 3. Find min and max overall values in this subset
  const values = lastSnapshots.map(s => s.overall);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  // 4. Map each point to SVG coordinates
  const points = lastSnapshots.map((snap, i) => {
    const x = (i / (lastSnapshots.length - 1)) * 80;
    // Inverted scale: higher score = lower y coordinate.
    // Leaves 2px padding at the top (y=2) and bottom (y=26)
    const y = 28 - (((snap.overall - min) / range) * 24 + 2);
    return { x, y };
  });

  // 5. Build polyline points string
  const pointsStr = points.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');
  const lastPoint = points[points.length - 1];

  return (
    <div className="py-1">
      <svg
        width="80"
        height="28"
        viewBox="0 0 80 28"
        className="text-primary overflow-visible"
        aria-hidden="true"
      >
        <polyline
          points={pointsStr}
          stroke="currentColor"
          strokeWidth="2"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <circle
          cx={lastPoint.x}
          cy={lastPoint.y}
          r="2.5"
          fill="currentColor"
        />
      </svg>
    </div>
  );
}
export default RRSSparkline;
