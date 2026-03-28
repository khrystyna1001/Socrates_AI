<template>
  <header class="sticky top-0 z-50 transition-all duration-300 bg-slate-900">
    <section :class="['w-full', isScrolled ? 'backdrop-blur shadow-md py-2': 'py-4']">
        <div class="max-2-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex flex-col md:flex-row items-center justify-between gap-3 md:gap-6">
                <div class="flex justify-between items-center w-full md:w-auto">
                    <a href="/" class="text-5xl font-bold text-slate-300">SocratesAI</a>
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
                        <Icon icon="mdi:account-outline" :style="{ fontSize: '36px', color: 'white' }" />
                    </button>
                </aside>
            </div>
        </div>
    </section>
    <nav class="flex items-center h-24" aria-label="Main navigation">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <ul class="text-2xl hidden md:flex justify-center py-3 flex-wrap gap-x-20 font-medium text-cyan-500" :style="{ textShadow: '1px 1px 1px cyan'}">
                <li v-for="item in navItems" :key="item.id">
                    <RouterLink :to="item.path" class="hover:text-indigo-300 transition-colors">{{  item.name  }}</RouterLink>
                </li>
            </ul>
            <section v-if="isMobileMenuOpen"
            class="md:hidden mt-2 bg-white rounded-lg shadow-md p-4 space-y-3 text-[#5D4037] text-center"
            aria-label="Mobile Navigation">
                <a v-for="item in navItems" :href="item.path" :key="item.id"
                class="block hover:text-amber-600 text-sm font-medium">{{  item.name  }}</a>
            </section>
        </div>
    </nav>
  </header>
</template>

<script setup>

import { ref } from 'vue';
import { RouterLink } from 'vue-router';

const isScrolled = ref(false)
const isMobileMenuOpen = ref(false)

const navItems=[
    {id: 1, name: 'Home', path: '/'},
    {id: 2, name: 'Upload File', path: '/upload' },
    {id: 3, name: 'Chat with Socrates', path: '/chat' },
    {id: 4, name: 'About', path: '/about' },
]

</script>