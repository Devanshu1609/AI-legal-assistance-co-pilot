import { useState, useEffect } from "react";
import Navbar from "./components/navbar";
import WelcomeScreen from "./components/WelcomeScreen";
import DocumentUpload from "./components/DocumentUpload";
import ReportSection from "./components/ReportSection";
import ChatSection from "./components/ChatSection";
import Login from "./components/login";

import { DocumentReport } from "./types/api";
import { MessageCircle, X } from "lucide-react";

import { auth } from "./firebase";
import {
  onAuthStateChanged,
  signOut,
  User,
} from "firebase/auth";

type AppState =
  | "welcome"
  | "upload"
  | "results"
  | "chat";

function App() {
  const [appState, setAppState] =
    useState<AppState>("welcome");

  const [report, setReport] =
    useState<DocumentReport | null>(
      null
    );

  const [documentId, setDocumentId] =
    useState<string | null>(null);

  const [isLoading, setIsLoading] =
    useState(false);

  const [chatOpen, setChatOpen] =
    useState(false);

  const [user, setUser] =
    useState<User | null>(null);

  const [authLoading, setAuthLoading] =
    useState(true);

  // Listen auth state
  useEffect(() => {
    const unsubscribe =
      onAuthStateChanged(
        auth,
        (currentUser) => {
          setUser(currentUser);
          setAuthLoading(false);
        }
      );

    return () => unsubscribe();
  }, []);

  // Restore saved report + document + page
  useEffect(() => {
    if (!user) return;

    const savedReport =
      localStorage.getItem(
        "documentReport"
      );

    const savedDocumentId =
      localStorage.getItem(
        "documentId"
      );

    const savedPage =
      localStorage.getItem(
        "currentPage"
      );

    if (
      savedReport &&
      savedDocumentId
    ) {
      setReport(
        JSON.parse(savedReport)
      );

      setDocumentId(
        savedDocumentId
      );

      if (
        savedPage === "welcome" ||
        savedPage === "upload" ||
        savedPage === "results" ||
        savedPage === "chat"
      ) {
        setAppState(
          savedPage as AppState
        );
      } else {
        setAppState("results");
      }
    }
  }, [user]);

  // Save report + document
  useEffect(() => {
    if (report && documentId) {
      localStorage.setItem(
        "documentReport",
        JSON.stringify(report)
      );

      localStorage.setItem(
        "documentId",
        documentId
      );
    }
  }, [report, documentId]);

  // Save current page
  useEffect(() => {
    localStorage.setItem(
      "currentPage",
      appState
    );
  }, [appState]);

  const handleUploadSuccess = (
    reportData: DocumentReport,
    docId: string
  ) => {
    setReport(reportData);
    setDocumentId(docId);
    setAppState("results");

    localStorage.setItem(
      "documentReport",
      JSON.stringify(reportData)
    );

    localStorage.setItem(
      "documentId",
      docId
    );
  };

  const resetApp = () => {
    setReport(null);
    setDocumentId(null);
    setIsLoading(false);
    setAppState("welcome");
    setChatOpen(false);

    localStorage.removeItem(
      "documentReport"
    );

    localStorage.removeItem(
      "documentId"
    );

    localStorage.removeItem(
      "chatMessages"
    );

    localStorage.removeItem(
      "currentPage"
    );
  };

  const handleLogout =
    async () => {
      await signOut(auth);
      resetApp();
    };

  const handleGetStarted = () => {
    setAppState("upload");
  };

  const handleBackToWelcome =
    () => {
      setAppState("welcome");
    };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#0a0e1a] flex items-center justify-center text-white">
        Loading...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0e1a] text-white">

      {/* Navbar */}
      <Navbar
        currentPage={appState}
        onNavigate={(page) =>
          setAppState(page)
        }
        hasResults={!!report}
        isLoggedIn={!!user}
        user={user}
        onLogout={handleLogout}
      />

      <main>
        {/* Welcome */}
        {appState === "welcome" && (
          <WelcomeScreen
            onGetStarted={
              handleGetStarted
            }
          />
        )}

        {/* Upload */}
        {appState === "upload" &&
          (user ? (
            <DocumentUpload
              onUploadSuccess={
                handleUploadSuccess
              }
              isLoading={isLoading}
              setIsLoading={
                setIsLoading
              }
              onBack={
                handleBackToWelcome
              }
            />
          ) : (
            <Login />
          ))}

        {/* Results */}
        {appState === "results" &&
          report && (
            <div className="w-full px-6 py-8 bg-[#010409]">
              <ReportSection
                report={report}
              />

              {/* Floating Chat Panel */}
              {/* {chatOpen &&
                documentId && (
                  <div className="fixed bottom-24 right-6 w-[420px] z-50 shadow-2xl">
                    <ChatSection />
                  </div>
                )} */}

              {/* Chat Toggle */}
              {/* {documentId && (
                <button
                  onClick={() =>
                    setChatOpen(
                      !chatOpen
                    )
                  }
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
              )} */}
            </div>
          )}

        {/* Chat Page */}
        {appState === "chat" &&
          user && <ChatSection />}
      </main>
    </div>
  );
}

export default App;