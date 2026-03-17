package com.graduation.forum.service;

import com.graduation.forum.domain.ForumPost;
import com.graduation.forum.domain.ForumSection;
import com.graduation.forum.domain.PostComment;
import com.graduation.forum.domain.PostLike;
import com.graduation.forum.dto.CommentResponse;
import com.graduation.forum.dto.CreateCommentRequest;
import com.graduation.forum.dto.CreatePostRequest;
import com.graduation.forum.dto.PostDetailResponse;
import com.graduation.forum.dto.PostSummaryResponse;
import com.graduation.forum.dto.SectionResponse;
import com.graduation.forum.dto.UpdateCommentRequest;
import com.graduation.forum.dto.UpdatePostRequest;
import com.graduation.forum.exception.ForumBusinessException;
import com.graduation.forum.repository.ForumPostRepository;
import com.graduation.forum.repository.PostCommentRepository;
import com.graduation.forum.repository.PostLikeRepository;
import com.graduation.forum.repository.ForumSectionRepository;
import com.graduation.forum.security.RequestUser;
import java.time.Duration;
import java.time.OffsetDateTime;
import java.util.List;
import org.springframework.cache.annotation.Caching;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.dao.DataIntegrityViolationException;
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
    private final PostLikeRepository postLikeRepository;
    private final ForumSectionRepository forumSectionRepository;

    public ForumService(
            ForumPostRepository forumPostRepository,
            PostCommentRepository postCommentRepository,
            PostLikeRepository postLikeRepository,
            ForumSectionRepository forumSectionRepository
    ) {
        this.forumPostRepository = forumPostRepository;
        this.postCommentRepository = postCommentRepository;
        this.postLikeRepository = postLikeRepository;
        this.forumSectionRepository = forumSectionRepository;
    }

    @Transactional(readOnly = true)
    public List<SectionResponse> listSections() {
        return forumSectionRepository.findByEnabledTrueOrderBySortOrderAscIdAsc()
                .stream()
                .map(section -> new SectionResponse(section.getId(), section.getName(), section.getDescription()))
                .toList();
    }

    @Transactional
    @CacheEvict(cacheNames = CACHE_POST_LIST, allEntries = true)
    public PostSummaryResponse createPost(CreatePostRequest request, RequestUser user) {
        validateUser(user);
        ForumSection section = loadSection(request.sectionId());
        ForumPost post = new ForumPost();
        post.setTitle(request.title());
        post.setContent(request.content());
        post.setAuthorId(user.userId());
        post.setAuthorName(user.username());
        post.setSectionId(section.getId());
        post.setSectionName(section.getName());
        ForumPost saved = forumPostRepository.save(post);
        return toSummary(saved);
    }

    @Transactional
    @Caching(evict = {
            @CacheEvict(cacheNames = CACHE_POST_LIST, allEntries = true),
            @CacheEvict(cacheNames = CACHE_POST_DETAIL, key = "#postId")
    })
    public PostSummaryResponse updatePost(Long postId, UpdatePostRequest request, RequestUser user) {
        validateUser(user);
        ForumPost post = loadPost(postId);
        assertPostOwner(post, user);
        ForumSection section = loadSection(request.sectionId());
        post.setTitle(request.title());
        post.setContent(request.content());
        post.setSectionId(section.getId());
        post.setSectionName(section.getName());
        ForumPost saved = forumPostRepository.save(post);
        return toSummary(saved);
    }

    @Transactional
    @Caching(evict = {
            @CacheEvict(cacheNames = CACHE_POST_LIST, allEntries = true),
            @CacheEvict(cacheNames = CACHE_POST_DETAIL, key = "#postId")
    })
    public void deletePost(Long postId, RequestUser user) {
        validateUser(user);
        ForumPost post = loadPost(postId);
        assertPostOwner(post, user);
        postCommentRepository.deleteByPostId(postId);
        postLikeRepository.deleteByPostId(postId);
        forumPostRepository.delete(post);
    }

    @Transactional(readOnly = true)
    @Cacheable(cacheNames = CACHE_POST_LIST, key = "#page + ':' + #size")
    public List<PostSummaryResponse> listPosts(int page, int size) {
        return listPostsBySection(null, page, size);
    }

    @Transactional(readOnly = true)
    @Cacheable(cacheNames = CACHE_POST_LIST, key = "T(java.lang.String).valueOf(#sectionId) + ':' + #page + ':' + #size")
    public List<PostSummaryResponse> listPostsBySection(Long sectionId, int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "id"));
        if (sectionId == null) {
            return forumPostRepository.findAll(pageable).stream().map(this::toSummary).toList();
        }
        return forumPostRepository.findBySectionId(sectionId, pageable).stream().map(this::toSummary).toList();
    }

    @Transactional(readOnly = true)
    @Cacheable(cacheNames = CACHE_POST_DETAIL, key = "#postId")
    public PostDetailResponse getPostDetail(Long postId) {
        ForumPost post = loadPost(postId);
        List<CommentResponse> comments = postCommentRepository.findByPostIdOrderByCreatedAtAsc(postId)
                .stream()
                .map(this::toCommentResponse)
                .toList();
        return new PostDetailResponse(
                post.getId(),
                post.getTitle(),
                post.getContent(),
                post.getSectionId(),
                post.getSectionName(),
                post.getAuthorId(),
                post.getAuthorName(),
                post.getLikeCount(),
                post.getCreatedAt(),
                buildEditedHint(post.getCreatedAt(), post.getUpdatedAt()),
                comments
        );
    }

    @Transactional
    @Caching(evict = {
            @CacheEvict(cacheNames = CACHE_POST_LIST, allEntries = true),
            @CacheEvict(cacheNames = CACHE_POST_DETAIL, key = "#postId")
    })
    public CommentResponse addComment(Long postId, CreateCommentRequest request, RequestUser user) {
        validateUser(user);
        loadPost(postId);
        Long parentCommentId = resolveParentCommentId(postId, request.parentCommentId());
        PostComment comment = new PostComment();
        comment.setPostId(postId);
        comment.setUserId(user.userId());
        comment.setUsername(user.username());
        comment.setContent(request.content());
        comment.setParentCommentId(parentCommentId);
        PostComment saved = postCommentRepository.save(comment);
        return toCommentResponse(saved);
    }

    @Transactional
    @Caching(evict = {
            @CacheEvict(cacheNames = CACHE_POST_LIST, allEntries = true),
            @CacheEvict(cacheNames = CACHE_POST_DETAIL, key = "#postId")
    })
    public CommentResponse updateComment(Long postId, Long commentId, UpdateCommentRequest request, RequestUser user) {
        validateUser(user);
        loadPost(postId);
        PostComment comment = postCommentRepository.findByIdAndPostId(commentId, postId)
                .orElseThrow(() -> new ForumBusinessException(4042, "comment not found"));
        if (!comment.getUserId().equals(user.userId())) {
            throw new ForumBusinessException(4033, "no permission to edit comment");
        }
        comment.setContent(request.content());
        PostComment saved = postCommentRepository.save(comment);
        return toCommentResponse(saved);
    }

    @Transactional
    @Caching(evict = {
            @CacheEvict(cacheNames = CACHE_POST_LIST, allEntries = true),
            @CacheEvict(cacheNames = CACHE_POST_DETAIL, key = "#postId")
    })
    public void deleteComment(Long postId, Long commentId, RequestUser user) {
        validateUser(user);
        ForumPost post = loadPost(postId);
        PostComment comment = postCommentRepository.findByIdAndPostId(commentId, postId)
                .orElseThrow(() -> new ForumBusinessException(4042, "comment not found"));
        if (!canDeleteComment(post, comment, user)) {
            throw new ForumBusinessException(4032, "no permission to delete comment");
        }
        postCommentRepository.delete(comment);
    }

    @Transactional
    @Caching(evict = {
            @CacheEvict(cacheNames = CACHE_POST_LIST, allEntries = true),
            @CacheEvict(cacheNames = CACHE_POST_DETAIL, key = "#postId")
    })
    public PostSummaryResponse likePost(Long postId, RequestUser user) {
        validateUser(user);
        ForumPost post = loadPost(postId);
        if (postLikeRepository.existsByPostIdAndUserId(postId, user.userId())) {
            throw new ForumBusinessException(4091, "you already liked this post");
        }
        PostLike postLike = new PostLike();
        postLike.setPostId(postId);
        postLike.setUserId(user.userId());
        try {
            postLikeRepository.save(postLike);
        } catch (DataIntegrityViolationException ex) {
            throw new ForumBusinessException(4091, "you already liked this post");
        }
        post.setLikeCount(post.getLikeCount() + 1);
        ForumPost saved = forumPostRepository.save(post);
        return toSummary(saved);
    }

    private ForumPost loadPost(Long postId) {
        return forumPostRepository.findById(postId)
                .orElseThrow(() -> new ForumBusinessException(4041, "post not found"));
    }

    private void validateUser(RequestUser user) {
        if (user.userId() <= 0 || user.username() == null || user.username().isBlank()) {
            throw new ForumBusinessException(4013, "invalid user identity");
        }
    }

    private void assertPostOwner(ForumPost post, RequestUser user) {
        if (!post.getAuthorId().equals(user.userId())) {
            throw new ForumBusinessException(4031, "no permission to operate this post");
        }
    }

    private boolean canDeleteComment(ForumPost post, PostComment comment, RequestUser user) {
        return comment.getUserId().equals(user.userId()) || post.getAuthorId().equals(user.userId());
    }

    private PostSummaryResponse toSummary(ForumPost post) {
        return new PostSummaryResponse(
                post.getId(),
                post.getTitle(),
                preview(post.getContent()),
                post.getSectionId(),
                post.getSectionName(),
                post.getAuthorId(),
                post.getAuthorName(),
                post.getLikeCount(),
                post.getCreatedAt(),
                buildEditedHint(post.getCreatedAt(), post.getUpdatedAt())
        );
    }

    private CommentResponse toCommentResponse(PostComment comment) {
        return new CommentResponse(
                comment.getId(),
                comment.getUserId(),
                comment.getUsername(),
                comment.getContent(),
                comment.getParentCommentId(),
                comment.getCreatedAt(),
                buildEditedHint(comment.getCreatedAt(), comment.getUpdatedAt())
        );
    }

    private String preview(String content) {
        if (content.length() <= PREVIEW_MAX_LENGTH) {
            return content;
        }
        return content.substring(0, PREVIEW_MAX_LENGTH);
    }

    private ForumSection loadSection(Long sectionId) {
        if (sectionId == null) {
            throw new ForumBusinessException(4004, "sectionId is required");
        }
        return forumSectionRepository.findByIdAndEnabledTrue(sectionId)
                .orElseThrow(() -> new ForumBusinessException(4043, "section not found"));
    }

    private Long resolveParentCommentId(Long postId, Long parentCommentId) {
        if (parentCommentId == null) {
            return null;
        }
        PostComment parentComment = postCommentRepository.findByIdAndPostId(parentCommentId, postId)
                .orElseThrow(() -> new ForumBusinessException(4042, "parent comment not found"));
        if (parentComment.getParentCommentId() != null) {
            throw new ForumBusinessException(4005, "only two-level comments are supported");
        }
        return parentComment.getId();
    }

    private String buildEditedHint(OffsetDateTime createdAt, OffsetDateTime updatedAt) {
        if (createdAt == null || updatedAt == null || !updatedAt.isAfter(createdAt.plusSeconds(5))) {
            return "";
        }
        Duration duration = Duration.between(updatedAt, OffsetDateTime.now());
        long minutes = Math.max(1, duration.toMinutes());
        if (minutes < 60) {
            return "该消息编辑于" + minutes + "分钟前";
        }
        long hours = Math.max(1, duration.toHours());
        if (hours < 24) {
            return "该消息编辑于" + hours + "小时前";
        }
        long days = Math.max(1, duration.toDays());
        return "该消息编辑于" + days + "天前";
    }
}
