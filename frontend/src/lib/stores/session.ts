import { writable } from 'svelte/store';

interface SessionState {
  queriesRemaining: number | null;
  isFreeTier: boolean;
}

function createSessionStore() {
  const { subscribe, set, update } = writable<SessionState>({
    queriesRemaining: null,
    isFreeTier: true,
  });

  return {
    subscribe,
    updateFromResponse: (credits_remaining: number) => {
      update((state) => ({
        ...state,
        queriesRemaining: credits_remaining,
      }));
    },
  };
}

export const sessionStore = createSessionStore();
