"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TopicCard } from "./TopicCard";
import { Target, BookOpen, Brain } from "lucide-react";
import type { Recommendation } from "@/types";

interface PracticePlanProps {
  recommendations: Recommendation[];
  onComplete: (id: string) => void;
  isCompleting?: boolean;
}

export function PracticePlan({ recommendations, onComplete, isCompleting }: PracticePlanProps) {
  const topics = recommendations.filter((r) => r.type === "topic");
  const plans = recommendations.filter((r) => r.type === "practice_plan");
  const mocks = recommendations.filter((r) => r.type === "mock_interview");

  const completedCount = recommendations.filter((r) => r.is_completed).length;
  const totalCount = recommendations.length;
  const progressPercent = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* Progress */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Overall Progress</span>
            <span className="text-sm text-muted-foreground">
              {completedCount}/{totalCount} completed
            </span>
          </div>
          <div className="h-2 rounded-full bg-muted overflow-hidden">
            <div
              className="h-full rounded-full bg-primary transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </CardContent>
      </Card>

      {/* Topics to Study */}
      {topics.length > 0 && (
        <div>
          <h3 className="flex items-center gap-2 text-sm font-semibold mb-3">
            <BookOpen className="h-4 w-4" />
            Topics to Study ({topics.length})
          </h3>
          <div className="space-y-3">
            {topics.map((rec) => (
              <TopicCard key={rec.id} recommendation={rec} onComplete={onComplete} isCompleting={isCompleting} />
            ))}
          </div>
        </div>
      )}

      {/* Practice Plans */}
      {plans.length > 0 && (
        <div>
          <h3 className="flex items-center gap-2 text-sm font-semibold mb-3">
            <Target className="h-4 w-4" />
            Practice Plans ({plans.length})
          </h3>
          <div className="space-y-3">
            {plans.map((rec) => (
              <TopicCard key={rec.id} recommendation={rec} onComplete={onComplete} isCompleting={isCompleting} />
            ))}
          </div>
        </div>
      )}

      {/* Suggested Mocks */}
      {mocks.length > 0 && (
        <div>
          <h3 className="flex items-center gap-2 text-sm font-semibold mb-3">
            <Brain className="h-4 w-4" />
            Suggested Mock Interviews ({mocks.length})
          </h3>
          <div className="space-y-3">
            {mocks.map((rec) => (
              <TopicCard key={rec.id} recommendation={rec} onComplete={onComplete} isCompleting={isCompleting} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
