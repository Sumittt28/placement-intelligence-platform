"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { experienceAPI, companyAPI } from "@/lib/api";
import { Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

const schema = z.object({
  company_id: z.string().min(1, "Select a company"),
  role: z.string().min(1, "Role is required"),
  interview_date: z.string().min(1, "Date is required"),
  round_type: z.string().min(1, "Round type is required"),
  difficulty: z.string().min(1, "Difficulty is required"),
  outcome: z.string().min(1, "Outcome is required"),
  student_notes: z.string().optional(),
  questions: z.array(z.object({
    topic: z.string().min(1, "Topic required"),
    question_text: z.string().min(1, "Question required"),
    could_answer: z.string().min(1, "Required"),
  })).min(1, "At least one question"),
});

type FormData = z.infer<typeof schema>;

export default function NewExperiencePage() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: companies } = useQuery({
    queryKey: ["companies"],
    queryFn: async () => { const res = await companyAPI.list(); return res.data.data as { id: string; name: string }[]; },
  });

  const { register, handleSubmit, control, setValue, watch, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { questions: [{ topic: "", question_text: "", could_answer: "" }] },
  });

  const { fields, append, remove } = useFieldArray({ control, name: "questions" });

  const mutation = useMutation({
    mutationFn: (data: FormData) => experienceAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["experiences"] });
      toast.success("Experience submitted! AI is processing...");
      router.push("/experiences");
    },
    onError: () => toast.error("Failed to submit"),
  });

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold">Submit Interview Experience</h2>

      <form onSubmit={handleSubmit((data) => mutation.mutate(data))} className="space-y-6">
        <Card>
          <CardHeader><CardTitle>Interview Details</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Company</Label>
                <Select onValueChange={(v: string | null) => { if (v) setValue("company_id", v); }}>
                  <SelectTrigger><SelectValue placeholder="Select company" /></SelectTrigger>
                  <SelectContent>
                    {(companies || []).map((c: { id: string; name: string }) => (
                      <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.company_id && <p className="text-sm text-destructive">{errors.company_id.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Role</Label>
                <Input placeholder="e.g., SDE Intern" {...register("role")} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Interview Date</Label>
                <Input type="date" {...register("interview_date")} />
              </div>
              <div className="space-y-2">
                <Label>Round Type</Label>
                <Select onValueChange={(v: string | null) => { if (v) setValue("round_type", v); }}>
                  <SelectTrigger><SelectValue placeholder="Select round" /></SelectTrigger>
                  <SelectContent>
                    {["OA", "Technical", "HM", "HR", "System Design", "Other"].map((r) => (
                      <SelectItem key={r} value={r}>{r}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Difficulty</Label>
                <Select onValueChange={(v: string | null) => { if (v) setValue("difficulty", v); }}>
                  <SelectTrigger><SelectValue placeholder="Difficulty" /></SelectTrigger>
                  <SelectContent>
                    {["Easy", "Medium", "Hard"].map((d) => (
                      <SelectItem key={d} value={d}>{d}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Outcome</Label>
                <Select onValueChange={(v: string | null) => { if (v) setValue("outcome", v); }}>
                  <SelectTrigger><SelectValue placeholder="Outcome" /></SelectTrigger>
                  <SelectContent>
                    {["Selected", "Rejected", "Waiting", "Unknown"].map((o) => (
                      <SelectItem key={o} value={o}>{o}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label>Notes (optional)</Label>
              <Textarea placeholder="Any additional notes..." {...register("student_notes")} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Questions Asked</CardTitle>
              <Button type="button" variant="outline" size="sm" onClick={() => append({ topic: "", question_text: "", could_answer: "" })}>
                <Plus className="h-4 w-4 mr-1" /> Add Question
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {fields.map((field, index) => (
              <div key={field.id} className="border rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Question {index + 1}</span>
                  {fields.length > 1 && (
                    <Button type="button" variant="ghost" size="sm" onClick={() => remove(index)}>
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label>Topic</Label>
                    <Input placeholder="e.g., Arrays, SQL, React" {...register(`questions.${index}.topic`)} />
                  </div>
                  <div className="space-y-1">
                    <Label>Could Answer?</Label>
                    <Select onValueChange={(v: string | null) => { if (v) setValue(`questions.${index}.could_answer`, v); }}>
                      <SelectTrigger><SelectValue placeholder="Select" /></SelectTrigger>
                      <SelectContent>
                        {["Yes", "Partially", "No"].map((a) => (
                          <SelectItem key={a} value={a}>{a}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label>Question</Label>
                  <Textarea placeholder="Write the exact question..." {...register(`questions.${index}.question_text`)} />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Button type="submit" className="w-full" size="lg" disabled={mutation.isPending}>
          {mutation.isPending ? "Submitting..." : "Submit Experience"}
        </Button>
      </form>
    </div>
  );
}
