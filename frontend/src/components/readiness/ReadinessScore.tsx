"use client";

import { Card, CardContent } from "@/components/ui/card";

interface ReadinessScoreProps {
  percent: number;
  label: string;
  size?: "sm" | "lg";
}

export function ReadinessScore({ percent, label, size = "lg" }: ReadinessScoreProps) {
  const radius = size === "lg" ? 60 : 40;
  const stroke = size === "lg" ? 8 : 6;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percent / 100) * circumference;
  const svgSize = (radius + stroke) * 2;

  const color = percent >= 80 ? "#22c55e" : percent >= 60 ? "#f59e0b" : "#ef4444";

  return (
    <Card className="flex items-center justify-center">
      <CardContent className="pt-6 text-center">
        <svg width={svgSize} height={svgSize} className="mx-auto">
          <circle
            cx={radius + stroke}
            cy={radius + stroke}
            r={radius}
            fill="none"
            stroke="hsl(var(--muted))"
            strokeWidth={stroke}
          />
          <circle
            cx={radius + stroke}
            cy={radius + stroke}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={stroke}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            transform={`rotate(-90 ${radius + stroke} ${radius + stroke})`}
            className="transition-all duration-1000 ease-out"
          />
          <text
            x={radius + stroke}
            y={radius + stroke}
            textAnchor="middle"
            dominantBaseline="central"
            className="fill-foreground text-xl font-bold"
            fontSize={size === "lg" ? 24 : 16}
          >
            {Math.round(percent)}%
          </text>
        </svg>
        <p className="mt-2 text-sm font-medium">{label}</p>
      </CardContent>
    </Card>
  );
}
