"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { authAPI, userAPI } from "@/lib/api";
import { useAuthStore } from "@/stores/authStore";
import { useRouter } from "next/navigation";
import type { AuthResponse, User } from "@/types";

export function useLogin() {
  const { setAuth } = useAuthStore();
  const router = useRouter();

  return useMutation({
    mutationFn: (data: { email: string; password: string }) => authAPI.login(data),
    onSuccess: (res) => {
      const auth = res.data.data as AuthResponse;
      setAuth(auth.user, auth.access_token);
      router.push("/dashboard");
    },
  });
}

export function useRegister() {
  const { setAuth } = useAuthStore();
  const router = useRouter();

  return useMutation({
    mutationFn: (data: {
      email: string;
      password: string;
      full_name: string;
      kalvium_id?: string;
      batch?: string;
      graduation_year?: number;
    }) => authAPI.register(data),
    onSuccess: (res) => {
      const auth = res.data.data as AuthResponse;
      setAuth(auth.user, auth.access_token);
      router.push("/dashboard");
    },
  });
}

export function useGoogleAuth() {
  const { setAuth } = useAuthStore();
  const router = useRouter();

  return useMutation({
    mutationFn: (data: { access_token: string }) => authAPI.googleAuth(data),
    onSuccess: (res) => {
      const auth = res.data.data as AuthResponse;
      setAuth(auth.user, auth.access_token);
      router.push("/dashboard");
    },
  });
}

export function useCurrentUser() {
  return useQuery({
    queryKey: ["currentUser"],
    queryFn: async () => {
      const res = await userAPI.getMe();
      return res.data.data as User;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false,
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Record<string, unknown>) => userAPI.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["currentUser"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useLogout() {
  const { logout } = useAuthStore();
  const router = useRouter();
  const queryClient = useQueryClient();

  return () => {
    logout();
    queryClient.clear();
    router.push("/login");
  };
}
