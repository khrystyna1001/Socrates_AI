<template>
  <div class="space-y-6">
    <div v-if="response || isLoading" 
         class="bg-white border border-slate-200 rounded-3xl shadow-sm overflow-hidden transition-all duration-500">
      
      <div v-if="isLoading" class="p-8 space-y-4 animate-pulse">
        <div class="h-4 bg-slate-100 rounded w-3/4"></div>
        <div class="h-4 bg-slate-100 rounded w-5/6"></div>
        <div class="h-4 bg-slate-100 rounded w-1/2"></div>
      </div>

      <div v-else class="p-8">
        <div class="flex items-center gap-3 mb-6">
          <div class="p-2 bg-blue-600 rounded-xl text-white shadow-lg shadow-blue-200">
            <MessageSquare class="w-5 h-5" />
          </div>
          <h2 class="text-lg font-bold text-slate-800">Synthesized Summary</h2>
        </div>

        <div class="prose prose-slate max-w-none">
          <p class="text-slate-700 leading-relaxed text-lg whitespace-pre-line">
            {{ response }}
          </p>
        </div>

        <div class="mt-8 flex gap-4 border-t border-slate-50 pt-6">
          <div class="flex flex-col">
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Sources Verified</span>
            <span class="text-sm font-semibold text-blue-600">{{ uniqueDocuments }} Documents</span>
          </div>
          <div class="w-px h-8 bg-slate-100"></div>
          <div class="flex flex-col">
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Page Range</span>
            <span class="text-sm font-semibold text-blue-600">PG {{ pageRange }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="sources.length > 0" class="mt-8">
      <div class="flex items-center gap-2 mb-4 px-2">
        <Quote class="w-4 h-4 text-slate-400" />
        <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">Supporting Evidence</span>
      </div>

      <div class="grid grid-cols-1 gap-4">
        <div 
          v-for="(source, index) in sources" 
          :key="index"
          class="group flex flex-col p-5 bg-white border border-slate-200 rounded-2xl hover:border-blue-400 hover:shadow-xl transition-all duration-300"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3 min-w-0">
              <div class="p-2 bg-slate-50 rounded-lg text-slate-400 group-hover:bg-blue-50 group-hover:text-blue-600 transition-colors">
                <FileText class="w-4 h-4" />
              </div>
              <span class="text-sm font-bold text-slate-800 truncate">
                {{ source.filename }}
              </span>
            </div>
            
            <div class="px-2 py-1 bg-slate-100 text-slate-500 rounded-md text-[10px] font-black group-hover:bg-blue-100 group-hover:text-blue-700 transition-colors">
              PG {{ source.page }}
            </div>
          </div>

          <div v-if="source.content" class="relative">
            <div class="text-sm leading-relaxed text-slate-600 bg-slate-50/50 border border-slate-100 p-4 rounded-xl max-h-64 overflow-y-auto custom-scrollbar">
              <p class="italic font-serif">
                "{{ source.content }}"
              </p>
            </div>
            <div class="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-white/10 to-transparent pointer-events-none"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { MessageSquare, Quote, FileText } from 'lucide-vue-next'

interface Source {
  filename: string
  page: string | number
  content: string
}

const props = defineProps<{
  response: string
  isLoading: boolean
  sources: Source[]
}>()

const uniqueDocuments = computed(() => {
  return new Set(props.sources.map(s => s.filename)).size
})

const pageRange = computed(() => {
  const pages = props.sources
    .map(s => parseInt(s.page.toString()))
    .filter(p => !isNaN(p))
  
  if (pages.length === 0) return 'N/A'
  const min = Math.min(...pages)
  const max = Math.max(...pages)
  return min === max ? `${min}` : `${min} - ${max}`
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  @apply bg-slate-200 rounded-full;
}
</style>