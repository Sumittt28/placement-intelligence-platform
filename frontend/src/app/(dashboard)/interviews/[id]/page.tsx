"use client";

import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { InterviewChat } from "@/components/interviews/InterviewChat";
import { useInterview } from "@/hooks/useInterview";
import { useInterviewStore } from "@/stores/interviewStore";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function InterviewSessionPage() {
  const { id } = useParams();
  const router = useRouter();
  const { currentQuestion } = useInterviewStore();
  const { data: interview, isLoading } = useInterview(id as string);

  useEffect(() => {
    if (interview?.status === "completed") {
      router.push(`/interviews/${id}/replay`);
    }
  }, [interview, id, router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <LoadingSpinner />
      </div>
    );
  }

  // Build initial messages from existing questions or current question
  const initialMessages: { role: "ai" | "user"; content: string; topic?: string }[] = [];
  if (interview?.questions) {
    for (const q of interview.questions) {
      initialMessages.push({
        role: "ai",
        content: q.question_text,
        topic: q.topic || undefined,
      });
    }
  } else if (currentQuestion) {
    initialMessages.push({
      role: "ai",
      content: currentQuestion.question_text,
      topic: currentQuestion.topic || undefined,
    });
  }

  return (
    <div className="space-y-4">
      {/* Interview Header */}
      <Card>
        <CardContent className="pt-4 pb-3">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-semibold capitalize">
              {interview?.interview_type || "Mock"} Interview
            </h1>
            <Badge variant="outline">{interview?.difficulty || "Medium"}</Badge>
            <Badge variant="outline">{interview?.mode || "text"}</Badge>
            <Badge variant="secondary">{interview?.status || "in_progress"}</Badge>
          </div>
        </CardContent>
      </Card>

      {/* Chat Interface */}
      <InterviewChat
        interviewId={id as string}
        mode={(interview?.mode as "text" | "voice") || "text"}
        initialMessages={initialMessages}
      />
    </div>
  );
}
