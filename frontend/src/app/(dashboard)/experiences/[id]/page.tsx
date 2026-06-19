"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { experienceAPI } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { InterviewExperience } from "@/types";

export default function ExperienceDetailPage() {
  const { id } = useParams();
  const { data, isLoading } = useQuery({
    queryKey: ["experience", id],
    queryFn: async () => { const res = await experienceAPI.get(id as string); return res.data.data as InterviewExperience; },
  });

  if (isLoading) return <p>Loading...</p>;
  if (!data) return <p>Experience not found</p>;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold">{data.company_name} - {data.role}</h2>
        <div className="flex gap-2 mt-2">
          <Badge variant="outline">{data.round_type}</Badge>
          <Badge variant="outline">{data.difficulty}</Badge>
          <Badge>{data.outcome}</Badge>
          <span className="text-sm text-muted-foreground">{new Date(data.interview_date).toLocaleDateString()}</span>
        </div>
      </div>

      {data.student_notes && (
        <Card>
          <CardHeader><CardTitle>Notes</CardTitle></CardHeader>
          <CardContent><p className="text-sm">{data.student_notes}</p></CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle>Questions Asked ({data.questions.length})</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          {data.questions.map((q, i) => (
            <div key={q.id} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <Badge variant="secondary">{q.topic}</Badge>
                <Badge variant={q.could_answer === "Yes" ? "default" : q.could_answer === "No" ? "destructive" : "outline"}>
                  {q.could_answer}
                </Badge>
              </div>
              <p className="text-sm">{q.question_text}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      {data.ai_extracted && (
        <Card>
          <CardHeader><CardTitle>AI Insights</CardTitle></CardHeader>
          <CardContent>
            <pre className="text-xs bg-secondary p-4 rounded-lg overflow-auto">{JSON.stringify(data.ai_extracted, null, 2)}</pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
