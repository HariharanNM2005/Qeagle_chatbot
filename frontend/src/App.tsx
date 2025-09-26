import { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import Header from './components/Header'
import DocumentUpload from './components/DocumentUpload'
import DocumentList from './components/DocumentList'
import { Message } from './types/chat'
import { FileText, MessageSquare } from 'lucide-react'
// import { Button } from './components/ui/button'

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
      role: 'assistant',
      timestamp: new Date()
    })
  }

  const handleDocumentSelect = (documentId: string) => {
    setSelectedDocumentId(documentId)
    setActiveTab('chat')
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/50">
      {/* Sidebar - hidden on mobile, visible on xl screens; fixed height, no scroll */}
      <aside className="hidden xl:flex xl:flex-col xl:w-80 h-screen flex-shrink-0 p-6 bg-white/80 backdrop-blur-sm rounded-none xl:rounded-r-2xl shadow-xl border-r border-white/20">
        <h3 className="text-lg font-semibold mb-6 text-gray-900">AI Features</h3>
        <div className="space-y-6">
          <div className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border border-blue-200">
            <div className="flex items-center space-x-4 mb-4">
              <div className="w-12 h-12 bg-blue-500 rounded-2xl flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-white" />
              </div>
              <div>
                <h4 className="text-lg font-bold text-blue-900">Multi-Language Support</h4>
                <p className="text-sm text-blue-700">Tamil, Hindi, English</p>
              </div>
            </div>
            <p className="text-sm text-blue-700 mb-4 leading-relaxed">
              Chat in Tamil, Hindi, or English. The AI understands and responds in your preferred language with accurate translations.
            </p>
            <div className="flex flex-wrap gap-2">
              <span className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium">தமிழ்</span>
              <span className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium">हिन्दी</span>
              <span className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium">English</span>
            </div>
          </div>

          <div className="p-6 bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl border border-green-200">
            <div className="flex items-center space-x-4 mb-4">
              <div className="w-12 h-12 bg-green-500 rounded-2xl flex items-center justify-center">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <div>
                <h4 className="text-lg font-bold text-green-900">Document Analysis</h4>
                <p className="text-sm text-green-700">PDF processing & Q&A</p>
              </div>
            </div>
            <p className="text-sm text-green-700 mb-4 leading-relaxed">
              Upload PDF documents and ask questions. Get accurate answers with source citations and page references.
            </p>
            <div className="flex flex-wrap gap-2">
              <span className="text-sm bg-green-100 text-green-700 px-3 py-1 rounded-full font-medium">PDF Upload</span>
              <span className="text-sm bg-green-100 text-green-700 px-3 py-1 rounded-full font-medium">Source Citations</span>
              <span className="text-sm bg-green-100 text-green-700 px-3 py-1 rounded-full font-medium">Page References</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content - fills remaining width; header sticky, body fills height */}
      <main className="flex-1 flex flex-col h-screen px-2 sm:px-4">
        {/* Sticky Header inside main */}
        <div className="sticky top-0 z-20 bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/50/80 backdrop-blur supports-[backdrop-filter]:bg-white/60 border-b border-white/20 px-2 sm:px-4 py-4">
          <Header 
            onClear={clearMessages} 
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />
        </div>

        {/* Content grows to fill remaining height; prevent extra scroll */}
        <div className="flex-1 py-4 sm:py-8 overflow-hidden min-h-0">
          {/* Tab Content */}
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 h-full min-h-0">
            {activeTab === 'chat' && (
              <div className="xl:col-span-3 h-full min-h-0">
                <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 h-full min-h-0 flex flex-col">
                  <ChatInterface 
                    messages={messages}
                    onAddMessage={addMessage}
                    isLoading={isLoading}
                    onLoadingChange={setIsLoading}
                    selectedDocumentId={selectedDocumentId || undefined}
                  />
                </div>
              </div>
            )}

            {activeTab === 'documents' && (
              <div className="xl:col-span-3 h-full">
                <DocumentList 
                  onDocumentSelect={handleDocumentSelect}
                  selectedDocumentId={selectedDocumentId || undefined}
                />
              </div>
            )}

            {activeTab === 'upload' && (
              <div className="xl:col-span-3 h-full">
                <DocumentUpload 
                  onUploadSuccess={handleDocumentUpload}
                />
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default App




