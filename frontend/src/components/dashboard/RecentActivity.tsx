"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Clock } from "lucide-react";

interface ActivityItem {
  action: string;
  resource?: string;
  resource_id?: string;
  created_at: string;
}

interface RecentActivityProps {
  activities: ActivityItem[];
}

export function RecentActivity({ activities }: RecentActivityProps) {
  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Activity className="h-5 w-5" />
          Recent Activity
        </CardTitle>
      </CardHeader>
      <CardContent>
        {activities.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">No recent activity</p>
        ) : (
          <div className="space-y-3">
            {activities.map((item, idx) => (
              <div key={idx} className="flex items-start gap-3 text-sm">
                <div className="mt-0.5 rounded-full bg-primary/10 p-1">
                  <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{item.action}</p>
                  {item.resource && (
                    <p className="text-xs text-muted-foreground">{item.resource}</p>
                  )}
                </div>
                <span className="text-xs text-muted-foreground flex items-center gap-1 shrink-0">
                  <Clock className="h-3 w-3" />
                  {formatTime(item.created_at)}
                </span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
