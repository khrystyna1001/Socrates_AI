<template>
  <Transition name="fade-up">
    <section v-if="response || isLoading" class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      <div class="p-8">
        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-blue-50 rounded-lg">
              <MessageSquare class="w-5 h-5 text-blue-600" />
            </div>
            <h2 class="font-bold text-slate-800">Response</h2>
          </div>
        </div>

        <div v-if="isLoading" class="space-y-4">
          <div class="h-4 bg-slate-100 rounded-full w-3/4 animate-pulse"></div>
          <div class="h-4 bg-slate-100 rounded-full w-full animate-pulse"></div>
          <div class="h-4 bg-slate-100 rounded-full w-5/6 animate-pulse"></div>
        </div>

        <div v-else class="animate-in fade-in slide-in-from-bottom-2 duration-700">
          <p class="text-slate-700 leading-relaxed text-lg whitespace-pre-wrap">
            {{ response }}
          </p>

          <div v-if="sources.length > 0" class="mt-8 pt-6 border-t border-slate-100">
            <div class="flex items-center gap-2 mb-4">
              <Quote class="w-4 h-4 text-slate-400" />
              <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">Grounding Sources</span>
            </div>
            <div class="flex flex-wrap gap-2">
              <div 
                v-for="(source, index) in sources" 
                :key="index"
                class="px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-600 hover:bg-white hover:border-blue-300 transition-colors cursor-default"
              >
                {{ source }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </Transition>
</template>

<script setup lang="ts">
import { MessageSquare, Quote } from 'lucide-vue-next'

defineProps<{
  response: string
  isLoading: boolean
  sources: string[]
}>()
</script>

<style scoped>
.fade-up-enter-active, .fade-up-leave-active {
  transition: all 0.4s ease-out;
}
.fade-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
</style>