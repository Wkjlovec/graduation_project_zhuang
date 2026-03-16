package com.graduation.forum.dto;

import java.time.OffsetDateTime;
import java.util.List;

public record PostDetailResponse(
        Long postId,
        String title,
        String content,
        Long authorId,
        String authorName,
        Integer likeCount,
        OffsetDateTime createdAt,
        List<CommentResponse> comments
) {
}
