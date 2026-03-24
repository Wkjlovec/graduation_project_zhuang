import { http } from "./http";

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export interface PostSummary {
  postId: number;
  title: string;
  contentPreview: string;
  sectionId: number;
  sectionName: string;
  authorId: number;
  authorName: string;
  likeCount: number;
  createdAt: string;
  editedHint: string;
}

export interface CommentItem {
  commentId: number;
  userId: number;
  username: string;
  content: string;
  parentCommentId: number | null;
  createdAt: string;
  editedHint: string;
}

export interface PostDetail extends Omit<PostSummary, "contentPreview"> {
  content: string;
  comments: CommentItem[];
}

export interface SectionItem {
  sectionId: number;
  name: string;
  description: string;
}

export async function listPosts(sectionId?: number, page = 0, size = 10) {
  const params = {
    page,
    size,
    ...(sectionId ? { sectionId } : {})
  };
  const response = await http.get<ApiResponse<PostSummary[]>>("/api/forum/posts", { params });
  return response.data.data;
}

export async function listSections() {
  const response = await http.get<ApiResponse<SectionItem[]>>("/api/forum/sections");
  return response.data.data;
}

export async function createPost(title: string, content: string, sectionId: number) {
  const response = await http.post<ApiResponse<PostSummary>>("/api/forum/posts", { title, content, sectionId });
  return response.data.data;
}

export async function updatePost(postId: string, title: string, content: string, sectionId: number) {
  const response = await http.put<ApiResponse<PostSummary>>(`/api/forum/posts/${postId}`, { title, content, sectionId });
  return response.data.data;
}

export async function deletePost(postId: string) {
  await http.delete(`/api/forum/posts/${postId}`);
}

export async function getPostDetail(postId: string) {
  const response = await http.get<ApiResponse<PostDetail>>(`/api/forum/posts/${postId}`);
  return response.data.data;
}

export async function addComment(postId: string, content: string, parentCommentId?: number) {
  const response = await http.post<ApiResponse<CommentItem>>(`/api/forum/posts/${postId}/comments`, {
    content,
    parentCommentId: parentCommentId ?? null
  });
  return response.data.data;
}

export async function updateComment(postId: string, commentId: string, content: string) {
  const response = await http.put<ApiResponse<CommentItem>>(`/api/forum/posts/${postId}/comments/${commentId}`, { content });
  return response.data.data;
}

export async function deleteComment(postId: string, commentId: string) {
  await http.delete(`/api/forum/posts/${postId}/comments/${commentId}`);
}

export async function likePost(postId: string) {
  const response = await http.post<ApiResponse<PostSummary>>(`/api/forum/posts/${postId}/like`);
  return response.data.data;
}

export async function searchPosts(keyword: string, sectionId?: number, page = 0, size = 10) {
  const response = await http.get<ApiResponse<PostSummary[]>>("/api/search/posts", {
    params: {
      keyword,
      page,
      size,
      ...(sectionId ? { sectionId } : {})
    }
  });
  return response.data.data;
}

export async function listHotPosts(limit = 5, sampleSize = 50) {
  const posts = await listPosts(undefined, 0, sampleSize);
  return [...posts]
    .sort((a, b) => {
      if (b.likeCount !== a.likeCount) {
        return b.likeCount - a.likeCount;
      }
      return String(b.createdAt).localeCompare(String(a.createdAt));
    })
    .slice(0, limit);
}
