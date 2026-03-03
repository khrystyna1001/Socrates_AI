<template>
  <header class="sticky top-0 z-50 backdrop-blur-md bg-white/75 border-b border-slate-200/60">
    <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
      
      <div class="flex items-center gap-4 group cursor-default">
        <div class="relative">
          <div class="absolute -inset-1 bg-gradient-to-tr from-blue-600 to-indigo-500 rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-1000"></div>
          
          <div class="relative p-2.5 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-xl shadow-lg shadow-blue-200/50">
            <Brain class="w-6 h-6 text-white" />
          </div>
        </div>

        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-2xl font-black tracking-tight text-slate-800">
              Socrates<span class="text-blue-600 italic">AI</span>
            </h1>
            <span class="px-2 py-0.5 rounded-md bg-blue-50 text-[10px] font-bold text-blue-600 uppercase tracking-tighter border border-blue-100">
              v2.0
            </span>
          </div>
          <p class="text-[10px] uppercase tracking-[0.2em] font-bold text-slate-400 mt-0.5">
            Advanced RAG Protocol
          </p>
        </div>
      </div>

      <div class="hidden sm:flex items-center gap-4">
        <div class="flex items-center gap-2.5 bg-slate-50 border border-slate-200/60 px-4 py-2 rounded-full shadow-sm transition-all hover:bg-white hover:shadow-md">
          <div class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </div>
          <span class="text-xs font-semibold text-slate-600 tracking-wide">Systems Nominal</span>
        </div>
        
        <div class="h-8 w-8 rounded-full bg-slate-200 border border-white shadow-sm overflow-hidden bg-gradient-to-br from-slate-100 to-slate-300"></div>
      </div>

    </div>
  </header>
</template>

<script setup lang="ts">
import { Brain } from 'lucide-vue-next'
</script>