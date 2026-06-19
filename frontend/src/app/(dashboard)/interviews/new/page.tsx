"use client";

import { InterviewConfig } from "@/components/interviews/InterviewConfig";

export default function NewInterviewPage() {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold">Start Mock Interview</h1>
        <p className="text-muted-foreground">
          Configure your AI-powered interview session
        </p>
      </div>
      <InterviewConfig />
    </div>
  );
}
