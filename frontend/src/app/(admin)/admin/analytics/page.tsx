"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { adminAPI } from "@/lib/api";
import { Users, MessageSquare, Brain, TrendingUp } from "lucide-react";

export default function AdminAnalyticsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["admin-analytics-full"],
    queryFn: async () => {
      const res = await adminAPI.analytics();
      return res.data.data as {
        total_users: number;
        total_experiences: number;
        total_mock_interviews: number;
      };
    },
  });

  if (isLoading) return <p className="text-muted-foreground">Loading analytics...</p>;

  const metrics = [
    { label: "Total Registered Users", value: data?.total_users || 0, icon: Users, color: "bg-blue-50 text-blue-600", description: "Students + Admins" },
    { label: "Interview Experiences", value: data?.total_experiences || 0, icon: MessageSquare, color: "bg-green-50 text-green-600", description: "Community submissions" },
    { label: "AI Mock Interviews", value: data?.total_mock_interviews || 0, icon: Brain, color: "bg-purple-50 text-purple-600", description: "Completed sessions" },
    { label: "Knowledge Base Size", value: (data?.total_experiences || 0) * 3, icon: TrendingUp, color: "bg-orange-50 text-orange-600", description: "Estimated questions" },
  ];

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Platform Analytics</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {metrics.map((m) => (
          <Card key={m.label}>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-lg ${m.color}`}>
                  <m.icon className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">{m.label}</p>
                  <p className="text-3xl font-bold">{m.value}</p>
                  <p className="text-xs text-muted-foreground mt-1">{m.description}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader><CardTitle>Growth Insights</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between py-3 border-b">
              <span className="text-sm font-medium">Avg Experiences per User</span>
              <span className="text-sm font-bold">
                {data?.total_users ? ((data?.total_experiences || 0) / data.total_users).toFixed(1) : "0"}
              </span>
            </div>
            <div className="flex items-center justify-between py-3 border-b">
              <span className="text-sm font-medium">Avg Mock Interviews per User</span>
              <span className="text-sm font-bold">
                {data?.total_users ? ((data?.total_mock_interviews || 0) / data.total_users).toFixed(1) : "0"}
              </span>
            </div>
            <div className="flex items-center justify-between py-3">
              <span className="text-sm font-medium">Platform Data Moat</span>
              <span className="text-sm font-bold text-green-600">
                {(data?.total_experiences || 0) > 100 ? "Strong" : (data?.total_experiences || 0) > 10 ? "Growing" : "Early Stage"}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
