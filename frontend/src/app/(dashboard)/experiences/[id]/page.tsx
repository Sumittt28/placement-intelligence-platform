"use client";

import { useParams } from "next/navigation";
import { ExperienceDetail } from "@/components/experiences/ExperienceDetail";
import { useExperience } from "@/hooks/useInterview";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function ExperienceDetailPage() {
  const { id } = useParams();
  const { data, isLoading, error } = useExperience(id as string);

  return (
    <div className="space-y-6">
      <Link href="/experiences">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="mr-1 h-4 w-4" /> Back to Experiences
        </Button>
      </Link>

      {isLoading ? (
        <div className="flex justify-center py-20"><LoadingSpinner /></div>
      ) : error || !data ? (
        <div className="text-center py-20 text-muted-foreground">Experience not found.</div>
      ) : (
        <ExperienceDetail experience={data} />
      )}
    </div>
  );
}
