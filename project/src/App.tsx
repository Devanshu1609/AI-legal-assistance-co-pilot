import { useState, useEffect } from 'react';
import Navbar from './components/navbar';
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
  const [chatOpen, setChatOpen] = useState(false);

  // Load saved data
  useEffect(() => {
    const savedReport = localStorage.getItem('documentReport');
    const savedDocumentId = localStorage.getItem('documentId');

    if (savedReport && savedDocumentId) {
      setReport(JSON.parse(savedReport));
      setDocumentId(savedDocumentId);
      setAppState('results');
    }
  }, []);

  // Save data
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
    <div className="min-h-screen bg-[#0a0e1a] text-white">

      {/* NAVBAR (always visible) */}
      <Navbar
        currentPage={appState}
        onNavigate={(page) => setAppState(page)}
        hasResults={!!report}
      />

      <main>

        {/* WELCOME */}
        {appState === 'welcome' && (
          <WelcomeScreen onGetStarted={handleGetStarted} />
        )}

        {/* UPLOAD */}
        {appState === 'upload' && (
          <DocumentUpload
            onUploadSuccess={handleUploadSuccess}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
            onBack={handleBackToWelcome}
          />
        )}

        {/* RESULTS */}
        {appState === 'results' && report && (
          <div className="w-full px-6 py-8">

            {/* REPORT */}
            <ReportSection report={report} />

            {/* CHAT PANEL */}
            {chatOpen && documentId && (
              <div className="fixed bottom-24 right-6 w-[420px] z-50 shadow-2xl">
                <ChatSection documentId={documentId} />
              </div>
            )}

            {/* CHAT BUTTON */}
            {documentId && (
              <button
                onClick={() => setChatOpen(!chatOpen)}
                className="fixed bottom-6 right-6 
                bg-[#0f172a] hover:bg-[#111827] 
                border border-blue-500/30 
                text-blue-400 
                p-4 rounded-full 
                shadow-lg shadow-blue-500/20 
                transition-all duration-200 hover:scale-105 z-50"
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
