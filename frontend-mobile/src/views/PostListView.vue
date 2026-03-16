<template>
  <div class="page">
    <van-nav-bar title="帖子列表">
      <template #right>
        <van-button size="small" type="primary" @click="goCreate">发帖</van-button>
      </template>
    </van-nav-bar>

    <van-empty v-if="posts.length === 0" description="暂无帖子" />
    <van-cell-group v-else inset>
      <van-cell
        v-for="item in posts"
        :key="item.postId"
        :title="item.title"
        :label="item.contentPreview"
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
import { listPosts, type PostSummary } from "../api/forum";

const router = useRouter();
const posts = ref<PostSummary[]>([]);

onMounted(async () => {
  posts.value = await listPosts();
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
