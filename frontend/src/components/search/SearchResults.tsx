"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Building2, Hash, HelpCircle } from "lucide-react";
import type { SearchResult } from "@/types";

interface SearchResultsProps {
  results: SearchResult[];
  isLoading: boolean;
  query: string;
}

const difficultyColor: Record<string, string> = {
  Easy: "text-green-600 bg-green-100 dark:bg-green-950",
  Medium: "text-yellow-600 bg-yellow-100 dark:bg-yellow-950",
  Hard: "text-red-600 bg-red-100 dark:bg-red-950",
};

export function SearchResults({ results, isLoading, query }: SearchResultsProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <Card key={i}>
            <CardContent className="pt-6">
              <div className="animate-pulse space-y-2">
                <div className="h-4 bg-muted rounded w-3/4" />
                <div className="h-3 bg-muted rounded w-1/2" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (query && results.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center">
          <HelpCircle className="h-8 w-8 mx-auto mb-3 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            No results found for &quot;{query}&quot;
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Try different keywords or adjust filters.
          </p>
        </CardContent>
      </Card>
    );
  }

  if (!query) {
    return (
      <Card>
        <CardContent className="py-8 text-center">
          <HelpCircle className="h-8 w-8 mx-auto mb-3 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            Search across all interview experiences by topic, question, or technology.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      <p className="text-sm text-muted-foreground">{results.length} result(s)</p>
      {results.map((result, idx) => (
        <Card key={idx} className="hover:border-primary/30 transition-colors">
          <CardContent className="pt-6">
            <p className="text-sm font-medium">{result.question_text}</p>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <Badge variant="outline" className="text-xs flex items-center gap-1">
                <Building2 className="h-3 w-3" />
                {result.company_name}
              </Badge>
              <Badge variant="outline" className="text-xs flex items-center gap-1">
                <Hash className="h-3 w-3" />
                {result.topic}
              </Badge>
              <Badge variant="outline" className="text-xs">{result.round_type}</Badge>
              <Badge className={`text-xs ${difficultyColor[result.difficulty] || ""}`} variant="outline">
                {result.difficulty}
              </Badge>
              {result.frequency > 1 && (
                <Badge variant="secondary" className="text-xs">
                  Asked {result.frequency}x
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
