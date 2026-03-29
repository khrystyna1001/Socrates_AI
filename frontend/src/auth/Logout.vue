<template>
  <main class="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center px-4">
    <section class="w-full max-w-md rounded-xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl">
      <h1 class="text-2xl font-semibold mb-3">Logging you out</h1>

      <p v-if="status === 'loading'" class="text-slate-300">
        Please wait while we end your session...
      </p>

      <p v-else-if="status === 'success'" class="text-emerald-300">
        You have been logged out. Redirecting to login page...
      </p>

      <div v-else>
        <p class="text-rose-300 mb-4">
          {{ errorMessage }}
        </p>

        <div class="flex gap-3">
          <button
            class="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 transition-colors"
            @click="runLogout"
          >
            Try again
          </button>

          <button
            class="px-4 py-2 rounded-lg border border-slate-600 hover:bg-slate-800 transition-colors"
            @click="router.push('/login')"
          >
            Go to login
          </button>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

import { useAuthStore } from '../store/auth';

type LogoutStatus = 'loading' | 'success' | 'error';

const router = useRouter();
const authStore = useAuthStore();

const status = ref<LogoutStatus>('loading');
const errorMessage = ref('Logout failed. Please try again.');

const runLogout = async () => {
  status.value = 'loading';

  try {
    await authStore.logout();
    status.value = 'success';

    setTimeout(() => {
      router.push('/login');
    }, 700);
  } catch {
    status.value = 'error';
  }
};

onMounted(() => {
  void runLogout();
});
</script>
