<template>
  <el-card v-if="profile">
    <template #header>
      <strong>个人中心</strong>
    </template>
    <p>用户ID：{{ profile.userId }}</p>
    <p>用户名：{{ profile.username }}</p>
    <p>昵称：{{ profile.nickname }}</p>
    <p>注册时间：{{ profile.createdAt }}</p>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { getProfile, type ProfilePayload } from "../api/auth";

const profile = ref<ProfilePayload | null>(null);

onMounted(async () => {
  profile.value = await getProfile();
});
</script>
