<template>
  <el-card v-if="detail">
    <template #header>
      <strong>{{ detail.title }}</strong>
    </template>
    <p>{{ detail.content }}</p>
    <el-space>
      <span>作者：{{ detail.authorName }}</span>
      <span>点赞：{{ detail.likeCount }}</span>
      <el-button @click="handleLike">点赞</el-button>
    </el-space>

    <el-divider />
    <el-form :model="commentForm" inline>
      <el-form-item>
        <el-input v-model="commentForm.content" placeholder="写下你的评论" style="min-width: 380px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleComment">发表评论</el-button>
      </el-form-item>
    </el-form>

    <el-timeline>
      <el-timeline-item v-for="item in detail.comments" :key="item.commentId">
        <strong>{{ item.username }}：</strong>{{ item.content }}
      </el-timeline-item>
    </el-timeline>
  </el-card>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import { addComment, getPostDetail, likePost, type PostDetail } from "../api/forum";

const route = useRoute();
const detail = ref<PostDetail | null>(null);
const commentForm = reactive({ content: "" });

async function loadDetail() {
  detail.value = await getPostDetail(String(route.params.id));
}

async function handleComment() {
  await addComment(String(route.params.id), commentForm.content);
  commentForm.content = "";
  ElMessage.success("评论成功");
  await loadDetail();
}

async function handleLike() {
  await likePost(String(route.params.id));
  await loadDetail();
}

void loadDetail();
</script>
