"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TopicFrequency } from "./TopicFrequency";
import { DifficultyTrends } from "./DifficultyTrends";
import { ExperienceCard } from "@/components/experiences/ExperienceCard";
import { Building2, TrendingUp, Target, AlertTriangle, Layers } from "lucide-react";
import type { CompanyIntelligence as CompanyIntelligenceType } from "@/types";

interface CompanyIntelligenceProps {
  data: CompanyIntelligenceType;
}

export function CompanyIntelligence({ data }: CompanyIntelligenceProps) {
  const { company, analytics, recent_experiences, questions_by_round } = data;

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            {company.logo_url ? (
              <img src={company.logo_url} alt={company.name} className="h-12 w-12 rounded-lg" />
            ) : (
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <Building2 className="h-6 w-6 text-primary" />
              </div>
            )}
            <div>
              <CardTitle className="text-2xl">{company.name}</CardTitle>
              {company.industry && (
                <Badge variant="outline" className="mt-1">{company.industry}</Badge>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="text-center">
              <p className="text-2xl font-bold">{analytics.total_experiences}</p>
              <p className="text-xs text-muted-foreground">Experiences</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold">{analytics.total_questions}</p>
              <p className="text-xs text-muted-foreground">Questions</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-500">{analytics.success_rate}%</p>
              <p className="text-xs text-muted-foreground">Success Rate</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold">{Object.keys(analytics.round_dist || {}).length}</p>
              <p className="text-xs text-muted-foreground">Round Types</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Analytics Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        <TopicFrequency topics={analytics.top_topics || []} />
        <DifficultyTrends distribution={analytics.difficulty_dist || {}} />
      </div>

      {/* Round Breakdown */}
      {questions_by_round && Object.keys(questions_by_round).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Layers className="h-5 w-5" />
              Questions by Round
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(questions_by_round).map(([round, questions]) => (
              <div key={round}>
                <h4 className="font-medium mb-2">{round}</h4>
                <div className="space-y-2">
                  {questions.slice(0, 5).map((q, idx) => (
                    <div key={idx} className="text-sm border-l-2 pl-3 py-1">
                      <p>{q.question}</p>
                      <Badge variant="outline" className="text-xs mt-1">{q.topic}</Badge>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Common Weaknesses */}
      {analytics.common_weaknesses && analytics.common_weaknesses.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-yellow-500" />
              Common Weaknesses
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {analytics.common_weaknesses.map((w, i) => (
                <Badge key={i} variant="secondary">{typeof w === "string" ? w : (w as {topic: string}).topic}</Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Success Patterns */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-green-500" />
            Success Patterns
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2">
            {Object.entries(analytics.round_dist || {}).map(([round, count]) => (
              <div key={round} className="flex items-center justify-between rounded-lg border p-3">
                <span className="text-sm font-medium">{round}</span>
                <Badge variant="outline">{Math.round(count as number)} interviews</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Experiences */}
      {recent_experiences && recent_experiences.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Recent Experiences
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2">
              {recent_experiences.map((exp) => (
                <div key={exp.id} className="rounded-lg border p-3 space-y-1 text-sm">
                  <p className="font-medium">{exp.role}</p>
                  <div className="flex gap-2">
                    <Badge variant="outline" className="text-xs">{exp.round_type}</Badge>
                    <Badge variant="outline" className="text-xs">{exp.difficulty}</Badge>
                    <Badge variant={exp.outcome === "Selected" ? "default" : "secondary"} className="text-xs">
                      {exp.outcome}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
