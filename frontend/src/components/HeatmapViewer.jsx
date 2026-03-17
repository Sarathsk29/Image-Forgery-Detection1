import React, { useState } from 'react';

const HeatmapViewer = ({ originalImage, heatmapImage }) => {
  const [opacity, setOpacity] = useState(50); // 0 to 100

  // We assume images are passed as correctly formatted data URIs
  // from the backend (e.g., 'data:image/jpeg;base64,...')
  // Original is either the base64 or a blob URL object. Let's assume standard base64 from backend or Object URL.

  return (
    <div className="flex flex-col space-y-4 w-full h-full">
      <div className="flex justify-between items-center text-sm">
        <span className="font-semibold text-slate-700">Heatmap Overlay</span>
        <span className="text-red-500 font-medium">Red = High Suspicion Areas</span>
      </div>
      
      <div className="relative w-full aspect-video bg-slate-100 rounded-lg overflow-hidden border border-slate-200">
        <img 
          src={originalImage} 
          alt="Original" 
          className="absolute inset-0 w-full h-full object-contain"
        />
        {heatmapImage && (
          <img 
            src={heatmapImage} 
            alt="Heatmap" 
            className="absolute inset-0 w-full h-full object-contain mix-blend-multiply pointer-events-none transition-opacity duration-200"
            style={{ opacity: opacity / 100 }}
          />
        )}
      </div>

      <div className="flex items-center space-x-4">
        <span className="text-sm text-slate-500 w-24">Opacity: {opacity}%</span>
        <input 
          type="range" 
          min="0" 
          max="100" 
          value={opacity} 
          onChange={(e) => setOpacity(parseInt(e.target.value))}
          className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
        />
      </div>
    </div>
  );
};

export default HeatmapViewer;
