"use client";

import { PracticePlan } from "@/components/recommendations/PracticePlan";
import { useRecommendations } from "@/hooks/useDashboard";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { recommendationAPI } from "@/lib/api";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { EmptyState } from "@/components/ui/empty-state";
import { Lightbulb } from "lucide-react";
import { toast } from "sonner";

export default function RecommendationsPage() {
  const { data: recommendations, isLoading } = useRecommendations();
  const queryClient = useQueryClient();

  const completeMutation = useMutation({
    mutationFn: (id: string) => recommendationAPI.complete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
      toast.success("Recommendation marked as completed!");
    },
  });

  if (isLoading) {
    return <div className="flex justify-center py-20"><LoadingSpinner /></div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Learning Recommendations</h1>
        <p className="text-muted-foreground">
          Personalized study plans based on your resume, interview history, and target companies
        </p>
      </div>

      {!recommendations || recommendations.length === 0 ? (
        <EmptyState
          icon={<Lightbulb className="h-12 w-12" />}
          title="No recommendations yet"
          description="Complete mock interviews or upload your resume to get personalized recommendations."
        />
      ) : (
        <PracticePlan
          recommendations={recommendations}
          onComplete={(id) => completeMutation.mutate(id)}
          isCompleting={completeMutation.isPending}
        />
      )}
    </div>
  );
}
