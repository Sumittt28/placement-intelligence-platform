"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { TrendingUp } from "lucide-react";

interface TrendData {
  date: string;
  scores: {
    communication: number;
    technical_depth: number;
    problem_solving: number;
    behavioral: number;
    project_discussions: number;
  };
}

interface TrendGraphProps {
  data: TrendData[];
}

const lines = [
  { key: "communication", color: "#3b82f6", label: "Communication" },
  { key: "technical_depth", color: "#8b5cf6", label: "Technical" },
  { key: "problem_solving", color: "#22c55e", label: "Problem Solving" },
  { key: "behavioral", color: "#f97316", label: "Behavioral" },
  { key: "project_discussions", color: "#ec4899", label: "Project" },
];

export function TrendGraph({ data }: TrendGraphProps) {
  // Flatten data for recharts
  const chartData = data.map((item) => ({
    date: new Date(item.date).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
    ...item.scores,
  }));

  if (chartData.length === 0) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <TrendingUp className="h-5 w-5" />
            Performance Trends
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            Complete mock interviews to see your performance trends over time.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <TrendingUp className="h-5 w-5" />
          Performance Trends (Last 10 Interviews)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey="date" className="text-xs" tick={{ fontSize: 12 }} />
            <YAxis domain={[0, 10]} tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            {lines.map(({ key, color, label }) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={color}
                name={label}
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
