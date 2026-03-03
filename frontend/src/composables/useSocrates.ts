// composables/useSocrates.ts
import { ref } from 'vue'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export function useSocrates() {
  const query = ref('')
  const response = ref('')
  const isLoading = ref(false)
  const sources = ref<string[]>([])
  const chatHistory = ref<Array<{ question: string; answer: string; sources: string[] }>>([])

  const submitQuery = async () => {
    if (!query.value.trim() || isLoading.value) return
    
    isLoading.value = true
    const currentQuery = query.value
    response.value = ''
    sources.value = []
    
    try {
      const result = await axios.post(`${API_BASE_URL}/query`, {
        question: currentQuery
      })
      
      response.value = result.data.answer
      sources.value = result.data.sources || []
      
      chatHistory.value.unshift({
        question: currentQuery,
        answer: result.data.answer,
        sources: result.data.sources || []
      })
      
      query.value = ''
    } catch (error) {
      console.error('Error:', error)
      response.value = 'I encountered a philosophical roadblock. Please try again.'
    } finally {
      isLoading.value = false
    }
  }

  return { query, response, isLoading, sources, chatHistory, submitQuery }
}