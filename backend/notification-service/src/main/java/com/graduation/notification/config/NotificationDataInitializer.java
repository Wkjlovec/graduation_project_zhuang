package com.graduation.notification.config;

import com.graduation.notification.domain.NotificationMessage;
import com.graduation.notification.domain.NotificationType;
import com.graduation.notification.repository.NotificationMessageRepository;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

@Component
public class NotificationDataInitializer implements ApplicationRunner {

    private final NotificationMessageRepository repository;

    public NotificationDataInitializer(NotificationMessageRepository repository) {
        this.repository = repository;
    }

    @Override
    public void run(ApplicationArguments args) {
        if (repository.count() > 0) {
            return;
        }
        repository.save(buildAnnouncement("系统公告", "欢迎使用微服务论坛系统，首页已支持通知、搜索与推荐模块。"));
        repository.save(buildAnnouncement("活动提醒", "本周五将开展技术分享，欢迎在技术问答分区讨论。"));
        repository.save(buildAnnouncement("维护通知", "每日凌晨2:00进行例行备份，可能有短暂波动。"));
        repository.save(buildUserMessage(1L, "私信提醒", "你收到一条新的评论回复，请前往帖子详情查看。"));
    }

    private NotificationMessage buildAnnouncement(String title, String content) {
        NotificationMessage message = new NotificationMessage();
        message.setType(NotificationType.ANNOUNCEMENT);
        message.setTitle(title);
        message.setContent(content);
        message.setRead(false);
        return message;
    }

    private NotificationMessage buildUserMessage(Long userId, String title, String content) {
        NotificationMessage message = new NotificationMessage();
        message.setType(NotificationType.USER);
        message.setUserId(userId);
        message.setTitle(title);
        message.setContent(content);
        message.setRead(false);
        return message;
    }
}
