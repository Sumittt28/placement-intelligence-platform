"use client";

import { ProfileSummary } from "@/components/dashboard/ProfileSummary";
import { PlacementStats } from "@/components/dashboard/PlacementStats";
import { RecentActivity } from "@/components/dashboard/RecentActivity";
import { PerformanceOverview } from "@/components/dashboard/PerformanceOverview";
import { TrendGraph } from "@/components/dashboard/TrendGraph";
import { useDashboard } from "@/hooks/useDashboard";
import { LoadingSpinner } from "@/components/ui/loading-spinner";

export default function DashboardPage() {
  const { data, isLoading, error } = useDashboard();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <LoadingSpinner />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="text-center py-20 text-muted-foreground">
        <p>Failed to load dashboard data.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Your placement preparation overview</p>
      </div>

      {/* Placement Stats */}
      <PlacementStats
        interviewsAttempted={data.stats.interviews_attempted}
        aiInterviewsCompleted={data.stats.ai_interviews_completed}
        contributionsSubmitted={data.stats.contributions_submitted}
        companyReportsViewed={data.stats.company_reports_viewed}
      />

      {/* Profile + Performance */}
      <div className="grid gap-6 md:grid-cols-2">
        <ProfileSummary
          fullName={data.profile_summary.full_name}
          batch={data.profile_summary.batch}
          resumeStatus={data.profile_summary.resume_status}
          targetCompanies={data.profile_summary.target_companies}
        />
        <PerformanceOverview
          communication={data.performance.communication}
          technical_depth={data.performance.technical_depth}
          problem_solving={data.performance.problem_solving}
          behavioral={data.performance.behavioral}
          project_discussions={data.performance.project_discussions}
        />
      </div>

      {/* Trend Graph */}
      <TrendGraph data={data.trends || []} />

      {/* Recent Activity */}
      <RecentActivity activities={data.recent_activity || []} />
    </div>
  );
}
