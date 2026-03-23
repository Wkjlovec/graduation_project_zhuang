package com.graduation.forum.repository;

import com.graduation.forum.domain.ForumPost;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ForumPostRepository extends JpaRepository<ForumPost, Long> {

    Page<ForumPost> findBySectionId(Long sectionId, Pageable pageable);
}
