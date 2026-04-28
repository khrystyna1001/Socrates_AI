<template>
  <Header />
  <main class="min-h-screen">
    <section class="mx-auto max-w-6xl px-6 py-16 md:py-24">
      <p class="inline-block rounded-full border border-cyan-600/40 bg-cyan-600/10 px-4 py-1 text-sm tracking-wide text-slate-900">
        User Profile
      </p>
      
      <div class="mt-10 max-w-4xl rounded-2xl border border-slate-700 bg-slate-800/70 p-8 leading-8 text-slate-300 shadow-lg shadow-cyan-900/20">
        <label class="block mb-2 text-sm text-cyan-400">Username</label>
        <input 
          disabled 
          type="text" 
          :value="userData?.username || 'N/A'" 
          class="w-full rounded-lg border border-slate-600 bg-slate-900 px-3 py-2 text-slate-100 outline-none" 
        />

        <label class="block mb-2 text-sm text-slate-900">Password</label>
        <input disabled="" type="text" v-model="password" class="w-full rounded-lg border border-slate-600 bg-slate-900 px-3 py-2 text-slate-100 outline-none focus:border-cyan-400" />
      </div>

      <div class="mt-10 flex flex-wrap gap-4">
        <button
          class="rounded-xl bg-cyan-400 px-6 py-3 text-lg font-semibold text-slate-900 transition hover:bg-cyan-300"
          @click="goToHome"
        >
          Return
        </button>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref, onMounted } from "vue";
import Header from "@/components/Header.vue";

import { useAuthStore } from '../store/auth'

const authStore = useAuthStore()
const userData = ref(null);
const password = ref("********");

const router = useRouter();
const token = localStorage.getItem("accessToken");

const goToHome = () => router.push("/");

const getProfile = async () => {
  await authStore.fetchUser(token); 
  
  if (authStore.isAuthenticated) {
    userData.value = authStore.user;
  } else {
    console.error("User is not authenticated");
    router.push("/login");
  }
};

onMounted(() => {
  getProfile();
});
</script>
