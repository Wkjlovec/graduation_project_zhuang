import axios, { AxiosError, type AxiosRequestConfig } from "axios";
import { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY } from "../stores/auth";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8080";

export const http = axios.create({
  baseURL,
  timeout: 10000
});

const refreshClient = axios.create({
  baseURL,
  timeout: 10000
});

type RetryConfig = AxiosRequestConfig & { _retry?: boolean };
let isRefreshing = false;
let pendingQueue: Array<(token: string | null) => void> = [];

function setSessionToStorage(accessToken: string, refreshToken: string) {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  window.dispatchEvent(new Event("auth-session-changed"));
}

function clearSessionFromStorage() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  window.dispatchEvent(new Event("auth-session-changed"));
}

function redirectToLogin() {
  if (window.location.pathname !== "/login") {
    window.location.href = "/login";
  }
}

function resolveQueue(token: string | null) {
  pendingQueue.forEach((resolver) => resolver(token));
  pendingQueue = [];
}

function isAuthApi(url?: string) {
  if (!url) {
    return false;
  }
  return url.includes("/api/auth/login")
    || url.includes("/api/auth/register")
    || url.includes("/api/auth/refresh")
    || url.includes("/api/auth/logout");
}

function toError(error: unknown, fallback: string) {
  if (axios.isAxiosError(error)) {
    const message = (error.response?.data as { message?: string } | undefined)?.message;
    return new Error(message || fallback);
  }
  if (error instanceof Error) {
    return error;
  }
  return new Error(fallback);
}

http.interceptors.request.use((config) => {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

http.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<{ message?: string }>) => {
    const originalRequest = (error.config || {}) as RetryConfig;
    const status = error.response?.status;

    if (status === 401 && !originalRequest._retry && !isAuthApi(originalRequest.url)) {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (!refreshToken) {
        clearSessionFromStorage();
        redirectToLogin();
        return Promise.reject(new Error("登录已过期，请重新登录"));
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingQueue.push((newToken) => {
            if (!newToken) {
              reject(new Error("登录已过期，请重新登录"));
              return;
            }
            const headers = (originalRequest.headers ?? {}) as Record<string, string>;
            headers.Authorization = `Bearer ${newToken}`;
            originalRequest.headers = headers;
            resolve(http(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;
      try {
        const refreshResponse = await refreshClient.post("/api/auth/refresh", { refreshToken });
        const data = refreshResponse.data?.data as { token?: string; refreshToken?: string } | undefined;
        if (!data?.token || !data?.refreshToken) {
          throw new Error("刷新令牌失败");
        }
        setSessionToStorage(data.token, data.refreshToken);
        resolveQueue(data.token);
        const headers = (originalRequest.headers ?? {}) as Record<string, string>;
        headers.Authorization = `Bearer ${data.token}`;
        originalRequest.headers = headers;
        return http(originalRequest);
      } catch (refreshError) {
        resolveQueue(null);
        clearSessionFromStorage();
        redirectToLogin();
        return Promise.reject(toError(refreshError, "登录已过期，请重新登录"));
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(toError(error, "请求失败，请稍后重试"));
  }
);
