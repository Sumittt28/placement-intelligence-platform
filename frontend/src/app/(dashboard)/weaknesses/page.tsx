"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useWeaknesses } from "@/hooks/useDashboard";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { weaknessAPI } from "@/lib/api";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { EmptyState } from "@/components/ui/empty-state";
import { AlertTriangle, CheckCircle, Clock, Target } from "lucide-react";
import { toast } from "sonner";

export default function WeaknessesPage() {
  const { data: weaknesses, isLoading } = useWeaknesses();
  const queryClient = useQueryClient();

  const resolveMutation = useMutation({
    mutationFn: (id: string) => weaknessAPI.resolve(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["weaknesses"] });
      toast.success("Weakness marked as resolved!");
    },
  });

  const severityColor: Record<string, string> = {
    low: "text-yellow-600 bg-yellow-100 dark:bg-yellow-950",
    medium: "text-orange-600 bg-orange-100 dark:bg-orange-950",
    high: "text-red-600 bg-red-100 dark:bg-red-950",
  };

  if (isLoading) {
    return <div className="flex justify-center py-20"><LoadingSpinner /></div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Weakness Analysis</h1>
        <p className="text-muted-foreground">
          Track recurring weaknesses across your interviews and take targeted action
        </p>
      </div>

      {!weaknesses || weaknesses.length === 0 ? (
        <EmptyState
          icon={<Target className="h-12 w-12" />}
          title="No weaknesses detected"
          description="Complete mock interviews to have your performance analyzed for weak areas."
        />
      ) : (
        <div className="space-y-4">
          {/* Summary */}
          <div className="grid grid-cols-3 gap-4">
            <Card>
              <CardContent className="pt-6 text-center">
                <p className="text-2xl font-bold text-red-500">
                  {weaknesses.filter((w) => w.severity === "high").length}
                </p>
                <p className="text-xs text-muted-foreground">High Severity</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6 text-center">
                <p className="text-2xl font-bold text-orange-500">
                  {weaknesses.filter((w) => w.severity === "medium").length}
                </p>
                <p className="text-xs text-muted-foreground">Medium Severity</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6 text-center">
                <p className="text-2xl font-bold text-green-500">
                  {weaknesses.filter((w) => w.is_resolved).length}
                </p>
                <p className="text-xs text-muted-foreground">Resolved</p>
              </CardContent>
            </Card>
          </div>

          {/* Weakness Cards */}
          {weaknesses
            .sort((a, b) => b.occurrence_count - a.occurrence_count)
            .map((weakness) => (
            <Card key={weakness.id} className={weakness.is_resolved ? "opacity-60" : ""}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2 text-base">
                    <AlertTriangle className="h-4 w-4 text-yellow-500" />
                    {weakness.topic}
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <Badge className={severityColor[weakness.severity || "low"]} variant="outline">
                      {weakness.severity}
                    </Badge>
                    {weakness.is_resolved && (
                      <Badge variant="default" className="text-xs">Resolved</Badge>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Occurrences</span>
                  <span className="font-medium">{weakness.occurrence_count} time(s)</span>
                </div>
                <Progress value={Math.min(weakness.occurrence_count * 20, 100)} className="h-2" />

                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  First: {new Date(weakness.first_detected).toLocaleDateString()} ·
                  Last: {new Date(weakness.last_detected).toLocaleDateString()}
                </div>

                {weakness.category && (
                  <Badge variant="outline" className="text-xs">{weakness.category}</Badge>
                )}

                {/* Recommended Actions */}
                {weakness.recommended_actions && weakness.recommended_actions.length > 0 && (
                  <div className="rounded-lg bg-muted p-3 space-y-1">
                    <p className="text-xs font-medium">Recommended Actions:</p>
                    {weakness.recommended_actions.map((action, i) => (
                      <p key={i} className="text-xs text-muted-foreground">• {action}</p>
                    ))}
                  </div>
                )}

                {!weakness.is_resolved && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => resolveMutation.mutate(weakness.id)}
                    disabled={resolveMutation.isPending}
                  >
                    <CheckCircle className="mr-1 h-3.5 w-3.5" />
                    Mark as Resolved
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
