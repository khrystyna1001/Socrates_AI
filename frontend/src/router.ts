import { createWebHistory, createRouter } from 'vue-router';

import AboutView from './pages/About.vue';
import UploadView from './pages/UploadFile.vue';
import ChatView from './pages/Chat.vue';
import GuideView from './pages/Guide.vue';
import Home from './pages/Home.vue';

import LoginView from './auth/Login.vue';
import SignUpView from './auth/SignUp.vue';
import ProfileView from './auth/Profile.vue';
import LogoutView from './auth/Logout.vue';

const routes = [
  { path: '/', component: Home },
  { path: '/about', component: AboutView },
  { path: '/upload', component: UploadView },
  { path: '/chat', component: ChatView },
  { path: '/guide', component: GuideView },
  { path: '/login', component: LoginView },
  { path: '/signup', component: SignUpView },
  { path: '/profile', component: ProfileView },
  { path: '/logout', component: LogoutView }
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
