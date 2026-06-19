"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ReadinessScore } from "./ReadinessScore";
import { Target, AlertTriangle, Building2 } from "lucide-react";
import type { CompanyReadiness } from "@/types";

interface ReadinessBreakdownProps {
  companies: CompanyReadiness[];
}

export function ReadinessBreakdown({ companies }: ReadinessBreakdownProps) {
  if (companies.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center">
          <Target className="h-8 w-8 mx-auto mb-3 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            Set target companies in your profile to see readiness scores.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {companies.map((company) => (
        <Card key={company.company_id}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Building2 className="h-5 w-5" />
                {company.company_name}
              </CardTitle>
              <Badge
                variant={
                  company.readiness_percent >= 80 ? "default" :
                  company.readiness_percent >= 60 ? "secondary" : "destructive"
                }
              >
                {Math.round(company.readiness_percent)}% Ready
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Dimension scores */}
            {(company.dimensions || []).map((dim, idx) => (
              <div key={idx} className="space-y-1.5">
                <div className="flex items-center justify-between text-sm">
                  <span>{dim.name}</span>
                  <span className="font-medium">{dim.score}/10</span>
                </div>
                <Progress value={(dim.score / 10) * 100} className="h-2" />
                {dim.gap && (
                  <p className="text-xs text-muted-foreground flex items-start gap-1">
                    <AlertTriangle className="h-3 w-3 mt-0.5 shrink-0 text-yellow-500" />
                    {dim.gap}
                  </p>
                )}
              </div>
            ))}

            {/* Recommendations */}
            {company.recommendations && company.recommendations.length > 0 && (
              <div className="mt-3 rounded-lg bg-muted p-3">
                <p className="text-xs font-medium mb-1">Recommendations to close gaps:</p>
                <ul className="space-y-1">
                  {company.recommendations.map((rec, i) => (
                    <li key={i} className="text-xs text-muted-foreground">• {rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
