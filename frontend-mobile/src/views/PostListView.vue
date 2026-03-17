<template>
  <div class="page">
    <van-nav-bar title="帖子列表">
      <template #right>
        <van-button size="small" type="primary" @click="goCreate">发帖</van-button>
      </template>
    </van-nav-bar>

    <van-cell-group inset style="margin-bottom: 8px;">
      <van-field v-model="keyword" label="搜索" placeholder="输入关键词搜索帖子" />
      <van-cell>
        <template #title>
          <van-button size="small" type="primary" @click="loadPosts">执行搜索</van-button>
          <van-button size="small" style="margin-left: 8px;" @click="resetSearch">重置</van-button>
        </template>
      </van-cell>
    </van-cell-group>

    <van-cell-group inset style="margin-bottom: 8px;">
      <van-cell title="通知中心" :value="'未读 ' + (notificationHome?.unreadCount ?? 0)" />
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

    <van-empty v-if="posts.length === 0" description="暂无帖子" />
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

    <van-floating-bubble axis="xy" magnetic="x" :offset="{ x: 320, y: 600 }" @click="goProfile">
      我
    </van-floating-bubble>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { listPosts, searchPosts, type PostSummary } from "../api/forum";
import { getNotificationHome, type NotificationHomePayload } from "../api/notification";
import { getMediaHome, type MediaHomePayload } from "../api/media";

const router = useRouter();
const posts = ref<PostSummary[]>([]);
const keyword = ref("");
const notificationHome = ref<NotificationHomePayload | null>(null);
const mediaHome = ref<MediaHomePayload | null>(null);

async function loadPosts() {
  if (keyword.value.trim()) {
    posts.value = await searchPosts(keyword.value.trim());
    return;
  }
  posts.value = await listPosts();
}

function resetSearch() {
  keyword.value = "";
  void loadPosts();
}

onMounted(async () => {
  notificationHome.value = await getNotificationHome();
  mediaHome.value = await getMediaHome();
  await loadPosts();
});

function goCreate() {
  router.push("/create");
}
function goProfile() {
  router.push("/profile");
}
function goDetail(id: number) {
  router.push(`/posts/${id}`);
}
</script>
