import React, { useState, useEffect } from 'react';
import { FileText, Trash2, Search, Calendar, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';

interface Document {
  _id: string;
  document_id: string;
  filename: string;
  file_size: number;
  total_pages: number;
  extracted_pages: number;
  total_characters: number;
  uploaded_at: string;
  status: string;
}

interface DocumentListProps {
  onDocumentSelect?: (documentId: string) => void;
  selectedDocumentId?: string;
}

const DocumentList: React.FC<DocumentListProps> = ({ 
  onDocumentSelect, 
  selectedDocumentId 
}) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/documents/list');
      
      if (!response.ok) {
        throw new Error('Failed to fetch documents');
      }
      
      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  const deleteDocument = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/documents/${documentId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete document');
      }
      
      setDocuments(prev => prev.filter(doc => doc.document_id !== documentId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete document');
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-blue-200 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Loading Documents</h3>
          <p className="text-gray-600">Please wait while we fetch your documents...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-red-100 to-red-200 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <AlertCircle className="w-8 h-8 text-red-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Documents</h3>
          <p className="text-red-600 mb-6">{error}</p>
          <Button 
            onClick={fetchDocuments} 
            className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-xl px-6 py-2"
          >
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8">
        <div className="text-center">
          <div className="w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <FileText className="w-10 h-10 text-gray-400" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">No Documents Yet</h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Upload your first PDF document to get started with intelligent document-based Q&A.
          </p>
          <div className="flex flex-wrap justify-center gap-2 text-sm text-gray-500">
            <span className="bg-gray-100 px-3 py-1 rounded-full">PDF support</span>
            <span className="bg-gray-100 px-3 py-1 rounded-full">AI analysis</span>
            <span className="bg-gray-100 px-3 py-1 rounded-full">Source citations</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
            <FileText className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">Your Documents</h3>
            <p className="text-sm text-gray-600">Manage and select documents for AI analysis</p>
          </div>
        </div>
        <Button 
          onClick={fetchDocuments} 
          variant="outline" 
          size="sm"
          className="rounded-xl border-gray-200 hover:border-blue-300 hover:bg-blue-50"
        >
          Refresh
        </Button>
      </div>
      
      <div className="space-y-4">
        {documents.map((doc) => (
          <Card 
            key={doc.document_id} 
            className={`p-5 cursor-pointer transition-all duration-200 rounded-xl border-2 ${
              selectedDocumentId === doc.document_id 
                ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50 shadow-lg' 
                : 'border-gray-200 hover:border-blue-300 hover:shadow-md'
            }`}
            onClick={() => onDocumentSelect?.(doc.document_id)}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4 flex-1">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                  selectedDocumentId === doc.document_id 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  <FileText className="w-6 h-6" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-gray-900 truncate text-lg">
                    {doc.filename}
                  </h4>
                  <div className="flex items-center space-x-6 text-sm text-gray-600 mt-2">
                    <span className="flex items-center space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                      <span>{formatFileSize(doc.file_size)}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                      <span>{doc.extracted_pages} pages</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                      <span>{doc.total_characters.toLocaleString()} chars</span>
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 text-xs text-gray-500 mt-3">
                    <Calendar className="w-4 h-4" />
                    <span>{formatDate(doc.uploaded_at)}</span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <span className={`text-xs px-3 py-1 rounded-full font-medium ${
                  doc.status === 'processed' 
                    ? 'bg-green-100 text-green-700 border border-green-200' 
                    : 'bg-yellow-100 text-yellow-700 border border-yellow-200'
                }`}>
                  {doc.status}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteDocument(doc.document_id);
                  }}
                  className="text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default DocumentList;
