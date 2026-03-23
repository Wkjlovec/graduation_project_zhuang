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

export async function getMyNotifications() {
  const response = await http.get<ApiResponse<NotificationItem[]>>("/api/notifications/my");
  return response.data.data;
}

export async function markNotificationRead(notificationId: number) {
  await http.post<ApiResponse<null>>(`/api/notifications/${notificationId}/read`);
}
