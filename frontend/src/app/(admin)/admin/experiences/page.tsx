"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { adminAPI } from "@/lib/api";
import { toast } from "sonner";
import { Check, Flag, AlertTriangle } from "lucide-react";

interface Experience {
  id: string;
  company_name?: string;
  role: string;
  round_type: string;
  difficulty: string;
  outcome: string;
  is_approved: boolean;
  is_flagged?: boolean;
  questions: { question_text: string; topic: string }[];
  created_at: string;
}

export default function AdminExperiencesPage() {
  const queryClient = useQueryClient();
  const [filter, setFilter] = useState<string | undefined>(undefined);
  const [flagReason, setFlagReason] = useState<Record<string, string>>({});

  const { data, isLoading } = useQuery({
    queryKey: ["admin-experiences", filter],
    queryFn: async () => {
      const res = await adminAPI.listExperiences(filter);
      return (res.data.data || []) as Experience[];
    },
  });

  const approveMutation = useMutation({
    mutationFn: (id: string) => adminAPI.approve(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-experiences"] });
      toast.success("Experience approved!");
    },
  });

  const flagMutation = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) => adminAPI.flag(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-experiences"] });
      toast.success("Experience flagged.");
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Moderate Experiences</h2>
        <div className="flex gap-2">
          <Button variant={!filter ? "default" : "outline"} size="sm" onClick={() => setFilter(undefined)}>All</Button>
          <Button variant={filter === "pending" ? "default" : "outline"} size="sm" onClick={() => setFilter("pending")}>Pending</Button>
          <Button variant={filter === "flagged" ? "default" : "outline"} size="sm" onClick={() => setFilter("flagged")}>Flagged</Button>
        </div>
      </div>

      {isLoading ? (
        <p className="text-muted-foreground">Loading experiences...</p>
      ) : (data || []).length === 0 ? (
        <p className="text-muted-foreground">No experiences found.</p>
      ) : (
        <div className="space-y-4">
          {(data || []).map((exp) => (
            <Card key={exp.id}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold">{exp.company_name || "Unknown"}</h3>
                      <Badge variant="outline">{exp.round_type}</Badge>
                      <Badge variant="outline">{exp.difficulty}</Badge>
                      <Badge variant={exp.outcome === "Selected" ? "default" : "secondary"}>{exp.outcome}</Badge>
                      {exp.is_approved && <Badge className="bg-green-100 text-green-700">Approved</Badge>}
                      {exp.is_flagged && <Badge className="bg-red-100 text-red-700">Flagged</Badge>}
                    </div>
                    <p className="text-sm text-muted-foreground">Role: {exp.role}</p>
                    <p className="text-xs text-muted-foreground mt-1">{exp.questions.length} question(s) | {new Date(exp.created_at).toLocaleDateString()}</p>

                    {exp.questions.length > 0 && (
                      <div className="mt-3 space-y-1">
                        {exp.questions.slice(0, 3).map((q, i) => (
                          <p key={i} className="text-sm text-muted-foreground">
                            <span className="font-medium">[{q.topic}]</span> {q.question_text.slice(0, 120)}
                          </p>
                        ))}
                        {exp.questions.length > 3 && (
                          <p className="text-xs text-muted-foreground">+{exp.questions.length - 3} more</p>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col gap-2 ml-4">
                    {!exp.is_approved && (
                      <Button
                        size="sm"
                        variant="default"
                        onClick={() => approveMutation.mutate(exp.id)}
                        disabled={approveMutation.isPending}
                      >
                        <Check className="h-4 w-4 mr-1" /> Approve
                      </Button>
                    )}
                    <div className="flex gap-1">
                      <Input
                        placeholder="Flag reason"
                        className="h-8 text-xs w-32"
                        value={flagReason[exp.id] || ""}
                        onChange={(e) => setFlagReason({ ...flagReason, [exp.id]: e.target.value })}
                      />
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => {
                          const reason = flagReason[exp.id] || "Flagged by admin";
                          flagMutation.mutate({ id: exp.id, reason });
                        }}
                        disabled={flagMutation.isPending}
                      >
                        <Flag className="h-4 w-4" />
                      </Button>
                    </div>
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
