package com.graduation.forum.dto;

import java.time.OffsetDateTime;

public record CommentResponse(
        Long commentId,
        Long userId,
        String username,
        String content,
        Long parentCommentId,
        OffsetDateTime createdAt,
        String editedHint
) {
}
