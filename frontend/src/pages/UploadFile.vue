<template>
  <Header />
  <main class="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 text-slate-100">
    <section class="mx-auto max-w-6xl px-6 py-16 md:py-20">
      <p class="inline-block rounded-full border border-cyan-600/40 bg-cyan-600/10 px-4 py-1 text-sm tracking-wide text-cyan-200">
        Upload Documents
      </p>
      <h1 class="mt-5 max-w-4xl text-4xl font-semibold leading-tight md:text-5xl">
        Add your PDF and start indexing.
      </h1>
      <p class="mt-4 max-w-3xl text-slate-300">
        Uploaded files are stored in MinIO, chunked and embedded in the background, then made ready for chat.
      </p>
    </section>

    <section class="mx-auto grid max-w-6xl gap-6 px-6 pb-16 md:grid-cols-[1fr_1.4fr]">
      <article class="rounded-2xl border border-slate-700 bg-slate-800/70 p-6 shadow-lg shadow-cyan-900/20">
        <h2 class="text-xl font-semibold text-cyan-200">New Upload</h2>

        <div class="mt-5">
          <label class="mb-2 block text-sm text-slate-300">Title</label>
          <input
            v-model="title"
            type="text"
            placeholder="e.g. AI Lecture Notes Week 3"
            class="w-full rounded-lg border border-slate-600 bg-slate-900 px-3 py-2 text-slate-100 outline-none focus:border-cyan-400"
          />
        </div>

        <div class="mt-5">
          <label class="mb-2 block text-sm text-slate-300">PDF File</label>
          <input
            type="file"
            accept="application/pdf"
            class="w-full rounded-lg border border-slate-600 bg-slate-900 px-3 py-2 text-slate-100 file:mr-4 file:rounded-md file:border-0 file:bg-cyan-500 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-slate-900 hover:file:bg-cyan-400"
            @change="onFileChange"
          />
        </div>

        <button
          class="mt-5 w-full rounded-xl bg-cyan-400 px-6 py-3 text-lg font-semibold text-slate-900 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="isSubmitting || !title.trim() || !file"
          @click="uploadDocument"
        >
          {{ isSubmitting ? "Uploading..." : "Upload PDF" }}
        </button>

        <p v-if="successMessage" class="mt-3 text-sm text-emerald-300">{{ successMessage }}</p>
        <p v-if="errorMessage" class="mt-3 text-sm text-rose-300">{{ errorMessage }}</p>
      </article>

      <article class="rounded-2xl border border-slate-700 bg-slate-800/70 p-6 shadow-lg shadow-cyan-900/20">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold text-cyan-200">Uploaded Documents</h2>
          <button
            class="rounded-lg border border-cyan-300/40 px-3 py-1 text-sm text-cyan-200 transition hover:bg-cyan-300/10"
            @click="loadDocuments"
          >
            Refresh
          </button>
        </div>

        <p v-if="documents.length === 0" class="mt-4 text-slate-400">No documents uploaded yet.</p>

        <div v-else class="mt-4 space-y-3">
          <div
            v-for="doc in documents"
            :key="doc.id"
            class="rounded-lg border border-slate-700 bg-slate-900/60 p-4"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-semibold text-slate-100">{{ doc.title }}</p>
                <p class="mt-1 text-xs text-slate-400">ID: {{ doc.id }}</p>
              </div>
            </div>
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

const api = axios.create({
  baseURL: import.meta.env.VITE_DOC_API_BASE_URL || "/doc_api",
  headers: {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc3NTU0MTUyLCJpYXQiOjE3NzYyNTgxNTIsImp0aSI6IjYxYmJjODFiMDZjYzRkMjliNDAzYTE0NGJiNTJmMzcwIiwidXNlcl9pZCI6IjEifQ.o1p2_QprapMLVRlBRHahzk9EhJAnSkE-If5MXFRxzbE'},
  withCredentials: true,
});

const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  return parts.length === 2 ? parts.pop().split(";").shift() : "";
};

const title = ref("");
const file = ref(null);
const isSubmitting = ref(false);
const successMessage = ref("");
const errorMessage = ref("");
const documents = ref([]);
const router = useRouter();

const onFileChange = (event) => {
  const selected = event.target.files?.[0] || null;
  file.value = selected;
};

const loadDocuments = async () => {
  try {
    const { data } = await api.get("/docs/");
    documents.value = Array.isArray(data) ? data : [];
  } catch (error) {
    const status = error?.response?.status;
    if (status === 401 || status === 403) {
      errorMessage.value = "Please log in to view your documents.";
      router.push("/login");
      return;
    }

    const apiData = error?.response?.data;
    errorMessage.value = apiData?.detail || "Could not load documents.";
  }
};

const uploadDocument = async () => {
  isSubmitting.value = true;
  successMessage.value = "";
  errorMessage.value = "";

  try {
    const formData = new FormData();
    formData.append("title", title.value.trim());
    formData.append("file", file.value);

    await api.post("/docs/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
        "X-CSRFToken": getCookie("csrftoken"),
      },
    });

    successMessage.value = "Upload successful. Processing started.";
    title.value = "";
    file.value = null;
    await loadDocuments();
  } catch (error) {
    const status = error?.response?.status;
    if (status === 401 || status === 403) {
      errorMessage.value = "Your session expired. Please log in again.";
      router.push("/login");
      return;
    }

    const apiData = error?.response?.data;
    if (apiData?.title?.[0]) {
      errorMessage.value = apiData.title[0];
    } else if (apiData?.file?.[0]) {
      errorMessage.value = apiData.file[0];
    } else if (apiData?.detail) {
      errorMessage.value = apiData.detail;
    } else {
      errorMessage.value = "Upload failed. Please try again.";
    }
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(() => {
  loadDocuments();
});
</script>
