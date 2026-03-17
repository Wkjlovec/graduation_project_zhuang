import { http } from "./http";

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export interface MediaRecommendationItem {
  type: string;
  title: string;
  author: string;
  reason: string;
}

export interface MediaHomePayload {
  music: MediaRecommendationItem[];
  books: MediaRecommendationItem[];
}

export async function getMediaHome() {
  const response = await http.get<ApiResponse<MediaHomePayload>>("/api/media/home");
  return response.data.data;
}
