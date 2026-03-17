package com.graduation.search.client;

import com.graduation.common.ApiResponse;
import com.graduation.search.dto.ForumPostSummary;
import java.util.List;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

@FeignClient(name = "forum-service")
public interface ForumClient {

    @GetMapping("/posts")
    ApiResponse<List<ForumPostSummary>> listPosts(
            @RequestParam(value = "sectionId", required = false) Long sectionId,
            @RequestParam("page") int page,
            @RequestParam("size") int size
    );
}
