package com.graduation.media.controller;

import com.graduation.common.ApiResponse;
import com.graduation.media.dto.MediaHomeResponse;
import com.graduation.media.dto.MediaRecommendationItem;
import com.graduation.media.service.MediaRecommendationService;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/media")
public class MediaController {

    private final MediaRecommendationService mediaRecommendationService;

    public MediaController(MediaRecommendationService mediaRecommendationService) {
        this.mediaRecommendationService = mediaRecommendationService;
    }

    @GetMapping("/home")
    public ApiResponse<MediaHomeResponse> home() {
        return ApiResponse.ok(mediaRecommendationService.home());
    }

    @GetMapping("/recommendations")
    public ApiResponse<List<MediaRecommendationItem>> recommendations(
            @RequestParam(defaultValue = "all") String type
    ) {
        return ApiResponse.ok(mediaRecommendationService.recommendations(type));
    }
}
