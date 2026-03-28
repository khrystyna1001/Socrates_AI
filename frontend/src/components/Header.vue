<template>
  <header class="sticky top-0 z-50 transition-all duration-300 bg-slate-900">
    <section :class="['w-full', isScrolled ? 'backdrop-blur shadow-md py-2': 'py-4']">
        <div class="max-2-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex flex-col md:flex-row items-center justify-between gap-3 md:gap-6">
                <div class="flex justify-between items-center w-full md:w-auto">
                    <a href="/" class="text-5xl font-bold text-slate-300">SocratesAI</a>
                    <button 
                    class="md:hidden text-gray-700 hover:text-indigo-600"
                    >
                        <Icon icon="mdi:menu" class="w-6 h-6" />
                    </button>
                </div>
                <aside ref="menuRef" class="relative flex items-center justify-end space-x-4 w-full md:w-auto">
                    <button class="relative p-2 text-gray-700 hover:text-indigo-600" aria-label="Account"
                    @click="openUserMenu = !openUserMenu">
                        <Icon icon="mdi:account-outline" :style="{ fontSize: '36px', color: 'white' }" />
                    </button>
                    <div
                    v-if="openUserMenu"
                    class="absolute right-0 top-12 w-48 rounded-lg border border-slate-700 bg-slate-800 shadow-lg z-50"
                    >
                    <button class="block w-full px-4 py-2 text-left text-white hover:bg-slate-700">Profile</button>
                    <button class="block w-full px-4 py-2 text-left text-white hover:bg-slate-700">Settings</button>
                    <button class="block w-full px-4 py-2 text-left text-white hover:bg-slate-700">Logout</button>
                    </div>
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
        </div>
    </nav>
  </header>
</template>

<script setup>

import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import { onClickOutside } from "@vueuse/core";


const isScrolled = ref(false)
const openUserMenu = ref(false)
const menuRef = ref(null);


const navItems=[
    {id: 1, name: 'Home', path: '/'},
    {id: 2, name: 'Upload File', path: '/upload' },
    {id: 3, name: 'Chat with Socrates', path: '/chat' },
    {id: 4, name: 'About', path: '/about' },
    {id: 5, name: 'How to Use', path: '/guide' },
]

onClickOutside(menuRef, () => {
  openUserMenu.value = false;
});


</script>
