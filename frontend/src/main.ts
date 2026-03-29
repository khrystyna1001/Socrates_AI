import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { Icon } from "@iconify/vue";
import { useAuthStore } from './store/auth';
import { createPinia } from 'pinia';


const app = createApp(App);

app.component('Icon', Icon);

app.use(createPinia());
app.use(router);

const authStore = useAuthStore();
authStore.setCsrfToken();

app.mount('#app');