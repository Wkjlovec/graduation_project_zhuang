package com.graduation.notification.repository;

import com.graduation.notification.domain.NotificationMessage;
import com.graduation.notification.domain.NotificationType;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface NotificationMessageRepository extends JpaRepository<NotificationMessage, Long> {

    List<NotificationMessage> findTop5ByTypeOrderByCreatedAtDesc(NotificationType type);

    List<NotificationMessage> findTop20ByUserIdOrderByCreatedAtDesc(Long userId);

    long countByUserIdAndReadFalse(Long userId);

    Optional<NotificationMessage> findByIdAndUserId(Long id, Long userId);
}
