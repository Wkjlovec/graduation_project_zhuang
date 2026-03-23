package com.graduation.search.dto;

public record SearchPostResponse(
        Long postId,
        String title,
        String contentPreview,
        Long sectionId,
        String sectionName,
        Long authorId,
        String authorName,
        Integer likeCount,
        String createdAt,
        String editedHint
) {
}
