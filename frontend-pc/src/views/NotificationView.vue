<template>
  <el-card>
    <template #header>
      <div class="header-row">
        <strong>我的通知</strong>
        <el-button :loading="loading" @click="loadNotifications">刷新</el-button>
      </div>
    </template>
    <el-skeleton v-if="loading" :rows="5" animated />
    <el-alert v-else-if="errorMessage" :title="errorMessage" type="error" show-icon :closable="false">
      <template #default>
        <el-button text type="primary" @click="loadNotifications">重试</el-button>
      </template>
    </el-alert>
    <el-empty v-else-if="notifications.length === 0" description="暂无通知" />
    <el-space v-else direction="vertical" fill style="width: 100%">
      <el-card v-for="item in notifications" :key="item.notificationId" shadow="never">
        <div class="item-header">
          <strong>{{ item.title }}</strong>
          <el-tag :type="item.read ? 'info' : 'danger'" size="small">{{ item.read ? "已读" : "未读" }}</el-tag>
        </div>
        <p>{{ item.content }}</p>
        <div class="item-footer">
          <span>{{ item.createdAt }}</span>
          <el-button v-if="!item.read" link type="primary" @click="markRead(item.notificationId)">标记已读</el-button>
        </div>
      </el-card>
    </el-space>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { getMyNotifications, markNotificationRead, type NotificationItem } from "../api/notification";

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
    ElMessage.success("已标记为已读");
    await loadNotifications();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "操作失败");
  }
}

onMounted(async () => {
  await loadNotifications();
});
</script>

<style scoped>
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #999;
}
</style>
