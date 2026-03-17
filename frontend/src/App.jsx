import React, { useState } from 'react';
import { Shield, Fingerprint } from 'lucide-react';
import UploadZone from './components/UploadZone';
import ResultPanel from './components/ResultPanel';
import AIExplainer from './components/AIExplainer';
import APIKeySlot from './components/APIKeySlot';
import { detectForgery } from './utils/api';

function App() {
  const [file, setFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // AI settings state
  const [apiKey, setApiKey] = useState('');
  const [aiProvider, setAiProvider] = useState('Claude');
  const [aiEnabled, setAiEnabled] = useState(false);

  const handleAnalyze = async () => {
    if (!file) return;
    
    setIsAnalyzing(true);
    setError(null);
    setResult(null);

    try {
      const data = await detectForgery(file);
      setResult(data);
    } catch (err) {
      console.error(err);
      setError(err.message || 'An error occurred during verification.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleFileSelect = (newFile) => {
    setFile(newFile);
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-20 font-sans">
      {/* Header Section */}
      <header className="bg-navy-900 text-white shadow-lg relative overflow-hidden border-b-4 border-blue-600">
        <div className="absolute inset-0 opacity-10 pointer-events-none" 
             style={{ backgroundImage: 'radial-gradient(#4f46e5 1.5px, transparent 1.5px)', backgroundSize: '24px 24px' }}>
        </div>
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 relative z-10 text-center md:text-left flex flex-col md:flex-row items-center justify-between">
          <div className="flex flex-col items-center md:items-start">
            <div className="flex items-center space-x-3 mb-3 text-blue-400">
              <Fingerprint size={36} strokeWidth={1.5} />
              <Shield size={36} strokeWidth={1.5} />
            </div>
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-black tracking-tight text-white mb-2">
              Image Forgery Detector
            </h1>
            <h2 className="text-lg md:text-xl text-blue-200 font-medium tracking-wide">SIFT Algorithm + ELA Analysis for Digital Authentication</h2>
            
            <div className="mt-5 inline-flex items-center px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-500/30 backdrop-blur-sm">
              MCA Final Year Project
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 mt-2">
        
        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 font-medium shadow-sm flex items-start animate-in fade-in slide-in-from-top-4">
             <Shield className="text-red-500 mr-3 mt-0.5 shrink-0" size={20} />
             <span>{error}</span>
          </div>
        )}

        <APIKeySlot 
          apiKey={apiKey} 
          setApiKey={setApiKey}
          aiProvider={aiProvider}
          setAiProvider={setAiProvider}
          aiEnabled={aiEnabled}
          setAiEnabled={setAiEnabled}
        />

        <UploadZone 
          file={file} 
          onFileSelect={handleFileSelect}
          onAnalyze={handleAnalyze} 
          isAnalyzing={isAnalyzing} 
        />

        {/* Results Flow */}
        {result && (
          <div className="animate-in slide-in-from-bottom-8 duration-700 ease-out pb-10">
            <ResultPanel result={result} />
            
            {aiEnabled && (
              <AIExplainer 
                resultData={result} 
                apiKey={apiKey} 
                provider={aiProvider} 
              />
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
