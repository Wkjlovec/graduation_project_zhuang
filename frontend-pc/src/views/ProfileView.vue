<template>
  <el-card v-if="profile">
    <template #header>
      <strong>个人中心</strong>
    </template>
    <div class="avatar-box">
      <el-avatar :size="64">{{ avatarText }}</el-avatar>
    </div>
    <p>用户ID：{{ profile.userId }}</p>
    <p>用户名：{{ profile.username }}</p>
    <p>昵称：{{ profile.nickname }}</p>
    <p>注册时间：{{ profile.createdAt }}</p>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { getProfile, type ProfilePayload } from "../api/auth";

const profile = ref<ProfilePayload | null>(null);
const avatarText = computed(() => {
  const nickname = profile.value?.nickname?.trim();
  if (nickname) {
    return nickname.slice(0, 1).toUpperCase();
  }
  const username = profile.value?.username?.trim();
  return username ? username.slice(0, 1).toUpperCase() : "U";
});

onMounted(async () => {
  profile.value = await getProfile();
});
</script>

<style scoped>
.avatar-box {
  margin-bottom: 12px;
}
</style>
