<template>
  <el-row :gutter="16">
    <el-col :span="16">
      <el-card>
        <template #header>
          <div class="header-row">
            <strong>帖子列表</strong>
            <div class="header-actions">
              <el-input
                v-model="keyword"
                placeholder="搜索标题/内容/作者/分区"
                style="width: 280px"
                @keyup.enter="loadPosts"
              />
              <el-select v-model="selectedSectionId" placeholder="全部分区" clearable style="width: 180px" @change="loadPosts">
                <el-option v-for="item in sections" :key="item.sectionId" :label="item.name" :value="item.sectionId" />
              </el-select>
              <el-button @click="loadPosts">搜索</el-button>
              <el-button type="primary" @click="goCreate">去发帖</el-button>
            </div>
          </div>
        </template>
        <el-empty v-if="posts.length === 0" description="暂无帖子" />
        <el-space v-else direction="vertical" fill style="width: 100%">
          <el-card v-for="post in posts" :key="post.postId" shadow="never">
            <h3>{{ post.title }}</h3>
            <p>分区：{{ post.sectionName }}</p>
            <p>{{ post.contentPreview }}</p>
            <div class="meta">
              <span>作者：{{ post.authorName }}</span>
              <span>点赞：{{ post.likeCount }}</span>
              <span v-if="post.editedHint">{{ post.editedHint }}</span>
              <el-button link @click="goDetail(post.postId)">查看详情</el-button>
            </div>
          </el-card>
        </el-space>
      </el-card>
    </el-col>

    <el-col :span="8">
      <el-card class="side-card" shadow="hover">
        <template #header>
          <strong>通知中心</strong>
          <span class="unread">未读 {{ notificationHome?.unreadCount ?? 0 }}</span>
        </template>
        <el-empty v-if="!notificationHome || notificationHome.announcements.length === 0" description="暂无通知" />
        <div v-else>
          <p v-for="item in notificationHome.announcements" :key="item.notificationId" class="side-item">
            {{ item.title }}：{{ item.content }}
          </p>
        </div>
      </el-card>

      <el-card class="side-card" shadow="hover">
        <template #header><strong>音乐推荐</strong></template>
        <p v-for="(item, idx) in mediaHome?.music ?? []" :key="'music-' + idx" class="side-item">
          {{ item.title }} - {{ item.author }}
        </p>
      </el-card>

      <el-card class="side-card" shadow="hover">
        <template #header><strong>书籍推荐</strong></template>
        <p v-for="(item, idx) in mediaHome?.books ?? []" :key="'book-' + idx" class="side-item">
          {{ item.title }} - {{ item.author }}
        </p>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { listPosts, listSections, searchPosts, type PostSummary, type SectionItem } from "../api/forum";
import { getNotificationHome, type NotificationHomePayload } from "../api/notification";
import { getMediaHome, type MediaHomePayload } from "../api/media";

const router = useRouter();
const keyword = ref("");
const posts = ref<PostSummary[]>([]);
const sections = ref<SectionItem[]>([]);
const selectedSectionId = ref<number | undefined>(undefined);
const notificationHome = ref<NotificationHomePayload | null>(null);
const mediaHome = ref<MediaHomePayload | null>(null);

async function loadPosts() {
  if (keyword.value.trim()) {
    posts.value = await searchPosts(keyword.value.trim(), selectedSectionId.value);
    return;
  }
  posts.value = await listPosts(selectedSectionId.value);
}

onMounted(async () => {
  sections.value = await listSections();
  notificationHome.value = await getNotificationHome();
  mediaHome.value = await getMediaHome();
  await loadPosts();
});

function goCreate() {
  router.push("/create");
}

function goDetail(postId: number) {
  router.push(`/posts/${postId}`);
}
</script>

<style scoped>
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 8px;
  color: #666;
}

.side-card {
  margin-bottom: 12px;
}

.side-item {
  font-size: 13px;
  color: #555;
  line-height: 1.6;
}

.unread {
  float: right;
  color: #f56c6c;
  font-size: 12px;
}
</style>
