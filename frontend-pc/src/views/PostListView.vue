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
                @keyup.enter="handleSearch"
              />
              <el-select v-model="selectedSectionId" placeholder="全部分区" clearable style="width: 180px" @change="handleSectionChange">
                <el-option v-for="item in sections" :key="item.sectionId" :label="item.name" :value="item.sectionId" />
              </el-select>
              <el-select v-model="pageSize" style="width: 120px" @change="handlePageSizeChange">
                <el-option :value="5" label="5条/页" />
                <el-option :value="10" label="10条/页" />
                <el-option :value="20" label="20条/页" />
              </el-select>
              <el-button :loading="loadingList" @click="handleSearch">搜索</el-button>
              <el-button type="primary" @click="goCreate">去发帖</el-button>
            </div>
          </div>
        </template>
        <el-skeleton v-if="loadingList" :rows="6" animated />
        <el-alert v-else-if="listError" :title="listError" type="error" show-icon :closable="false">
          <template #default>
            <el-button text type="primary" @click="loadPosts">重试</el-button>
          </template>
        </el-alert>
        <el-empty v-else-if="posts.length === 0" description="暂无帖子" />
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
        <div class="pager-row">
          <el-button :disabled="loadingList || page <= 1" @click="prevPage">上一页</el-button>
          <span>第 {{ page }} 页</span>
          <el-button :disabled="loadingList || !hasNextPage" @click="nextPage">下一页</el-button>
        </div>
      </el-card>
    </el-col>

    <el-col :span="8">
      <el-card class="side-card" shadow="hover" v-loading="loadingSide">
        <template #header>
          <strong>通知中心</strong>
          <span class="unread">未读 {{ notificationHome?.unreadCount ?? 0 }}</span>
        </template>
        <el-alert v-if="sideError" :title="sideError" type="error" show-icon :closable="false">
          <template #default>
            <el-button text type="primary" @click="loadSideModules">重试</el-button>
          </template>
        </el-alert>
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
const loadingList = ref(false);
const loadingSide = ref(false);
const listError = ref("");
const sideError = ref("");
const page = ref(1);
const pageSize = ref(10);
const hasNextPage = ref(false);

async function loadPosts() {
  loadingList.value = true;
  listError.value = "";
  try {
    if (keyword.value.trim()) {
      posts.value = await searchPosts(keyword.value.trim(), selectedSectionId.value, page.value - 1, pageSize.value);
    } else {
      posts.value = await listPosts(selectedSectionId.value, page.value - 1, pageSize.value);
    }
    hasNextPage.value = posts.value.length >= pageSize.value;
  } catch (error) {
    const message = error instanceof Error ? error.message : "加载帖子失败";
    listError.value = message;
    posts.value = [];
    hasNextPage.value = false;
  } finally {
    loadingList.value = false;
  }
}

async function loadSideModules() {
  loadingSide.value = true;
  sideError.value = "";
  try {
    notificationHome.value = await getNotificationHome();
    mediaHome.value = await getMediaHome();
  } catch (error) {
    sideError.value = error instanceof Error ? error.message : "加载首页模块失败";
  } finally {
    loadingSide.value = false;
  }
}

async function handleSearch() {
  page.value = 1;
  await loadPosts();
}

async function handleSectionChange() {
  page.value = 1;
  await loadPosts();
}

async function handlePageSizeChange() {
  page.value = 1;
  await loadPosts();
}

async function prevPage() {
  if (page.value <= 1) {
    return;
  }
  page.value -= 1;
  await loadPosts();
}

async function nextPage() {
  if (!hasNextPage.value) {
    return;
  }
  page.value += 1;
  await loadPosts();
}

onMounted(async () => {
  try {
    sections.value = await listSections();
  } catch {
    sections.value = [];
  }
  await Promise.all([loadSideModules(), loadPosts()]);
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

.pager-row {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
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
