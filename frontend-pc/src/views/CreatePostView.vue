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
        <el-button type="primary" :loading="submitting" @click="handleCreate">发布</el-button>
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
const submitting = ref(false);
const form = reactive({
  sectionId: 0,
  title: "",
  content: ""
});

async function handleCreate() {
  submitting.value = true;
  try {
    const post = await createPost(form.title, form.content, form.sectionId);
    ElMessage.success("发布成功");
    router.push(`/posts/${post.postId}`);
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "发布失败");
  } finally {
    submitting.value = false;
  }
}

onMounted(async () => {
  try {
    sections.value = await listSections();
    if (sections.value.length > 0) {
      form.sectionId = sections.value[0].sectionId;
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "加载分区失败");
  }
});
</script>
