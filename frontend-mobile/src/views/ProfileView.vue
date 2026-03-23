<template>
  <div class="page" v-if="profile">
    <van-nav-bar title="个人中心" left-arrow @click-left="goBack" />
    <van-cell-group inset>
      <van-cell title="用户ID" :value="String(profile.userId)" />
      <van-cell title="用户名" :value="profile.username" />
      <van-cell title="昵称" :value="profile.nickname" />
      <van-cell title="注册时间" :value="profile.createdAt" />
      <van-cell title="我的通知" is-link @click="goNotifications" />
    </van-cell-group>
    <div style="margin: 16px;">
      <van-button block type="danger" :loading="logoutLoading" @click="logout">退出登录</van-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { showToast } from "vant";
import { getProfile, type ProfilePayload } from "../api/auth";
import { useAuthStore } from "../stores/auth";
import { logout as logoutApi } from "../api/auth";

const router = useRouter();
const authStore = useAuthStore();
const profile = ref<ProfilePayload | null>(null);
const logoutLoading = ref(false);

onMounted(async () => {
  profile.value = await getProfile();
});

async function logout() {
  logoutLoading.value = true;
  try {
    await logoutApi();
  } catch {
    // 忽略服务端登出失败，仍执行本地会话清理。
  } finally {
    authStore.clearSession();
    logoutLoading.value = false;
    showToast("已退出登录");
    router.replace("/login");
  }
}

function goBack() {
  router.back();
}

function goNotifications() {
  router.push("/notifications");
}
</script>
