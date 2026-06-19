"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { TrendingUp } from "lucide-react";

interface PerformanceOverviewProps {
  communication: number;
  technical_depth: number;
  problem_solving: number;
  behavioral: number;
  project_discussions: number;
}

const dimensions = [
  { key: "communication", label: "Communication", color: "bg-blue-500" },
  { key: "technical_depth", label: "Technical Depth", color: "bg-purple-500" },
  { key: "problem_solving", label: "Problem Solving", color: "bg-green-500" },
  { key: "behavioral", label: "Behavioral", color: "bg-orange-500" },
  { key: "project_discussions", label: "Project Discussion", color: "bg-pink-500" },
] as const;

export function PerformanceOverview(props: PerformanceOverviewProps) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <TrendingUp className="h-5 w-5" />
          Performance Overview
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {dimensions.map(({ key, label }) => {
          const score = props[key] || 0;
          const percentage = (score / 10) * 100;
          return (
            <div key={key} className="space-y-1.5">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">{label}</span>
                <span className="font-medium">{score.toFixed(1)}/10</span>
              </div>
              <Progress value={percentage} className="h-2" />
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
