import axios from 'axios'
import { ChatResponse, ModelInfo } from '../types/chat'

const API_BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const chatApi = {
  // Simple chat endpoint
  async sendMessage(query: string): Promise<ChatResponse> {
    const response = await api.post('/chat', { query })
    return response.data
  },

  // Document-based chat endpoint
  async sendDocumentMessage(query: string, documentId: string): Promise<ChatResponse> {
    const response = await api.post('/document-chat/chat', { 
      query,
      course_id: documentId
    })
    return response.data
  },

  // Advanced chat with vector search
  async sendAdvancedMessage(query: string, topK: number = 5): Promise<ChatResponse> {
    const response = await api.post('/answer', { 
      query, 
      top_k: topK
    })
    return response.data
  },

  // Translation API
  async translate(text: string, targetLang: string): Promise<{ translated: string }> {
    const response = await api.post('/simple-chat/translate', { text, target_lang: targetLang })
    return response.data
  },

  // Get model information
  async getModelInfo(): Promise<ModelInfo> {
    const response = await api.get('/models')
    return response.data
  },

  // Check service status
  async getStatus(): Promise<any> {
    const response = await api.get('/status')
    return response.data
  },

  // Search content
  async searchContent(query: string, courseId?: string, topK: number = 5): Promise<any> {
    const params = new URLSearchParams({ query, top_k: topK.toString() })
    if (courseId) params.append('course_id', courseId)
    
    const response = await api.get(`/search?${params}`)
    return response.data
  },

  // Add course content
  async addContent(content: {
    title: string
    content: string
    course_id: string
    section_id?: string
    page_number?: number
    metadata?: Record<string, any>
  }): Promise<{ message: string; content_id: string }> {
    const response = await api.post('/content', content)
    return response.data
  },

  // Document management
  async uploadDocument(file: File): Promise<any> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async getDocuments(): Promise<any> {
    const response = await api.get('/documents/list')
    return response.data
  },

  async deleteDocument(documentId: string): Promise<any> {
    const response = await api.delete(`/documents/${documentId}`)
    return response.data
  },

  async searchDocuments(query: string, documentId?: string, topK: number = 5): Promise<any> {
    const params = new URLSearchParams({ query, top_k: topK.toString() })
    if (documentId) params.append('document_id', documentId)
    
    const response = await api.get(`/documents/search?${params}`)
    return response.data
  }
}

export default api
