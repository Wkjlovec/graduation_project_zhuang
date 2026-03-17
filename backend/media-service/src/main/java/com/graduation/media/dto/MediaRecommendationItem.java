package com.graduation.media.dto;

public record MediaRecommendationItem(
        String type,
        String title,
        String author,
        String reason
) {
}
