import React, { useState } from 'react';
import { Sparkles, Loader2, AlertCircle, Bot, Copy, CheckCircle2, ShieldAlert } from 'lucide-react';
import { explainWithAI } from '../utils/api';

const AIExplainer = ({ resultData, apiKey, provider }) => {
  const [explanation, setExplanation] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleExplain = async () => {
    if (!apiKey) {
      setError(`Please enter your ${provider} API Key in the settings panel.`);
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setExplanation('');
    setCopied(false);

    try {
      const result = await explainWithAI(resultData, apiKey, provider);
      setExplanation(result);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to fetch AI explanation. Please check your API key and connection.');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (!explanation) return;
    navigator.clipboard.writeText(explanation).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  // Function to highlight key forensic terms
  const highlightKeyPhrases = (text) => {
    if (!text) return null;
    
    // List of important forensic/manipulation terms to highlight
    const keywords = [
      'forgery', 'forged', 'manipulation', 'manipulated', 'tampered', 'tampering',
      'copy-move', 'splicing', 'clone', 'cloned', 'anomalies', 'anomaly',
      'inconsistent', 'inconsistencies', 'suspicious', 'authentic', 'unaltered',
      'high confidence', 'low confidence', 'error level analysis', 'sift'
    ];

    // Create a regex pattern dynamically
    const regex = new RegExp(`(${keywords.join('|')})`, 'gi');
    
    // Split and map to insert highlight spans
    const parts = text.split(regex);
    
    return parts.map((part, i) => {
      if (keywords.some(k => k.toLowerCase() === part.toLowerCase())) {
        return <mark key={i} className="bg-yellow-200 text-yellow-900 px-1 rounded font-medium">{part}</mark>;
      }
      return <span key={i}>{part}</span>;
    });
  };

  if (!apiKey) {
    return (
      <div className="card mt-6 bg-slate-50 border-slate-200 border-dashed text-center py-8">
        <Sparkles className="mx-auto h-8 w-8 text-slate-400 mb-3" />
        <h3 className="text-lg font-medium text-slate-700">AI Explanations Disabled</h3>
        <p className="text-sm text-slate-500 mt-1 max-w-sm mx-auto">
          Add your {provider} API key in the settings panel above to get an automated forensic analysis of these results.
        </p>
      </div>
    );
  }

  return (
    <div className="card mt-6 border-indigo-100 bg-gradient-to-br from-indigo-50/50 to-white relative overflow-hidden shadow-sm">
      <div className="absolute top-0 right-0 p-4 opacity-5">
        <Bot size={120} className="text-indigo-600" />
      </div>
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
          <h3 className="text-xl font-bold text-slate-800 flex items-center">
            <Bot className="text-indigo-600 mr-2" size={24} />
            Forensic AI Assistant
          </h3>
          <span className="text-xs font-medium bg-indigo-100 text-indigo-700 px-3 py-1.5 rounded-full border border-indigo-200 flex items-center shadow-sm">
            <Sparkles size={12} className="mr-1.5" />
            Analyzed by {provider}
          </span>
        </div>

        {!explanation && !isLoading && !error && (
          <button 
            onClick={handleExplain}
            className="w-full sm:w-auto px-5 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm flex items-center justify-center space-x-2"
          >
            <Sparkles size={18} />
            <span>Generate AI Forensic Report</span>
          </button>
        )}

        {isLoading && (
          <div className="flex flex-col items-center justify-center py-12 text-indigo-600 bg-white/50 rounded-xl border border-indigo-50">
            <Loader2 size={40} className="animate-spin mb-4" />
            <p className="text-sm font-medium animate-pulse text-indigo-700/80">Analyzing image metrics and generating expert explanation...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg flex items-start text-sm border border-red-200 mt-4 shadow-sm">
            <AlertCircle className="shrink-0 mr-3 mt-0.5" size={18} />
            <div className="flex-1">
              <strong className="block font-semibold mb-1">Analysis Failed</strong>
              <p>{error}</p>
            </div>
          </div>
        )}

        {explanation && (
          <div className="mt-4 opacity-100 transition-opacity duration-500">
            
            <div className="bg-white p-5 sm:p-6 rounded-xl border border-indigo-100 shadow-md relative group">
              {/* Copy Button */}
              <button 
                onClick={copyToClipboard}
                className="absolute top-4 right-4 p-2 bg-slate-50 hover:bg-indigo-50 text-slate-500 hover:text-indigo-600 rounded-lg border border-slate-200 hover:border-indigo-200 transition-all shadow-sm flex items-center justify-center"
                title="Copy to clipboard"
              >
                {copied ? <CheckCircle2 size={18} className="text-green-600" /> : <Copy size={18} />}
              </button>

              <div className="prose prose-sm sm:prose-base max-w-none prose-indigo text-slate-700 leading-relaxed pr-10 whitespace-pre-wrap">
                {highlightKeyPhrases(explanation)}
              </div>
            </div>

            {/* Legal Disclaimer */}
            <div className="mt-4 flex items-start p-3 bg-amber-50 rounded-lg border border-amber-200 text-amber-800 text-xs sm:text-sm">
              <ShieldAlert className="shrink-0 mr-2 mt-0.5 text-amber-600" size={16} />
              <p>
                <strong>Disclaimer:</strong> This AI explanation is for guidance and educational purposes only. 
                Do not use these automated findings as sole evidence in legal proceedings. Always consult a certified digital forensics expert for legal or official use.
              </p>
            </div>
            
          </div>
        )}
      </div>
    </div>
  );
};

export default AIExplainer;
