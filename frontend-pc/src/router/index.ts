import { createRouter, createWebHistory } from "vue-router";
import LoginView from "../views/LoginView.vue";
import PostListView from "../views/PostListView.vue";
import PostDetailView from "../views/PostDetailView.vue";
import CreatePostView from "../views/CreatePostView.vue";
import ProfileView from "../views/ProfileView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/posts" },
    { path: "/login", component: LoginView },
    { path: "/posts", component: PostListView },
    { path: "/posts/:id", component: PostDetailView },
    { path: "/create", component: CreatePostView },
    { path: "/profile", component: ProfileView }
  ]
});

router.beforeEach((to) => {
  if (to.path === "/login" || to.path === "/posts" || to.path.startsWith("/posts/")) {
    return true;
  }
  const token = localStorage.getItem("forum_pc_token");
  if (!token) {
    return "/login";
  }
  return true;
});

export default router;
