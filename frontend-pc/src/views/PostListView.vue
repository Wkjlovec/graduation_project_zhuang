<template>
  <el-card>
    <template #header>
      <div class="header-row">
        <strong>帖子列表</strong>
        <div class="header-actions">
          <el-select v-model="selectedSectionId" placeholder="全部分区" clearable style="width: 200px" @change="loadPosts">
            <el-option v-for="item in sections" :key="item.sectionId" :label="item.name" :value="item.sectionId" />
          </el-select>
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
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { listPosts, listSections, type PostSummary, type SectionItem } from "../api/forum";

const router = useRouter();
const posts = ref<PostSummary[]>([]);
const sections = ref<SectionItem[]>([]);
const selectedSectionId = ref<number | undefined>(undefined);

async function loadPosts() {
  posts.value = await listPosts(selectedSectionId.value);
}

onMounted(async () => {
  sections.value = await listSections();
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
</style>
