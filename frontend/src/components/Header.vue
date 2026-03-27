<template>
  <header class="sticky top-0 z-50 transition-all duration-300">
    <section :class="['w-full', isScrolled ? 'bg-gray-100/95 backdrop-blur shadow-md py-2': 'bg-gray-100 py-4']">
        <div class="max-2-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex flex-col md:flex-row items-center justify-between gap-3 md:gap-6">
                <div class="flex justify-between items-center w-full md:w-auto">
                    <a href="/" class="text-2xl font-bold text-slate-600">SocratesAI</a>
                    <button 
                    class="md:hidden text-gray-700 hover:text-indigo:600"
                    aria-label="Toggle mobile menu"
                    @click="isMobileMenuOpen = !isMobileMenuOpen"
                    >
                        <Icon icon="mdi:menu" class="w-6 h-6" />
                    </button>
                </div>
                <aside class="flex items-center justify-end space-x-4 w-full md:w-auto">
                    <button class="relative p-2 text-gray-700 hover:text-indigo-600" aria-label="Wishlist">
                        <Icon icon="mdi:account-outline" class="w-5 h-5" />
                    </button>
                </aside>
            </div>
        </div>
    </section>
    <nav class="bg-slate-950" aria-label="Main navigation">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <ul class="hidden md:flex justify-center py-3 flex-wrap gap-x-6 text-sm font-medium text-white">
                <li v-for="item in navItems" :key="item.id">
                    <a :href="item.link" class="hover:text-indigo-300 transition-colors">{{  item.name  }}</a>
                </li>
            </ul>
            <section v-if="isMobileMenuOpen"
            class="md:hidden mt-2 bg-white rounded-lg shadow-md p-4 space-y-3 text-[#5D4037] text-center"
            aria-label="Mobile Navigation">
                <a v-for="item in navItems" :href="item.link" :key="item.id"
                class="block hover:text-amber-600 text-sm font-medium">{{  item.name  }}</a>
            </section>
        </div>
    </nav>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
const isScrolled = ref(false)
const isMobileMenuOpen = ref(false)
const navItems=[
    {id: 1, name: 'Home', link: '#home'},
    {id: 2, name: 'Upload File', link: '#upload'},
    {id: 3, name: 'Chat with Socrates', link: '#chat'},
    {id: 4, name: 'About', link: '#about'},
]

const handleScroll = () => {
    isScrolled.value = window.scrollY > 10
}

onMounted(() => {
    window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll)
})

</script>