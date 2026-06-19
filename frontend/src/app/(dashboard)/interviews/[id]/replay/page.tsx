"use client";

import { useParams } from "next/navigation";
import { ReplayViewer } from "@/components/interviews/ReplayViewer";
import { useInterviewReplay } from "@/hooks/useInterview";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function InterviewReplayPage() {
  const { id } = useParams();
  const { data, isLoading, error } = useInterviewReplay(id as string);

  return (
    <div className="space-y-6">
      <Link href="/interviews">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="mr-1 h-4 w-4" /> Back to Interviews
        </Button>
      </Link>

      <div>
        <h1 className="text-2xl font-bold">Interview Replay</h1>
        <p className="text-muted-foreground">Review your Q&A, evaluations, and ideal answers</p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20"><LoadingSpinner /></div>
      ) : error || !data ? (
        <div className="text-center py-20 text-muted-foreground">Replay data not found.</div>
      ) : (
        <ReplayViewer questions={data.questions || []} evaluation={data.evaluation} />
      )}
    </div>
  );
}
