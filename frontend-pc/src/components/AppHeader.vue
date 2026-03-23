<template>
  <el-header class="header">
    <div class="title">微服务论坛系统（PC）</div>
    <div class="actions">
      <el-button link @click="goPosts">帖子</el-button>
      <el-button link @click="goNotifications">通知</el-button>
      <el-button link @click="goCreate">发帖</el-button>
      <el-button link @click="goProfile">个人中心</el-button>
      <el-button v-if="isLogin" :loading="logoutLoading" type="danger" size="small" @click="logout">退出</el-button>
      <el-button v-else type="primary" size="small" @click="goLogin">登录</el-button>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../stores/auth";
import { logout as logoutApi } from "../api/auth";

const router = useRouter();
const authStore = useAuthStore();
const isLogin = computed(() => Boolean(authStore.token));
const logoutLoading = ref(false);

function goPosts() {
  router.push("/posts");
}
function goNotifications() {
  router.push("/notifications");
}
function goCreate() {
  router.push("/create");
}
function goProfile() {
  router.push("/profile");
}
function goLogin() {
  router.push("/login");
}
async function logout() {
  logoutLoading.value = true;
  try {
    await logoutApi();
  } catch {
    // 忽略服务端登出失败，仍执行本地会话清理。
  } finally {
    authStore.clearSession();
    logoutLoading.value = false;
    ElMessage.success("已退出登录");
    router.push("/login");
  }
}
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  background: #1f4b99;
  color: #fff;
  padding: 0 16px;
}

.title {
  font-weight: 700;
}

.actions {
  display: flex;
  gap: 8px;
  align-items: center;
}
</style>
