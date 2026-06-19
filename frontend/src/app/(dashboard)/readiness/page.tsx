"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { readinessAPI } from "@/lib/api";
import { Target } from "lucide-react";
import type { CompanyReadiness } from "@/types";

export default function ReadinessPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["readiness"],
    queryFn: async () => { const res = await readinessAPI.overall(); return res.data.data; },
  });

  if (isLoading) return <p>Loading...</p>;

  const overall = data?.overall_readiness || 0;
  const companies: CompanyReadiness[] = data?.companies || [];

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Placement Readiness</h2>

      {/* Overall */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-center">
            <div className="relative w-40 h-40">
              <svg className="w-40 h-40 -rotate-90" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="50" fill="none" stroke="#e5e7eb" strokeWidth="10" />
                <circle cx="60" cy="60" r="50" fill="none" stroke="#3b82f6" strokeWidth="10"
                  strokeDasharray={`${overall * 3.14} ${314 - overall * 3.14}`}
                  strokeLinecap="round" />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-3xl font-bold">{overall}%</span>
              </div>
            </div>
          </div>
          <p className="text-center text-muted-foreground mt-4">Overall Placement Readiness</p>
        </CardContent>
      </Card>

      {/* Per Company */}
      {companies.length > 0 ? (
        <div className="grid gap-4">
          {companies.map((c) => (
            <Card key={c.company_id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5 text-primary" /> {c.company_name}
                  </CardTitle>
                  <span className="text-2xl font-bold text-primary">{c.readiness_percent}%</span>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {c.dimensions.map((d) => (
                    <div key={d.name}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="capitalize">{d.name.replace("_", " ")}</span>
                        <span className="font-medium">{d.score}/10</span>
                      </div>
                      <div className="bg-secondary rounded-full h-2">
                        <div className="bg-primary rounded-full h-2" style={{ width: `${d.score * 10}%` }} />
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">{d.gap}</p>
                    </div>
                  ))}
                </div>
                {c.recommendations.length > 0 && (
                  <div className="mt-4 pt-4 border-t">
                    <p className="text-sm font-medium mb-2">Recommendations:</p>
                    {c.recommendations.map((r, i) => <p key={i} className="text-sm text-muted-foreground">• {r}</p>)}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card><CardContent className="py-8 text-center text-muted-foreground">Add target companies in your profile to see company-specific readiness scores.</CardContent></Card>
      )}
    </div>
  );
}
