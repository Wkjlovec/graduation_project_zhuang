package com.graduation.forum.dto;

import java.time.OffsetDateTime;
import java.util.List;

public record PostDetailResponse(
        Long postId,
        String title,
        String content,
        Long sectionId,
        String sectionName,
        Long authorId,
        String authorName,
        Integer likeCount,
        OffsetDateTime createdAt,
        String editedHint,
        List<CommentResponse> comments
) {
}
