import React, { useState } from 'react'
import { Message } from '../types/chat'
import { Bot, User, Copy, Check, Languages, Clock, Zap } from 'lucide-react'
import { Button } from './ui/button'
import SourceDisplay from './SourceDisplay'

interface MessageBubbleProps {
  message: Message
  showTranslation: 'none' | 'ta' | 'hi' | 'en'
  onTranslationChange: (lang: 'none' | 'ta' | 'hi' | 'en') => void
  onTranslate: (message: Message, targetLang: string) => Promise<void>
}

const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  showTranslation,
  onTranslationChange,
  onTranslate
}) => {
  const [copied, setCopied] = useState(false)
  const [isTranslating, setIsTranslating] = useState<Set<string>>(new Set())

  const detectLanguageCode = (text: string): 'hi' | 'ta' | 'en' => {
    if (!text) return 'en'
    for (let i = 0; i < text.length; i++) {
      const code = text.charCodeAt(i)
      if (code >= 0x0900 && code <= 0x097F) return 'hi' // Devanagari
      if (code >= 0x0B80 && code <= 0x0BFF) return 'ta' // Tamil
    }
    // heuristic for romanized
    const t = text.toLowerCase()
    const tokens = new Set(t.replace(/[?!.,]/g, ' ').split(/\s+/))
    const romanHi = new Set(['hai','kitna','kitni','kya','kyun','kaun','kahan','mein','hain','tha','thi'])
    const romanTa = new Set(['irukku','ethana','evlo','enna','epdi'])
    for (const w of tokens) if (romanHi.has(w)) return 'hi'
    for (const w of tokens) if (romanTa.has(w)) return 'ta'
    return 'en'
  }

  const handleCopy = async () => {
    const textToCopy = showTranslation !== 'none' && message.translatedContent && message.translatedContent[showTranslation]
      ? message.translatedContent[showTranslation]
      : message.content
    
    try {
      await navigator.clipboard.writeText(textToCopy)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const handleTranslate = async (targetLang: string) => {
    if (isTranslating.has(targetLang)) return
    
    setIsTranslating(prev => new Set(prev).add(targetLang))
    try {
      await onTranslate(message, targetLang)
    } finally {
      setIsTranslating(prev => {
        const newSet = new Set(prev)
        newSet.delete(targetLang)
        return newSet
      })
    }
  }

  const getDisplayContent = () => {
    if (showTranslation !== 'none' && message.translatedContent && message.translatedContent[showTranslation]) {
      return message.translatedContent[showTranslation]
    }
    return message.content
  }

  const isUser = message.role === 'user'
  const detectedLang = detectLanguageCode(message.content)

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div className={`flex items-start space-x-3 max-w-[85%] ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center shadow-sm ${
          isUser 
            ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white' 
            : 'bg-gradient-to-br from-gray-100 to-gray-200 text-gray-600 border border-gray-200'
        }`}>
          {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
        </div>
        
        {/* Message Content */}
        <div className={`flex-1 min-w-0`}>
          <div className={`rounded-2xl px-4 py-3 shadow-sm ${
            isUser
              ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
              : 'bg-white text-gray-900 border border-gray-200'
          }`}>
            {/* Message Text */}
            <div className="prose prose-sm max-w-none">
              <p className="whitespace-pre-wrap leading-relaxed m-0">
                {getDisplayContent()}
              </p>
            </div>

            {/* Message Actions */}
            <div className="flex items-center justify-between mt-3 pt-2 border-t border-white/20">
              <div className="flex items-center space-x-2">
                <div className="flex items-center space-x-1 text-xs opacity-75">
                  <Clock className="w-3 h-3" />
                  <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
                </div>
                
                {message.latency_ms && (
                  <div className="flex items-center space-x-1 text-xs opacity-75">
                    <Zap className="w-3 h-3" />
                    <span>{message.latency_ms.toFixed(0)}ms</span>
                  </div>
                )}
              </div>

              <div className="flex items-center space-x-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCopy}
                  className={`h-6 w-6 p-0 ${isUser ? 'text-white/70 hover:text-white' : 'text-gray-400 hover:text-gray-600'}`}
                >
                  {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                </Button>

                {!isUser && (
                  <div className="flex items-center space-x-1">
                    {['ta', 'hi', 'en'].map((lang) => {
                      const isActive = showTranslation === lang || (showTranslation === 'none' && detectedLang === lang)
                      const isTranslatingThis = isTranslating.has(lang)
                      
                      return (
                        <Button
                          key={lang}
                          variant="ghost"
                          size="sm"
                          onClick={async () => {
                            if (isActive) {
                              onTranslationChange('none')
                            } else {
                              if (!message.translatedContent?.[lang as 'ta' | 'hi']) {
                                await handleTranslate(lang)
                              }
                              onTranslationChange(lang as 'none' | 'ta' | 'hi' | 'en')
                            }
                          }}
                          disabled={isTranslatingThis}
                          className={`h-6 px-2 text-xs font-medium ${
                            isActive 
                              ? (isUser ? 'bg-white/20 text-white' : 'bg-blue-100 text-blue-700')
                              : (isUser ? 'text-white/70 hover:text-white hover:bg-white/10' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100')
                          }`}
                        >
                          {isTranslatingThis ? (
                            <div className="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin" />
                          ) : (
                            lang.toUpperCase()
                          )}
                        </Button>
                      )
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sources for Assistant Messages */}
          {!isUser && message.citations && message.citations.length > 0 && (
            <SourceDisplay citations={message.citations} className="mt-3" />
          )}

          {/* Usage Stats for Assistant Messages */}
          {!isUser && message.usage && (
            <div className="mt-2 text-xs text-gray-500 flex items-center space-x-4">
              <span>Tokens: {message.usage.total_tokens}</span>
              {message.cost && <span>Cost: {message.cost}</span>}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default MessageBubble
