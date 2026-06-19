"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { VoiceRecorder } from "./VoiceRecorder";
import { useSubmitAnswer, useCompleteInterview } from "@/hooks/useInterview";
import { useInterviewStore } from "@/stores/interviewStore";
import { Send, CheckCircle, Brain, Mic } from "lucide-react";
import { toast } from "sonner";

interface Message {
  role: "ai" | "user";
  content: string;
  topic?: string;
}

interface InterviewChatProps {
  interviewId: string;
  mode: "text" | "voice";
  initialMessages?: Message[];
}

export function InterviewChat({ interviewId, mode, initialMessages = [] }: InterviewChatProps) {
  const router = useRouter();
  const { isComplete } = useInterviewStore();
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [answer, setAnswer] = useState("");
  const [voiceMode, setVoiceMode] = useState(mode === "voice");
  const bottomRef = useRef<HTMLDivElement>(null);

  const answerMutation = useSubmitAnswer(interviewId);
  const completeMutation = useCompleteInterview(interviewId);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmitAnswer = () => {
    if (!answer.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: answer }]);
    const currentAnswer = answer;
    setAnswer("");

    answerMutation.mutate(
      { answer: currentAnswer },
      {
        onSuccess: (res) => {
          const data = res.data.data;
          if (data?.is_complete) {
            toast.info("Interview complete! Getting your evaluation...");
          } else if (data?.question) {
            setMessages((prev) => [
              ...prev,
              { role: "ai", content: data.question.question_text, topic: data.question.topic },
            ]);
          }
        },
        onError: () => toast.error("Failed to submit answer."),
      }
    );
  };

  const handleVoiceTranscript = (text: string) => {
    setAnswer(text);
  };

  const handleComplete = () => {
    completeMutation.mutate(undefined, {
      onSuccess: () => {
        toast.success("Interview evaluated!");
        router.push(`/interviews/${interviewId}/replay`);
      },
      onError: () => toast.error("Failed to complete."),
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmitAnswer();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)]">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                msg.role === "ai"
                  ? "bg-muted"
                  : "bg-primary text-primary-foreground"
              }`}
            >
              {msg.role === "ai" && msg.topic && (
                <Badge variant="outline" className="mb-2 text-xs">{msg.topic}</Badge>
              )}
              {msg.role === "ai" && (
                <div className="flex items-center gap-1 mb-1 text-xs text-muted-foreground">
                  <Brain className="h-3 w-3" /> Interviewer
                </div>
              )}
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input Area */}
      <div className="border-t p-4 space-y-3">
        {isComplete ? (
          <div className="text-center space-y-3">
            <p className="text-sm text-muted-foreground">Interview complete!</p>
            <Button onClick={handleComplete} disabled={completeMutation.isPending}>
              <CheckCircle className="mr-2 h-4 w-4" />
              {completeMutation.isPending ? "Evaluating..." : "Get Evaluation"}
            </Button>
          </div>
        ) : (
          <>
            {voiceMode && (
              <VoiceRecorder onTranscript={handleVoiceTranscript} />
            )}
            <div className="flex gap-2">
              <Textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your answer... (Shift+Enter for new line)"
                rows={2}
                className="flex-1 resize-none"
              />
              <div className="flex flex-col gap-1">
                <Button
                  onClick={handleSubmitAnswer}
                  disabled={!answer.trim() || answerMutation.isPending}
                  size="icon"
                >
                  <Send className="h-4 w-4" />
                </Button>
                <Button
                  variant={voiceMode ? "default" : "outline"}
                  size="icon"
                  onClick={() => setVoiceMode(!voiceMode)}
                  title="Toggle voice mode"
                >
                  <Mic className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
