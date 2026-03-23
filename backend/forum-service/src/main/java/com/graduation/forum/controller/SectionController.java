package com.graduation.forum.controller;

import com.graduation.common.ApiResponse;
import com.graduation.forum.dto.SectionResponse;
import com.graduation.forum.service.ForumService;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/sections")
public class SectionController {

    private final ForumService forumService;

    public SectionController(ForumService forumService) {
        this.forumService = forumService;
    }

    @GetMapping
    public ApiResponse<List<SectionResponse>> list() {
        return ApiResponse.ok(forumService.listSections());
    }
}
