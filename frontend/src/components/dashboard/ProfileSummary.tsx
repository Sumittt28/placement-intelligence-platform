"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { User, FileText, Target } from "lucide-react";

interface ProfileSummaryProps {
  fullName: string;
  batch?: string;
  resumeStatus: string;
  targetCompanies: string;
}

export function ProfileSummary({ fullName, batch, resumeStatus, targetCompanies }: ProfileSummaryProps) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <User className="h-5 w-5" />
          Profile Summary
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Name</span>
          <span className="font-medium">{fullName}</span>
        </div>
        {batch && (
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Batch</span>
            <Badge variant="outline">{batch}</Badge>
          </div>
        )}
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground flex items-center gap-1">
            <FileText className="h-3 w-3" /> Resume
          </span>
          <Badge variant={resumeStatus === "uploaded" ? "default" : "secondary"}>
            {resumeStatus}
          </Badge>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground flex items-center gap-1">
            <Target className="h-3 w-3" /> Targets
          </span>
          <span className="text-sm font-medium">{targetCompanies || "Not set"}</span>
        </div>
      </CardContent>
    </Card>
  );
}
