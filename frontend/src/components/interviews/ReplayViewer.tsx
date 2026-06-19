"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { EvaluationDisplay } from "./EvaluationDisplay";
import { Brain, User, ChevronLeft, ChevronRight, Eye, Lightbulb, Volume2 } from "lucide-react";
import { useVoiceSynthesizer } from "@/hooks/useVoice";
import type { ReplayQuestion, Evaluation } from "@/types";

interface ReplayViewerProps {
  questions: ReplayQuestion[];
  evaluation: Evaluation;
}

export function ReplayViewer({ questions, evaluation }: ReplayViewerProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showIdeal, setShowIdeal] = useState(false);
  const [showEvaluation, setShowEvaluation] = useState(false);
  const { synthesizeAndPlay, isSynthesizing, isPlaying } = useVoiceSynthesizer();

  const q = questions[currentIndex];

  if (showEvaluation) {
    return (
      <div className="space-y-4">
        <Button variant="outline" onClick={() => setShowEvaluation(false)}>
          <ChevronLeft className="mr-1 h-4 w-4" /> Back to Questions
        </Button>
        <EvaluationDisplay evaluation={evaluation} />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Navigation */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={currentIndex === 0}
            onClick={() => { setCurrentIndex(currentIndex - 1); setShowIdeal(false); }}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm font-medium">
            Question {currentIndex + 1} of {questions.length}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={currentIndex === questions.length - 1}
            onClick={() => { setCurrentIndex(currentIndex + 1); setShowIdeal(false); }}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
        <Button variant="outline" size="sm" onClick={() => setShowEvaluation(true)}>
          <Eye className="mr-1 h-4 w-4" /> View Full Evaluation
        </Button>
      </div>

      {/* Question */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-base">
              <Brain className="h-4 w-4" /> Interviewer
            </CardTitle>
            {q?.topic && <Badge variant="outline">{q.topic}</Badge>}
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm">{q?.question_text}</p>
          {q?.audio_url && (
            <Button
              variant="ghost"
              size="sm"
              className="mt-2"
              onClick={() => synthesizeAndPlay(q.question_text)}
              disabled={isSynthesizing || isPlaying}
            >
              <Volume2 className="mr-1 h-3.5 w-3.5" />
              {isPlaying ? "Playing..." : "Play Audio"}
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Student Answer */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <User className="h-4 w-4" /> Your Answer
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm whitespace-pre-wrap">
            {q?.student_answer || <span className="text-muted-foreground italic">No answer provided</span>}
          </p>
        </CardContent>
      </Card>

      {/* Per-question Evaluation */}
      {q?.evaluation && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Question Evaluation</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{q.feedback}</p>
          </CardContent>
        </Card>
      )}

      {/* Ideal Answer Toggle */}
      {q?.ideal_answer && (
        <div>
          <Button variant="outline" size="sm" onClick={() => setShowIdeal(!showIdeal)} className="mb-2">
            <Lightbulb className="mr-1 h-4 w-4" />
            {showIdeal ? "Hide" : "Show"} Ideal Answer
          </Button>
          {showIdeal && (
            <Card className="border-green-200 dark:border-green-900">
              <CardContent className="pt-4">
                <p className="text-sm whitespace-pre-wrap">{q.ideal_answer}</p>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Quick Navigation */}
      <div className="flex flex-wrap gap-1">
        {questions.map((_, idx) => (
          <Button
            key={idx}
            variant={idx === currentIndex ? "default" : "outline"}
            size="sm"
            className="h-8 w-8 p-0"
            onClick={() => { setCurrentIndex(idx); setShowIdeal(false); }}
          >
            {idx + 1}
          </Button>
        ))}
      </div>
    </div>
  );
}
