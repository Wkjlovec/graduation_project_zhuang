<template>
  <el-card>
    <template #header>
      <strong>发布帖子</strong>
    </template>
    <el-form :model="form" label-width="70px">
      <el-form-item label="标题">
        <el-input v-model="form.title" />
      </el-form-item>
      <el-form-item label="内容">
        <el-input v-model="form.content" type="textarea" :rows="10" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleCreate">发布</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { reactive } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { createPost } from "../api/forum";

const router = useRouter();
const form = reactive({
  title: "",
  content: ""
});

async function handleCreate() {
  const post = await createPost(form.title, form.content);
  ElMessage.success("发布成功");
  router.push(`/posts/${post.postId}`);
}
</script>
