<template>
  <Header />
  <main class="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 text-slate-100">
    <section class="mx-auto max-w-6xl px-6 py-16 md:py-20">
      <p class="inline-block rounded-full border border-cyan-600/40 bg-cyan-600/10 px-4 py-1 text-sm tracking-wide text-cyan-200">
        Chat with SocratesAI
      </p>
      <h1 class="mt-5 max-w-4xl text-4xl font-semibold leading-tight md:text-5xl">
        Ask a question against your uploaded document.
      </h1>
      <p class="mt-4 max-w-3xl text-slate-300">
        Select a processed document, write your prompt, and get a grounded response from your indexed PDF chunks.
      </p>
    </section>

    <section class="mx-auto grid max-w-6xl gap-6 px-6 pb-16 md:grid-cols-[1fr_1.4fr]">
      <article class="rounded-2xl border border-slate-700 bg-slate-800/70 p-6 shadow-lg shadow-cyan-900/20">
        <h2 class="text-xl font-semibold text-cyan-200">Prompt Setup</h2>

        <div class="mt-5">
          <label class="mb-2 block text-sm text-slate-300">Document</label>
          <select
            v-model="selectedDocumentId"
            class="w-full rounded-lg border border-slate-600 bg-slate-900 px-3 py-2 text-slate-100 outline-none focus:border-cyan-400"
          >
            <option disabled value="">Select a document</option>
            <option v-for="doc in documents" :key="doc.id" :value="doc.id">
              {{ doc.title }}
            </option>
          </select>
          <p class="mt-2 text-xs text-slate-400">Only documents with status = ready are shown.</p>
        </div>

        <div class="mt-5">
          <label class="mb-2 block text-sm text-slate-300">Prompt</label>
          <textarea
            v-model="prompt"
            rows="7"
            placeholder="Ask something specific about the selected PDF..."
            class="w-full rounded-lg border border-slate-600 bg-slate-900 px-3 py-2 text-slate-100 outline-none focus:border-cyan-400"
          />
        </div>

        <button
          class="mt-5 w-full rounded-xl bg-cyan-400 px-6 py-3 text-lg font-semibold text-slate-900 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="isSubmitting || !selectedDocumentId || !prompt.trim()"
          @click="submitPrompt"
        >
          {{ isSubmitting ? "Generating response..." : "Send Prompt" }}
        </button>

        <p v-if="errorMessage" class="mt-3 text-sm text-rose-300">{{ errorMessage }}</p>
      </article>

      <article class="rounded-2xl border border-slate-700 bg-slate-800/70 p-6 shadow-lg shadow-cyan-900/20">
        <h2 class="text-xl font-semibold text-cyan-200">Response</h2>
        <p v-if="!latestResponse" class="mt-4 text-slate-400">
          Your generated answer will appear here.
        </p>

        <div v-else class="mt-4 space-y-4">
          <div class="rounded-lg border border-slate-700 bg-slate-900/70 p-4">
            <p class="text-sm text-slate-400">Prompt</p>
            <p class="mt-2 whitespace-pre-wrap text-slate-100">{{ latestResponse.prompt }}</p>
          </div>

          <div class="rounded-lg border border-cyan-800/50 bg-cyan-950/20 p-4">
            <p class="text-sm text-cyan-200">Answer</p>
            <p class="mt-2 whitespace-pre-wrap leading-7 text-slate-100">{{ latestResponse.response }}</p>
          </div>
        </div>
      </article>
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import Header from "@/components/Header.vue";

const docsApi = axios.create({
  baseURL: import.meta.env.VITE_DOC_API_BASE_URL || "/doc_api",
  headers: {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc3NTU0MTUyLCJpYXQiOjE3NzYyNTgxNTIsImp0aSI6IjYxYmJjODFiMDZjYzRkMjliNDAzYTE0NGJiNTJmMzcwIiwidXNlcl9pZCI6IjEifQ.o1p2_QprapMLVRlBRHahzk9EhJAnSkE-If5MXFRxzbE'},
  withCredentials: true,
});

const bartApi = axios.create({
  baseURL: import.meta.env.VITE_BART_API_BASE_URL || "/bart_api",
  headers: {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc3NTU0MTUyLCJpYXQiOjE3NzYyNTgxNTIsImp0aSI6IjYxYmJjODFiMDZjYzRkMjliNDAzYTE0NGJiNTJmMzcwIiwidXNlcl9pZCI6IjEifQ.o1p2_QprapMLVRlBRHahzk9EhJAnSkE-If5MXFRxzbE'},
  withCredentials: true,
});

const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  return parts.length === 2 ? parts.pop().split(";").shift() : "";
};

const documents = ref([]);
const selectedDocumentId = ref("");
const prompt = ref("");
const isSubmitting = ref(false);
const errorMessage = ref("");
const latestResponse = ref(null);
const router = useRouter();

const loadDocuments = async () => {
  try {
    const { data } = await docsApi.get("/docs/");
    documents.value = Array.isArray(data) ? data : [];
  } catch (error) {
    const status = error?.response?.status;
    if (status === 401 || status === 403) {
      errorMessage.value = "Please log in to access your documents.";
      router.push("/login");
      return;
    }
    errorMessage.value = "Could not load documents. Check backend connection.";
  }
};

const submitPrompt = async () => {
  isSubmitting.value = true;
  errorMessage.value = "";

  try {
    const payload = {
      document: selectedDocumentId.value,
      prompt: prompt.value.trim(),
    };
    const { data } = await bartApi.post("/bart/", payload, {
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
    });
    latestResponse.value = data;
  } catch (error) {
    const status = error?.response?.status;
    if (status === 401) {
      errorMessage.value = "Your session expired. Please log in again.";
      router.push("/login");
      return;
    }
    const apiMessage = error?.response?.data?.detail;
    errorMessage.value = apiMessage || "Failed to generate response.";
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(() => {
  loadDocuments();
});
</script>
