"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle } from "lucide-react";
import type { Weakness } from "@/types";

const severityColors: Record<string, string> = { low: "bg-yellow-100 text-yellow-800", medium: "bg-orange-100 text-orange-800", high: "bg-red-100 text-red-800" };

export default function WeaknessesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["weaknesses"],
    queryFn: async () => {
      const { weaknessAPI } = await import("@/lib/api");
      const res = await weaknessAPI.list();
      return res.data.data as Weakness[];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Weakness Analysis</h2>
        <p className="text-muted-foreground">Recurring weaknesses detected across your mock interviews</p>
      </div>

      {isLoading ? <p>Loading...</p> : (data || []).length === 0 ? (
        <Card><CardContent className="py-12 text-center"><AlertTriangle className="h-10 w-10 mx-auto mb-4 text-muted-foreground" /><p className="text-muted-foreground">No weaknesses detected yet. Complete more mock interviews.</p></CardContent></Card>
      ) : (
        <div className="grid gap-4">
          {(data || []).map((w) => (
            <Card key={w.id}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-lg capitalize">{w.topic.replace("_", " ")}</h3>
                    <div className="flex gap-2 mt-2">
                      {w.severity && <Badge className={severityColors[w.severity] || ""}>{w.severity}</Badge>}
                      <Badge variant="outline">{w.category || "general"}</Badge>
                      <Badge variant="secondary">Appeared {w.occurrence_count}x</Badge>
                    </div>
                    {w.recommended_actions.length > 0 && (
                      <div className="mt-3">
                        <p className="text-sm font-medium mb-1">Recommended Actions:</p>
                        <ul className="text-sm text-muted-foreground list-disc list-inside">
                          {w.recommended_actions.map((a, i) => <li key={i}>{a}</li>)}
                        </ul>
                      </div>
                    )}
                  </div>
                  <div className="text-right text-sm text-muted-foreground">
                    <p>First: {new Date(w.first_detected).toLocaleDateString()}</p>
                    <p>Last: {new Date(w.last_detected).toLocaleDateString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
