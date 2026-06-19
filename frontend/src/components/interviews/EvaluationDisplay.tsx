"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from "recharts";
import { Award, TrendingUp, AlertTriangle, CheckCircle } from "lucide-react";
import type { Evaluation } from "@/types";

interface EvaluationDisplayProps {
  evaluation: Evaluation;
}

const dimensionLabels: Record<string, string> = {
  communication: "Communication",
  technical: "Technical Depth",
  confidence: "Confidence",
  problem_solving: "Problem Solving",
  behavioral: "Behavioral",
  project: "Project Understanding",
};

export function EvaluationDisplay({ evaluation }: EvaluationDisplayProps) {
  const dimensions = ["communication", "technical", "confidence", "problem_solving", "behavioral", "project"];

  const radarData = dimensions.map((dim) => ({
    dimension: dimensionLabels[dim] || dim,
    score: (evaluation[dim as keyof Evaluation] as { score: number })?.score || 0,
  }));

  const scoreColor = (score: number) => {
    if (score >= 8) return "text-green-500";
    if (score >= 6) return "text-yellow-500";
    return "text-red-500";
  };

  return (
    <div className="space-y-6">
      {/* Overall Score */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <Award className="h-5 w-5" />
            Overall Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center">
            <div className="text-center">
              <p className={`text-5xl font-bold ${scoreColor(evaluation.overall_score)}`}>
                {evaluation.overall_score?.toFixed(1)}
              </p>
              <p className="text-sm text-muted-foreground mt-1">out of 10</p>
            </div>
          </div>
          <p className="mt-4 text-sm text-muted-foreground">{evaluation.overall_feedback}</p>
        </CardContent>
      </Card>

      {/* Radar Chart */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Performance Radar</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 11 }} />
              <PolarRadiusAxis domain={[0, 10]} tick={{ fontSize: 10 }} />
              <Radar
                name="Score"
                dataKey="score"
                stroke="#8b5cf6"
                fill="#8b5cf6"
                fillOpacity={0.3}
                strokeWidth={2}
              />
            </RadarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Dimension Breakdown */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Score Breakdown</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {dimensions.map((dim) => {
            const dimData = evaluation[dim as keyof Evaluation] as { score: number; reason: string } | undefined;
            if (!dimData) return null;
            return (
              <div key={dim} className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{dimensionLabels[dim]}</span>
                  <span className={`text-sm font-bold ${scoreColor(dimData.score)}`}>
                    {dimData.score}/10
                  </span>
                </div>
                <Progress value={(dimData.score / 10) * 100} className="h-2" />
                <p className="text-xs text-muted-foreground">{dimData.reason}</p>
              </div>
            );
          })}
        </CardContent>
      </Card>

      {/* Strengths & Improvements */}
      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <CheckCircle className="h-4 w-4 text-green-500" />
              Strengths
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {(evaluation.strengths || []).map((s, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <TrendingUp className="h-3.5 w-3.5 mt-0.5 text-green-500 shrink-0" />
                  {s}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <AlertTriangle className="h-4 w-4 text-yellow-500" />
              Areas for Improvement
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {(evaluation.improvements || []).map((imp, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <AlertTriangle className="h-3.5 w-3.5 mt-0.5 text-yellow-500 shrink-0" />
                  {imp}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
