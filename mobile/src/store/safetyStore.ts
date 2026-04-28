import { create } from 'zustand';

type AccompanimentSession = {
  id: string;
  expected_arrival_at: string;
  status: string;
};

type SafetyState = {
  accompanimentSession: AccompanimentSession | null;
  serverClientDriftMs: number;
  setAccompanimentSession: (session: AccompanimentSession | null) => void;
  setServerClientDriftMs: (serverNowIso: string) => void;
};

export const useSafetyStore = create<SafetyState>((set) => ({
  accompanimentSession: null,
  serverClientDriftMs: 0,
  setAccompanimentSession: (accompanimentSession) => set({ accompanimentSession }),
  setServerClientDriftMs: (serverNowIso) => {
    const serverNow = new Date(serverNowIso).getTime();
    const clientNow = Date.now();
    set({ serverClientDriftMs: serverNow - clientNow });
  },
}));
