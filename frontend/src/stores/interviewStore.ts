import { create } from "zustand";
import type { MockInterviewQuestion } from "@/types";

interface InterviewState {
  interviewId: string | null;
  currentQuestion: MockInterviewQuestion | null;
  isComplete: boolean;
  setInterview: (id: string, question: MockInterviewQuestion) => void;
  setCurrentQuestion: (question: MockInterviewQuestion | null) => void;
  setComplete: () => void;
  reset: () => void;
}

export const useInterviewStore = create<InterviewState>((set) => ({
  interviewId: null,
  currentQuestion: null,
  isComplete: false,

  setInterview: (id, question) => set({ interviewId: id, currentQuestion: question, isComplete: false }),
  setCurrentQuestion: (question) => set({ currentQuestion: question }),
  setComplete: () => set({ isComplete: true, currentQuestion: null }),
  reset: () => set({ interviewId: null, currentQuestion: null, isComplete: false }),
}));
