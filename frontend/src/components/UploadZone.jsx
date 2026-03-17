import React, { useCallback, useState, useEffect } from 'react';
import { UploadCloud, File, FileText, Image as ImageIcon, X, Loader2 } from 'lucide-react';

const UploadZone = ({ onFileSelect, onAnalyze, isAnalyzing, file }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    
    if (file.type.startsWith('image/')) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      return () => URL.revokeObjectURL(url);
    } else if (file.type === 'application/pdf') {
      setPreviewUrl('pdf'); // Special marker for PDF
    }
  }, [file]);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      validateAndFormatFile(droppedFile);
    }
  }, [onFileSelect]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndFormatFile(e.target.files[0]);
    }
  };

  const validateAndFormatFile = (selectedFile) => {
    const validTypes = ['image/jpeg', 'image/png', 'application/pdf'];
    if (validTypes.includes(selectedFile.type)) {
      onFileSelect(selectedFile);
    } else {
      alert('Please upload a JPG, PNG, or PDF file.');
    }
  };

  const removeFile = (e) => {
    e.stopPropagation();
    onFileSelect(null);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="card w-full">
      <h2 className="text-xl font-bold text-slate-800 mb-4">Inspection Subject</h2>
      
      {!file ? (
        <div
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
            isDragging ? 'border-blue-500 bg-blue-50' : 'border-slate-300 hover:border-slate-400 bg-slate-50'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-upload').click()}
        >
          <input
            id="file-upload"
            type="file"
            className="hidden"
            accept=".jpg,.jpeg,.png,.pdf"
            onChange={handleFileChange}
          />
          <div className="flex flex-col items-center justify-center cursor-pointer">
            <UploadCloud size={48} className="text-slate-400 mb-4" />
            <p className="text-slate-700 font-medium text-lg mb-1">Click to upload or drag and drop</p>
            <p className="text-slate-500 text-sm">JPG, PNG, or PDF (First page only)</p>
          </div>
        </div>
      ) : (
        <div className="border border-slate-200 rounded-xl p-4 bg-slate-50 relative">
          <button 
            onClick={removeFile}
            className="absolute top-2 right-2 p-1 bg-white rounded-full text-slate-400 hover:text-red-500 shadow-sm transition-colors z-10"
            disabled={isAnalyzing}
          >
            <X size={16} />
          </button>
          
          <div className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-6">
            <div className="w-32 h-32 rounded-lg bg-white shadow-sm flex items-center justify-center overflow-hidden border border-slate-200 shrink-0">
              {previewUrl === 'pdf' ? (
                <FileText size={48} className="text-red-500" />
              ) : previewUrl ? (
                <img src={previewUrl} alt="Preview" className="w-full h-full object-cover" />
              ) : (
                <ImageIcon size={48} className="text-slate-400" />
              )}
            </div>
            
            <div className="flex-1 text-center sm:text-left">
              <h3 className="font-semibold text-slate-800 truncate max-w-[200px] sm:max-w-[400px]">{file.name}</h3>
              <p className="text-slate-500 text-sm mb-4">{formatFileSize(file.size)}</p>
              
              <button
                onClick={onAnalyze}
                disabled={isAnalyzing}
                className="btn-primary w-full sm:w-auto flex items-center justify-center space-x-2"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    <span>Analyzing Image...</span>
                  </>
                ) : (
                  <>
                    <UploadCloud size={18} />
                    <span>Analyse Image</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadZone;
