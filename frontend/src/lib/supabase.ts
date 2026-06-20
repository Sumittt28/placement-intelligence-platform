import { createClient, type SupabaseClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_KEY || "";

let _supabase: SupabaseClient | null = null;

function getSupabase(): SupabaseClient {
  if (!_supabase) {
    if (!supabaseUrl || !supabaseAnonKey) {
      console.warn(
        "Supabase URL or Key is missing. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_KEY in .env.local"
      );
      // Return a dummy client that won't crash during build
      // Real calls will fail gracefully at runtime
      _supabase = createClient("https://placeholder.supabase.co", "placeholder-key");
    } else {
      _supabase = createClient(supabaseUrl, supabaseAnonKey);
    }
  }
  return _supabase;
}

export const supabase = getSupabase();

// Auth helpers
export const supabaseAuth = {
  signInWithGoogle: async () => {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: `${typeof window !== "undefined" ? window.location.origin : ""}/login`,
          skipBrowserRedirect: true,
        },
      });
      if (error) {
        return { data: null, error };
      }
      // Only redirect if we got a valid URL
      if (data?.url) {
        window.location.href = data.url;
      }
      return { data, error: null };
    } catch (err) {
      return { data: null, error: { message: "Google sign-in is not available" } as any };
    }
  },

  signOut: async () => {
    const { error } = await supabase.auth.signOut();
    return { error };
  },

  getSession: async () => {
    const { data, error } = await supabase.auth.getSession();
    return { session: data.session, error };
  },

  onAuthStateChange: (callback: (event: string, session: unknown) => void) => {
    return supabase.auth.onAuthStateChange(callback);
  },
};
