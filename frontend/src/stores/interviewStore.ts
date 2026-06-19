import { create } from "zustand";

interface InterviewQuestion {
  id: string;
  sequence_num: number;
  question_text: string;
  question_type?: string;
  topic?: string;
}

interface InterviewSession {
  interviewId: string | null;
  interviewType: string | null;
  difficulty: string | null;
  mode: "text" | "voice";
  companyId: string | null;
  questionCount: number;
}

interface InterviewState {
  // Current session
  session: InterviewSession;
  currentQuestion: InterviewQuestion | null;
  isComplete: boolean;
  isLoading: boolean;

  // Actions
  startSession: (params: {
    interviewId: string;
    interviewType: string;
    difficulty: string;
    mode: "text" | "voice";
    companyId?: string;
  }) => void;
  setCurrentQuestion: (question: InterviewQuestion) => void;
  setComplete: () => void;
  setLoading: (loading: boolean) => void;
  resetSession: () => void;
}

const initialSession: InterviewSession = {
  interviewId: null,
  interviewType: null,
  difficulty: null,
  mode: "text",
  companyId: null,
  questionCount: 0,
};

export const useInterviewStore = create<InterviewState>((set) => ({
  session: initialSession,
  currentQuestion: null,
  isComplete: false,
  isLoading: false,

  startSession: ({ interviewId, interviewType, difficulty, mode, companyId }) => {
    set({
      session: {
        interviewId,
        interviewType,
        difficulty,
        mode: mode as "text" | "voice",
        companyId: companyId || null,
        questionCount: 0,
      },
      currentQuestion: null,
      isComplete: false,
      isLoading: false,
    });
  },

  setCurrentQuestion: (question) => {
    set((state) => ({
      currentQuestion: question,
      session: {
        ...state.session,
        questionCount: state.session.questionCount + 1,
      },
    }));
  },

  setComplete: () => {
    set({ isComplete: true });
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },

  resetSession: () => {
    set({
      session: initialSession,
      currentQuestion: null,
      isComplete: false,
      isLoading: false,
    });
  },
}));
