"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useStartInterview } from "@/hooks/useInterview";
import { useCompanyList } from "@/hooks/useCompany";
import { Brain, Play } from "lucide-react";
import { toast } from "sonner";

export function InterviewConfig() {
  const router = useRouter();
  const startMutation = useStartInterview();
  const { data: companies } = useCompanyList();

  const [config, setConfig] = useState({
    interview_type: "",
    difficulty: "",
    company_id: "",
    mode: "text",
  });

  const handleStart = () => {
    if (!config.interview_type || !config.difficulty) {
      toast.error("Please select interview type and difficulty.");
      return;
    }

    startMutation.mutate(
      {
        interview_type: config.interview_type,
        difficulty: config.difficulty,
        company_id: config.company_id || undefined,
        mode: config.mode,
      },
      {
        onSuccess: (res) => {
          const data = res.data.data as { interview_id: string } | null;
          const interviewId = data?.interview_id;
          if (interviewId) {
            router.push(`/interviews/${interviewId}`);
          }
        },
        onError: (err) => {
          toast.error(`Failed to start: ${(err as Error).message}`);
        },
      }
    );
  };

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-5 w-5" />
          Configure Mock Interview
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-1.5">
            <Label>Interview Type *</Label>
            <Select value={config.interview_type} onValueChange={(v) => setConfig((p) => ({ ...p, interview_type: v }))}>
              <SelectTrigger><SelectValue placeholder="Select type" /></SelectTrigger>
              <SelectContent>
                {[
                  { value: "behavioral", label: "Behavioral" },
                  { value: "technical", label: "Technical" },
                  { value: "hm", label: "Hiring Manager" },
                  { value: "project", label: "Project Discussion" },
                  { value: "company", label: "Company Specific" },
                  { value: "custom", label: "Custom" },
                ].map((t) => (
                  <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <Label>Difficulty *</Label>
            <Select value={config.difficulty} onValueChange={(v) => setConfig((p) => ({ ...p, difficulty: v }))}>
              <SelectTrigger><SelectValue placeholder="Select difficulty" /></SelectTrigger>
              <SelectContent>
                {["Easy", "Medium", "Hard"].map((d) => (
                  <SelectItem key={d} value={d}>{d}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <Label>Target Company (optional)</Label>
            <Select value={config.company_id} onValueChange={(v) => setConfig((p) => ({ ...p, company_id: v === "none" ? "" : v }))}>
              <SelectTrigger><SelectValue placeholder="Any company" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="none">Any Company</SelectItem>
                {(companies || []).map((c) => (
                  <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <Label>Mode</Label>
            <Select value={config.mode} onValueChange={(v) => setConfig((p) => ({ ...p, mode: v }))}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="text">Text</SelectItem>
                <SelectItem value="voice">Voice</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="rounded-lg bg-muted p-4 text-sm text-muted-foreground space-y-1">
          <p>• Interview will include <strong>8-12 questions</strong> including follow-ups</p>
          <p>• Questions are <strong>resume-aware</strong> and <strong>company-specific</strong></p>
          <p>• Follow-ups are <strong>dynamic</strong> — every interview is unique</p>
          <p>• You&apos;ll receive a <strong>detailed evaluation</strong> after completion</p>
        </div>

        <Button onClick={handleStart} disabled={startMutation.isPending} className="w-full" size="lg">
          <Play className="mr-2 h-4 w-4" />
          {startMutation.isPending ? "Starting..." : "Start Interview"}
        </Button>
      </CardContent>
    </Card>
  );
}
