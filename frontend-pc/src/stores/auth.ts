import { defineStore } from "pinia";

export const ACCESS_TOKEN_KEY = "forum_pc_token";
export const REFRESH_TOKEN_KEY = "forum_pc_refresh_token";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem(ACCESS_TOKEN_KEY) ?? "",
    refreshToken: localStorage.getItem(REFRESH_TOKEN_KEY) ?? ""
  }),
  actions: {
    setSession(token: string, refreshToken: string) {
      this.token = token;
      this.refreshToken = refreshToken;
      localStorage.setItem(ACCESS_TOKEN_KEY, token);
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    },
    clearSession() {
      this.token = "";
      this.refreshToken = "";
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
    },
    syncFromStorage() {
      this.token = localStorage.getItem(ACCESS_TOKEN_KEY) ?? "";
      this.refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY) ?? "";
    }
  }
});
