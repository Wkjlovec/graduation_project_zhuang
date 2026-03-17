<template>
  <div class="page">
    <van-nav-bar title="发布帖子" left-arrow @click-left="goBack" />
    <van-form @submit="handleCreate">
      <van-cell-group inset>
        <van-field v-model.number="form.sectionId" label="分区ID" placeholder="请输入分区ID" type="number" />
        <van-field v-model="form.title" label="标题" placeholder="请输入标题" />
        <van-field v-model="form.content" rows="8" autosize label="内容" type="textarea" placeholder="请输入帖子内容" />
      </van-cell-group>
      <div style="margin: 16px;">
        <van-button round block type="primary" native-type="submit" :loading="submitting">发布</van-button>
      </div>
    </van-form>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { showToast } from "vant";
import { createPost, listSections } from "../api/forum";

const router = useRouter();
const form = reactive({ sectionId: 0, title: "", content: "" });
const submitting = ref(false);

async function handleCreate() {
  submitting.value = true;
  try {
    const post = await createPost(form.title, form.content, form.sectionId);
    showToast("发布成功");
    router.replace(`/posts/${post.postId}`);
  } catch (error) {
    showToast(error instanceof Error ? error.message : "发布失败");
  } finally {
    submitting.value = false;
  }
}

function goBack() {
  router.back();
}

onMounted(async () => {
  try {
    const sections = await listSections();
    if (sections.length > 0) {
      form.sectionId = sections[0].sectionId;
    }
  } catch (error) {
    showToast(error instanceof Error ? error.message : "加载分区失败");
  }
});
</script>
