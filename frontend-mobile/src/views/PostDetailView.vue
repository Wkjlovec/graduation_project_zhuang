<template>
  <div class="page" v-if="detail">
    <van-nav-bar :title="detail.title" left-arrow @click-left="goBack" />
    <van-cell-group inset>
      <van-cell :title="detail.authorName" :label="detail.content" />
      <van-cell title="点赞数" :value="String(detail.likeCount)">
        <template #right-icon>
          <van-button size="small" type="primary" @click="handleLike">点赞</van-button>
        </template>
      </van-cell>
    </van-cell-group>

    <van-divider>评论</van-divider>
    <van-field v-model="comment" label="评论" placeholder="说点什么..." />
    <div style="padding: 8px 0 16px;">
      <van-button block type="primary" @click="handleComment">发送评论</van-button>
    </div>
    <van-cell-group inset>
      <van-cell v-for="item in detail.comments" :key="item.commentId" :title="item.username" :label="item.content" />
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

async function loadDetail() {
  detail.value = await getPostDetail(String(route.params.id));
}

async function handleLike() {
  await likePost(String(route.params.id));
  await loadDetail();
}

async function handleComment() {
  await addComment(String(route.params.id), comment.value);
  comment.value = "";
  showToast("评论成功");
  await loadDetail();
}

function goBack() {
  router.back();
}

void loadDetail();
</script>
