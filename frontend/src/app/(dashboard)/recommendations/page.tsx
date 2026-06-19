"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { recommendationAPI } from "@/lib/api";
import { CheckCircle, BookOpen } from "lucide-react";
import { toast } from "sonner";
import type { Recommendation } from "@/types";

export default function RecommendationsPage() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["recommendations"],
    queryFn: async () => { const res = await recommendationAPI.list(); return res.data.data as Recommendation[]; },
  });

  const completeMutation = useMutation({
    mutationFn: (id: string) => recommendationAPI.complete(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["recommendations"] }); toast.success("Marked complete!"); },
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Learning Recommendations</h2>
        <p className="text-muted-foreground">Personalized study plan based on your weaknesses and target companies</p>
      </div>

      {isLoading ? <p>Loading...</p> : (data || []).length === 0 ? (
        <Card><CardContent className="py-12 text-center"><BookOpen className="h-10 w-10 mx-auto mb-4 text-muted-foreground" /><p className="text-muted-foreground">No recommendations yet. Complete interviews to get personalized suggestions.</p></CardContent></Card>
      ) : (
        <div className="grid gap-4">
          {(data || []).map((rec) => (
            <Card key={rec.id}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold">{rec.title}</h3>
                      <Badge variant="outline" className="capitalize">{rec.type.replace("_", " ")}</Badge>
                      <Badge variant="secondary">Priority: {rec.priority}</Badge>
                    </div>
                    {rec.description && <p className="text-sm text-muted-foreground">{rec.description}</p>}
                  </div>
                  <Button variant="outline" size="sm" onClick={() => completeMutation.mutate(rec.id)} disabled={completeMutation.isPending}>
                    <CheckCircle className="h-4 w-4 mr-1" /> Done
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
