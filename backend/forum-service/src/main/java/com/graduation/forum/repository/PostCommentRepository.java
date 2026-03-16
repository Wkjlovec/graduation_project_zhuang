package com.graduation.forum.repository;

import com.graduation.forum.domain.PostComment;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PostCommentRepository extends JpaRepository<PostComment, Long> {

    List<PostComment> findByPostIdOrderByCreatedAtAsc(Long postId);

    Optional<PostComment> findByIdAndPostId(Long id, Long postId);

    long deleteByPostId(Long postId);
}
