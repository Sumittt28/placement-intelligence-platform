"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Hash } from "lucide-react";

interface TopicFrequencyProps {
  topics: { topic: string; count: number }[];
}

export function TopicFrequency({ topics }: TopicFrequencyProps) {
  const maxCount = Math.max(...topics.map((t) => t.count), 1);

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Hash className="h-5 w-5" />
          Most Asked Topics
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {topics.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">No topics data yet</p>
        ) : (
          topics.slice(0, 10).map((item, idx) => (
            <div key={idx} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">{item.topic}</span>
                <Badge variant="secondary" className="text-xs">{item.count}</Badge>
              </div>
              <Progress value={(item.count / maxCount) * 100} className="h-1.5" />
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
