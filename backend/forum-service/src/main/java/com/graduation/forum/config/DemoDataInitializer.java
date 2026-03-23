package com.graduation.forum.config;

import com.graduation.forum.domain.ForumPost;
import com.graduation.forum.domain.ForumSection;
import com.graduation.forum.repository.ForumPostRepository;
import com.graduation.forum.repository.ForumSectionRepository;
import java.util.List;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

@Component
public class DemoDataInitializer implements ApplicationRunner {

    private static final int DEMO_POST_COUNT = 8;

    private final ForumPostRepository forumPostRepository;
    private final ForumSectionRepository forumSectionRepository;

    public DemoDataInitializer(ForumPostRepository forumPostRepository, ForumSectionRepository forumSectionRepository) {
        this.forumPostRepository = forumPostRepository;
        this.forumSectionRepository = forumSectionRepository;
    }

    @Override
    public void run(ApplicationArguments args) {
        initializeSections();
        if (forumPostRepository.count() > 0) {
            return;
        }
        List<ForumSection> sections = forumSectionRepository.findByEnabledTrueOrderBySortOrderAscIdAsc();
        if (sections.isEmpty()) {
            return;
        }
        for (int i = 1; i <= DEMO_POST_COUNT; i++) {
            ForumSection section = sections.get((i - 1) % sections.size());
            ForumPost post = new ForumPost();
            post.setTitle("演示帖子 " + i);
            post.setContent("这是用于联调和演示的初始化帖子内容，编号：" + i + "，所属分区：" + section.getName());
            post.setAuthorId(1L);
            post.setAuthorName("demo_user");
            post.setSectionId(section.getId());
            post.setSectionName(section.getName());
            post.setLikeCount(i * 2);
            forumPostRepository.save(post);
        }
    }

    private void initializeSections() {
        if (forumSectionRepository.count() > 0) {
            return;
        }
        forumSectionRepository.save(buildSection("校园交流", "课程、活动、校园生活讨论", 1));
        forumSectionRepository.save(buildSection("技术问答", "代码问题与项目经验分享", 2));
        forumSectionRepository.save(buildSection("二手闲置", "学习资料和闲置物品交换", 3));
    }

    private ForumSection buildSection(String name, String description, int sortOrder) {
        ForumSection section = new ForumSection();
        section.setName(name);
        section.setDescription(description);
        section.setSortOrder(sortOrder);
        section.setEnabled(true);
        return section;
    }
}
