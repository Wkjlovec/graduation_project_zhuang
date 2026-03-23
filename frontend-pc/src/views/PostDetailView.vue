<template>
  <el-card>
    <template #header>
      <strong>{{ detail?.title ?? "帖子详情" }}</strong>
    </template>
    <el-skeleton v-if="detailLoading" :rows="6" animated />
    <el-alert v-else-if="detailError" :title="detailError" type="error" show-icon :closable="false">
      <template #default>
        <el-button text type="primary" @click="loadDetail">重试</el-button>
      </template>
    </el-alert>
    <template v-else-if="detail">
    <p>分区：{{ detail.sectionName }}</p>
    <p>{{ detail.content }}</p>
    <p v-if="detail.editedHint">{{ detail.editedHint }}</p>
    <el-space>
      <span>作者：{{ detail.authorName }}</span>
      <span>点赞：{{ detail.likeCount }}</span>
      <el-button :loading="actionLoading" @click="handleLike">点赞</el-button>
    </el-space>

    <el-divider />
    <p v-if="replyToCommentId">当前回复评论 #{{ replyToCommentId }} <el-button link @click="clearReply">取消</el-button></p>
    <el-form :model="commentForm" inline>
      <el-form-item>
        <el-input v-model="commentForm.content" placeholder="写下你的评论" style="min-width: 380px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="actionLoading" @click="handleComment">发表评论</el-button>
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
    </template>
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
const detailLoading = ref(false);
const actionLoading = ref(false);
const detailError = ref("");

async function loadDetail() {
  detailLoading.value = true;
  detailError.value = "";
  try {
    detail.value = await getPostDetail(String(route.params.id));
  } catch (error) {
    detailError.value = error instanceof Error ? error.message : "加载失败";
  } finally {
    detailLoading.value = false;
  }
}

async function handleComment() {
  actionLoading.value = true;
  try {
    await addComment(String(route.params.id), commentForm.content, replyToCommentId.value);
    commentForm.content = "";
    replyToCommentId.value = undefined;
    ElMessage.success("评论成功");
    await loadDetail();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "评论失败");
  } finally {
    actionLoading.value = false;
  }
}

async function handleLike() {
  actionLoading.value = true;
  try {
    await likePost(String(route.params.id));
    await loadDetail();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "点赞失败");
  } finally {
    actionLoading.value = false;
  }
}

function setReply(commentId: number) {
  replyToCommentId.value = commentId;
}

function clearReply() {
  replyToCommentId.value = undefined;
}

void loadDetail();
</script>
