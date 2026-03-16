<template>
  <el-card>
    <template #header>
      <div class="header-row">
        <strong>帖子列表</strong>
        <el-button type="primary" @click="goCreate">去发帖</el-button>
      </div>
    </template>
    <el-empty v-if="posts.length === 0" description="暂无帖子" />
    <el-space v-else direction="vertical" fill style="width: 100%">
      <el-card v-for="post in posts" :key="post.postId" shadow="never">
        <h3>{{ post.title }}</h3>
        <p>{{ post.contentPreview }}</p>
        <div class="meta">
          <span>作者：{{ post.authorName }}</span>
          <span>点赞：{{ post.likeCount }}</span>
          <el-button link @click="goDetail(post.postId)">查看详情</el-button>
        </div>
      </el-card>
    </el-space>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { listPosts, type PostSummary } from "../api/forum";

const router = useRouter();
const posts = ref<PostSummary[]>([]);

onMounted(async () => {
  posts.value = await listPosts();
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

.meta {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 8px;
  color: #666;
}
</style>
