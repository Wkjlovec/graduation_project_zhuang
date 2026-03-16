package com.graduation.forum.config;

import com.graduation.forum.domain.ForumPost;
import com.graduation.forum.repository.ForumPostRepository;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

@Component
public class DemoDataInitializer implements ApplicationRunner {

    private static final int DEMO_POST_COUNT = 8;

    private final ForumPostRepository forumPostRepository;

    public DemoDataInitializer(ForumPostRepository forumPostRepository) {
        this.forumPostRepository = forumPostRepository;
    }

    @Override
    public void run(ApplicationArguments args) {
        if (forumPostRepository.count() > 0) {
            return;
        }
        for (int i = 1; i <= DEMO_POST_COUNT; i++) {
            ForumPost post = new ForumPost();
            post.setTitle("演示帖子 " + i);
            post.setContent("这是用于联调和演示的初始化帖子内容，编号：" + i);
            post.setAuthorId(1L);
            post.setAuthorName("demo_user");
            post.setLikeCount(i * 2);
            forumPostRepository.save(post);
        }
    }
}
