"use client";

import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Building2, Calendar, ArrowRight } from "lucide-react";
import type { InterviewExperience } from "@/types";

interface ExperienceCardProps {
  experience: InterviewExperience;
}

const outcomeBadge: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  Selected: "default",
  Rejected: "destructive",
  Waiting: "secondary",
  Unknown: "outline",
};

const difficultyColor: Record<string, string> = {
  Easy: "text-green-600 bg-green-100 dark:bg-green-950",
  Medium: "text-yellow-600 bg-yellow-100 dark:bg-yellow-950",
  Hard: "text-red-600 bg-red-100 dark:bg-red-950",
};

export function ExperienceCard({ experience }: ExperienceCardProps) {
  return (
    <Link href={`/experiences/${experience.id}`}>
      <Card className="hover:border-primary/50 transition-colors cursor-pointer">
        <CardContent className="pt-6">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <h3 className="font-semibold">{experience.role}</h3>
              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                <Building2 className="h-3.5 w-3.5" />
                {experience.company_name || "Company"}
              </div>
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Calendar className="h-3 w-3" />
                {new Date(experience.interview_date).toLocaleDateString()}
              </div>
            </div>
            <ArrowRight className="h-4 w-4 text-muted-foreground" />
          </div>

          <div className="mt-3 flex flex-wrap gap-2">
            <Badge variant="outline">{experience.round_type}</Badge>
            <Badge className={difficultyColor[experience.difficulty] || ""} variant="outline">
              {experience.difficulty}
            </Badge>
            <Badge variant={outcomeBadge[experience.outcome] || "outline"}>
              {experience.outcome}
            </Badge>
          </div>

          <p className="mt-2 text-xs text-muted-foreground">
            {experience.questions?.length || 0} question(s)
          </p>
        </CardContent>
      </Card>
    </Link>
  );
}
