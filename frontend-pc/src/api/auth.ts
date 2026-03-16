import { http } from "./http";

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export interface AuthTokenPayload {
  userId: number;
  username: string;
  nickname: string;
  token: string;
  tokenType: string;
}

export interface ProfilePayload {
  userId: number;
  username: string;
  nickname: string;
  createdAt: string;
}

export async function login(username: string, password: string) {
  const response = await http.post<ApiResponse<AuthTokenPayload>>("/api/auth/login", { username, password });
  return response.data.data;
}

export async function register(username: string, password: string, nickname: string) {
  const response = await http.post<ApiResponse<AuthTokenPayload>>("/api/auth/register", {
    username,
    password,
    nickname
  });
  return response.data.data;
}

export async function getProfile() {
  const response = await http.get<ApiResponse<ProfilePayload>>("/api/users/me");
  return response.data.data;
}
