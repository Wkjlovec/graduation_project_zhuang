import { defineStore } from "pinia";

const TOKEN_KEY = "forum_mobile_token";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) ?? ""
  }),
  actions: {
    setToken(token: string) {
      this.token = token;
      localStorage.setItem(TOKEN_KEY, token);
    },
    clearToken() {
      this.token = "";
      localStorage.removeItem(TOKEN_KEY);
    }
  }
});
