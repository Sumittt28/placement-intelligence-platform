import { supabase } from "./supabase";
import { authAPI } from "./api";
import { useAuthStore } from "@/stores/authStore";

/**
 * Handle Supabase OAuth callback.
 * After Google OAuth redirect, exchange the Supabase session token
 * with our backend to get a JWT.
 */
export async function handleOAuthCallback(): Promise<boolean> {
  try {
    const { data } = await supabase.auth.getSession();
    const session = data.session;

    if (!session?.access_token) return false;

    // Exchange Supabase token with our backend
    const res = await authAPI.googleAuth({ access_token: session.access_token });
    const authData = res.data.data as {
      access_token: string;
      user: { id: string; email: string; full_name: string; role: string };
    };

    const store = useAuthStore.getState();
    store.setAuth(authData.user, authData.access_token);
    return true;
  } catch {
    return false;
  }
}

/**
 * Check if user is authenticated (has valid token in storage).
 */
export function isAuthenticated(): boolean {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("token");
}

/**
 * Get the current user's role from the store.
 */
export function getUserRole(): string | null {
  const store = useAuthStore.getState();
  return store.user?.role || null;
}
