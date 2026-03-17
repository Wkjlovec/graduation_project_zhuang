<template>
  <div class="page" v-if="detail">
    <van-nav-bar :title="detail.title" left-arrow @click-left="goBack" />
    <van-cell-group inset>
      <van-cell :title="detail.authorName + ' · ' + detail.sectionName" :label="detail.content + (detail.editedHint ? '\n' + detail.editedHint : '')" />
      <van-cell title="点赞数" :value="String(detail.likeCount)">
        <template #right-icon>
          <van-button size="small" type="primary" @click="handleLike">点赞</van-button>
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
      <van-button block type="primary" @click="handleComment">发送评论</van-button>
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

async function loadDetail() {
  detail.value = await getPostDetail(String(route.params.id));
}

async function handleLike() {
  await likePost(String(route.params.id));
  await loadDetail();
}

async function handleComment() {
  await addComment(String(route.params.id), comment.value, replyToCommentId.value);
  comment.value = "";
  replyToCommentId.value = undefined;
  showToast("评论成功");
  await loadDetail();
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
