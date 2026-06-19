"use client";

import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Search, X } from "lucide-react";

interface SearchFilters {
  q: string;
  type?: string;
  company?: string;
  round_type?: string;
  difficulty?: string;
}

interface SearchBarProps {
  filters: SearchFilters;
  onFiltersChange: (filters: SearchFilters) => void;
  onClear: () => void;
}

export function SearchBar({ filters, onFiltersChange, onClear }: SearchBarProps) {
  const updateFilter = (key: keyof SearchFilters, value: string) => {
    onFiltersChange({ ...filters, [key]: value || undefined });
  };

  return (
    <div className="space-y-3">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          value={filters.q}
          onChange={(e) => updateFilter("q", e.target.value)}
          placeholder="Search questions by topic, technology, or keyword..."
          className="pl-10 pr-10"
        />
        {filters.q && (
          <Button
            variant="ghost"
            size="icon"
            className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7"
            onClick={onClear}
          >
            <X className="h-3.5 w-3.5" />
          </Button>
        )}
      </div>

      <div className="flex flex-wrap gap-2">
        <Select value={filters.type || ""} onValueChange={(v) => updateFilter("type", v)}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Search type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Types</SelectItem>
            <SelectItem value="company">Company</SelectItem>
            <SelectItem value="topic">Topic</SelectItem>
            <SelectItem value="question">Question</SelectItem>
            <SelectItem value="technology">Technology</SelectItem>
          </SelectContent>
        </Select>

        <Select value={filters.round_type || ""} onValueChange={(v) => updateFilter("round_type", v)}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Round type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Rounds</SelectItem>
            {["OA", "Technical", "HM", "HR", "System Design", "Other"].map((r) => (
              <SelectItem key={r} value={r}>{r}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={filters.difficulty || ""} onValueChange={(v) => updateFilter("difficulty", v)}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Difficulty" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Levels</SelectItem>
            {["Easy", "Medium", "Hard"].map((d) => (
              <SelectItem key={d} value={d}>{d}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
