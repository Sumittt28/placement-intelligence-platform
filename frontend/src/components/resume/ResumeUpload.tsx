"use client";

import { useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { resumeAPI } from "@/lib/api";
import { Upload, FileText, CheckCircle, Loader2 } from "lucide-react";
import { toast } from "sonner";

export function ResumeUpload() {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: (file: File) => resumeAPI.upload(file),
    onSuccess: () => {
      toast.success("Resume uploaded and parsed successfully!");
      queryClient.invalidateQueries({ queryKey: ["resumeInsights"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["currentUser"] });
    },
    onError: (err) => {
      toast.error(`Upload failed: ${(err as Error).message}`);
    },
  });

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.type === "application/pdf" || droppedFile.type === "text/plain")) {
      setFile(droppedFile);
    } else {
      toast.error("Please upload a PDF or text file.");
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleUpload = () => {
    if (file) {
      uploadMutation.mutate(file);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Upload Resume
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
            isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50"
          }`}
          onClick={() => document.getElementById("resume-input")?.click()}
        >
          <Upload className="h-8 w-8 mx-auto mb-3 text-muted-foreground" />
          <p className="text-sm font-medium">
            {file ? file.name : "Drag & drop your resume here"}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Supports PDF and text files
          </p>
          <input
            id="resume-input"
            type="file"
            accept=".pdf,.txt,application/pdf,text/plain"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>

        {file && (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm">
              <FileText className="h-4 w-4 text-primary" />
              <span className="font-medium">{file.name}</span>
              <span className="text-muted-foreground">
                ({(file.size / 1024).toFixed(1)} KB)
              </span>
            </div>
            <Button onClick={handleUpload} disabled={uploadMutation.isPending} size="sm">
              {uploadMutation.isPending ? (
                <><Loader2 className="mr-1 h-3.5 w-3.5 animate-spin" /> Parsing...</>
              ) : uploadMutation.isSuccess ? (
                <><CheckCircle className="mr-1 h-3.5 w-3.5" /> Uploaded</>
              ) : (
                <><Upload className="mr-1 h-3.5 w-3.5" /> Upload & Parse</>
              )}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
