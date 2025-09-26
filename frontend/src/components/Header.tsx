import React from 'react'
import { Button } from './ui/button'
import { Trash2, Zap, Sparkles, MessageSquare, FileText, Upload } from 'lucide-react'

type TabType = 'chat' | 'documents' | 'upload'

interface HeaderProps {
  onClear: () => void
  activeTab: TabType
  onTabChange: (tab: TabType) => void
}

const Header: React.FC<HeaderProps> = ({ onClear, activeTab, onTabChange }) => {
  return (
    <header className="bg-white/90 backdrop-blur-sm shadow-lg border-b border-gray-200/50 sticky top-0 z-50">
      <div className="container mx-auto px-4 sm:px-6 py-4">
        <div className="flex flex-col space-y-4 lg:flex-row lg:items-center lg:justify-between lg:space-y-0">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl shadow-lg">
                <Sparkles className="w-5 h-5 sm:w-7 sm:h-7 text-white" />
              </div>
              <div>
                <h1 className="text-xl sm:text-2xl font-bold text-gray-900">AI Assistant</h1>
                <p className="text-xs sm:text-sm text-gray-600 hidden sm:block">Intelligent document analysis & chat</p>
              </div>
            </div>
          </div>
          
          {/* Tab Navigation - Responsive */}
          <nav className="flex space-x-1 bg-gray-100 rounded-xl p-1 w-full lg:w-auto">
            <button
              onClick={() => onTabChange('chat')}
              className={`flex items-center justify-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all duration-200 flex-1 sm:flex-none ${
                activeTab === 'chat'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <MessageSquare className="w-3 h-3 sm:w-4 sm:h-4" />
              <span className="hidden sm:inline">Chat</span>
            </button>
            <button
              onClick={() => onTabChange('documents')}
              className={`flex items-center justify-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all duration-200 flex-1 sm:flex-none ${
                activeTab === 'documents'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <FileText className="w-3 h-3 sm:w-4 sm:h-4" />
              <span className="hidden sm:inline">Documents</span>
            </button>
            <button
              onClick={() => onTabChange('upload')}
              className={`flex items-center justify-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all duration-200 flex-1 sm:flex-none ${
                activeTab === 'upload'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <Upload className="w-3 h-3 sm:w-4 sm:h-4" />
              <span className="hidden sm:inline">Upload</span>
            </button>
          </nav>
          
          <div className="flex items-center justify-between lg:justify-end space-x-2 sm:space-x-4">
            <div className="flex items-center space-x-2 sm:space-x-3 px-2 sm:px-4 py-2 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <Zap className="w-3 h-3 sm:w-4 sm:h-4 text-green-600" />
              <span className="text-xs sm:text-sm font-medium text-green-700 hidden sm:inline">AI Online</span>
            </div>
            
            <Button
              variant="outline"
              size="sm"
              onClick={onClear}
              className="flex items-center space-x-1 sm:space-x-2 h-8 sm:h-10 px-2 sm:px-4 rounded-xl border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300 transition-all duration-200"
            >
              <Trash2 className="w-3 h-3 sm:w-4 sm:h-4" />
              <span className="text-xs sm:text-sm">Clear</span>
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
