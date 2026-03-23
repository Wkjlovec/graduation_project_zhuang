package com.graduation.notification.service;

import com.graduation.notification.domain.NotificationMessage;
import com.graduation.notification.domain.NotificationType;
import com.graduation.notification.dto.NotificationHomeResponse;
import com.graduation.notification.dto.NotificationItemResponse;
import com.graduation.notification.exception.NotificationBusinessException;
import com.graduation.notification.repository.NotificationMessageRepository;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class NotificationService {

    private final NotificationMessageRepository repository;

    public NotificationService(NotificationMessageRepository repository) {
        this.repository = repository;
    }

    @Transactional(readOnly = true)
    public NotificationHomeResponse home(Long userId) {
        List<NotificationItemResponse> announcements = repository.findTop5ByTypeOrderByCreatedAtDesc(NotificationType.ANNOUNCEMENT)
                .stream()
                .map(this::toResponse)
                .toList();
        long unreadCount = userId == null ? 0 : repository.countByUserIdAndReadFalse(userId);
        return new NotificationHomeResponse(announcements, unreadCount);
    }

    @Transactional(readOnly = true)
    public List<NotificationItemResponse> my(Long userId) {
        if (userId == null) {
            throw new NotificationBusinessException(4010, "missing user identity");
        }
        return repository.findTop20ByUserIdOrderByCreatedAtDesc(userId).stream().map(this::toResponse).toList();
    }

    @Transactional
    public void markRead(Long userId, Long notificationId) {
        if (userId == null) {
            throw new NotificationBusinessException(4010, "missing user identity");
        }
        NotificationMessage message = repository.findByIdAndUserId(notificationId, userId)
                .orElseThrow(() -> new NotificationBusinessException(4041, "notification not found"));
        message.setRead(true);
        repository.save(message);
    }

    private NotificationItemResponse toResponse(NotificationMessage message) {
        return new NotificationItemResponse(
                message.getId(),
                message.getTitle(),
                message.getContent(),
                message.getRead(),
                message.getCreatedAt()
        );
    }
}
