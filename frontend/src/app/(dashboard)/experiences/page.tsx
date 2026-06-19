"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { experienceAPI } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Plus } from "lucide-react";
import type { InterviewExperience } from "@/types";

const outcomeColors: Record<string, string> = {
  Selected: "bg-green-100 text-green-800",
  Rejected: "bg-red-100 text-red-800",
  Waiting: "bg-yellow-100 text-yellow-800",
  Unknown: "bg-gray-100 text-gray-800",
};

export default function ExperiencesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["experiences"],
    queryFn: async () => {
      const res = await experienceAPI.list();
      return res.data.data;
    },
  });

  const experiences: InterviewExperience[] = data?.experiences || [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Interview Experiences</h2>
          <p className="text-muted-foreground">Your submitted interview experiences</p>
        </div>
        <Link href="/experiences/new">
          <Button><Plus className="h-4 w-4 mr-2" /> Submit Experience</Button>
        </Link>
      </div>

      {isLoading ? (
        <p className="text-muted-foreground">Loading...</p>
      ) : experiences.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground mb-4">No experiences submitted yet.</p>
            <Link href="/experiences/new">
              <Button>Submit Your First Experience</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {experiences.map((exp) => (
            <Link key={exp.id} href={`/experiences/${exp.id}`}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-lg">{exp.company_name || "Company"} - {exp.role}</h3>
                      <div className="flex gap-2 mt-2">
                        <Badge variant="outline">{exp.round_type}</Badge>
                        <Badge variant="outline">{exp.difficulty}</Badge>
                        <Badge className={outcomeColors[exp.outcome] || ""}>{exp.outcome}</Badge>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-muted-foreground">{new Date(exp.interview_date).toLocaleDateString()}</p>
                      <p className="text-sm text-muted-foreground">{exp.questions.length} questions</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
