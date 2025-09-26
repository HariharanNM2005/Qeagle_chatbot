import React, { useState, useEffect } from 'react'
import ChatInterface from './components/ChatInterface'
import Header from './components/Header'
import DocumentUpload from './components/DocumentUpload'
import DocumentList from './components/DocumentList'
import { Message } from './types/chat'
import { FileText, MessageSquare, Upload } from 'lucide-react'
import { Button } from './components/ui/button'

type TabType = 'chat' | 'documents' | 'upload'

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<TabType>('chat')
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null)

  const addMessage = (message: Message) => {
    setMessages(prev => [...prev, message])
  }

  const clearMessages = () => {
    setMessages([])
  }

  const handleDocumentUpload = (documentId: string) => {
    setSelectedDocumentId(documentId)
    setActiveTab('chat')
    // Show success message
    addMessage({
      id: Date.now().toString(),
      content: `Document uploaded successfully! You can now ask questions about it.`,
      role: 'user',
      timestamp: new Date()
    })
  }

  const handleDocumentSelect = (documentId: string) => {
    setSelectedDocumentId(documentId)
    setActiveTab('chat')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/50">
      <Header onClear={clearMessages} />
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Tab Navigation */}
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 mb-8">
            <div className="border-b border-gray-200/50">
              <nav className="flex space-x-8 px-8">
                <button
                  onClick={() => setActiveTab('chat')}
                  className={`py-5 px-1 border-b-2 font-medium text-sm transition-all duration-200 ${
                    activeTab === 'chat'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <MessageSquare className="w-5 h-5 inline mr-2" />
                  AI Chat
                </button>
                <button
                  onClick={() => setActiveTab('documents')}
                  className={`py-5 px-1 border-b-2 font-medium text-sm transition-all duration-200 ${
                    activeTab === 'documents'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <FileText className="w-5 h-5 inline mr-2" />
                  Documents
                </button>
                <button
                  onClick={() => setActiveTab('upload')}
                  className={`py-5 px-1 border-b-2 font-medium text-sm transition-all duration-200 ${
                    activeTab === 'upload'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Upload className="w-5 h-5 inline mr-2" />
                  Upload
                </button>
              </nav>
            </div>
          </div>

          {/* Tab Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {activeTab === 'chat' && (
              <div className="lg:col-span-2">
                <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 overflow-hidden">
                  <div className="p-8 border-b border-gray-200/50 bg-gradient-to-r from-blue-50/50 to-indigo-50/50">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                        <MessageSquare className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h1 className="text-2xl font-bold text-gray-900">
                          AI Assistant
                        </h1>
                        <p className="text-gray-600 text-sm">
                          Powered by advanced AI with document analysis
                        </p>
                      </div>
                    </div>
                    <p className="text-gray-600 text-sm">
                      Ask questions about your documents or general topics. 
                      {selectedDocumentId && (
                        <span className="inline-flex items-center ml-2 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                          <div className="w-2 h-2 bg-blue-500 rounded-full mr-1"></div>
                          Using document context
                        </span>
                      )}
                    </p>
                  </div>
                  <ChatInterface 
                    messages={messages}
                    onAddMessage={addMessage}
                    isLoading={isLoading}
                    onLoadingChange={setIsLoading}
                    selectedDocumentId={selectedDocumentId}
                  />
                </div>
              </div>
            )}

            {activeTab === 'documents' && (
              <div className="lg:col-span-2">
                <DocumentList 
                  onDocumentSelect={handleDocumentSelect}
                  selectedDocumentId={selectedDocumentId}
                />
              </div>
            )}

            {activeTab === 'upload' && (
              <div className="lg:col-span-2">
                <DocumentUpload 
                  onUploadSuccess={handleDocumentUpload}
                />
              </div>
            )}

            {/* Sidebar */}
            <div className="lg:col-span-1">
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6">
                <h3 className="text-lg font-semibold mb-6 text-gray-900">Quick Actions</h3>
                <div className="space-y-3">
                  <Button 
                    onClick={() => setActiveTab('upload')}
                    className="w-full justify-start h-12 rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-lg hover:shadow-xl transition-all duration-200"
                  >
                    <Upload className="w-5 h-5 mr-3" />
                    Upload Document
                  </Button>
                  <Button 
                    onClick={() => setActiveTab('documents')}
                    className="w-full justify-start h-12 rounded-xl border-2 border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-200"
                    variant="outline"
                  >
                    <FileText className="w-5 h-5 mr-3" />
                    View Documents
                  </Button>
                  <Button 
                    onClick={() => setActiveTab('chat')}
                    className="w-full justify-start h-12 rounded-xl border-2 border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-200"
                    variant="outline"
                  >
                    <MessageSquare className="w-5 h-5 mr-3" />
                    Start Chat
                  </Button>
                </div>
                
                {selectedDocumentId && (
                  <div className="mt-8 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
                    <div className="flex items-center space-x-2 mb-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <h4 className="font-semibold text-blue-900">Active Document</h4>
                    </div>
                    <p className="text-sm text-blue-700 mb-4">
                      AI is currently using uploaded documents for context in responses.
                    </p>
                    <Button 
                      onClick={() => setSelectedDocumentId(null)}
                      className="w-full text-xs h-8 rounded-lg"
                      variant="outline"
                      size="sm"
                    >
                      Clear Selection
                    </Button>
                  </div>
                )}

                <div className="mt-8 p-4 bg-gray-50 rounded-xl">
                  <h4 className="font-semibold text-gray-900 mb-3">Features</h4>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                      <span>Multi-language support</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                      <span>Source citations</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                      <span>Document analysis</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                      <span>Real-time responses</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
