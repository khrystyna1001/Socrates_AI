<template lang="">
  <div class="bg-slate-900 h-auto flex items-center justify-center flex-col p-20">
    <div class="relative">
      <h2 class="flex items-center text-white text-shadow-blue-300 text-5xl font-sans">Start Using Socrates AI</h2>
    </div>
    <div class="relative grid grid-cols-2 gap-10 p-20">
      <button class="bg-cyan-500 border-amber-200 border-2 shadow-lg shadow-cyan-500/50 text-white h-24 w-64 text-2xl rounded-2xl font-mono" @click="goToAbout">Start Using</button>
      <button class="bg-cyan-500 border-amber-200 border-2 shadow-lg shadow-cyan-500/50 text-white h-24 w-64 text-2xl rounded-2xl font-mono" @click="goToGuide">Learn More</button>
    </div>
  </div>

  <RouterView />
  
</template>

<script>
import { RouterView } from 'vue-router';

export default {

  methods: {
    goToAbout() {
      this.$router.push('/about')
    },
    goToGuide() {
      this.$router.push('/guide')
    },
  },
}

</script>