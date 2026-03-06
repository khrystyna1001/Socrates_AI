<template>
  <div v-if="sources.length > 0" class="mt-8 pt-6 border-t border-slate-100">
    <div class="flex items-center gap-2 mb-4">
      <Quote class="w-4 h-4 text-slate-400" />
      <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">Grounding Sources</span>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
      <div 
        v-for="(source, index) in sources" 
        :key="index"
        class="group flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-xl hover:bg-white hover:border-blue-400 hover:shadow-md transition-all duration-300"
      >
        <div class="flex items-center gap-3 min-w-0">
          <div class="p-1.5 bg-blue-50 rounded-lg text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors">
            <FileText class="w-4 h-4" />
          </div>
          <span class="text-sm font-semibold text-slate-700 truncate">
            {{ source.filename }}
          </span>
        </div>

        <div class="px-2 py-1 bg-blue-100 text-blue-700 rounded-md text-[10px] font-black uppercase tracking-tighter whitespace-nowrap border border-blue-200">
          PG {{ source.page }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { MessageSquare, Quote, FileText } from 'lucide-vue-next'

// Define the interface for the structured source object
interface Source {
  filename: string
  page: string | number
}

defineProps<{
  response: string
  isLoading: boolean
  sources: any[]
}>()
</script>