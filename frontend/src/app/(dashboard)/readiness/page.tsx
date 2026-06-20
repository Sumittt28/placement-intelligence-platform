"use client";

import { ReadinessScore } from "@/components/readiness/ReadinessScore";
import { ReadinessBreakdown } from "@/components/readiness/ReadinessBreakdown";
import { useOverallReadiness } from "@/hooks/useDashboard";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { EmptyState } from "@/components/ui/empty-state";
import { Target } from "lucide-react";

export default function ReadinessPage() {
  const { data, isLoading, error } = useOverallReadiness();

  if (isLoading) {
    return <div className="flex justify-center py-20"><LoadingSpinner /></div>;
  }

  if (error || !data) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Placement Readiness</h1>
          <p className="text-muted-foreground">Your readiness scores per target company</p>
        </div>
        <EmptyState
          icon={<Target className="h-12 w-12" />}
          title="Readiness data unavailable"
          description="Complete mock interviews and set target companies in your profile to see readiness scores."
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Placement Readiness</h1>
        <p className="text-muted-foreground">
          Explainable readiness scores — every percentage is traceable
        </p>
      </div>

      {/* Overall Score */}
      <div className="flex justify-center">
        <ReadinessScore percent={data.overall_readiness || 0} label="Overall Readiness" size="lg" />
      </div>

      {/* Per-Company Breakdown */}
      <ReadinessBreakdown companies={data.companies || []} />
    </div>
  );
}
