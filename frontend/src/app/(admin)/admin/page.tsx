"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { adminAPI } from "@/lib/api";
import { Users, MessageSquare, Brain, Activity } from "lucide-react";

export default function AdminDashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["admin-analytics"],
    queryFn: async () => {
      const res = await adminAPI.analytics();
      return res.data.data as {
        total_users: number;
        total_experiences: number;
        total_mock_interviews: number;
      };
    },
  });

  if (isLoading) return <p className="text-muted-foreground">Loading admin dashboard...</p>;

  const stats = [
    { label: "Total Users", value: data?.total_users || 0, icon: Users, color: "text-blue-500" },
    { label: "Total Experiences", value: data?.total_experiences || 0, icon: MessageSquare, color: "text-green-500" },
    { label: "Mock Interviews", value: data?.total_mock_interviews || 0, icon: Brain, color: "text-purple-500" },
    { label: "Platform Health", value: "Healthy", icon: Activity, color: "text-emerald-500" },
  ];

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Platform Overview</h2>

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
    </div>
  );
}
