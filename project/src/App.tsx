import { useState, useEffect } from 'react';
import Header from './components/Header';
import WelcomeScreen from './components/WelcomeScreen';
import DocumentUpload from './components/DocumentUpload';
import ReportSection from './components/ReportSection';
import ChatSection from './components/ChatSection';
import { DocumentReport } from './types/api';
import { MessageCircle, X } from 'lucide-react';

type AppState = 'welcome' | 'upload' | 'results';

function App() {
  const [appState, setAppState] = useState<AppState>('welcome');
  const [report, setReport] = useState<DocumentReport | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // NEW: chat toggle state
  const [chatOpen, setChatOpen] = useState(false);

  useEffect(() => {
    const savedReport = localStorage.getItem('documentReport');
    const savedDocumentId = localStorage.getItem('documentId');

    if (savedReport && savedDocumentId) {
      setReport(JSON.parse(savedReport));
      setDocumentId(savedDocumentId);
      setAppState('results');
    }
  }, []);

  useEffect(() => {
    if (report && documentId) {
      localStorage.setItem('documentReport', JSON.stringify(report));
      localStorage.setItem('documentId', documentId);
    }
  }, [report, documentId]);

  const handleUploadSuccess = (reportData: DocumentReport, docId: string) => {
    setReport(reportData);
    setDocumentId(docId);
    setAppState('results');

    localStorage.setItem('documentReport', JSON.stringify(reportData));
    localStorage.setItem('documentId', docId);
  };

  const resetApp = () => {
    setReport(null);
    setDocumentId(null);
    setIsLoading(false);
    setAppState('welcome');
    setChatOpen(false);

    localStorage.removeItem('documentReport');
    localStorage.removeItem('documentId');
    localStorage.removeItem('chatMessages');
  };

  const handleGetStarted = () => {
    setAppState('upload');
  };

  const handleBackToWelcome = () => {
    setAppState('welcome');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50/30">
      <Header
        onBackHome={resetApp}
        onUploadNew={() => setAppState('upload')}
        showNav={appState === 'results' || appState === 'upload'}
      />

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
<div className="w-full px-6 py-8">
            {/* REPORT FULL WIDTH */}
            <ReportSection report={report} />

            {/* CHAT FLOATING PANEL */}
            {chatOpen && documentId && (
              <div className="fixed bottom-24 right-6 w-[500px] z-50 shadow-2xl">
                <ChatSection documentId={documentId} />
              </div>
            )}

            {/* CHAT TOGGLE BUTTON */}
            {documentId && (
              <button
                onClick={() => setChatOpen(!chatOpen)}
                className="fixed bottom-6 right-6 bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 rounded-full shadow-xl hover:scale-105 transition-all duration-200 z-50"
              >
                {chatOpen ? (
                  <X className="h-6 w-6" />
                ) : (
                  <MessageCircle className="h-6 w-6" />
                )}
              </button>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;