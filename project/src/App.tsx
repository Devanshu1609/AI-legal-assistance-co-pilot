import React, { useState } from 'react';
import Header from './components/Header';
import WelcomeScreen from './components/WelcomeScreen';
import DocumentUpload from './components/DocumentUpload';
import ReportSection from './components/ReportSection';
import ChatSection from './components/ChatSection';
import { DocumentReport } from './types/api';

type AppState = 'welcome' | 'upload' | 'results';
function App() {
  const [appState, setAppState] = useState<AppState>('welcome');
  const [report, setReport] = useState<DocumentReport | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleUploadSuccess = (reportData: DocumentReport, docId: string) => {
    setReport(reportData);
    setDocumentId(docId);
    setAppState('results');
  };

  const resetApp = () => {
    setReport(null);
    setDocumentId(null);
    setIsLoading(false);
    setAppState('welcome');
  };

  const handleGetStarted = () => {
    setAppState('upload');
  };

  const handleBackToWelcome = () => {
    setAppState('welcome');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50/30">
      <Header />
      
      <main>
        {appState === 'welcome' && (
          <WelcomeScreen onGetStarted={handleGetStarted} />
        )}
        
        {appState === 'upload' && (
          <DocumentUpload
            onUploadSuccess={handleUploadSuccess}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
            onBack={handleBackToWelcome}
          />
        )}
        
        {appState === 'results' && report && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
              <button
                onClick={resetApp}
                className="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-2xl hover:from-gray-700 hover:to-gray-800 transition-all duration-200 font-medium shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Upload New Document
              </button>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-12">
              <div className="lg:col-span-3">
                <ReportSection report={report} />
              </div>
              
              <div className="lg:col-span-2" >
                {documentId && <ChatSection documentId={documentId} />}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;