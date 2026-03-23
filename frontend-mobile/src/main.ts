import { createApp } from "vue";
import { createPinia } from "pinia";
import { Button, Cell, CellGroup, Field, Form, NavBar, List, Tag, Divider, Empty, FloatingBubble, Toast, Loading } from "vant";
import "vant/lib/index.css";
import App from "./App.vue";
import router from "./router";
import { useAuthStore } from "./stores/auth";
import "./styles.css";

const app = createApp(App);
const pinia = createPinia();
app.use(pinia);
app.use(router);
app.use(Button);
app.use(Cell);
app.use(CellGroup);
app.use(Field);
app.use(Form);
app.use(NavBar);
app.use(List);
app.use(Tag);
app.use(Divider);
app.use(Empty);
app.use(FloatingBubble);
app.use(Toast);
app.use(Loading);

const authStore = useAuthStore(pinia);
window.addEventListener("auth-session-changed", () => {
  authStore.syncFromStorage();
});

app.mount("#app");
