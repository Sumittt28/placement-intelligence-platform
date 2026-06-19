"use client";

import { ResumeUpload } from "@/components/resume/ResumeUpload";
import { ResumeInsights } from "@/components/resume/ResumeInsights";
import { useQuery } from "@tanstack/react-query";
import { resumeAPI } from "@/lib/api";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import type { ResumeInsights as ResumeInsightsType } from "@/types";

export default function ResumePage() {
  const { data: insights, isLoading } = useQuery({
    queryKey: ["resumeInsights"],
    queryFn: async () => {
      const res = await resumeAPI.insights();
      return res.data.data as ResumeInsightsType;
    },
    retry: false,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Resume Intelligence</h1>
        <p className="text-muted-foreground">
          Upload your resume for AI-powered skill extraction and gap analysis
        </p>
      </div>

      <ResumeUpload />

      {isLoading ? (
        <div className="flex justify-center py-10"><LoadingSpinner /></div>
      ) : insights ? (
        <ResumeInsights data={insights} />
      ) : (
        <div className="text-center py-8 text-muted-foreground text-sm">
          Upload your resume to see AI-generated insights.
        </div>
      )}
    </div>
  );
}
