"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Building2, Calendar, HelpCircle, CheckCircle, XCircle, MinusCircle } from "lucide-react";
import type { InterviewExperience } from "@/types";

interface ExperienceDetailProps {
  experience: InterviewExperience;
}

const answerIcon = {
  Yes: <CheckCircle className="h-4 w-4 text-green-500" />,
  Partially: <MinusCircle className="h-4 w-4 text-yellow-500" />,
  No: <XCircle className="h-4 w-4 text-red-500" />,
};

export function ExperienceDetail({ experience }: ExperienceDetailProps) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-xl">{experience.role}</CardTitle>
              <div className="flex items-center gap-1 mt-1 text-muted-foreground">
                <Building2 className="h-4 w-4" />
                {experience.company_name || "Company"}
              </div>
            </div>
            <Badge variant={experience.outcome === "Selected" ? "default" : experience.outcome === "Rejected" ? "destructive" : "secondary"}>
              {experience.outcome}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Badge variant="outline">{experience.round_type}</Badge>
            <Badge variant="outline">{experience.difficulty}</Badge>
            <span className="flex items-center gap-1 text-sm text-muted-foreground">
              <Calendar className="h-3.5 w-3.5" />
              {new Date(experience.interview_date).toLocaleDateString()}
            </span>
          </div>
          {experience.student_notes && (
            <p className="mt-4 text-sm text-muted-foreground border-l-2 pl-3">{experience.student_notes}</p>
          )}
        </CardContent>
      </Card>

      {/* Questions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <HelpCircle className="h-5 w-5" />
            Questions ({experience.questions?.length || 0})
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {(experience.questions || []).map((q, idx) => (
            <div key={q.id || idx} className="rounded-lg border p-4 space-y-2">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs">{q.topic}</Badge>
                  <span className="text-xs text-muted-foreground">Q{idx + 1}</span>
                </div>
                <div className="flex items-center gap-1 text-sm">
                  {answerIcon[q.could_answer as keyof typeof answerIcon] || null}
                  <span className="text-xs">{q.could_answer}</span>
                </div>
              </div>
              <p className="text-sm">{q.question_text}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* AI Extracted Data */}
      {experience.ai_extracted && Object.keys(experience.ai_extracted).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">AI-Extracted Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {Array.isArray((experience.ai_extracted as Record<string, unknown>)?.topics) &&
                ((experience.ai_extracted as Record<string, unknown>).topics as string[]).map((t: string, i: number) => (
                  <Badge key={i} variant="secondary">{t}</Badge>
                ))}
              {Array.isArray((experience.ai_extracted as Record<string, unknown>)?.skills) &&
                ((experience.ai_extracted as Record<string, unknown>).skills as string[]).map((s: string, i: number) => (
                  <Badge key={`s-${i}`} variant="outline">{s}</Badge>
                ))}
              {Array.isArray((experience.ai_extracted as Record<string, unknown>)?.technologies) &&
                ((experience.ai_extracted as Record<string, unknown>).technologies as string[]).map((t: string, i: number) => (
                  <Badge key={`t-${i}`} variant="outline">{t}</Badge>
                ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
