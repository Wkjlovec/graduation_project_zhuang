package com.graduation.search.service;

import com.graduation.search.client.ForumClient;
import com.graduation.search.dto.ForumPostSummary;
import com.graduation.search.dto.SearchPostResponse;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class SearchService {

    private static final int DEFAULT_PAGE_SIZE = 50;

    private final ForumClient forumClient;

    public SearchService(ForumClient forumClient) {
        this.forumClient = forumClient;
    }

    public List<SearchPostResponse> searchPosts(String keyword, Long sectionId, int page, int size) {
        int resolvedSize = size <= 0 ? DEFAULT_PAGE_SIZE : size;
        List<ForumPostSummary> posts = forumClient.listPosts(sectionId, page, resolvedSize).data();
        if (posts == null) {
            throw new IllegalStateException("forum-service returned empty search data");
        }
        if (keyword == null || keyword.isBlank()) {
            return posts.stream().map(this::toResponse).toList();
        }
        String lowerKeyword = keyword.toLowerCase();
        return posts.stream()
                .filter(post -> hit(post, lowerKeyword))
                .map(this::toResponse)
                .toList();
    }

    private boolean hit(ForumPostSummary post, String keyword) {
        return contains(post.title(), keyword)
                || contains(post.contentPreview(), keyword)
                || contains(post.authorName(), keyword)
                || contains(post.sectionName(), keyword);
    }

    private boolean contains(String source, String keyword) {
        return source != null && source.toLowerCase().contains(keyword);
    }

    private SearchPostResponse toResponse(ForumPostSummary post) {
        return new SearchPostResponse(
                post.postId(),
                post.title(),
                post.contentPreview(),
                post.sectionId(),
                post.sectionName(),
                post.authorId(),
                post.authorName(),
                post.likeCount(),
                post.createdAt(),
                post.editedHint()
        );
    }
}
