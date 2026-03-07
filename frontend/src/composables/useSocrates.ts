import { ref } from 'vue'
import axios from 'axios'


const API_BASE_URL = import.meta.env.API_BASE_URL || 'http://localhost:8000'

// Define exactly what a Source looks like
export interface Source {
  filename: string;
  page: number | string;
  content: string;
}

export interface ChatMessage {
  question: string;
  answer: string;
  sources: Source[];
}

export function useSocrates() {
  const query = ref('')
  const response = ref('')
  const isLoading = ref(false)
  
  // Updated: Now using the Source interface instead of string[]
  const sources = ref<Source[]>([])
  const chatHistory = ref<ChatMessage[]>([])

  const submitQuery = async () => {
    if (!query.value.trim() || isLoading.value) return
    
    isLoading.value = true
    const currentQuery = query.value
    
    // Reset state for new query
    response.value = ''
    sources.value = []
    
    try {
      const result = await axios.post(`${API_BASE_URL}/query`, {
        question: currentQuery
      })
      
      // Axios will automatically parse the JSON list of objects
      response.value = result.data.answer
      sources.value = result.data.sources || []
      
      chatHistory.value.unshift({
        question: currentQuery,
        answer: result.data.answer,
        sources: result.data.sources || []
      })
      
      query.value = ''
    } catch (error) {
      console.error('Error fetching Socrates response:', error)
      response.value = 'I encountered a philosophical roadblock. Please try again.'
    } finally {
      isLoading.value = false
    }
  }

  return { query, response, isLoading, sources, chatHistory, submitQuery }
}