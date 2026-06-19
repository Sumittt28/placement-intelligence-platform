"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { interviewAPI, companyAPI } from "@/lib/api";
import { useInterviewStore } from "@/stores/interviewStore";
import { toast } from "sonner";

export default function NewInterviewPage() {
  const router = useRouter();
  const { setInterview } = useInterviewStore();
  const [config, setConfig] = useState({ interview_type: "", difficulty: "", company_id: "", mode: "text" });

  const { data: companies } = useQuery({
    queryKey: ["companies"],
    queryFn: async () => { const res = await companyAPI.list(); return res.data.data; },
  });

  const mutation = useMutation({
    mutationFn: () => interviewAPI.start(config),
    onSuccess: (res) => {
      const { interview_id, first_question } = res.data.data;
      setInterview(interview_id, first_question);
      toast.success("Interview started!");
      router.push(`/interviews/${interview_id}`);
    },
    onError: () => toast.error("Failed to start interview"),
  });

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold">Configure Mock Interview</h2>

      <Card>
        <CardHeader><CardTitle>Interview Settings</CardTitle></CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label>Interview Type</Label>
            <Select onValueChange={(v) => v && setConfig({ ...config, interview_type: v })}>
              <SelectTrigger><SelectValue placeholder="Select type" /></SelectTrigger>
              <SelectContent>
                {["behavioral", "technical", "hm", "project", "company", "custom"].map((t) => (
                  <SelectItem key={t} value={t} className="capitalize">{t === "hm" ? "Hiring Manager" : t}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Difficulty</Label>
            <Select onValueChange={(v) => v && setConfig({ ...config, difficulty: v })}>
              <SelectTrigger><SelectValue placeholder="Select difficulty" /></SelectTrigger>
              <SelectContent>
                {["Easy", "Medium", "Hard"].map((d) => (
                  <SelectItem key={d} value={d}>{d}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Target Company (optional)</Label>
            <Select onValueChange={(v) => v && setConfig({ ...config, company_id: v })}>
              <SelectTrigger><SelectValue placeholder="Any company" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="none">No specific company</SelectItem>
                {(companies || []).map((c: { id: string; name: string }) => (
                  <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Mode</Label>
            <Select onValueChange={(v) => v && setConfig({ ...config, mode: v })} defaultValue="text">
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="text">Text</SelectItem>
                <SelectItem value="voice">Voice</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button
            className="w-full"
            size="lg"
            disabled={!config.interview_type || !config.difficulty || mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            {mutation.isPending ? "Starting..." : "Start Interview"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
