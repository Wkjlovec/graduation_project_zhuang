<template>
  <div class="page">
    <van-nav-bar title="我的通知" left-arrow @click-left="goBack">
      <template #right>
        <van-button size="mini" :loading="loading" @click="loadNotifications">刷新</van-button>
      </template>
    </van-nav-bar>

    <div v-if="loading" class="loading-box">
      <van-loading size="24px" type="spinner" /> 加载中...
    </div>
    <van-cell-group v-else-if="errorMessage" inset>
      <van-cell title="加载失败" :label="errorMessage">
        <template #right-icon>
          <van-button size="mini" type="primary" plain @click="loadNotifications">重试</van-button>
        </template>
      </van-cell>
    </van-cell-group>
    <van-empty v-else-if="notifications.length === 0" description="暂无通知" />
    <van-cell-group v-else inset>
      <van-cell
        v-for="item in notifications"
        :key="item.notificationId"
        :title="item.title + (item.read ? '（已读）' : '（未读）')"
        :label="item.content + '\n' + item.createdAt"
      >
        <template #right-icon>
          <van-button
            v-if="!item.read"
            size="mini"
            type="primary"
            plain
            @click="markRead(item.notificationId)"
          >
            标记已读
          </van-button>
        </template>
      </van-cell>
    </van-cell-group>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { showToast } from "vant";
import { getMyNotifications, markNotificationRead, type NotificationItem } from "../api/notification";

const router = useRouter();
const notifications = ref<NotificationItem[]>([]);
const loading = ref(false);
const errorMessage = ref("");

async function loadNotifications() {
  loading.value = true;
  errorMessage.value = "";
  try {
    notifications.value = await getMyNotifications();
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "加载通知失败";
  } finally {
    loading.value = false;
  }
}

async function markRead(notificationId: number) {
  try {
    await markNotificationRead(notificationId);
    showToast("已标记为已读");
    await loadNotifications();
  } catch (error) {
    showToast(error instanceof Error ? error.message : "操作失败");
  }
}

function goBack() {
  router.back();
}

onMounted(async () => {
  await loadNotifications();
});
</script>

<style scoped>
.loading-box {
  padding: 16px;
  text-align: center;
  color: #666;
}
</style>
