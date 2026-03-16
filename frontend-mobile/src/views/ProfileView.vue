<template>
  <div class="page" v-if="profile">
    <van-nav-bar title="个人中心" left-arrow @click-left="goBack" />
    <van-cell-group inset>
      <van-cell title="用户ID" :value="String(profile.userId)" />
      <van-cell title="用户名" :value="profile.username" />
      <van-cell title="昵称" :value="profile.nickname" />
      <van-cell title="注册时间" :value="profile.createdAt" />
    </van-cell-group>
    <div style="margin: 16px;">
      <van-button block type="danger" @click="logout">退出登录</van-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { getProfile, type ProfilePayload } from "../api/auth";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const profile = ref<ProfilePayload | null>(null);

onMounted(async () => {
  profile.value = await getProfile();
});

function logout() {
  authStore.clearToken();
  router.replace("/login");
}

function goBack() {
  router.back();
}
</script>
