<template>
  <Header />
  <main class="min-h-screen">
    <section class="mx-auto max-w-6xl px-6 py-16 md:py-24">
      <p class="inline-block rounded-full border border-cyan-600/40 bg-cyan-600/10 px-4 py-1 text-sm tracking-wide text-slate-900">
        About SocratesAI
      </p>
      <h1 class="mt-5 max-w-4xl text-4xl font-semibold leading-tight md:text-6xl">
        What this project is
        <span class="text-cyan-300">and why it exists.</span>
      </h1>
      <div class="mt-10 max-w-4xl rounded-2xl border border-slate-700 bg-slate-800/70 p-8 leading-8 text-slate-300 shadow-lg shadow-cyan-900/20">
        <p>
          SocratesAI is a retrieval-augmented assistant designed to answer questions using your own documents instead
          of relying only on general model memory. When a PDF is uploaded, the system stores the file in MinIO, extracts
          and chunks the text through background Celery tasks, and saves vector embeddings in PostgreSQL with pgvector.
          Later, when a user submits a prompt, the most relevant chunks are retrieved and passed as context to the LLM,
          so responses are grounded in the source content. The goal is simple: make answers more reliable, more traceable,
          and genuinely useful for studying, research, and document-heavy workflows.
        </p>
      </div>

      <div class="mt-10 flex flex-wrap gap-4">
        <button
          class="rounded-xl bg-cyan-400 px-6 py-3 text-lg font-semibold text-slate-900 transition hover:bg-cyan-300"
          @click="goToUpload"
        >
          Upload Document
        </button>
        <button
          class="rounded-xl border border-cyan-300/50 bg-transparent px-6 py-3 text-lg font-semibold text-slate-900 transition hover:bg-cyan-300/10"
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
