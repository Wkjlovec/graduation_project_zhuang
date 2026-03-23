import { createRouter, createWebHistory } from "vue-router";
import LoginView from "../views/LoginView.vue";
import PostListView from "../views/PostListView.vue";
import PostDetailView from "../views/PostDetailView.vue";
import CreatePostView from "../views/CreatePostView.vue";
import ProfileView from "../views/ProfileView.vue";
import NotificationView from "../views/NotificationView.vue";
import { ACCESS_TOKEN_KEY } from "../stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/posts" },
    { path: "/login", component: LoginView },
    { path: "/posts", component: PostListView },
    { path: "/posts/:id", component: PostDetailView },
    { path: "/create", component: CreatePostView },
    { path: "/profile", component: ProfileView },
    { path: "/notifications", component: NotificationView }
  ]
});

router.beforeEach((to) => {
  if (to.path === "/login" || to.path === "/posts" || to.path.startsWith("/posts/")) {
    return true;
  }
  const token = localStorage.getItem(ACCESS_TOKEN_KEY);
  if (!token) {
    return "/login";
  }
  return true;
});

export default router;
