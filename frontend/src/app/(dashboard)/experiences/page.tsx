"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ExperienceCard } from "@/components/experiences/ExperienceCard";
import { useExperienceList } from "@/hooks/useInterview";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { EmptyState } from "@/components/ui/empty-state";
import { Plus, MessageSquare } from "lucide-react";

export default function ExperiencesPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useExperienceList(page);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Interview Experiences</h1>
          <p className="text-muted-foreground">Browse and share real interview experiences</p>
        </div>
        <Link href="/experiences/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" /> Submit Experience
          </Button>
        </Link>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20"><LoadingSpinner /></div>
      ) : !data || (data.experiences || []).length === 0 ? (
        <EmptyState
          icon={<MessageSquare className="h-12 w-12" />}
          title="No experiences yet"
          description="Be the first to share an interview experience and help others prepare!"
          action={
            <Link href="/experiences/new">
              <Button><Plus className="mr-2 h-4 w-4" /> Submit Experience</Button>
            </Link>
          }
        />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.experiences.map((exp) => (
              <ExperienceCard key={exp.id} experience={exp} />
            ))}
          </div>

          {/* Pagination */}
          {data.total > 20 && (
            <div className="flex justify-center gap-2">
              <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
                Previous
              </Button>
              <span className="text-sm text-muted-foreground flex items-center">
                Page {page} of {Math.ceil(data.total / 20)}
              </span>
              <Button variant="outline" size="sm" disabled={page >= Math.ceil(data.total / 20)} onClick={() => setPage(page + 1)}>
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
