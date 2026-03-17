package com.graduation.search.controller;

import com.graduation.common.ApiResponse;
import com.graduation.search.dto.SearchPostResponse;
import com.graduation.search.service.SearchService;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/search")
public class SearchController {

    private final SearchService searchService;

    public SearchController(SearchService searchService) {
        this.searchService = searchService;
    }

    @GetMapping("/posts")
    public ApiResponse<List<SearchPostResponse>> posts(
            @RequestParam(defaultValue = "") String keyword,
            @RequestParam(required = false) Long sectionId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size
    ) {
        return ApiResponse.ok(searchService.searchPosts(keyword, sectionId, page, size));
    }
}
