<template>
  <main class="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center px-4 py-10">
    <section class="w-full max-w-md rounded-xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl">
      <h1 class="text-3xl font-semibold mb-8">Log in to your account</h1>

      <form class="space-y-4" @submit.prevent="submitLogIn">
        <div>
          <label for="email" class="block text-sm text-slate-300 mb-1">Email</label>
          <input
            id="email"
            v-model.trim="email"
            type="email"
            autocomplete="email"
            required
            class="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 outline-none focus:ring-2 focus:ring-cyan-500"
          />
        </div>

        <div>
          <label for="password" class="block text-sm text-slate-300 mb-1">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="new-password"
            required
            class="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 outline-none focus:ring-2 focus:ring-cyan-500"
          />
        </div>

        <button
          type="submit"
          :disabled="isLoading"
          class="w-full rounded-lg bg-cyan-600 px-4 py-2 font-medium text-white hover:bg-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isLoading ? 'Checking credentials...' : 'Log In' }}
        </button>
      </form>

      <p v-if="error" class="mt-4 text-rose-300">{{ error }}</p>
      <p v-if="successMessage" class="mt-4 text-emerald-300">{{ successMessage }}</p>

      <p class="mt-6 text-sm text-slate-400">
        Don't have an account?
        <RouterLink to="/signup" class="text-cyan-400 hover:text-cyan-300">Sign up</RouterLink>
      </p>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { useAuthStore } from '../store/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const successMessage = ref('')
const isLoading = ref(false)

const submitLogIn = async () => {
  error.value = ''
  successMessage.value = ''

  isLoading.value = true

  const result = await authStore.login(email.value, password.value)

  isLoading.value = false

  if (!result.success) {
    error.value = result.message
    return
  }

  successMessage.value = result.message
  setTimeout(() => {
    router.push('/')
  }, 900)
}
</script>
