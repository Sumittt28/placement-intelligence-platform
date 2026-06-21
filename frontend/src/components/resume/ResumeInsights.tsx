"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Code, Briefcase, FolderOpen, Lightbulb, AlertTriangle, CheckCircle } from "lucide-react";
import type { ResumeInsights as ResumeInsightsType } from "@/types";

interface ResumeInsightsProps {
  data: ResumeInsightsType;
}

export function ResumeInsights({ data }: ResumeInsightsProps) {
  return (
    <div className="space-y-4">
      {/* Skills */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <Code className="h-4 w-4" />
            Skills & Technologies
          </CardTitle>
        </CardHeader>
        <CardContent>
          {(data.skills?.length || 0) === 0 && (data.technologies?.length || 0) === 0 ? (
            <div className="text-center py-4">
              <p className="text-sm text-muted-foreground">
                No skills extracted yet. This can happen if the AI service is temporarily unavailable.
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Try re-uploading your resume, or check back later.
              </p>
            </div>
          ) : (
          <div className="flex flex-wrap gap-2">
            {(data.skills || []).map((s, i) => (
              <Badge key={i} variant="default">{s}</Badge>
            ))}
            {(data.technologies || []).map((t, i) => (
              <Badge key={`t-${i}`} variant="secondary">{t}</Badge>
            ))}
          </div>
          )}
          {data.domains && data.domains.length > 0 && (
            <div className="mt-3">
              <p className="text-xs text-muted-foreground mb-1">Domains</p>
              <div className="flex flex-wrap gap-1">
                {data.domains.map((d, i) => (
                  <Badge key={i} variant="outline" className="text-xs">{d}</Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Projects */}
      {data.projects && data.projects.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <FolderOpen className="h-4 w-4" />
              Projects
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {data.projects.map((p, i) => (
              <div key={i} className="rounded-lg border p-3">
                <h4 className="font-medium text-sm">{p.name}</h4>
                <p className="text-xs text-muted-foreground mt-1">{p.description}</p>
                <div className="flex flex-wrap gap-1 mt-2">
                  {(p.technologies || []).map((t, j) => (
                    <Badge key={j} variant="outline" className="text-xs">{t}</Badge>
                  ))}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Experience */}
      {data.experience && data.experience.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Briefcase className="h-4 w-4" />
              Experience
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {data.experience.map((exp, i) => (
              <div key={i} className="border-l-2 pl-3 py-1">
                <p className="text-sm font-medium">{exp.title}</p>
                <p className="text-xs text-muted-foreground">{exp.company} · {exp.duration}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* AI Insights */}
      {data.insights && (
        <div className="grid gap-4 sm:grid-cols-2">
          {data.insights.strength_areas && data.insights.strength_areas.length > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  Strengths
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-1">
                  {data.insights.strength_areas.map((s, i) => (
                    <li key={i} className="text-sm flex items-start gap-2">
                      <CheckCircle className="h-3.5 w-3.5 mt-0.5 text-green-500 shrink-0" />
                      {s}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {data.insights.missing_skills && data.insights.missing_skills.length > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <AlertTriangle className="h-4 w-4 text-yellow-500" />
                  Missing Skills
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-1">
                  {data.insights.missing_skills.map((s, i) => (
                    <li key={i} className="text-sm flex items-start gap-2">
                      <AlertTriangle className="h-3.5 w-3.5 mt-0.5 text-yellow-500 shrink-0" />
                      {s}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Potential Interview Topics */}
      {data.insights?.potential_interview_topics && data.insights.potential_interview_topics.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Lightbulb className="h-4 w-4 text-amber-500" />
              Potential Interview Topics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {data.insights.potential_interview_topics.map((t, i) => (
                <Badge key={i} variant="secondary">{t}</Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
