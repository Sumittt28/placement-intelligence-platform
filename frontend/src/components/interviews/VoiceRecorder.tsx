"use client";

import { useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { useVoiceRecorder } from "@/hooks/useVoice";
import { Mic, MicOff, Loader2 } from "lucide-react";

interface VoiceRecorderProps {
  onTranscript: (text: string) => void;
}

export function VoiceRecorder({ onTranscript }: VoiceRecorderProps) {
  const { isRecording, isTranscribing, startRecording, stopRecording, transcribedText, error } =
    useVoiceRecorder();
  const prevTranscriptRef = useRef("");

  // Pass transcribed text to parent via useEffect (prevents infinite re-renders)
  useEffect(() => {
    if (transcribedText && transcribedText !== prevTranscriptRef.current) {
      prevTranscriptRef.current = transcribedText;
      onTranscript(transcribedText);
    }
  }, [transcribedText, onTranscript]);

  const handleToggle = async () => {
    if (isRecording) {
      await stopRecording();
    } else {
      await startRecording();
    }
  };

  return (
    <div className="flex items-center gap-3">
      <Button
        type="button"
        variant={isRecording ? "destructive" : "outline"}
        size="sm"
        onClick={handleToggle}
        disabled={isTranscribing}
        className="gap-2"
      >
        {isTranscribing ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Transcribing...
          </>
        ) : isRecording ? (
          <>
            <MicOff className="h-4 w-4" />
            Stop Recording
          </>
        ) : (
          <>
            <Mic className="h-4 w-4" />
            Record Answer
          </>
        )}
      </Button>

      {isRecording && (
        <div className="flex items-center gap-1.5">
          <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
          <span className="text-xs text-muted-foreground">Recording...</span>
        </div>
      )}

      {error && (
        <p className="text-xs text-destructive">{error}</p>
      )}
    </div>
  );
}
