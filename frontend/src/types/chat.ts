export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  citations?: Citation[]
  translatedContent?: {
    ta?: string
    hi?: string
  }
  usage?: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
  latency_ms?: number
  answer_id?: string
  cost?: string
}

export interface Citation {
  source_id: string
  title: string
  content: string
  confidence: number
  page_number?: number
  course_id: string
  filename?: string
  score?: number
}

export interface ChatResponse {
  answer: string
  citations: Citation[]
  usage: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
  latency_ms: number
  answer_id: string
  cost?: string
}

export interface ModelInfo {
  chat_model: string
  embedding_model: string
  provider: string
  cost: string
  features: string[]
}
