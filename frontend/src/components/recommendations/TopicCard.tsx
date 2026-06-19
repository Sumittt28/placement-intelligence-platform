"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CheckCircle, BookOpen, Brain, Target } from "lucide-react";
import type { Recommendation } from "@/types";

interface TopicCardProps {
  recommendation: Recommendation;
  onComplete: (id: string) => void;
  isCompleting?: boolean;
}

const typeIcons: Record<string, typeof BookOpen> = {
  topic: BookOpen,
  practice_plan: Target,
  mock_interview: Brain,
};

const typeBadge: Record<string, string> = {
  topic: "Study Topic",
  practice_plan: "Practice Plan",
  mock_interview: "Suggested Mock",
};

export function TopicCard({ recommendation, onComplete, isCompleting }: TopicCardProps) {
  const Icon = typeIcons[recommendation.type] || BookOpen;

  return (
    <Card className={recommendation.is_completed ? "opacity-60" : ""}>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3">
            <div className="rounded-lg bg-primary/10 p-2 shrink-0">
              <Icon className="h-4 w-4 text-primary" />
            </div>
            <div className="space-y-1">
              <h4 className="font-medium text-sm">{recommendation.title}</h4>
              {recommendation.description && (
                <p className="text-xs text-muted-foreground">{recommendation.description}</p>
              )}
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs">
                  {typeBadge[recommendation.type] || recommendation.type}
                </Badge>
                <Badge variant="secondary" className="text-xs">
                  Priority: {recommendation.priority}
                </Badge>
              </div>
            </div>
          </div>

          {!recommendation.is_completed && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onComplete(recommendation.id)}
              disabled={isCompleting}
              className="shrink-0"
            >
              <CheckCircle className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
