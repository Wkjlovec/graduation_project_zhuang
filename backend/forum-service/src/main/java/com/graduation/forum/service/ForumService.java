package com.graduation.forum.service;

import com.graduation.forum.domain.ForumPost;
import com.graduation.forum.domain.PostComment;
import com.graduation.forum.dto.CommentResponse;
import com.graduation.forum.dto.CreateCommentRequest;
import com.graduation.forum.dto.CreatePostRequest;
import com.graduation.forum.dto.PostDetailResponse;
import com.graduation.forum.dto.PostSummaryResponse;
import com.graduation.forum.exception.ForumBusinessException;
import com.graduation.forum.repository.ForumPostRepository;
import com.graduation.forum.repository.PostCommentRepository;
import com.graduation.forum.security.RequestUser;
import java.util.List;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ForumService {

    private static final int PREVIEW_MAX_LENGTH = 120;
    public static final String CACHE_POST_LIST = "forum:post:list";
    public static final String CACHE_POST_DETAIL = "forum:post:detail";

    private final ForumPostRepository forumPostRepository;
    private final PostCommentRepository postCommentRepository;

    public ForumService(ForumPostRepository forumPostRepository, PostCommentRepository postCommentRepository) {
        this.forumPostRepository = forumPostRepository;
        this.postCommentRepository = postCommentRepository;
    }

    @Transactional
    @CacheEvict(cacheNames = CACHE_POST_LIST, allEntries = true)
    public PostSummaryResponse createPost(CreatePostRequest request, RequestUser user) {
        ForumPost post = new ForumPost();
        post.setTitle(request.title());
        post.setContent(request.content());
        post.setAuthorId(user.userId());
        post.setAuthorName(user.username());
        ForumPost saved = forumPostRepository.save(post);
        return toSummary(saved);
    }

    @Transactional(readOnly = true)
    @Cacheable(cacheNames = CACHE_POST_LIST, key = "#page + ':' + #size")
    public List<PostSummaryResponse> listPosts(int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "id"));
        return forumPostRepository.findAll(pageable).stream().map(this::toSummary).toList();
    }

    @Transactional(readOnly = true)
    @Cacheable(cacheNames = CACHE_POST_DETAIL, key = "#postId")
    public PostDetailResponse getPostDetail(Long postId) {
        ForumPost post = loadPost(postId);
        List<CommentResponse> comments = postCommentRepository.findByPostIdOrderByCreatedAtAsc(postId)
                .stream()
                .map(comment -> new CommentResponse(
                        comment.getId(),
                        comment.getUserId(),
                        comment.getUsername(),
                        comment.getContent(),
                        comment.getCreatedAt()
                ))
                .toList();
        return new PostDetailResponse(
                post.getId(),
                post.getTitle(),
                post.getContent(),
                post.getAuthorId(),
                post.getAuthorName(),
                post.getLikeCount(),
                post.getCreatedAt(),
                comments
        );
    }

    @Transactional
    @CacheEvict(cacheNames = {CACHE_POST_DETAIL, CACHE_POST_LIST}, allEntries = true)
    public CommentResponse addComment(Long postId, CreateCommentRequest request, RequestUser user) {
        loadPost(postId);
        PostComment comment = new PostComment();
        comment.setPostId(postId);
        comment.setUserId(user.userId());
        comment.setUsername(user.username());
        comment.setContent(request.content());
        PostComment saved = postCommentRepository.save(comment);
        return new CommentResponse(saved.getId(), saved.getUserId(), saved.getUsername(), saved.getContent(), saved.getCreatedAt());
    }

    @Transactional
    @CacheEvict(cacheNames = {CACHE_POST_DETAIL, CACHE_POST_LIST}, allEntries = true)
    public PostSummaryResponse likePost(Long postId, RequestUser user) {
        if (user.userId() <= 0) {
            throw new ForumBusinessException(4013, "invalid user id");
        }
        ForumPost post = loadPost(postId);
        post.setLikeCount(post.getLikeCount() + 1);
        ForumPost saved = forumPostRepository.save(post);
        return toSummary(saved);
    }

    private ForumPost loadPost(Long postId) {
        return forumPostRepository.findById(postId)
                .orElseThrow(() -> new ForumBusinessException(4041, "post not found"));
    }

    private PostSummaryResponse toSummary(ForumPost post) {
        return new PostSummaryResponse(
                post.getId(),
                post.getTitle(),
                preview(post.getContent()),
                post.getAuthorId(),
                post.getAuthorName(),
                post.getLikeCount(),
                post.getCreatedAt()
        );
    }

    private String preview(String content) {
        if (content.length() <= PREVIEW_MAX_LENGTH) {
            return content;
        }
        return content.substring(0, PREVIEW_MAX_LENGTH);
    }
}
