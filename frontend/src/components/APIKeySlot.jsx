import React, { useState } from 'react';
import { Settings, Key, ChevronDown, ChevronUp, Check } from 'lucide-react';

const APIKeySlot = ({ apiKey, setApiKey, aiProvider, setAiProvider, aiEnabled, setAiEnabled }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mb-6">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 bg-slate-50 hover:bg-slate-100 transition-colors"
      >
        <div className="flex items-center space-x-2 text-slate-700 font-medium">
          <Settings size={18} />
          <span>AI Explanation Settings</span>
        </div>
        {isOpen ? <ChevronUp size={18} className="text-slate-500" /> : <ChevronDown size={18} className="text-slate-500" />}
      </button>

      {isOpen && (
        <div className="p-4 border-t border-slate-200 space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-slate-700">Enable AI Explanation</label>
            <button 
              onClick={() => setAiEnabled(!aiEnabled)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${aiEnabled ? 'bg-blue-600' : 'bg-slate-300'}`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${aiEnabled ? 'translate-x-6' : 'translate-x-1'}`} />
            </button>
          </div>

          {aiEnabled && (
            <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">AI Provider</label>
                <select 
                  value={aiProvider}
                  onChange={(e) => setAiProvider(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                >
                  <option value="Claude">Anthropic Claude</option>
                  <option value="GPT-4">OpenAI GPT-4</option>
                  <option value="Gemini">Google Gemini</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">API Key</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Key size={16} className="text-slate-400" />
                  </div>
                  <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder={`Enter your ${aiProvider} API Key`}
                    className="w-full pl-10 pr-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  />
                  {apiKey && (
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                      <Check size={16} className="text-green-500" />
                    </div>
                  )}
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  Your key is never stored. Used only in your browser to analyze the forensic results.
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default APIKeySlot;
