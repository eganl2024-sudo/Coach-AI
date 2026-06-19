'use client';

import React, { useState } from 'react';

interface Snapshot {
  date: string;
  overall: number;
}

interface RRSLineChartProps {
  snapshots: Snapshot[];
}

export function RRSLineChart({ snapshots }: RRSLineChartProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  // If fewer than 2 snapshots: show centered text "Not enough data yet"
  if (!snapshots || snapshots.length < 2) {
    return (
      <div className="flex h-36 items-center justify-center border border-border/40 rounded-xl bg-card/20 text-muted-foreground text-sm">
        Not enough data yet
      </div>
    );
  }

  // Sort snapshots by date ascending
  const sortedSnapshots = [...snapshots].sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
  );

  const paddingLeft = 40;
  const paddingRight = 20;
  const paddingTop = 16;
  const paddingBottom = 32;
  const chartWidth = 400 - paddingLeft - paddingRight; // 340
  const chartHeight = 160 - paddingTop - paddingBottom; // 112

  const scores = sortedSnapshots.map(s => s.overall);
  let minScore = Math.max(0, Math.min(...scores) - 5);
  let maxScore = Math.min(100, Math.max(...scores) + 5);

  if (minScore === maxScore) {
    minScore = Math.max(0, minScore - 10);
    maxScore = Math.min(100, maxScore + 10);
  }

  const scoreRange = maxScore - minScore;
  const midScore = Math.round((minScore + maxScore) / 2);

  // Get coordinates for each data point
  const count = sortedSnapshots.length;
  const points = sortedSnapshots.map((s, i) => {
    const x = paddingLeft + (i / (count - 1)) * chartWidth;
    const y =
      paddingTop +
      chartHeight -
      ((s.overall - minScore) / scoreRange) * chartHeight;
    return { x, y, snapshot: s };
  });

  // Polyline points string
  const polylinePoints = points.map(p => `${p.x},${p.y}`).join(' ');

  // Shaded area path
  const areaPath = points.length > 0
    ? `M ${points[0].x} ${paddingTop + chartHeight} L ${polylinePoints} L ${points[points.length - 1].x} ${paddingTop + chartHeight} Z`
    : '';

  // Get date label
  const formatDateLabel = (dateStr: string) => {
    try {
      const [y, m, d] = dateStr.split('-').map(Number);
      const months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
      ];
      return `${months[m - 1]} ${d}`;
    } catch {
      return dateStr;
    }
  };

  // Render Y axis values (max, mid, min)
  const yLabels = [
    { value: maxScore, y: paddingTop },
    { value: midScore, y: paddingTop + chartHeight / 2 },
    { value: minScore, y: paddingTop + chartHeight }
  ];

  return (
    <div className="relative w-full">
      <svg
        viewBox="0 0 400 160"
        width="100%"
        preserveAspectRatio="none"
        onMouseLeave={() => setHoveredIndex(null)}
        className="overflow-visible select-none"
      >
        {/* Horizontal grid lines */}
        {yLabels.map((lbl, idx) => (
          <line
            key={idx}
            x1={paddingLeft}
            y1={lbl.y}
            x2={400 - paddingRight}
            y2={lbl.y}
            stroke="hsl(0 0% 18%)"
            strokeWidth="1"
            strokeDasharray="4 4"
          />
        ))}

        {/* Shaded Area fill */}
        <path d={areaPath} fill="hsla(142, 71%, 45%, 0.1)" />

        {/* Trend Polyline */}
        <polyline
          points={polylinePoints}
          stroke="hsl(142, 71%, 45%)"
          strokeWidth="2.5"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Y Axis Labels */}
        {yLabels.map((lbl, idx) => (
          <text
            key={idx}
            x={paddingLeft}
            y={lbl.y}
            dx="-6"
            dy="3"
            fill="hsl(0 0% 55%)"
            fontSize="10"
            textAnchor="end"
          >
            {lbl.value}
          </text>
        ))}

        {/* X Axis Labels */}
        {points.map((p, idx) => (
          <text
            key={idx}
            x={p.x}
            y={paddingTop + chartHeight}
            dy="14"
            fill="hsl(0 0% 55%)"
            fontSize="10"
            textAnchor="middle"
          >
            {formatDateLabel(p.snapshot.date)}
          </text>
        ))}

        {/* Interactive Data dots */}
        {points.map((p, idx) => (
          <circle
            key={idx}
            cx={p.x}
            cy={p.y}
            r="4"
            fill="hsl(142, 71%, 45%)"
            stroke="hsl(0 0% 9%)"
            strokeWidth="2"
            onMouseEnter={() => setHoveredIndex(idx)}
            className="cursor-pointer transition-all duration-200 hover:r-5"
          />
        ))}

        {/* Tooltip Overlay */}
        {hoveredIndex !== null && points[hoveredIndex] && (
          (() => {
            const p = points[hoveredIndex];
            const width = 52;
            const height = 28;
            
            // Positioning of the tooltip box
            let tx = p.x - width / 2;
            let ty = p.y - height - 8;

            // Constrain within the bounds of the chart
            if (tx < 5) tx = 5;
            if (tx + width > 395) tx = 395 - width;
            if (ty < 2) ty = p.y + 8; // flip below if it hits the top border

            return (
              <g className="pointer-events-none transition-all duration-200">
                <rect
                  x={tx}
                  y={ty}
                  width={width}
                  height={height}
                  rx="4"
                  fill="hsl(0 0% 12%)"
                  stroke="hsl(142, 71%, 45%)"
                  strokeWidth="1"
                />
                <text
                  x={tx + width / 2}
                  y={ty + 12}
                  fill="white"
                  fontSize="10"
                  fontWeight="bold"
                  textAnchor="middle"
                >
                  {p.snapshot.overall}
                </text>
                <text
                  x={tx + width / 2}
                  y={ty + 22}
                  fill="hsl(0 0% 55%)"
                  fontSize="7"
                  fontWeight="medium"
                  textAnchor="middle"
                >
                  RRS SCORE
                </text>
              </g>
            );
          })()
        )}
      </svg>
    </div>
  );
}
