<template>
  <div class="page">
    <van-nav-bar title="登录 / 注册" />
    <van-form @submit="handleLogin">
      <van-cell-group inset>
        <van-field v-model="form.username" label="用户名" placeholder="请输入用户名" />
        <van-field v-model="form.password" label="密码" type="password" placeholder="请输入密码" />
        <van-field v-model="form.nickname" label="昵称" placeholder="注册时可填写" />
      </van-cell-group>
      <div style="margin: 16px;">
        <van-button round block type="primary" native-type="submit" :loading="loginLoading">登录</van-button>
      </div>
    </van-form>
    <div style="margin: 0 16px;">
      <van-button round block plain type="primary" :loading="registerLoading" @click="handleRegister">注册并登录</van-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { showToast } from "vant";
import { login, register } from "../api/auth";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const form = reactive({ username: "", password: "", nickname: "" });
const loginLoading = ref(false);
const registerLoading = ref(false);

async function handleLogin() {
  loginLoading.value = true;
  try {
    const data = await login(form.username, form.password);
    authStore.setToken(data.token);
    showToast("登录成功");
    router.push("/posts");
  } catch (error) {
    showToast(error instanceof Error ? error.message : "登录失败");
  } finally {
    loginLoading.value = false;
  }
}

async function handleRegister() {
  registerLoading.value = true;
  try {
    const data = await register(form.username, form.password, form.nickname);
    authStore.setToken(data.token);
    showToast("注册成功");
    router.push("/posts");
  } catch (error) {
    showToast(error instanceof Error ? error.message : "注册失败");
  } finally {
    registerLoading.value = false;
  }
}
</script>
