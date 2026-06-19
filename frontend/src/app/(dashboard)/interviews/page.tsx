"use client";

import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useInterviewList } from "@/hooks/useInterview";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { EmptyState } from "@/components/ui/empty-state";
import { Plus, Brain, Calendar, ArrowRight } from "lucide-react";

export default function InterviewsPage() {
  const { data: interviews, isLoading } = useInterviewList();

  const statusBadge: Record<string, "default" | "secondary" | "destructive"> = {
    completed: "default",
    in_progress: "secondary",
    abandoned: "destructive",
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Mock Interviews</h1>
          <p className="text-muted-foreground">AI-powered interview practice sessions</p>
        </div>
        <Link href="/interviews/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" /> New Interview
          </Button>
        </Link>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20"><LoadingSpinner /></div>
      ) : !interviews || interviews.length === 0 ? (
        <EmptyState
          icon={<Brain className="h-12 w-12" />}
          title="No interviews yet"
          description="Start your first AI mock interview to practice and get evaluated."
          action={
            <Link href="/interviews/new">
              <Button><Plus className="mr-2 h-4 w-4" /> Start Interview</Button>
            </Link>
          }
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {interviews.map((interview) => (
            <Link
              key={interview.id}
              href={
                interview.status === "completed"
                  ? `/interviews/${interview.id}/replay`
                  : `/interviews/${interview.id}`
              }
            >
              <Card className="hover:border-primary/50 transition-colors cursor-pointer h-full">
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1.5">
                      <h3 className="font-semibold capitalize">{interview.interview_type} Interview</h3>
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Calendar className="h-3 w-3" />
                        {new Date(interview.started_at).toLocaleDateString()}
                      </div>
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Badge variant={statusBadge[interview.status] || "outline"}>
                      {interview.status}
                    </Badge>
                    <Badge variant="outline">{interview.difficulty}</Badge>
                    <Badge variant="outline">{interview.mode}</Badge>
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
