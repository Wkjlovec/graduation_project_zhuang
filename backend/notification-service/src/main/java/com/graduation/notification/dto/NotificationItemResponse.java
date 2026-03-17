package com.graduation.notification.dto;

import java.time.OffsetDateTime;

public record NotificationItemResponse(
        Long notificationId,
        String title,
        String content,
        boolean read,
        OffsetDateTime createdAt
) {
}
