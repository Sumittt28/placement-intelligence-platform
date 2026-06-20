"use client";

import { useState, useRef, useCallback } from "react";
import { useMutation } from "@tanstack/react-query";
import { voiceAPI } from "@/lib/api";

interface UseVoiceRecorderReturn {
  isRecording: boolean;
  isTranscribing: boolean;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<Blob | null>;
  transcribedText: string;
  error: string | null;
}

export function useVoiceRecorder(): UseVoiceRecorderReturn {
  const [isRecording, setIsRecording] = useState(false);
  const [transcribedText, setTranscribedText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const transcribeMutation = useMutation({
    mutationFn: async (audioBlob: Blob) => {
      const res = await voiceAPI.transcribe(audioBlob);
      const data = res.data.data as { text: string } | string;
      return typeof data === 'string' ? data : data?.text || '';
    },
    onSuccess: (text) => {
      setTranscribedText(text);
      setError(null);
    },
    onError: (err) => {
      setError("Transcription failed. Please type your answer instead.");
      console.error("Transcription error:", err);
    },
  });

  const startRecording = useCallback(async () => {
    try {
      setError(null);
      setTranscribedText("");
      chunksRef.current = [];

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported("audio/webm")
          ? "audio/webm"
          : "audio/mp4",
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
    } catch (err) {
      setError("Microphone access denied. Please allow microphone access or type your answer.");
      console.error("Microphone error:", err);
    }
  }, []);

  const stopRecording = useCallback(async (): Promise<Blob | null> => {
    return new Promise((resolve) => {
      const mediaRecorder = mediaRecorderRef.current;
      if (!mediaRecorder || mediaRecorder.state === "inactive") {
        setIsRecording(false);
        resolve(null);
        return;
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });

        // Stop all tracks
        mediaRecorder.stream.getTracks().forEach((track) => track.stop());

        setIsRecording(false);

        // Transcribe
        if (audioBlob.size > 0) {
          transcribeMutation.mutate(audioBlob);
          resolve(audioBlob);
        } else {
          resolve(null);
        }
      };

      mediaRecorder.stop();
    });
  }, [transcribeMutation]);

  return {
    isRecording,
    isTranscribing: transcribeMutation.isPending,
    startRecording,
    stopRecording,
    transcribedText,
    error,
  };
}

interface UseVoiceSynthesizerReturn {
  isSynthesizing: boolean;
  isPlaying: boolean;
  synthesizeAndPlay: (text: string) => Promise<void>;
  stop: () => void;
  error: string | null;
}

export function useVoiceSynthesizer(): UseVoiceSynthesizerReturn {
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const synthesizeMutation = useMutation({
    mutationFn: async (text: string) => {
      const res = await voiceAPI.synthesize(text);
      const data = res.data.data as { audio_base64: string } | string;
      return typeof data === 'string' ? data : data?.audio_base64 || '';
    },
  });

  const synthesizeAndPlay = useCallback(
    async (text: string) => {
      try {
        setError(null);
        const base64Audio = await synthesizeMutation.mutateAsync(text);

        if (!base64Audio) {
          setError("Voice synthesis unavailable. Reading text instead.");
          return;
        }

        // Decode base64 and play
        const audioData = atob(base64Audio);
        const audioArray = new Uint8Array(audioData.length);
        for (let i = 0; i < audioData.length; i++) {
          audioArray[i] = audioData.charCodeAt(i);
        }
        const audioBlob = new Blob([audioArray], { type: "audio/wav" });
        const audioUrl = URL.createObjectURL(audioBlob);

        const audio = new Audio(audioUrl);
        audioRef.current = audio;

        audio.onplay = () => setIsPlaying(true);
        audio.onended = () => {
          setIsPlaying(false);
          URL.revokeObjectURL(audioUrl);
        };
        audio.onerror = () => {
          setIsPlaying(false);
          setError("Audio playback failed.");
        };

        await audio.play();
      } catch (err) {
        setError("Voice synthesis failed.");
        console.error("Synthesis error:", err);
      }
    },
    [synthesizeMutation]
  );

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  }, []);

  return {
    isSynthesizing: synthesizeMutation.isPending,
    isPlaying,
    synthesizeAndPlay,
    stop,
    error,
  };
}
