<template>
  <Header />
  <main class="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 text-slate-100">
    <section class="mx-auto max-w-6xl px-6 py-16 md:py-24">
      <p class="inline-block rounded-full border border-cyan-600/40 bg-cyan-600/10 px-4 py-1 text-sm tracking-wide text-cyan-200">
        Quick Tutorial
      </p>
      <h1 class="mt-5 max-w-4xl text-4xl font-semibold leading-tight md:text-6xl">
        How to use SocratesAI
        <span class="text-cyan-300">from upload to answer.</span>
      </h1>

      <div class="mt-10 max-w-4xl rounded-2xl border border-slate-700 bg-slate-800/70 p-8 text-slate-300 shadow-lg shadow-cyan-900/20">
        <ol class="space-y-5 leading-8">
          <li>
            <span class="font-semibold text-cyan-200">1. Upload your PDF.</span>
            Go to the Upload page, provide a title, and choose a PDF file.
          </li>
          <li>
            <span class="font-semibold text-cyan-200">2. Wait for processing.</span>
            The backend extracts text, splits chunks, creates embeddings, and stores them in pgvector.
          </li>
          <li>
            <span class="font-semibold text-cyan-200">3. Open Chat.</span>
            Pick the related document and write your prompt.
          </li>
          <li>
            <span class="font-semibold text-cyan-200">4. Submit your question.</span>
            SocratesAI retrieves relevant chunks and asks the LLM to generate a grounded response.
          </li>
          <li>
            <span class="font-semibold text-cyan-200">5. Refine and iterate.</span>
            Ask follow-up questions for deeper explanations, summaries, or clarifications.
          </li>
        </ol>
      </div>

      <div class="mt-10 flex flex-wrap gap-4">
        <button
          class="rounded-xl bg-cyan-400 px-6 py-3 text-lg font-semibold text-slate-900 transition hover:bg-cyan-300"
          @click="goToUpload"
        >
          Upload Document
        </button>
        <button
          class="rounded-xl bg-cyan-400 px-6 py-3 text-lg font-semibold text-slate-900 transition hover:bg-cyan-300"
          @click="goToChat"
        >
          Chat with Socrates
        </button>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useRouter } from "vue-router";
import Header from "@/components/Header.vue";

const router = useRouter();
const goToUpload = () => router.push("/upload");
const goToChat = () => router.push("/chat");
</script>
