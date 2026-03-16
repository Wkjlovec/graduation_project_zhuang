package com.graduation.forum.controller;

import com.graduation.common.ApiResponse;
import com.graduation.forum.dto.CommentResponse;
import com.graduation.forum.dto.CreateCommentRequest;
import com.graduation.forum.dto.CreatePostRequest;
import com.graduation.forum.dto.PostDetailResponse;
import com.graduation.forum.dto.PostSummaryResponse;
import com.graduation.forum.security.RequestUser;
import com.graduation.forum.security.RequestUserResolver;
import com.graduation.forum.service.ForumService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/posts")
public class ForumController {

    private final ForumService forumService;
    private final RequestUserResolver requestUserResolver;

    public ForumController(ForumService forumService, RequestUserResolver requestUserResolver) {
        this.forumService = forumService;
        this.requestUserResolver = requestUserResolver;
    }

    @GetMapping
    public ApiResponse<List<PostSummaryResponse>> list(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size
    ) {
        return ApiResponse.ok(forumService.listPosts(page, size));
    }

    @PostMapping
    public ApiResponse<PostSummaryResponse> create(
            @Valid @RequestBody CreatePostRequest request,
            HttpServletRequest httpServletRequest
    ) {
        RequestUser user = requestUserResolver.resolve(httpServletRequest);
        return ApiResponse.ok(forumService.createPost(request, user));
    }

    @GetMapping("/{postId}")
    public ApiResponse<PostDetailResponse> detail(@PathVariable Long postId) {
        return ApiResponse.ok(forumService.getPostDetail(postId));
    }

    @PostMapping("/{postId}/comments")
    public ApiResponse<CommentResponse> addComment(
            @PathVariable Long postId,
            @Valid @RequestBody CreateCommentRequest request,
            HttpServletRequest httpServletRequest
    ) {
        RequestUser user = requestUserResolver.resolve(httpServletRequest);
        return ApiResponse.ok(forumService.addComment(postId, request, user));
    }

    @PostMapping("/{postId}/like")
    public ApiResponse<PostSummaryResponse> like(@PathVariable Long postId, HttpServletRequest httpServletRequest) {
        RequestUser user = requestUserResolver.resolve(httpServletRequest);
        return ApiResponse.ok(forumService.likePost(postId, user));
    }
}
