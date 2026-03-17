package com.graduation.media.dto;

import java.util.List;

public record MediaHomeResponse(
        List<MediaRecommendationItem> music,
        List<MediaRecommendationItem> books
) {
}
