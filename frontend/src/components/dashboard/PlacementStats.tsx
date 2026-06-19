"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Briefcase, Brain, MessageSquare, BarChart3 } from "lucide-react";

interface PlacementStatsProps {
  interviewsAttempted: number;
  aiInterviewsCompleted: number;
  contributionsSubmitted: number;
  companyReportsViewed: number;
}

const statConfig = [
  { key: "interviewsAttempted", label: "Interviews Attempted", icon: Briefcase, color: "text-blue-500" },
  { key: "aiInterviewsCompleted", label: "AI Interviews", icon: Brain, color: "text-purple-500" },
  { key: "contributionsSubmitted", label: "Contributions", icon: MessageSquare, color: "text-green-500" },
  { key: "companyReportsViewed", label: "Reports Viewed", icon: BarChart3, color: "text-orange-500" },
] as const;

export function PlacementStats(props: PlacementStatsProps) {
  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {statConfig.map(({ key, label, icon: Icon, color }) => (
        <Card key={key}>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className={`rounded-lg bg-muted p-2 ${color}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{props[key]}</p>
                <p className="text-xs text-muted-foreground">{label}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
