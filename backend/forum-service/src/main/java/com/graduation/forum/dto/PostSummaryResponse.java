package com.graduation.forum.dto;

import java.time.OffsetDateTime;

public record PostSummaryResponse(
        Long postId,
        String title,
        String contentPreview,
        Long authorId,
        String authorName,
        Integer likeCount,
        OffsetDateTime createdAt
) {
}
