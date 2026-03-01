"use client";
import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { UserRead } from "@/types";

interface AuthState {
  user: UserRead | null;
  isAuthenticated: boolean;
  setUser: (user: UserRead | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      logout: () => set({ user: null, isAuthenticated: false }),
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);
