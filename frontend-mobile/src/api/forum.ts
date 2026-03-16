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
  authorId: number;
  authorName: string;
  likeCount: number;
  createdAt: string;
}

export interface CommentItem {
  commentId: number;
  userId: number;
  username: string;
  content: string;
  createdAt: string;
}

export interface PostDetail extends Omit<PostSummary, "contentPreview"> {
  content: string;
  comments: CommentItem[];
}

export async function listPosts() {
  const response = await http.get<ApiResponse<PostSummary[]>>("/api/forum/posts");
  return response.data.data;
}

export async function createPost(title: string, content: string) {
  const response = await http.post<ApiResponse<PostSummary>>("/api/forum/posts", { title, content });
  return response.data.data;
}

export async function getPostDetail(postId: string) {
  const response = await http.get<ApiResponse<PostDetail>>(`/api/forum/posts/${postId}`);
  return response.data.data;
}

export async function addComment(postId: string, content: string) {
  const response = await http.post<ApiResponse<CommentItem>>(`/api/forum/posts/${postId}/comments`, { content });
  return response.data.data;
}

export async function likePost(postId: string) {
  const response = await http.post<ApiResponse<PostSummary>>(`/api/forum/posts/${postId}/like`);
  return response.data.data;
}
