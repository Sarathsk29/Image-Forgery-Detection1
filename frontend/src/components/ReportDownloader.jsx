import React, { useState } from 'react';
import { Download, Loader2 } from 'lucide-react';
import { downloadReport } from '../utils/api';

const ReportDownloader = ({ resultData }) => {
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState(null);

  const handleDownload = async () => {
    setIsDownloading(true);
    setError(null);
    try {
      await downloadReport(resultData);
    } catch (err) {
      setError('Failed to generate PDF. Please try again.');
      console.error(err);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="w-full mt-6 flex flex-col items-center">
      {error && <p className="text-red-500 text-sm mb-2">{error}</p>}
      <button
        onClick={handleDownload}
        disabled={isDownloading}
        className="w-full sm:w-auto px-6 py-3 bg-navy-800 text-white font-medium rounded-lg hover:bg-navy-900 transition-colors shadow-md flex items-center justify-center space-x-2 disabled:opacity-75 disabled:cursor-not-allowed"
      >
        {isDownloading ? (
          <>
            <Loader2 size={20} className="animate-spin" />
            <span>Generating PDF Report...</span>
          </>
        ) : (
          <>
            <Download size={20} />
            <span>Download Forensic Report (PDF)</span>
          </>
        )}
      </button>
    </div>
  );
};

export default ReportDownloader;
