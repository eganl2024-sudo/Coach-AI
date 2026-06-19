'use client';

import React from 'react';

interface RadarChartProps {
  axes: string[];     // dynamic skill names
  scores: number[];   // score per axis (0-100)
  size?: number;      // default 200
}

function splitLabel(label: string, maxCharsPerLine = 10): [string, string | null] {
  if (label.length <= maxCharsPerLine) return [label, null];
  
  const words = label.split(' ');
  if (words.length === 1) return [label.slice(0, maxCharsPerLine), label.slice(maxCharsPerLine)];
  
  // Find the best split point near the middle
  let line1 = '';
  let line2 = '';
  let splitIdx = 0;
  
  for (let i = 0; i < words.length; i++) {
    const candidate = words.slice(0, i + 1).join(' ');
    if (candidate.length <= maxCharsPerLine) {
      line1 = candidate;
      splitIdx = i + 1;
    } else {
      break;
    }
  }
  
  line2 = words.slice(splitIdx).join(' ');
  
  if (!line1) {
    line1 = words[0];
    line2 = words.slice(1).join(' ');
  }
  
  return [line1, line2 || null];
}

export function RadarChart({ axes, scores, size = 200 }: RadarChartProps) {
  const N = axes.length;

  if (N === 0 || scores.length === 0) {
    return (
      <div className="flex items-center justify-center text-muted-foreground text-xs font-semibold" style={{ height: size }}>
        No skill data yet
      </div>
    );
  }

  const cx = size / 2;
  const cy = size / 2;
  const radius = size * 0.35; // slightly smaller to give labels room

  const getPoint = (score: number, axisIndex: number) => {
    const ratio = score / 100;
    const angle = -Math.PI / 2 + (2 * Math.PI * axisIndex) / N;
    return {
      x: cx + Math.cos(angle) * radius * ratio,
      y: cy + Math.sin(angle) * radius * ratio,
    };
  };

  const getEdgePoint = (axisIndex: number) => {
    return getPoint(100, axisIndex);
  };

  const getLabelPoint = (axisIndex: number) => {
    const angle = -Math.PI / 2 + (2 * Math.PI * axisIndex) / N;
    const labelRadius = radius + size * 0.14;
    return {
      x: cx + Math.cos(angle) * labelRadius,
      y: cy + Math.sin(angle) * labelRadius,
      angle,
    };
  };

  // Build points string for the data polygon
  const dataPointsStr = axes
    .map((_, i) => {
      const pt = getPoint(scores[i] ?? 0, i);
      return `${pt.x},${pt.y}`;
    })
    .join(' ');

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      className="mx-auto block select-none overflow-visible"
    >
      {/* 1. Background grid: 3 concentric polygons at 33%, 66%, 100% */}
      {[0.33, 0.66, 1.0].map((rRatio, idx) => {
        const gridPointsStr = Array.from({ length: N })
          .map((_, i) => {
            const pt = getPoint(100 * rRatio, i);
            return `${pt.x},${pt.y}`;
          })
          .join(' ');
        return (
          <polygon
            key={idx}
            points={gridPointsStr}
            stroke="hsl(0 0% 20%)"
            strokeWidth="1"
            fill="none"
          />
        );
      })}

      {/* 2. Axis lines: center -> each edge point */}
      {Array.from({ length: N }).map((_, i) => {
        const edge = getEdgePoint(i);
        return (
          <line
            key={i}
            x1={cx}
            y1={cy}
            x2={edge.x}
            y2={edge.y}
            stroke="hsl(0 0% 25%)"
            strokeWidth="1"
          />
        );
      })}

      {/* 3. Data polygon */}
      {dataPointsStr && (
        <polygon
          points={dataPointsStr}
          fill="hsla(142, 71%, 45%, 0.25)"
          stroke="hsl(142, 71%, 45%)"
          strokeWidth="2"
        />
      )}

      {/* 4. Data dots at each score point */}
      {axes.map((_, i) => {
        const pt = getPoint(scores[i] ?? 0, i);
        return (
          <circle
            key={i}
            cx={pt.x}
            cy={pt.y}
            r={size * 0.025}
            fill="hsl(142, 71%, 45%)"
          />
        );
      })}

      {/* 5. Axis labels at label points */}
      {axes.map((axisName, i) => {
        const { x, y } = getLabelPoint(i);
        const [line1, line2] = splitLabel(axisName);

        let textAnchor: 'start' | 'end' | 'middle' = 'middle';
        if (x > cx + 5) textAnchor = 'start';
        else if (x < cx - 5) textAnchor = 'end';

        let dy = '0.35em';
        if (y > cy + 5) dy = '1em';
        else if (y < cy - 5) dy = '-0.3em';

        const isTopHalf = y < cy;
        const lineHeight = 11; // px between lines

        return line2 ? (
          <text
            key={i}
            x={x}
            y={isTopHalf ? y - lineHeight / 2 : y + lineHeight / 2}
            textAnchor={textAnchor}
            fontSize={size * 0.062}
            fill="hsl(0 0% 65%)"
            className="font-medium"
          >
            <tspan x={x} dy="0">{line1}</tspan>
            <tspan x={x} dy={lineHeight}>{line2}</tspan>
          </text>
        ) : (
          <text
            key={i}
            x={x}
            y={y}
            dy={dy}
            fontSize={size * 0.062}
            fill="hsl(0 0% 65%)"
            textAnchor={textAnchor}
            className="font-medium"
          >
            {line1}
          </text>
        );
      })}

      {/* 6. Score labels near each dot (offset slightly outward) */}
      {axes.map((_, i) => {
        const score = scores[i] ?? 0;
        const dotPt = getPoint(score, i);
        const angle = -Math.PI / 2 + (2 * Math.PI * i) / N;
        const offsetDistance = size * 0.065;
        const labelX = dotPt.x + Math.cos(angle) * offsetDistance;
        const labelY = dotPt.y + Math.sin(angle) * offsetDistance + (angle > 0 && angle < Math.PI ? 2 : -1);

        return (
          <text
            key={i}
            x={labelX}
            y={labelY}
            dy="0.35em"
            fontSize={size * 0.068}
            fill="white"
            fontWeight="bold"
            textAnchor="middle"
          >
            {score}
          </text>
        );
      })}
    </svg>
  );
}
