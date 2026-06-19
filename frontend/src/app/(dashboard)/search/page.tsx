"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { searchAPI } from "@/lib/api";
import { Search } from "lucide-react";
import type { SearchResult } from "@/types";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState({ round_type: "", difficulty: "" });
  const [searchTerm, setSearchTerm] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["search", searchTerm, filters],
    queryFn: async () => {
      if (!searchTerm) return null;
      const res = await searchAPI.search({ q: searchTerm, ...filters });
      return res.data.data;
    },
    enabled: !!searchTerm,
  });

  const handleSearch = () => setSearchTerm(query);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Knowledge Base Search</h2>
        <p className="text-muted-foreground">Search across all interview questions by company, topic, or technology</p>
      </div>

      {/* Search Bar */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search: Binary Search, React, SQL..."
            className="pl-10"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
        </div>
        <Button onClick={handleSearch}>Search</Button>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <Select onValueChange={(v) => v && setFilters({ ...filters, round_type: v === "all" ? "" : v })}>
          <SelectTrigger className="w-40"><SelectValue placeholder="Round Type" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Rounds</SelectItem>
            {["OA", "Technical", "HM", "HR", "System Design"].map((r) => <SelectItem key={r} value={r}>{r}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select onValueChange={(v) => v && setFilters({ ...filters, difficulty: v === "all" ? "" : v })}>
          <SelectTrigger className="w-40"><SelectValue placeholder="Difficulty" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Levels</SelectItem>
            {["Easy", "Medium", "Hard"].map((d) => <SelectItem key={d} value={d}>{d}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      {/* Results */}
      {isLoading ? <p>Searching...</p> : data ? (
        <div>
          <p className="text-sm text-muted-foreground mb-4">{data.total} results for &quot;{data.query}&quot;</p>
          <div className="grid gap-3">
            {(data.results as SearchResult[]).map((r, i) => (
              <Card key={i}>
                <CardContent className="pt-4 pb-4">
                  <p className="font-medium mb-2">{r.question_text}</p>
                  <div className="flex flex-wrap gap-2">
                    <Badge>{r.company_name}</Badge>
                    <Badge variant="outline">{r.topic}</Badge>
                    <Badge variant="outline">{r.round_type}</Badge>
                    <Badge variant="outline">{r.difficulty}</Badge>
                    <Badge variant="secondary">Asked {r.frequency}x</Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      ) : searchTerm ? (
        <p className="text-muted-foreground text-center py-8">No results found</p>
      ) : null}
    </div>
  );
}
