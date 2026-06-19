"use client";

import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Trash2 } from "lucide-react";

interface QuestionData {
  topic: string;
  question_text: string;
  could_answer: string;
}

interface QuestionEntryProps {
  index: number;
  data: QuestionData;
  onChange: (index: number, field: keyof QuestionData, value: string) => void;
  onRemove: (index: number) => void;
  removable: boolean;
}

export function QuestionEntry({ index, data, onChange, onRemove, removable }: QuestionEntryProps) {
  return (
    <div className="rounded-lg border p-4 space-y-3 relative">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium">Question {index + 1}</h4>
        {removable && (
          <Button variant="ghost" size="sm" onClick={() => onRemove(index)} className="h-8 w-8 p-0 text-destructive">
            <Trash2 className="h-4 w-4" />
          </Button>
        )}
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="space-y-1.5">
          <Label htmlFor={`topic-${index}`}>Topic</Label>
          <Input
            id={`topic-${index}`}
            placeholder="e.g., Arrays, Binary Search, SQL"
            value={data.topic}
            onChange={(e) => onChange(index, "topic", e.target.value)}
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor={`could-${index}`}>Could Answer?</Label>
          <Select value={data.could_answer} onValueChange={(v) => onChange(index, "could_answer", v)}>
            <SelectTrigger id={`could-${index}`}>
              <SelectValue placeholder="Select..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Yes">Yes</SelectItem>
              <SelectItem value="Partially">Partially</SelectItem>
              <SelectItem value="No">No</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor={`qtext-${index}`}>Question Text</Label>
        <Textarea
          id={`qtext-${index}`}
          placeholder="Describe the question asked..."
          value={data.question_text}
          onChange={(e) => onChange(index, "question_text", e.target.value)}
          rows={2}
        />
      </div>
    </div>
  );
}
