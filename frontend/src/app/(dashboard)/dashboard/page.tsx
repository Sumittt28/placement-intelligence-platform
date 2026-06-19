"use client";

import { useQuery } from "@tanstack/react-query";
import { dashboardAPI } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MessageSquare, Brain, Upload, Building2 } from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import type { DashboardData } from "@/types";

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => {
      const res = await dashboardAPI.get();
      return res.data.data as DashboardData;
    },
  });

  if (isLoading) {
    return <div className="flex items-center justify-center h-64"><p className="text-muted-foreground">Loading dashboard...</p></div>;
  }

  const d = data;
  const stats = [
    { label: "Interviews Attempted", value: d?.stats.interviews_attempted || 0, icon: MessageSquare, color: "text-blue-500" },
    { label: "AI Interviews", value: d?.stats.ai_interviews_completed || 0, icon: Brain, color: "text-purple-500" },
    { label: "Contributions", value: d?.stats.contributions_submitted || 0, icon: Upload, color: "text-green-500" },
    { label: "Reports Viewed", value: d?.stats.company_reports_viewed || 0, icon: Building2, color: "text-orange-500" },
  ];

  const perfData = d?.performance || { communication: 0, technical_depth: 0, problem_solving: 0, behavioral: 0, project_discussions: 0 };
  const radarItems = [
    { name: "Communication", value: perfData.communication },
    { name: "Technical", value: perfData.technical_depth },
    { name: "Problem Solving", value: perfData.problem_solving },
    { name: "Behavioral", value: perfData.behavioral },
    { name: "Project", value: perfData.project_discussions },
  ];

  return (
    <div className="space-y-6">
      {/* Profile Summary */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">{d?.profile_summary.full_name || "Student"}</h2>
              <p className="text-muted-foreground">Batch: {d?.profile_summary.batch || "N/A"}</p>
            </div>
            <Badge variant={d?.profile_summary.resume_status === "uploaded" ? "default" : "destructive"}>
              Resume: {d?.profile_summary.resume_status || "not_uploaded"}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s) => (
          <Card key={s.label}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{s.label}</p>
                  <p className="text-3xl font-bold mt-1">{s.value}</p>
                </div>
                <s.icon className={`h-8 w-8 ${s.color}`} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Performance Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>Performance Overview</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-4">
              {radarItems.map((item) => (
                <div key={item.name} className="flex items-center gap-4">
                  <span className="text-sm w-28 text-muted-foreground">{item.name}</span>
                  <div className="flex-1 bg-secondary rounded-full h-3">
                    <div
                      className="bg-primary rounded-full h-3 transition-all"
                      style={{ width: `${(item.value / 10) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium w-10 text-right">{item.value}/10</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Trend Graph */}
        <Card>
          <CardHeader><CardTitle>Performance Trends</CardTitle></CardHeader>
          <CardContent>
            {d?.trends && d.trends.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={d.trends.map((t, i) => ({ name: `#${i + 1}`, ...t.scores }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis domain={[0, 10]} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="communication" stroke="#3b82f6" strokeWidth={2} />
                  <Line type="monotone" dataKey="technical_depth" stroke="#8b5cf6" strokeWidth={2} />
                  <Line type="monotone" dataKey="problem_solving" stroke="#10b981" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[250px] text-muted-foreground">
                Complete mock interviews to see trends
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader><CardTitle>Recent Activity</CardTitle></CardHeader>
        <CardContent>
          {d?.recent_activity && d.recent_activity.length > 0 ? (
            <div className="space-y-3">
              {d.recent_activity.map((a, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b last:border-0">
                  <div>
                    <p className="text-sm font-medium">{a.action}</p>
                    {a.resource && <p className="text-xs text-muted-foreground">{a.resource}</p>}
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {new Date(a.created_at).toLocaleDateString()}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">No recent activity. Start by submitting an interview experience!</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
