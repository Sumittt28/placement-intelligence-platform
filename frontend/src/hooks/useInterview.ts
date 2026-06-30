"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { interviewAPI, evaluationAPI, experienceAPI } from "@/lib/api";
import { useInterviewStore } from "@/stores/interviewStore";
import type {
  MockInterview,
  InterviewExperience,
  Evaluation,
  ReplayQuestion,
} from "@/types";

// ============ Mock Interviews ============

export function useInterviewList() {
  return useQuery({
    queryKey: ["interviews"],
    queryFn: async () => {
      const res = await interviewAPI.list();
      return res.data.data as MockInterview[];
    },
    staleTime: 60 * 1000,
  });
}

export function useInterview(id: string) {
  return useQuery({
    queryKey: ["interviews", id],
    queryFn: async () => {
      const res = await interviewAPI.get(id);
      return res.data.data as MockInterview;
    },
    enabled: !!id,
  });
}

export function useStartInterview() {
  const queryClient = useQueryClient();
  const { startSession, setCurrentQuestion } = useInterviewStore();

  return useMutation({
    mutationFn: (data: {
      interview_type: string;
      difficulty: string;
      company_id?: string;
      mode?: string;
    }) => interviewAPI.start(data),
    onSuccess: (res, variables) => {
      const data = res.data.data as { interview_id: string; first_question: { id: string; sequence_num: number; question_text: string; question_type?: string; topic?: string } } | null;
      if (data) {
        startSession({
          interviewId: data.interview_id,
          interviewType: variables.interview_type,
          difficulty: variables.difficulty,
          mode: (variables.mode || "text") as "text" | "voice",
          companyId: variables.company_id,
        });
        if (data.first_question) {
          setCurrentQuestion(data.first_question);
        }
      }
      queryClient.invalidateQueries({ queryKey: ["interviews"] });
    },
  });
}

export function useSubmitAnswer(interviewId: string) {
  const { setCurrentQuestion, setComplete } = useInterviewStore();

  return useMutation({
    mutationFn: (data: { answer: string; audio_url?: string }) =>
      interviewAPI.answer(interviewId, data),
    onSuccess: (res) => {
      const data = res.data.data as { is_complete: boolean; question?: { id: string; sequence_num: number; question_text: string; question_type?: string; topic?: string } | null; message?: string | null } | null;
      if (data?.is_complete) {
        setComplete();
      } else if (data?.question) {
        setCurrentQuestion(data.question);
      }
    },
  });
}

export function useCompleteInterview(interviewId: string) {
  const queryClient = useQueryClient();
  const { resetSession } = useInterviewStore();

  return useMutation({
    mutationFn: () => interviewAPI.complete(interviewId),
    onSuccess: () => {
      resetSession();
      queryClient.invalidateQueries({ queryKey: ["interviews"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["weaknesses"] });
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
    },
  });
}

export function useInterviewReplay(id: string) {
  return useQuery({
    queryKey: ["interviews", id, "replay"],
    queryFn: async () => {
      const res = await interviewAPI.replay(id);
      return res.data.data as {
        questions: ReplayQuestion[];
        evaluation: Evaluation;
      };
    },
    enabled: !!id,
  });
}

export function useEvaluation(interviewId: string) {
  return useQuery({
    queryKey: ["evaluations", interviewId],
    queryFn: async () => {
      const res = await evaluationAPI.get(interviewId);
      return res.data.data as Evaluation;
    },
    enabled: !!interviewId,
  });
}

// ============ Interview Experiences ============

export function useExperienceList(page = 1, limit = 20) {
  return useQuery({
    queryKey: ["experiences", page, limit],
    queryFn: async () => {
      const res = await experienceAPI.list(page, limit);
      return res.data.data as {
        experiences: InterviewExperience[];
        total: number;
      };
    },
  });
}

export function useExperience(id: string) {
  return useQuery({
    queryKey: ["experiences", id],
    queryFn: async () => {
      const res = await experienceAPI.get(id);
      return res.data.data as InterviewExperience;
    },
    enabled: !!id,
  });
}

export function useSubmitExperience() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Record<string, unknown>) => experienceAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["experiences"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
