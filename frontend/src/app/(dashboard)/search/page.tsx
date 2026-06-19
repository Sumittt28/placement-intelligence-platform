"use client";

import { useState } from "react";
import { SearchBar } from "@/components/search/SearchBar";
import { SearchResults } from "@/components/search/SearchResults";
import { useKnowledgeBaseSearch } from "@/hooks/useCompany";

export default function SearchPage() {
  const [filters, setFilters] = useState({
    q: "",
    type: undefined as string | undefined,
    company: undefined as string | undefined,
    round_type: undefined as string | undefined,
    difficulty: undefined as string | undefined,
  });

  const { data: results, isLoading } = useKnowledgeBaseSearch(filters);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Knowledge Base Search</h1>
        <p className="text-muted-foreground">
          Search across all interview experiences by company, topic, question, or technology
        </p>
      </div>

      <SearchBar
        filters={filters}
        onFiltersChange={setFilters}
        onClear={() => setFilters({ q: "", type: undefined, company: undefined, round_type: undefined, difficulty: undefined })}
      />

      <SearchResults results={results || []} isLoading={isLoading} query={filters.q} />
    </div>
  );
}
