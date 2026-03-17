<template>
  <el-card>
    <template #header>
      <strong>发布帖子</strong>
    </template>
    <el-form :model="form" label-width="70px">
      <el-form-item label="分区">
        <el-select v-model="form.sectionId" placeholder="请选择分区" style="width: 240px">
          <el-option v-for="item in sections" :key="item.sectionId" :label="item.name" :value="item.sectionId" />
        </el-select>
      </el-form-item>
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
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { createPost, listSections, type SectionItem } from "../api/forum";

const router = useRouter();
const sections = ref<SectionItem[]>([]);
const form = reactive({
  sectionId: 0,
  title: "",
  content: ""
});

async function handleCreate() {
  const post = await createPost(form.title, form.content, form.sectionId);
  ElMessage.success("发布成功");
  router.push(`/posts/${post.postId}`);
}

onMounted(async () => {
  sections.value = await listSections();
  if (sections.value.length > 0) {
    form.sectionId = sections.value[0].sectionId;
  }
});
</script>
