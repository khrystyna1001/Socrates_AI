<template>
  <div class="upload-container">
    <h2>Upload to Minio</h2>
    <input type="file" @change="handleFileSelect" />
    <button @click="uploadFile" :disabled="!selectedFile || uploading">
      {{ uploading ? 'Uploading...' : 'Upload Now' }}
    </button>
    
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const selectedFile = ref(null);
const uploading = ref(false);
const message = ref('');

const handleFileSelect = (event) => {
  selectedFile.value = event.target.files[0];
};

const uploadFile = async () => {
  if (!selectedFile.value) return;

  const formData = new FormData();
  formData.append('document', selectedFile.value);

  try {
    uploading.value = true;
    const response = await axios.post('http://localhost:8000/api/docs/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    message.value = "Upload started! Processing in background...";
  } catch (error) {
    message.value = "Error uploading file.";
  } finally {
    uploading.value = false;
  }
};
</script>

<style scoped>
.upload-container { border: 1px solid #ccc; padding: 20px; border-radius: 8px; }
button { margin-left: 10px; cursor: pointer; }
</style>