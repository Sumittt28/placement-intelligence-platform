"use client";

import { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { interviewAPI } from "@/lib/api";
import { useInterviewStore } from "@/stores/interviewStore";
import { Send, CheckCircle, Brain } from "lucide-react";
import { toast } from "sonner";

interface Message {
  role: "ai" | "user";
  content: string;
  topic?: string;
}

export default function InterviewSessionPage() {
  const { id } = useParams();
  const router = useRouter();
  const { currentQuestion, setCurrentQuestion, setComplete, isComplete } = useInterviewStore();
  const [messages, setMessages] = useState<Message[]>([]);
  const [answer, setAnswer] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  // Load first question
  useEffect(() => {
    if (currentQuestion) {
      setMessages([{ role: "ai", content: currentQuestion.question_text, topic: currentQuestion.topic || undefined }]);
    } else {
      // Fetch interview data
      interviewAPI.get(id as string).then((res) => {
        const data = res.data.data;
        if (data.status === "completed") {
          router.push(`/interviews/${id}/replay`);
          return;
        }
        const msgs: Message[] = [];
        (data.questions || []).forEach((q: { question_text: string; topic?: string }) => {
          msgs.push({ role: "ai", content: q.question_text, topic: q.topic });
        });
        setMessages(msgs);
      });
    }
  }, [currentQuestion, id, router]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const answerMutation = useMutation({
    mutationFn: (ans: string) => interviewAPI.answer(id as string, { answer: ans }),
    onSuccess: (res) => {
      const data = res.data.data;
      if (data.is_complete) {
        setComplete();
        toast.info("Interview complete! Getting your evaluation...");
      } else if (data.question) {
        setMessages((prev) => [...prev, { role: "ai", content: data.question.question_text, topic: data.question.topic }]);
        setCurrentQuestion(data.question);
      }
    },
    onError: () => toast.error("Failed to submit answer"),
  });

  const completeMutation = useMutation({
    mutationFn: () => interviewAPI.complete(id as string),
    onSuccess: () => {
      toast.success("Evaluation ready!");
      router.push(`/interviews/${id}/replay`);
    },
    onError: () => toast.error("Failed to complete"),
  });

  const handleSend = () => {
    if (!answer.trim()) return;
    setMessages((prev) => [...prev, { role: "user", content: answer }]);
    answerMutation.mutate(answer);
    setAnswer("");
  };

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Brain className="h-5 w-5 text-primary" /> Mock Interview
        </h2>
        {isComplete && (
          <Button onClick={() => completeMutation.mutate()} disabled={completeMutation.isPending}>
            <CheckCircle className="h-4 w-4 mr-2" />
            {completeMutation.isPending ? "Evaluating..." : "Get Evaluation"}
          </Button>
        )}
        {!isComplete && (
          <Button variant="outline" onClick={() => { setComplete(); }}>
            End Interview
          </Button>
        )}
      </div>

      {/* Chat */}
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[80%] rounded-lg px-4 py-3 ${
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-secondary text-secondary-foreground"
                }`}>
                  {msg.topic && <span className="text-xs opacity-70 block mb-1">[{msg.topic}]</span>}
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            {answerMutation.isPending && (
              <div className="flex justify-start">
                <div className="bg-secondary rounded-lg px-4 py-3 text-sm text-muted-foreground animate-pulse">
                  AI is thinking...
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </CardContent>
      </Card>

      {/* Input */}
      {!isComplete && (
        <div className="flex gap-2">
          <Textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Type your answer..."
            className="min-h-[80px]"
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
          />
          <Button onClick={handleSend} disabled={answerMutation.isPending || !answer.trim()} className="self-end">
            <Send className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
