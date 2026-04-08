<template>
  <div class="page">
    <van-nav-bar title="帖子列表">
      <template #right>
        <van-button size="small" type="primary" style="margin-right: 3em;" @click="goCreate">发帖</van-button>
      </template>
    </van-nav-bar>

    <van-cell-group inset style="margin-bottom: 8px;">
      <van-field v-model="keyword" label="搜索" placeholder="输入关键词搜索帖子" @keyup.enter="loadPosts" />
      <van-cell>
        <template #title>
          <van-button size="small" type="primary" :loading="loadingPosts" @click="handleSearch">执行搜索</van-button>
          <van-button size="small" style="margin-left: 8px;" @click="resetSearch">重置</van-button>
        </template>
      </van-cell>
      <van-cell title="分区筛选">
        <template #label>
          <div class="section-actions">
            <van-button
              size="mini"
              :type="selectedSectionId === undefined ? 'primary' : 'default'"
              plain
              @click="selectAllSections"
            >
              全部
            </van-button>
            <van-button
              v-for="item in sections"
              :key="item.sectionId"
              size="mini"
              :type="selectedSectionId === item.sectionId ? 'primary' : 'default'"
              plain
              @click="selectSection(item.sectionId)"
            >
              {{ item.name }}
            </van-button>
          </div>
        </template>
      </van-cell>
    </van-cell-group>

    <van-cell-group inset style="margin-bottom: 8px;">
      <van-cell title="通知中心" :value="'未读 ' + (notificationHome?.unreadCount ?? 0)" value-class="notify-value">
        <template #right-icon>
          <van-button size="mini" plain type="primary" @click="goNotifications">我的通知</van-button>
        </template>
      </van-cell>
      <van-cell
        v-for="item in notificationHome?.announcements ?? []"
        :key="item.notificationId"
        :title="item.title"
        :label="item.content"
      />
    </van-cell-group>

    <van-cell-group inset style="margin-bottom: 8px;">
      <van-cell title="音乐推荐" />
      <van-cell v-for="(item, idx) in mediaHome?.music ?? []" :key="'m' + idx" :title="item.title" :label="item.author + ' · ' + item.reason" />
    </van-cell-group>

    <van-cell-group inset style="margin-bottom: 8px;">
      <van-cell title="书籍推荐" />
      <van-cell v-for="(item, idx) in mediaHome?.books ?? []" :key="'b' + idx" :title="item.title" :label="item.author + ' · ' + item.reason" />
    </van-cell-group>

    <div v-if="loadingPosts" class="loading-box">
      <van-loading size="24px" type="spinner" /> 加载中...
    </div>
    <van-cell-group v-else-if="listError" inset>
      <van-cell title="加载失败" :label="listError">
        <template #right-icon>
          <van-button size="mini" type="primary" plain @click="loadPosts">重试</van-button>
        </template>
      </van-cell>
    </van-cell-group>
    <van-empty v-else-if="posts.length === 0" description="暂无帖子" />
    <van-cell-group v-else inset>
      <van-cell
        v-for="item in posts"
        :key="item.postId"
        :title="item.title + ' [' + item.sectionName + ']'"
        :label="item.contentPreview + (item.editedHint ? ' · ' + item.editedHint : '')"
        is-link
        @click="goDetail(item.postId)"
      >
        <template #value>
          <van-tag plain type="primary">👍 {{ item.likeCount }}</van-tag>
        </template>
      </van-cell>
    </van-cell-group>
    <div class="pager-box">
      <van-button size="small" :disabled="loadingPosts || page <= 1" @click="prevPage">上一页</van-button>
      <span>第 {{ page }} 页</span>
      <van-button size="small" :disabled="loadingPosts || !hasNextPage" @click="nextPage">下一页</van-button>
    </div>

    <div class="profile-fixed-btn" @click="goProfile">我</div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { listPosts, listSections, searchPosts, type PostSummary, type SectionItem } from "../api/forum";
import { getNotificationHome, type NotificationHomePayload } from "../api/notification";
import { getMediaHome, type MediaHomePayload } from "../api/media";

const router = useRouter();
const posts = ref<PostSummary[]>([]);
const sections = ref<SectionItem[]>([]);
const keyword = ref("");
const notificationHome = ref<NotificationHomePayload | null>(null);
const mediaHome = ref<MediaHomePayload | null>(null);
const selectedSectionId = ref<number | undefined>(undefined);
const loadingPosts = ref(false);
const listError = ref("");
const page = ref(1);
const pageSize = ref(10);
const hasNextPage = ref(false);

async function loadPosts() {
  loadingPosts.value = true;
  listError.value = "";
  try {
    if (keyword.value.trim()) {
      posts.value = await searchPosts(keyword.value.trim(), selectedSectionId.value, page.value - 1, pageSize.value);
    } else {
      posts.value = await listPosts(selectedSectionId.value, page.value - 1, pageSize.value);
    }
    hasNextPage.value = posts.value.length >= pageSize.value;
  } catch (error) {
    listError.value = error instanceof Error ? error.message : "加载失败";
    posts.value = [];
    hasNextPage.value = false;
  } finally {
    loadingPosts.value = false;
  }
}

function resetSearch() {
  keyword.value = "";
  page.value = 1;
  void loadPosts();
}

function selectAllSections() {
  selectedSectionId.value = undefined;
  page.value = 1;
  void loadPosts();
}

function selectSection(sectionId: number) {
  selectedSectionId.value = sectionId;
  page.value = 1;
  void loadPosts();
}

function handleSearch() {
  page.value = 1;
  void loadPosts();
}

function prevPage() {
  if (page.value <= 1) {
    return;
  }
  page.value -= 1;
  void loadPosts();
}

function nextPage() {
  if (!hasNextPage.value) {
    return;
  }
  page.value += 1;
  void loadPosts();
}

onMounted(async () => {
  try {
    sections.value = await listSections();
  } catch {
    sections.value = [];
  }
  try {
    notificationHome.value = await getNotificationHome();
    mediaHome.value = await getMediaHome();
  } catch {
    // 首页推荐/通知失败时不阻塞主列表。
  }
  await loadPosts();
});

function goCreate() {
  router.push("/create");
}
function goProfile() {
  router.push("/profile");
}
function goNotifications() {
  router.push("/notifications");
}
function goDetail(id: number) {
  router.push(`/posts/${id}`);
}
</script>

<style scoped>
.loading-box {
  padding: 16px;
  text-align: center;
  color: #666;
}

.pager-box {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin: 12px 0;
}

.section-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}

.notify-value {
  padding-right: 2em;
}

.profile-fixed-btn {
  position: fixed;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #1989fa;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  z-index: 999;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  cursor: pointer;
}
</style>
