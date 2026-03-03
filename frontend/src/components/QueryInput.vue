<template>
  <section class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden transition-all hover:shadow-md">
    <div class="p-6">
      <div class="flex items-center gap-2 mb-4 text-blue-600">
        <Sparkles class="w-4 h-4" />
        <span class="text-xs font-bold uppercase tracking-wider">Inquiry</span>
      </div>
      
      <div class="relative group">
        <textarea
          :value="modelValue"
          @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
          @keypress.enter.prevent.stop="handleKeyPress"
          placeholder="Ask a question about Socratic philosophy..."
          class="w-full text-lg px-0 py-2 bg-transparent border-0 focus:border-0 focus:outline-none focus:ring-0 resize-none placeholder:text-slate-300"
          rows="3"
          :disabled="isLoading"
        ></textarea>
        
        <div class="flex items-center justify-between mt-4 pt-4 border-t border-slate-100">
          <span class="text-xs text-slate-400 font-medium">Shift + Enter for new line</span>
          <button
            @click="$emit('submit')"
            :disabled="!modelValue.trim() || isLoading"
            class="flex items-center gap-2 px-5 py-2.5 bg-slate-900 text-white rounded-xl font-semibold text-sm transition-all hover:bg-blue-600 hover:shadow-lg hover:shadow-blue-200 disabled:opacity-30 disabled:hover:bg-slate-900"
          >
            <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
            <template v-else>
              <span>Consult</span>
              <Send class="w-4 h-4" />
            </template>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { Sparkles, Loader2, Send } from 'lucide-vue-next'

const props = defineProps<{
  modelValue: string
  isLoading: boolean
}>()

const emit = defineEmits(['update:modelValue', 'submit'])

const handleKeyPress = (event: KeyboardEvent) => {
  if (!event.shiftKey) {
    emit('submit')
  }
}
</script>