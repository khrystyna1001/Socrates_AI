<template>
  <aside class="lg:col-span-4">
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sticky top-24">
      <div class="flex items-center gap-2 mb-6">
        <BookOpen class="w-5 h-5 text-indigo-600" />
        <h2 class="font-bold text-slate-800">Recent Threads</h2>
      </div>

      <div v-if="history.length === 0" class="text-center py-12 border-2 border-dashed border-slate-100 rounded-xl">
        <p class="text-sm text-slate-400 font-medium">Your knowledge journey <br> begins here.</p>
      </div>

      <div v-else class="space-y-3 max-h-[calc(100vh-300px)] overflow-y-auto pr-2 custom-scrollbar">
        <div 
          v-for="(chat, index) in history" 
          :key="index"
          class="group p-4 rounded-xl border border-transparent hover:border-slate-200 hover:bg-slate-50 transition-all cursor-pointer"
        >
          <p class="text-sm font-semibold text-slate-700 truncate group-hover:text-blue-600 transition-colors">
            {{ chat.question }}
          </p>
          <p class="text-xs text-slate-400 mt-1 line-clamp-1 italic">
            {{ chat.answer }}
          </p>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { BookOpen } from 'lucide-vue-next'

defineProps<{
  history: Array<{ question: string; answer: string }>
}>()
</script>

<style scoped>
/* Move scrollbar styles here */
.custom-scrollbar::-webkit-scrollbar { width: 5px; }
/* ... rest of your custom scrollbar CSS ... */
</style>