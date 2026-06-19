"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { interviewAPI } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Plus, Play, Eye } from "lucide-react";
import type { MockInterview } from "@/types";

export default function InterviewsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["interviews"],
    queryFn: async () => { const res = await interviewAPI.list(); return res.data.data as MockInterview[]; },
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Mock Interviews</h2>
          <p className="text-muted-foreground">AI-powered interview practice sessions</p>
        </div>
        <Link href="/interviews/new">
          <Button><Plus className="h-4 w-4 mr-2" /> New Interview</Button>
        </Link>
      </div>

      {isLoading ? <p>Loading...</p> : (data || []).length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground mb-4">No interviews yet. Start your first mock interview!</p>
            <Link href="/interviews/new"><Button>Start Interview</Button></Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {(data || []).map((interview) => (
            <Card key={interview.id} className="hover:shadow-md transition-shadow">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold capitalize">{interview.interview_type} Interview</h3>
                    <div className="flex gap-2 mt-2">
                      <Badge variant="outline">{interview.difficulty}</Badge>
                      <Badge variant="outline">{interview.mode}</Badge>
                      <Badge variant={interview.status === "completed" ? "default" : "secondary"}>{interview.status}</Badge>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {interview.status === "in_progress" ? (
                      <Link href={`/interviews/${interview.id}`}>
                        <Button size="sm" variant="outline"><Play className="h-4 w-4 mr-1" /> Continue</Button>
                      </Link>
                    ) : (
                      <Link href={`/interviews/${interview.id}/replay`}>
                        <Button size="sm" variant="outline"><Eye className="h-4 w-4 mr-1" /> Replay</Button>
                      </Link>
                    )}
                    <span className="text-sm text-muted-foreground">{new Date(interview.started_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
