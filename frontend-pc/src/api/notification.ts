import { http } from "./http";

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export interface NotificationItem {
  notificationId: number;
  title: string;
  content: string;
  read: boolean;
  createdAt: string;
}

export interface NotificationHomePayload {
  announcements: NotificationItem[];
  unreadCount: number;
}

export async function getNotificationHome() {
  const response = await http.get<ApiResponse<NotificationHomePayload>>("/api/notifications/home");
  return response.data.data;
}
