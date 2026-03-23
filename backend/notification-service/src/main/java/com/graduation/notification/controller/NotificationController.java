package com.graduation.notification.controller;

import com.graduation.common.ApiResponse;
import com.graduation.common.ServiceConstants;
import com.graduation.notification.dto.NotificationHomeResponse;
import com.graduation.notification.dto.NotificationItemResponse;
import com.graduation.notification.exception.NotificationBusinessException;
import com.graduation.notification.service.NotificationService;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/notifications")
public class NotificationController {

    private final NotificationService notificationService;

    public NotificationController(NotificationService notificationService) {
        this.notificationService = notificationService;
    }

    @GetMapping("/home")
    public ApiResponse<NotificationHomeResponse> home(
            @RequestHeader(value = ServiceConstants.HEADER_USER_ID, required = false) String userIdHeader
    ) {
        return ApiResponse.ok(notificationService.home(parseUserId(userIdHeader)));
    }

    @GetMapping("/my")
    public ApiResponse<List<NotificationItemResponse>> my(
            @RequestHeader(value = ServiceConstants.HEADER_USER_ID, required = false) String userIdHeader
    ) {
        return ApiResponse.ok(notificationService.my(parseUserId(userIdHeader)));
    }

    @PostMapping("/{notificationId}/read")
    public ApiResponse<Void> read(
            @PathVariable Long notificationId,
            @RequestHeader(value = ServiceConstants.HEADER_USER_ID, required = false) String userIdHeader
    ) {
        notificationService.markRead(parseUserId(userIdHeader), notificationId);
        return ApiResponse.ok(null);
    }

    private Long parseUserId(String userIdHeader) {
        if (userIdHeader == null || userIdHeader.isBlank()) {
            return null;
        }
        try {
            return Long.parseLong(userIdHeader);
        } catch (NumberFormatException ex) {
            throw new NotificationBusinessException(4001, "invalid user id header");
        }
    }
}
