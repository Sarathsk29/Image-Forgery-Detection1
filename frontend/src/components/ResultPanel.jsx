import React, { useState } from 'react';
import { Target, AlertTriangle, ShieldCheck, Activity, Layers } from 'lucide-react';
import HeatmapViewer from './HeatmapViewer';
import ReportDownloader from './ReportDownloader';

const ResultPanel = ({ result }) => {
  const [activeTab, setActiveTab] = useState('heatmap');
  
  if (!result) return null;

  const isForged = result.is_forged;
  // Fallbacks in case backend response keys vary slightly
  const confidence = result.confidence_score || result.confidence || 0;
  const matchCount = result.sift_matches || 0;
  const elaScore = (result.ela_score || 0).toFixed(2);
  const methodUsed = result.method_used || result.method || 'SIFT + ELA';

  const originalImage = `data:image/jpeg;base64,${result.original_image_base64 || result.original_image}`;
  const analyzedImage = `data:image/jpeg;base64,${result.analyzed_image_base64 || result.analyzed_image}`;
  const elaImage = `data:image/jpeg;base64,${result.ela_image_base64 || result.ela_image}`;
  const heatmapImage = result.heatmap_base64 || result.heatmap ? `data:image/jpeg;base64,${result.heatmap_base64 || result.heatmap}` : analyzedImage;

  const tabs = [
    { id: 'original', label: 'Original' },
    { id: 'annotated', label: 'Annotated View' },
    { id: 'ela', label: 'ELA View' },
    { id: 'heatmap', label: 'Heatmap' },
  ];

  return (
    <div className="card w-full mt-6 bg-white shadow-lg overflow-hidden border-t-4 p-0 md:p-0" style={{ borderTopColor: isForged ? '#ef4444' : '#22c55e' }}>
      
      {/* Verdict Header */}
      <div className={`px-6 py-8 border-b border-slate-200 flex flex-col md:flex-row items-center justify-between ${isForged ? 'bg-red-50/40' : 'bg-green-50/40'}`}>
        <div className="flex items-center space-x-5 text-center md:text-left mb-4 md:mb-0">
          <div className={`p-4 rounded-full flex-shrink-0 mx-auto md:mx-0 shadow-sm ${isForged ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600'}`}>
            {isForged ? <AlertTriangle size={36} /> : <ShieldCheck size={36} />}
          </div>
          <div>
            <h2 className={`text-3xl font-extrabold tracking-tight uppercase ${isForged ? 'text-red-700' : 'text-green-700'}`}>
              {isForged ? 'FORGED' : 'AUTHENTIC'}
            </h2>
            <p className={`font-medium mt-1 ${isForged ? 'text-red-600/80' : 'text-green-600/80'}`}>Digital forensic analysis complete</p>
          </div>
        </div>
        
        <div className="w-full md:w-72 bg-white p-4 rounded-xl shadow-sm border border-slate-200">
          <div className="flex justify-between text-sm mb-2 font-bold text-slate-700">
            <span>Confidence Score</span>
            <span className={isForged ? 'text-red-600' : 'text-green-600'}>{Math.round(confidence * 100)}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden shadow-inner">
            <div className={`h-3 rounded-full transition-all duration-1000 ease-out ${isForged ? 'bg-red-500' : 'bg-green-500'}`} style={{ width: `${Math.round(confidence * 100)}%` }}></div>
          </div>
        </div>
      </div>

      <div className="p-6 md:p-8">
        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">
          <div className="bg-slate-50 p-5 rounded-xl border border-slate-200 flex items-center space-x-4 shadow-sm">
            <div className="bg-blue-100 p-3 rounded-lg text-blue-600">
              <Target size={24} />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-1">Keypoints Matched</p>
              <p className="text-2xl font-black text-slate-800">{matchCount}</p>
            </div>
          </div>
          <div className="bg-slate-50 p-5 rounded-xl border border-slate-200 flex items-center space-x-4 shadow-sm">
            <div className="bg-purple-100 p-3 rounded-lg text-purple-600">
              <Activity size={24} />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-1">ELA Score</p>
              <p className="text-2xl font-black text-slate-800">{elaScore}</p>
            </div>
          </div>
          <div className="bg-slate-50 p-5 rounded-xl border border-slate-200 flex items-center space-x-4 shadow-sm">
            <div className="bg-amber-100 p-3 rounded-lg text-amber-600">
              <Layers size={24} />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-1">Method Used</p>
              <p className="text-base font-extrabold text-slate-800">{methodUsed}</p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-slate-200 mb-6 flex justify-center md:justify-start">
          <nav className="-mb-px flex space-x-2 md:space-x-6 overflow-x-auto pb-1 max-w-full">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`whitespace-nowrap py-3 px-3 md:px-4 border-b-2 font-semibold text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-700'
                    : 'border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="bg-slate-50 rounded-xl p-3 md:p-5 border border-slate-200 shadow-inner w-full flex items-center justify-center overflow-hidden min-h-[300px] md:min-h-[500px]">
          {activeTab === 'original' && (
            <img src={originalImage} alt="Original uploaded file" className="max-h-[500px] max-w-full object-contain rounded-lg shadow-sm" />
          )}
          {activeTab === 'annotated' && (
            <img src={analyzedImage} alt="Annotated detection output" className="max-h-[500px] max-w-full object-contain rounded-lg shadow-sm" />
          )}
          {activeTab === 'ela' && (
            <img src={elaImage} alt="Error Level Analysis output" className="max-h-[500px] max-w-full object-contain rounded-lg shadow-sm" />
          )}
          {activeTab === 'heatmap' && (
            <HeatmapViewer originalImage={originalImage} heatmapImage={heatmapImage} />
          )}
        </div>

        <ReportDownloader resultData={result} />
      </div>
    </div>
  );
};

export default ResultPanel;
