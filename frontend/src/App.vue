<script setup lang="ts">
import { useSocrates } from './composables/useSocrates'
import QueryInput from './components/QueryInput.vue'
import ResponseDisplay from './components/ResponseDisplay.vue'
import ChatHistory from './components/ChatHistory.vue'
import TheHeader from './components/TheHeader.vue'

const { query, response, isLoading, sources, chatHistory, submitQuery } = useSocrates()
</script>

<template>
  <div class="min-h-screen bg-[#f8fafc] text-slate-900 selection:bg-blue-100 font-sans">
    
    <div class="fixed inset-0 pointer-events-none overflow-hidden">
       <div class="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] rounded-full bg-blue-100/40 blur-[120px]"></div>
    </div>

    <TheHeader />

    <main class="relative max-w-6xl mx-auto px-6 pt-6 pb-12">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        <div class="lg:col-span-8 space-y-6">
          <QueryInput 
            v-model="query" 
            :is-loading="isLoading" 
            @submit="submitQuery" 
          />
          
          <ResponseDisplay 
            :response="response" 
            :is-loading="isLoading" 
            :sources="sources" 
          />
        </div>

        <ChatHistory :history="chatHistory" />
        
      </div>
    </main>
  </div>
</template>