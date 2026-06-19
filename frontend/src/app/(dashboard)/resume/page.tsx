"use client";

import { useState, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { resumeAPI } from "@/lib/api";
import { Upload, FileText, AlertTriangle, CheckCircle } from "lucide-react";
import { toast } from "sonner";
import type { ResumeInsights } from "@/types";

export default function ResumePage() {
  const queryClient = useQueryClient();
  const [dragActive, setDragActive] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["resume-insights"],
    queryFn: async () => { try { const res = await resumeAPI.insights(); return res.data.data as ResumeInsights; } catch { return null; } },
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => resumeAPI.upload(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resume-insights"] });
      toast.success("Resume parsed successfully!");
    },
    onError: () => toast.error("Failed to parse resume"),
  });

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault(); setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (file) uploadMutation.mutate(file);
  }, [uploadMutation]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadMutation.mutate(file);
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Resume Intelligence</h2>

      {/* Upload Zone */}
      <Card>
        <CardContent className="pt-6">
          <div
            className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${dragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25"}`}
            onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
          >
            <Upload className="h-10 w-10 mx-auto mb-4 text-muted-foreground" />
            <p className="text-lg font-medium mb-2">Drop your resume here</p>
            <p className="text-sm text-muted-foreground mb-4">PDF or text file</p>
            <label>
              <input type="file" accept=".pdf,.txt" onChange={handleFileChange} className="hidden" />
              <Button variant="outline" asChild><span>{uploadMutation.isPending ? "Parsing..." : "Browse Files"}</span></Button>
            </label>
          </div>
        </CardContent>
      </Card>

      {isLoading ? <p>Loading...</p> : data ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Skills */}
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2"><CheckCircle className="h-5 w-5 text-green-500" /> Skills</CardTitle></CardHeader>
            <CardContent><div className="flex flex-wrap gap-2">{(data.skills || []).map((s, i) => <Badge key={i}>{s}</Badge>)}</div></CardContent>
          </Card>

          {/* Technologies */}
          <Card>
            <CardHeader><CardTitle>Technologies</CardTitle></CardHeader>
            <CardContent><div className="flex flex-wrap gap-2">{(data.technologies || []).map((t, i) => <Badge key={i} variant="outline">{t}</Badge>)}</div></CardContent>
          </Card>

          {/* Projects */}
          <Card>
            <CardHeader><CardTitle>Projects</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              {(data.projects || []).map((p, i) => (
                <div key={i} className="border rounded-lg p-3">
                  <p className="font-medium">{p.name}</p>
                  <p className="text-sm text-muted-foreground">{p.description}</p>
                  <div className="flex gap-1 mt-2">{(p.technologies || []).map((t, j) => <Badge key={j} variant="secondary" className="text-xs">{t}</Badge>)}</div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Insights */}
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2"><AlertTriangle className="h-5 w-5 text-yellow-500" /> Insights</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              {data.insights?.missing_skills?.length ? (
                <div>
                  <p className="text-sm font-medium text-red-600 mb-2">Missing Skills:</p>
                  <div className="flex flex-wrap gap-2">{data.insights.missing_skills.map((s, i) => <Badge key={i} variant="destructive">{s}</Badge>)}</div>
                </div>
              ) : null}
              {data.insights?.strength_areas?.length ? (
                <div>
                  <p className="text-sm font-medium text-green-600 mb-2">Strengths:</p>
                  <div className="flex flex-wrap gap-2">{data.insights.strength_areas.map((s, i) => <Badge key={i} className="bg-green-100 text-green-800">{s}</Badge>)}</div>
                </div>
              ) : null}
              {data.insights?.potential_interview_topics?.length ? (
                <div>
                  <p className="text-sm font-medium mb-2">Likely Interview Topics:</p>
                  <div className="flex flex-wrap gap-2">{data.insights.potential_interview_topics.map((s, i) => <Badge key={i} variant="outline">{s}</Badge>)}</div>
                </div>
              ) : null}
            </CardContent>
          </Card>
        </div>
      ) : (
        <Card><CardContent className="py-12 text-center"><FileText className="h-10 w-10 mx-auto mb-4 text-muted-foreground" /><p className="text-muted-foreground">Upload your resume to get AI-powered insights</p></CardContent></Card>
      )}
    </div>
  );
}
