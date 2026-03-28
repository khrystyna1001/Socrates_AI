<template>
  <Header />
  <main class="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 text-slate-100">
    <section class="mx-auto max-w-6xl px-6 py-16 md:py-24">
      <p class="inline-block rounded-full border border-cyan-600/40 bg-cyan-600/10 px-4 py-1 text-sm tracking-wide text-cyan-200">
        Retrieval-Augmented Assistant
      </p>
      <h1 class="mt-5 max-w-4xl text-4xl font-semibold leading-tight md:text-6xl">
        Ask better questions.
        <span class="text-cyan-300">Get grounded answers from your own PDFs.</span>
      </h1>
      <p class="mt-6 max-w-3xl text-lg text-slate-300">
        Upload a document to MinIO, generate embeddings in pgvector, then chat with context-aware responses from SocratesAI.
      </p>

      <div class="mt-10 flex flex-wrap gap-4">
        <button
          class="rounded-xl bg-cyan-400 px-6 py-3 text-lg font-semibold text-slate-900 transition hover:bg-cyan-300"
          @click="goToUpload"
        >
          Upload First Document
        </button>
        <button
          class="rounded-xl border border-cyan-300/50 bg-transparent px-6 py-3 text-lg font-semibold text-cyan-200 transition hover:bg-cyan-300/10"
          @click="goToChat"
        >
          Open Chat
        </button>
        <button
          class="rounded-xl border border-slate-400/40 bg-transparent px-6 py-3 text-lg font-semibold text-slate-200 transition hover:bg-slate-700/40"
          @click="goToGuide"
        >
          Setup Guide
        </button>
      </div>
    </section>

    <section class="mx-auto grid max-w-6xl gap-6 px-6 pb-16 md:grid-cols-3">
      <article class="rounded-2xl border border-slate-700 bg-slate-800/70 p-6 shadow-lg shadow-cyan-900/20">
        <p class="text-sm text-cyan-300">Step 1</p>
        <h2 class="mt-2 text-2xl font-semibold">Upload PDF</h2>
        <p class="mt-3 text-slate-300">Store your file in MinIO and register document metadata in PostgreSQL.</p>
      </article>

      <article class="rounded-2xl border border-slate-700 bg-slate-800/70 p-6 shadow-lg shadow-cyan-900/20">
        <p class="text-sm text-cyan-300">Step 2</p>
        <h2 class="mt-2 text-2xl font-semibold">Build Embeddings</h2>
        <p class="mt-3 text-slate-300">Chunk content and save vectors in pgvector for fast semantic retrieval.</p>
      </article>

      <article class="rounded-2xl border border-slate-700 bg-slate-800/70 p-6 shadow-lg shadow-cyan-900/20">
        <p class="text-sm text-cyan-300">Step 3</p>
        <h2 class="mt-2 text-2xl font-semibold">Ask Socrates</h2>
        <p class="mt-3 text-slate-300">Submit a prompt and get a response grounded in the closest document chunks.</p>
      </article>
    </section>
  </main>
</template>

<script setup>
import { useRouter } from "vue-router";
import Header from "@/components/Header.vue";

const router = useRouter();

const goToUpload = () => router.push("/upload");
const goToChat = () => router.push("/chat");
const goToGuide = () => router.push("/guide");
</script>
