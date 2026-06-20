"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { QuestionEntry } from "./QuestionEntry";
import { useSubmitExperience } from "@/hooks/useInterview";
import { Plus, Send } from "lucide-react";
import { toast } from "sonner";

interface QuestionData {
  topic: string;
  question_text: string;
  could_answer: string;
}

export function ExperienceForm() {
  const router = useRouter();
  const submitMutation = useSubmitExperience();

  const [form, setForm] = useState({
    company_id: "",
    role: "",
    interview_date: "",
    round_type: "",
    difficulty: "",
    outcome: "",
    student_notes: "",
  });

  const [questions, setQuestions] = useState<QuestionData[]>([
    { topic: "", question_text: "", could_answer: "Yes" },
  ]);

  const handleFieldChange = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleQuestionChange = (index: number, field: keyof QuestionData, value: string) => {
    setQuestions((prev) => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      return updated;
    });
  };

  const addQuestion = () => {
    setQuestions((prev) => [...prev, { topic: "", question_text: "", could_answer: "Yes" }]);
  };

  const removeQuestion = (index: number) => {
    setQuestions((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!form.role || !form.interview_date || !form.round_type || !form.difficulty || !form.outcome) {
      toast.error("Please fill in all required fields.");
      return;
    }

    const validQuestions = questions.filter((q) => q.question_text.trim());
    if (validQuestions.length === 0) {
      toast.error("Please add at least one question.");
      return;
    }

    submitMutation.mutate(
      { ...form, questions: validQuestions },
      {
        onSuccess: () => {
          toast.success("Experience submitted successfully!");
          router.push("/experiences");
        },
        onError: (err: unknown) => {
          const axiosErr = err as { response?: { data?: { error?: string } } };
          toast.error(axiosErr.response?.data?.error || "Submission failed");
        },
      }
    );
  };

  return (
    <form onSubmit={handleSubmit}>
      <Card>
        <CardHeader>
          <CardTitle>Submit Interview Experience</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Basic Info */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label>Role *</Label>
              <Input
                placeholder="e.g., Software Engineer"
                value={form.role}
                onChange={(e) => handleFieldChange("role", e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Interview Date *</Label>
              <Input
                type="date"
                value={form.interview_date}
                onChange={(e) => handleFieldChange("interview_date", e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Round Type *</Label>
              <Select value={form.round_type} onValueChange={(v) => handleFieldChange("round_type", v)}>
                <SelectTrigger><SelectValue placeholder="Select round" /></SelectTrigger>
                <SelectContent>
                  {["OA", "Technical", "HM", "HR", "System Design", "Other"].map((r) => (
                    <SelectItem key={r} value={r}>{r}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Difficulty *</Label>
              <Select value={form.difficulty} onValueChange={(v) => handleFieldChange("difficulty", v)}>
                <SelectTrigger><SelectValue placeholder="Select difficulty" /></SelectTrigger>
                <SelectContent>
                  {["Easy", "Medium", "Hard"].map((d) => (
                    <SelectItem key={d} value={d}>{d}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Outcome *</Label>
              <Select value={form.outcome} onValueChange={(v) => handleFieldChange("outcome", v)}>
                <SelectTrigger><SelectValue placeholder="Select outcome" /></SelectTrigger>
                <SelectContent>
                  {["Selected", "Rejected", "Waiting", "Unknown"].map((o) => (
                    <SelectItem key={o} value={o}>{o}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Questions */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label className="text-base">Questions</Label>
              <Button type="button" variant="outline" size="sm" onClick={addQuestion}>
                <Plus className="mr-1 h-4 w-4" /> Add Question
              </Button>
            </div>
            {questions.map((q, i) => (
              <QuestionEntry
                key={i}
                index={i}
                data={q}
                onChange={handleQuestionChange}
                onRemove={removeQuestion}
                removable={questions.length > 1}
              />
            ))}
          </div>

          {/* Notes */}
          <div className="space-y-1.5">
            <Label>Student Notes (optional)</Label>
            <Textarea
              placeholder="Any additional notes about the interview..."
              value={form.student_notes}
              onChange={(e) => handleFieldChange("student_notes", e.target.value)}
              rows={3}
            />
          </div>

          <Button type="submit" disabled={submitMutation.isPending} className="w-full">
            <Send className="mr-2 h-4 w-4" />
            {submitMutation.isPending ? "Submitting..." : "Submit Experience"}
          </Button>
        </CardContent>
      </Card>
    </form>
  );
}
