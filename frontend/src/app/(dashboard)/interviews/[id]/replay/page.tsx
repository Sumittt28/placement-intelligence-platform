"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { interviewAPI } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

export default function ReplayPage() {
  const { id } = useParams();
  const { data, isLoading } = useQuery({
    queryKey: ["replay", id],
    queryFn: async () => { const res = await interviewAPI.replay(id as string); return res.data.data; },
  });

  if (isLoading) return <p>Loading replay...</p>;
  if (!data) return <p>Replay not found</p>;

  const { interview, questions, evaluation } = data;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold capitalize">{interview.interview_type} Interview Replay</h2>
        <p className="text-muted-foreground">{interview.difficulty} | {interview.mode} | {new Date(interview.started_at).toLocaleDateString()}</p>
      </div>

      {/* Evaluation Summary */}
      {evaluation && (
        <Card>
          <CardHeader><CardTitle>Evaluation Summary</CardTitle></CardHeader>
          <CardContent>
            <div className="text-center mb-6">
              <p className="text-5xl font-bold text-primary">{evaluation.overall_score}/10</p>
              <p className="text-muted-foreground mt-2">Overall Score</p>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
              {["communication", "technical", "confidence", "problem_solving", "behavioral", "project"].map((dim) => {
                const d = evaluation[dim];
                return (
                  <div key={dim} className="text-center p-3 border rounded-lg">
                    <p className="text-2xl font-bold">{d.score}/10</p>
                    <p className="text-xs capitalize text-muted-foreground">{dim.replace("_", " ")}</p>
                    <p className="text-xs mt-1">{d.reason}</p>
                  </div>
                );
              })}
            </div>
            <p className="text-sm">{evaluation.overall_feedback}</p>
            {evaluation.strengths?.length > 0 && (
              <div className="mt-4">
                <p className="text-sm font-medium mb-2">Strengths:</p>
                <div className="flex flex-wrap gap-2">{evaluation.strengths.map((s: string, i: number) => <Badge key={i} variant="outline" className="bg-green-50">{s}</Badge>)}</div>
              </div>
            )}
            {evaluation.improvements?.length > 0 && (
              <div className="mt-4">
                <p className="text-sm font-medium mb-2">Areas to Improve:</p>
                <div className="flex flex-wrap gap-2">{evaluation.improvements.map((s: string, i: number) => <Badge key={i} variant="outline" className="bg-red-50">{s}</Badge>)}</div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Q&A Replay */}
      <Card>
        <CardHeader><CardTitle>Interview Transcript</CardTitle></CardHeader>
        <CardContent className="space-y-6">
          {questions.map((q: { sequence_num: number; question_text: string; topic?: string; student_answer?: string; ideal_answer?: string; feedback?: string }, i: number) => (
            <div key={i}>
              <div className="mb-3">
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant="outline">Q{q.sequence_num}</Badge>
                  {q.topic && <Badge variant="secondary">{q.topic}</Badge>}
                </div>
                <p className="font-medium">{q.question_text}</p>
              </div>
              {q.student_answer && (
                <div className="bg-secondary/50 rounded-lg p-3 mb-2">
                  <p className="text-xs font-medium text-muted-foreground mb-1">Your Answer:</p>
                  <p className="text-sm">{q.student_answer}</p>
                </div>
              )}
              {q.ideal_answer && (
                <div className="bg-green-50 rounded-lg p-3 mb-2">
                  <p className="text-xs font-medium text-green-700 mb-1">Ideal Answer:</p>
                  <p className="text-sm">{q.ideal_answer}</p>
                </div>
              )}
              {q.feedback && (
                <p className="text-sm text-muted-foreground italic">{q.feedback}</p>
              )}
              {i < questions.length - 1 && <Separator className="mt-4" />}
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
