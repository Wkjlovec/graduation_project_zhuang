import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8080";

export const http = axios.create({
  baseURL,
  timeout: 10000
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem("forum_pc_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
