<template>
  <el-card>
    <template #header>
      <strong>登录 / 注册</strong>
    </template>
    <el-form :model="form" label-width="70px">
      <el-form-item label="用户名">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" show-password />
      </el-form-item>
      <el-form-item label="昵称">
        <el-input v-model="form.nickname" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loginLoading" @click="handleLogin">登录</el-button>
        <el-button :loading="registerLoading" @click="handleRegister">注册</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { login, register } from "../api/auth";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const form = reactive({
  username: "",
  password: "",
  nickname: ""
});
const loginLoading = ref(false);
const registerLoading = ref(false);

async function handleLogin() {
  loginLoading.value = true;
  try {
    const payload = await login(form.username, form.password);
    authStore.setToken(payload.token);
    ElMessage.success("登录成功");
    router.push("/posts");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "登录失败");
  } finally {
    loginLoading.value = false;
  }
}

async function handleRegister() {
  registerLoading.value = true;
  try {
    const payload = await register(form.username, form.password, form.nickname);
    authStore.setToken(payload.token);
    ElMessage.success("注册成功并已登录");
    router.push("/posts");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "注册失败");
  } finally {
    registerLoading.value = false;
  }
}
</script>
