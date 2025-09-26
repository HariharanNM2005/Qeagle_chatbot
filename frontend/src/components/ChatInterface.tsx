import React, { useState, useRef, useEffect } from 'react'
import { Button } from './ui/button'
import { Input } from './ui/input'
// import { Card } from './ui/card'
import { Message } from '../types/chat'
import { chatApi } from '../lib/api'
import { formatTimestamp } from '../lib/utils'
import { Send, Bot, User, Loader2, AlertCircle, Sparkles, FileText } from 'lucide-react'
// import MessageBubble from './MessageBubble'

interface ChatInterfaceProps {
  messages: Message[]
  onAddMessage: (message: Message) => void
  isLoading: boolean
  onLoadingChange: (loading: boolean) => void
  selectedDocumentId?: string | null
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onAddMessage,
  isLoading,
  onLoadingChange,
  selectedDocumentId
}) => {
  const [input, setInput] = useState('')
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input.trim(),
      role: 'user',
      timestamp: new Date()
    }

    onAddMessage(userMessage)
    setInput('')
    setError(null)
    onLoadingChange(true)

    try {
      let response;
      if (selectedDocumentId) {
        // Use document-based chat
        response = await chatApi.sendDocumentMessage(input.trim(), selectedDocumentId)
      } else {
        // Use regular chat
        response = await chatApi.sendMessage(input.trim())
      }
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.answer,
        role: 'assistant',
        timestamp: new Date(),
        citations: response.citations,
        usage: response.usage,
        latency_ms: response.latency_ms,
        answer_id: response.answer_id,
        cost: response.cost
      }

      onAddMessage(aiMessage)
    } catch (err) {
      console.error('Chat error:', err)
      setError('Failed to get response. Please try again.')
    } finally {
      onLoadingChange(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  // const handleTranslate = async (message: Message, targetLang: string) => {
  //   try {
  //     const res = await chatApi.translate(message.content, targetLang)
  //     message.translatedContent = { 
  //       ...(message.translatedContent || {}), 
  //       [targetLang]: res.translated 
  //     }
  //   } catch (e) {
  //     console.error(`Translate ${targetLang.toUpperCase()} failed`, e)
  //   }
  // }

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Messages */}
      <div className="flex-1 min-h-0 overflow-y-auto p-3 sm:p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-8 sm:py-16 px-4 sm:px-8">
            <div className="w-16 h-16 sm:w-20 sm:h-20 mx-auto mb-6 sm:mb-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-3xl flex items-center justify-center shadow-lg">
              <Sparkles className="w-8 h-8 sm:w-10 sm:h-10 text-white" />
            </div>
            <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-3">Welcome to AI Assistant!</h3>
            <p className="text-sm sm:text-base text-gray-600 mb-6 sm:mb-8 max-w-md mx-auto leading-relaxed">
              I'm your intelligent AI assistant. Ask me anything about your documents or general questions, and I'll provide detailed answers with source citations.
            </p>
            <div className="flex flex-wrap justify-center gap-2 sm:gap-3 text-xs sm:text-sm">
              <span className="bg-blue-100 text-blue-700 px-3 py-1 sm:px-4 sm:py-2 rounded-full font-medium">Multi-language</span>
              <span className="bg-green-100 text-green-700 px-3 py-1 sm:px-4 sm:py-2 rounded-full font-medium">Source citations</span>
              <span className="bg-purple-100 text-purple-700 px-3 py-1 sm:px-4 sm:py-2 rounded-full font-medium">Document analysis</span>
              <span className="bg-orange-100 text-orange-700 px-3 py-1 sm:px-4 sm:py-2 rounded-full font-medium">Real-time</span>
            </div>
            {selectedDocumentId && (
              <div className="mt-6 sm:mt-8 p-3 sm:p-4 bg-blue-50 rounded-xl border border-blue-200 max-w-md mx-auto">
                <div className="flex items-center justify-center space-x-2 mb-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-xs sm:text-sm font-medium text-blue-700">Document Context Active</span>
                </div>
                <p className="text-xs text-blue-600">
                  I'm ready to answer questions based on your uploaded document.
                </p>
              </div>
            )}
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4 sm:mb-6`}
            >
              <div className={`flex items-start space-x-2 sm:space-x-3 max-w-[90%] sm:max-w-[85%] ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <div className={`flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-full flex items-center justify-center shadow-sm ${
                  message.role === 'user' 
                    ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white' 
                    : 'bg-gradient-to-br from-gray-100 to-gray-200 text-gray-600 border border-gray-200'
                }`}>
                  {message.role === 'user' ? <User className="w-4 h-4 sm:w-5 sm:h-5" /> : <Bot className="w-4 h-4 sm:w-5 sm:h-5" />}
                </div>
                
                <div className={`rounded-xl sm:rounded-2xl px-3 py-2 sm:px-4 sm:py-3 shadow-sm ${
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                    : 'bg-white text-gray-900 border border-gray-200'
                }`}>
                  <p className="text-sm whitespace-pre-wrap leading-relaxed">
                    {message.content}
                  </p>
                  <div className="flex items-center justify-between mt-2">
                    <p className={`text-xs ${
                      message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                    }`}>
                      {formatTimestamp(message.timestamp)}
                    </p>
                    {message.latency_ms && (
                      <p className={`text-xs ${
                        message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {message.latency_ms.toFixed(0)}ms
                      </p>
                    )}
                  </div>
                  
                  {/* Show citations if available */}
                  {message.citations && message.citations.length > 0 && (
                    <div className="mt-3 sm:mt-4 pt-2 sm:pt-3 border-t border-gray-200">
                      <div className="flex items-center space-x-2 mb-2 sm:mb-3">
                        <div className="w-4 h-4 sm:w-5 sm:h-5 bg-blue-100 rounded-full flex items-center justify-center">
                          <FileText className="w-2 h-2 sm:w-3 sm:h-3 text-blue-600" />
                        </div>
                        <p className="text-xs sm:text-sm font-semibold text-gray-700">Sources ({message.citations.length})</p>
                      </div>
                      <div className="space-y-2 sm:space-y-3">
                        {message.citations.slice(0, 2).map((citation, index) => (
                          <div key={index} className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-2 sm:p-3 border border-blue-200">
                            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between mb-2 space-y-1 sm:space-y-0">
                              <div className="flex flex-col sm:flex-row sm:items-center space-y-1 sm:space-y-0 sm:space-x-2">
                                <span className="text-xs sm:text-sm font-semibold text-blue-900 truncate">
                                  {citation.title || citation.filename || 'Unknown Document'}
                                </span>
                              {citation.page_number && (
                                  <span className="text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded-full w-fit">
                                    Page {citation.page_number}
                                  </span>
                                )}
                              </div>
                            {(() => {
                              const raw = (typeof (citation as any).confidence === 'number'
                                ? (citation as any).confidence
                                : (typeof (citation as any).score === 'number' ? (citation as any).score : undefined)) as number | undefined
                              if (typeof raw !== 'number') return null
                              const pct = Math.max(0, Math.min(1, Number(raw))) * 100
                              return (
                                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium w-fit">
                                  {pct.toFixed(1)}% match
                                </span>
                              )
                            })()}
                            </div>
                            <div className="text-xs sm:text-sm text-gray-700 bg-white rounded-md p-2 border border-gray-200">
                              <p className="line-clamp-2 sm:line-clamp-3 leading-relaxed">
                                {citation.content || 'No content preview available'}
                              </p>
                            </div>
                          </div>
                        ))}
                        {message.citations.length > 2 && (
                          <div className="text-center">
                            <span className="text-xs sm:text-sm text-gray-500 bg-gray-100 px-2 sm:px-3 py-1 rounded-full">
                              +{message.citations.length - 2} more sources
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-100 to-blue-200 text-blue-600 flex items-center justify-center border border-blue-200 shadow-sm">
                <Bot className="w-5 h-5" />
              </div>
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl px-4 py-3 shadow-sm">
                <div className="flex items-center space-x-3">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                  <span className="text-sm font-medium text-blue-700">AI is thinking...</span>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
                <p className="text-xs text-blue-600 mt-1">Analyzing your question and preparing response...</p>
              </div>
            </div>
          </div>
        )}
        
        {error && (
          <div className="flex justify-center">
            <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-2 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-red-500" />
              <span className="text-sm text-red-700">{error}</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200/50 p-3 sm:p-6 bg-gradient-to-r from-gray-50/50 to-blue-50/30">
        <form onSubmit={handleSubmit} className="flex space-x-2 sm:space-x-4">
          <div className="flex-1 relative">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything..."
              disabled={isLoading}
              className="pr-12 sm:pr-16 h-10 sm:h-14 rounded-xl sm:rounded-2xl border-2 border-gray-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-200 text-gray-900 placeholder:text-gray-500 bg-white shadow-sm hover:shadow-md text-sm sm:text-base"
              style={{ caretColor: '#1f2937' }}
            />
            <div className="absolute right-3 sm:right-4 top-1/2 transform -translate-y-1/2 text-xs text-gray-400 bg-white px-1 sm:px-2 py-1 rounded-full hidden sm:block">
              Press Enter
            </div>
          </div>
          <Button 
            type="submit" 
            disabled={isLoading || !input.trim()}
            className="h-10 w-10 sm:h-14 sm:w-14 rounded-xl sm:rounded-2xl bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl hover:scale-105"
          >
            <Send className="w-4 h-4 sm:w-5 sm:h-5" />
          </Button>
        </form>
        
        {selectedDocumentId && (
          <div className="mt-2 sm:mt-3 flex items-center justify-center">
            <div className="flex items-center space-x-2 px-3 sm:px-4 py-1 sm:py-2 bg-blue-100 rounded-full border border-blue-200">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <span className="text-xs sm:text-sm font-medium text-blue-700">Using document context</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatInterface
