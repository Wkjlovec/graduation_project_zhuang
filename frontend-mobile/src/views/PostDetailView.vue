<template>
  <div class="page">
    <van-nav-bar :title="detail?.title || '帖子详情'" left-arrow @click-left="goBack" />
    <div v-if="detailLoading" class="loading-box">
      <van-loading size="24px" type="spinner" /> 加载中...
    </div>
    <van-cell-group v-else-if="detailError" inset>
      <van-cell title="加载失败" :label="detailError">
        <template #right-icon>
          <van-button size="mini" type="primary" plain @click="loadDetail">重试</van-button>
        </template>
      </van-cell>
    </van-cell-group>
    <template v-else-if="detail">
    <van-cell-group inset>
      <van-cell :title="detail.authorName + ' · ' + detail.sectionName" :label="detail.content + (detail.editedHint ? '\n' + detail.editedHint : '')" />
      <van-cell title="点赞数" :value="String(detail.likeCount)">
        <template #right-icon>
          <van-button size="small" type="primary" :loading="actionLoading" @click="handleLike">点赞</van-button>
        </template>
      </van-cell>
    </van-cell-group>

    <van-divider>评论</van-divider>
    <div v-if="replyToCommentId" style="margin-bottom: 8px;">
      正在回复评论 #{{ replyToCommentId }}
      <van-button size="mini" plain type="primary" @click="clearReply">取消</van-button>
    </div>
    <van-field v-model="comment" label="评论" placeholder="说点什么..." />
    <div style="padding: 8px 0 16px;">
      <van-button block type="primary" :loading="actionLoading" @click="handleComment">发送评论</van-button>
    </div>
    <van-cell-group inset>
      <van-cell
        v-for="item in detail.comments"
        :key="item.commentId"
        :title="item.username"
        :label="item.content + (item.parentCommentId ? '（回复 #' + item.parentCommentId + '）' : '') + (item.editedHint ? ' · ' + item.editedHint : '')"
      >
        <template #right-icon>
          <van-button size="mini" plain type="primary" @click="setReply(item.commentId)">回复</van-button>
        </template>
      </van-cell>
    </van-cell-group>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { showToast } from "vant";
import { addComment, getPostDetail, likePost, type PostDetail } from "../api/forum";

const route = useRoute();
const router = useRouter();
const detail = ref<PostDetail | null>(null);
const comment = ref("");
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

async function handleLike() {
  actionLoading.value = true;
  try {
    await likePost(String(route.params.id));
    await loadDetail();
  } catch (error) {
    showToast(error instanceof Error ? error.message : "点赞失败");
  } finally {
    actionLoading.value = false;
  }
}

async function handleComment() {
  actionLoading.value = true;
  try {
    await addComment(String(route.params.id), comment.value, replyToCommentId.value);
    comment.value = "";
    replyToCommentId.value = undefined;
    showToast("评论成功");
    await loadDetail();
  } catch (error) {
    showToast(error instanceof Error ? error.message : "评论失败");
  } finally {
    actionLoading.value = false;
  }
}

function goBack() {
  router.back();
}

function setReply(commentId: number) {
  replyToCommentId.value = commentId;
}

function clearReply() {
  replyToCommentId.value = undefined;
}

void loadDetail();
</script>

<style scoped>
.loading-box {
  padding: 16px;
  text-align: center;
  color: #666;
}
</style>
