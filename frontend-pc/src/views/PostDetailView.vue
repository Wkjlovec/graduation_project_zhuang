<template>
  <el-card v-if="detail">
    <template #header>
      <strong>{{ detail.title }}</strong>
    </template>
    <p>分区：{{ detail.sectionName }}</p>
    <p>{{ detail.content }}</p>
    <p v-if="detail.editedHint">{{ detail.editedHint }}</p>
    <el-space>
      <span>作者：{{ detail.authorName }}</span>
      <span>点赞：{{ detail.likeCount }}</span>
      <el-button @click="handleLike">点赞</el-button>
    </el-space>

    <el-divider />
    <p v-if="replyToCommentId">当前回复评论 #{{ replyToCommentId }} <el-button link @click="clearReply">取消</el-button></p>
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
        <span v-if="item.parentCommentId">（回复 #{{ item.parentCommentId }}）</span>
        <span v-if="item.editedHint"> {{ item.editedHint }}</span>
        <el-button link @click="setReply(item.commentId)">回复</el-button>
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
const replyToCommentId = ref<number | undefined>(undefined);

async function loadDetail() {
  detail.value = await getPostDetail(String(route.params.id));
}

async function handleComment() {
  await addComment(String(route.params.id), commentForm.content, replyToCommentId.value);
  commentForm.content = "";
  replyToCommentId.value = undefined;
  ElMessage.success("评论成功");
  await loadDetail();
}

async function handleLike() {
  await likePost(String(route.params.id));
  await loadDetail();
}

function setReply(commentId: number) {
  replyToCommentId.value = commentId;
}

function clearReply() {
  replyToCommentId.value = undefined;
}

void loadDetail();
</script>
