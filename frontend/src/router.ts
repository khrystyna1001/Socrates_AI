import { createWebHistory, createRouter } from 'vue-router';

import AboutView from './pages/About.vue';
import UploadView from './pages/UploadFile.vue';
import ChatView from './pages/Chat.vue';
import Guide from './pages/Guide.vue';
import Home from './pages/Home.vue';

const routes = [
  { path: '/', component: Home },
  { path: '/about', component: AboutView },
  { path: '/upload', component: UploadView },
  { path: '/chat', component: ChatView },
  { path: '/guide', component: Guide }
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;