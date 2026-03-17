package com.graduation.notification.dto;

import java.util.List;

public record NotificationHomeResponse(
        List<NotificationItemResponse> announcements,
        long unreadCount
) {
}
