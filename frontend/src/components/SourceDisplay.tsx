import React, { useState } from 'react'
import { Citation } from '../types/chat'
import { FileText, ExternalLink, ChevronDown, ChevronUp, BookOpen, File } from 'lucide-react'
import { Card } from './ui/card'
import { Button } from './ui/button'

interface SourceDisplayProps {
  citations: Citation[]
  className?: string
}

const SourceDisplay: React.FC<SourceDisplayProps> = ({ citations, className = '' }) => {
  const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set())
  const [showAll, setShowAll] = useState(false)

  if (!citations || citations.length === 0) {
    return null
  }

  const visibleCitations = showAll ? citations : citations.slice(0, 3)
  const hasMore = citations.length > 3

  const toggleSource = (sourceId: string) => {
    const newExpanded = new Set(expandedSources)
    if (newExpanded.has(sourceId)) {
      newExpanded.delete(sourceId)
    } else {
      newExpanded.add(sourceId)
    }
    setExpandedSources(newExpanded)
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-50'
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'High'
    if (confidence >= 0.6) return 'Medium'
    return 'Low'
  }

  return (
    <div className={`mt-4 ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <BookOpen className="w-4 h-4 text-blue-600" />
          <h4 className="text-sm font-semibold text-gray-700">Sources</h4>
          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
            {citations.length}
          </span>
        </div>
        {hasMore && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowAll(!showAll)}
            className="text-xs text-blue-600 hover:text-blue-700"
          >
            {showAll ? 'Show Less' : `Show All ${citations.length}`}
            {showAll ? <ChevronUp className="w-3 h-3 ml-1" /> : <ChevronDown className="w-3 h-3 ml-1" />}
          </Button>
        )}
      </div>

      <div className="space-y-2">
        {visibleCitations.map((citation, index) => {
          const isExpanded = expandedSources.has(citation.source_id)
          const confidence = citation.confidence || citation.score || 0
          
          return (
            <Card key={citation.source_id} className="p-3 border-l-4 border-l-blue-200 hover:border-l-blue-400 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-2">
                    <FileText className="w-4 h-4 text-gray-500 flex-shrink-0" />
                    <h5 className="text-sm font-medium text-gray-900 truncate">
                      {citation.title || citation.filename || 'Unknown Document'}
                    </h5>
                    {citation.page_number && (
                      <div className="flex items-center space-x-1 text-xs text-gray-500">
                        <File className="w-3 h-3" />
                        <span>Page {citation.page_number}</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2 mb-2">
                    <span className={`text-xs px-2 py-1 rounded-full ${getConfidenceColor(confidence)}`}>
                      {getConfidenceLabel(confidence)} Relevance
                    </span>
                    <span className="text-xs text-gray-500">
                      {(confidence * 100).toFixed(1)}%
                    </span>
                  </div>

                  {isExpanded && (
                    <div className="mt-2 p-2 bg-gray-50 rounded text-xs text-gray-700">
                      <p className="whitespace-pre-wrap">{citation.content}</p>
                    </div>
                  )}
                </div>

                <div className="flex items-center space-x-1 ml-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleSource(citation.source_id)}
                    className="h-6 w-6 p-0 text-gray-400 hover:text-gray-600"
                  >
                    {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0 text-gray-400 hover:text-gray-600"
                    title="View full source"
                  >
                    <ExternalLink className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            </Card>
          )
        })}
      </div>

      {citations.length > 0 && (
        <div className="mt-3 text-xs text-gray-500 text-center">
          Sources are ranked by relevance to your question
        </div>
      )}
    </div>
  )
}

export default SourceDisplay
