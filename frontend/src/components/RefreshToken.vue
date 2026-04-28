<template>
    <dialog>
        <main class="min-h-screen bg-slate-900 text-white">
        <section class="mx-auto max-w-2xl px-6 py-16 text-center">
            <h2 class="text-3xl font-semibold mb-4">Session Expired</h2>
            <p class="text-slate-300 mb-6">Your session has expired. Please log in again to continue.</p>
            <button
                class="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 transition-colors"
                @click="$emit('refresh')"
            >
                Refresh Token
            </button>
        </section>
        </main>
    </dialog>
</template>

<script setup>


</script>