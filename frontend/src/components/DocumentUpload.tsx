import React, { useState, useRef } from 'react';
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';

interface DocumentUploadProps {
  onUploadSuccess?: (documentId: string) => void;
  onUploadError?: (error: string) => void;
}

interface UploadedDocument {
  document_id: string;
  filename: string;
  status: string;
  message: string;
  chunks_created: number;
  processing_time_ms: number;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ 
  onUploadSuccess, 
  onUploadError 
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedDocuments, setUploadedDocuments] = useState<UploadedDocument[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    
    const file = files[0];
    if (file.type !== 'application/pdf') {
      onUploadError?.('Please select a PDF file');
      return;
    }
    
    uploadFile(file);
  };

  const uploadFile = async (file: File) => {
    setIsUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('/api/v1/documents/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }
      
      const result: UploadedDocument = await response.json();
      setUploadedDocuments(prev => [result, ...prev]);
      onUploadSuccess?.(result.document_id);
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      onUploadError?.(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files);
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <FileText className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-3">Upload PDF Documents</h3>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Upload PDF files to enable intelligent document-based Q&A. The AI will analyze your documents and provide accurate answers based on their content with source citations.
          </p>
        </div>

        {/* Upload Area */}
        <div
          className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-200 ${
            dragActive
              ? 'border-blue-500 bg-gradient-to-br from-blue-50 to-indigo-50 shadow-lg'
              : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          } ${isUploading ? 'opacity-50 pointer-events-none' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Upload className="w-10 h-10 text-gray-500" />
          </div>
          <h4 className="text-lg font-semibold text-gray-900 mb-2">
            {isUploading ? 'Processing your document...' : 'Drop your PDF here'}
          </h4>
          <p className="text-gray-600 mb-6">
            {isUploading 
              ? 'Please wait while we analyze your document' 
              : 'Drag and drop your PDF file here, or click to browse'
            }
          </p>
          <Button
            onClick={openFileDialog}
            disabled={isUploading}
            className={`h-12 px-8 rounded-xl font-medium ${
              isUploading 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700'
            } text-white shadow-lg hover:shadow-xl transition-all duration-200`}
          >
            {isUploading ? (
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Processing...</span>
              </div>
            ) : (
              'Choose File'
            )}
          </Button>
          <p className="text-sm text-gray-500 mt-4">
            Maximum file size: 10MB • Supported format: PDF
          </p>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={(e) => handleFileSelect(e.target.files)}
          className="hidden"
        />

        {/* Uploaded Documents List */}
        {uploadedDocuments.length > 0 && (
          <div className="mt-8">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
              <h4 className="text-lg font-semibold text-gray-900">Uploaded Documents</h4>
            </div>
            <div className="space-y-4">
              {uploadedDocuments.map((doc, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-5 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200"
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center">
                      <CheckCircle className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{doc.filename}</p>
                      <p className="text-sm text-gray-600">
                        {doc.chunks_created} chunks created • 
                        {(doc.processing_time_ms / 1000).toFixed(1)}s processing time
                      </p>
                    </div>
                  </div>
                  <span className="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full font-medium border border-green-200">
                    {doc.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentUpload;
