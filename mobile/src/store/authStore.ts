import { Session, User } from '@supabase/supabase-js';
import { create } from 'zustand';

type AuthState = {
  session: Session | null;
  user: User | null;
  jwt: string | null;
  loading: boolean;
  setSession: (session: Session | null) => void;
  setLoading: (loading: boolean) => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  session: null,
  user: null,
  jwt: null,
  loading: true,
  setSession: (session) =>
    set({
      session,
      user: session?.user ?? null,
      jwt: session?.access_token ?? null,
    }),
  setLoading: (loading) => set({ loading }),
}));
