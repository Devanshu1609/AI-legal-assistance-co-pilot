// src/components/DocumentUpload.tsx
import React, { useCallback, useState } from "react";
import {
  Upload,
  FileText,
  ArrowLeft,
  AlertCircle,BookOpen,Info,AlertTriangle,CheckCircle,Brain,Shield,Zap
} from "lucide-react";

interface DocumentUploadProps {
  onUploadSuccess: (report: any, documentId: string) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  onBack: () => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUploadSuccess,
  isLoading,
  setIsLoading,
  onBack,
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStatus, setCurrentStatus] = useState<string>('');
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);

  // ✅ Fixed extractor to get exact section content
  const extractSection = (markdown: string | undefined, sectionTitle: string): string => {
    if (!markdown || typeof markdown !== "string") return "";

    const lines = markdown.split("\n");
    let sectionStart = -1;
    let sectionEnd = -1;

    // Find section start: exact match with "## Section Name"
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].trim() === `## ${sectionTitle}`) {
        sectionStart = i;
        break;
      }
    }

    if (sectionStart === -1) return "";

    // Find next section start (next line starting with "##")
    for (let i = sectionStart + 1; i < lines.length; i++) {
      if (lines[i].startsWith("## ") && i !== sectionStart) {
        sectionEnd = i;
        break;
      }
    }

    if (sectionEnd === -1) sectionEnd = lines.length;

    return lines.slice(sectionStart + 1, sectionEnd).join("\n").trim() || "";
  };

  const handleFiles = useCallback(
    async (files: FileList | File[]) => {
      const file = files[0];
      if (!file) return;

      // Validate file type
      const validTypes = [".pdf", ".docx", ".txt"];
      const fileExtension = file.name
        .toLowerCase()
        .substring(file.name.lastIndexOf("."));

      if (!validTypes.includes(fileExtension)) {
        setError("Please upload a PDF, DOCX, or TXT file.");
        return;
      }

      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        setError("File size must be less than 10MB.");
        return;
      }

      setError(null);
      setIsLoading(true);
      setCurrentStatus('Uploading document...');
      setCompletedSteps([]);

      try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch("http://localhost:8000/upload-stream", {
          method: "POST", 
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.status}`);
        }

        // Handle SSE stream
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let finalReport = null;
        let documentId = '';

        if (reader) {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const jsonStr = line.slice(6); // Remove 'data: '
                  const data = JSON.parse(jsonStr);
                  
                  // Update status based on backend response
                  switch (data.status) {
                    case 'uploaded':
                      setCurrentStatus('Document uploaded successfully');
                      setCompletedSteps(['uploaded']);
                      break;
                    case 'parsed':
                      setCurrentStatus('Document parsed and text extracted');
                      setCompletedSteps(['uploaded', 'parsed']);
                      break;
                    case 'summarized':
                      setCurrentStatus('Document summarized');
                      setCompletedSteps(['uploaded', 'parsed', 'summarized']);
                      break;
                    case 'clauses_explained':
                      setCurrentStatus('Complex clauses explained');
                      setCompletedSteps(['uploaded', 'parsed', 'summarized', 'clauses_explained']);
                      break;
                    case 'risk_calculated':
                      setCurrentStatus('Risk analysis completed');
                      setCompletedSteps(['uploaded', 'parsed', 'summarized', 'clauses_explained', 'risk_calculated']);
                      break;
                    case 'completed':
                      setCurrentStatus('Report generation completed');
                      setCompletedSteps(['uploaded', 'parsed', 'summarized', 'clauses_explained', 'risk_calculated', 'completed']);
                      finalReport = data.report;
                      // Extract document ID from the file path or generate one
                      documentId = file.name.split('.')[0] + '_' + Date.now();
                      break;
                  }
                } catch (e) {
                  console.error('Error parsing SSE data:', e);
                }
              }
            }
          }
        }

        if (finalReport) {
          // Ensure report_markdown exists
          const markdown = finalReport?.report_markdown || "";

          // Transform backend response to frontend structure
          const transformedReport = {
            document_id: documentId,
            table_of_contents: extractSection(markdown, "Table of Contents"),
            executive_summary: extractSection(markdown, "1. Executive Summary"),
            key_points: extractSection(markdown, "2. Key Points"),
            complex_clauses: extractSection(markdown, "3. Complex Clauses Explained"),
            risk_assessment: extractSection(markdown, "4. Risk Assessment"),
            recommendations: extractSection(markdown, "5. Recommendations"),
            unclear_missing: extractSection(markdown, "6. Unclear or Missing Information"),
            appendix: extractSection(markdown, "7. Appendix (Method & Sources)"),
            overall_risk_level: finalReport?.overall_risk_level || "",
            overall_risk_score: finalReport?.overall_risk_score ?? null,
            highlights: finalReport?.highlights || [],
            risks_count: finalReport?.risks_count ?? 0,
            file_name: finalReport?.file_name || file.name,
          };

          console.log("transformed report :- ", transformedReport);
          onUploadSuccess(transformedReport, documentId);
        } else {
          throw new Error('No report received from server');
        }
      } catch (err) {
        setError("Failed to upload and analyze document. Please try again.");
        console.error("Upload error:", err);
      } finally {
        setIsLoading(false);
        setCurrentStatus('');
        setCompletedSteps([]);
      }
    },
    [onUploadSuccess, setIsLoading, extractSection]
  );

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFiles(e.dataTransfer.files);
      }
    },
    [handleFiles]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      e.preventDefault();
      if (e.target.files && e.target.files[0]) {
        handleFiles(e.target.files);
      }
    },
    [handleFiles]
  );

  // === LOADING UI ===
  if (isLoading) {
    const steps = [
      { id: 'uploaded', label: 'Document Uploaded', icon: Upload },
      { id: 'parsed', label: 'Text Extracted', icon: FileText },
      { id: 'summarized', label: 'Document Summarized', icon: BookOpen },
      { id: 'clauses_explained', label: 'Clauses Explained', icon: Info },
      { id: 'risk_calculated', label: 'Risk Analysis', icon: AlertTriangle },
      { id: 'completed', label: 'Report Generated', icon: CheckCircle },
    ];

    const currentStepIndex = completedSteps.length;
    const progressPercentage = Math.round((completedSteps.length / steps.length) * 100);

    return (
      <div className="mt-8 mb-8 min-h-[calc(100vh-80px)] bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20 flex items-center justify-center px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-12 relative overflow-hidden">
            {/* Background Elements */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-50/30 to-indigo-50/30"></div>
            <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-br from-blue-100/20 to-purple-100/20 rounded-full -translate-y-20 translate-x-20"></div>
            <div className="absolute bottom-0 left-0 w-32 h-32 bg-gradient-to-tr from-indigo-100/20 to-blue-100/20 rounded-full translate-y-16 -translate-x-16"></div>
            <div className="absolute top-1/2 left-1/2 w-24 h-24 bg-gradient-to-br from-purple-100/20 to-pink-100/20 rounded-full -translate-x-12 -translate-y-12"></div>

            <div className="relative">
              {/* Central Animation */}
              

              {/* Status Display */}
              <div className="mb-8">
                <div className="inline-flex items-center space-x-2 bg-blue-50 border border-blue-200 text-blue-700 px-4 py-2 rounded-full text-sm font-medium shadow-sm mb-4">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                  <span>Processing</span>
                </div>
                <h3 className="text-3xl font-bold text-gray-900 mb-2">
                  {currentStatus || 'Analyzing Your Document'}
                </h3>
                <p className="text-lg text-gray-600 mb-6">
                  {progressPercentage}% Complete
                </p>
              </div>

              {/* Progress Bar */}
              <div className="mb-12">
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden shadow-inner">
                  <div 
                    className="h-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 rounded-full transition-all duration-1000 ease-out relative"
                    style={{ width: `${progressPercentage}%` }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse"></div>
                  </div>
                </div>
              </div>

              {/* Progress Steps */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-6 mb-8">
                {steps.map((step, index) => {
                  const isCompleted = completedSteps.includes(step.id);
                  const isActive = currentStepIndex === index;
                  const StepIcon = step.icon;
                  
                  return (
                    <div
                      key={step.id}
                      className={`flex flex-col items-center p-4 rounded-2xl transition-all duration-500 ${
                        isCompleted 
                          ? 'bg-gradient-to-br from-green-50 to-blue-50 border-2 border-green-200' 
                          : isActive 
                          ? 'bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-300 animate-pulse' 
                          : 'bg-gray-50 border-2 border-gray-200'
                      }`}
                    >
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-3 transition-all duration-500 ${
                        isCompleted 
                          ? 'bg-gradient-to-br from-green-500 to-blue-500 text-white shadow-lg' 
                          : isActive 
                          ? 'bg-gradient-to-br from-blue-500 to-indigo-500 text-white shadow-lg animate-pulse' 
                          : 'bg-gray-300 text-gray-500'
                      }`}>
                        <StepIcon className="h-6 w-6" />
                      </div>
                      <span className={`text-sm font-medium text-center transition-colors duration-500 ${
                        isCompleted 
                          ? 'text-green-700' 
                          : isActive 
                          ? 'text-blue-700' 
                          : 'text-gray-500'
                      }`}>
                        {step.label}
                      </span>
                    </div>
                  );
                })}
              </div>

              {/* Info Cards */}
              <div className="grid md:grid-cols-3 gap-6">
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-6">
                  <div className="flex items-center space-x-3 mb-3">
                    <Brain className="h-6 w-6 text-blue-600" />
                    <h4 className="font-bold text-gray-900">AI-Powered Analysis</h4>
                  </div>
                  <p className="text-gray-600 text-sm">
                    Advanced AI agents are analyzing your document structure, content, and legal implications.
                  </p>
                </div>
                
                <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-2xl p-6">
                  <div className="flex items-center space-x-3 mb-3">
                    <Shield className="h-6 w-6 text-green-600" />
                    <h4 className="font-bold text-gray-900">Secure Processing</h4>
                  </div>
                  <p className="text-gray-600 text-sm">
                    Your document is processed securely with enterprise-grade encryption and privacy protection.
                  </p>
                </div>
                
                <div className="bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-2xl p-6">
                  <div className="flex items-center space-x-3 mb-3">
                    <Zap className="h-6 w-6 text-purple-600" />
                    <h4 className="font-bold text-gray-900">Comprehensive Report</h4>
                  </div>
                  <p className="text-gray-600 text-sm">
                    Generating detailed insights, risk assessments, and actionable recommendations.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // === UPLOAD UI ===
  return (
    <div className="min-h-[calc(100vh-80px)] bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20">
      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Back Button */}
        <button
          onClick={onBack}
          className="group inline-flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-12 transition-all duration-200 hover:translate-x-1"
        >
          <ArrowLeft className="h-5 w-5 group-hover:-translate-x-1 transition-transform" />
          <span className="font-medium">Back to Home</span>
        </button>

        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center space-x-2 bg-blue-50 border border-blue-200 text-blue-700 px-4 py-2 rounded-full text-sm font-medium shadow-sm mb-6">
            <Upload className="h-4 w-4" />
            <span>Document Analysis</span>
          </div>

          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6 leading-tight">
            Upload Your{" "}
            <span className="block bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent pb-2">
              Legal Document
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Upload your document and get comprehensive AI-powered analysis with
            actionable insights in minutes
          </p>
        </div>

        {/* Upload Box */}
        <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8 relative overflow-hidden">
          <div
            className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all ${
              dragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 bg-white"
            }`}
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              onChange={handleChange}
            />
            <FileText className="mx-auto h-16 w-16 text-gray-400 mb-4" />
            <p className="text-gray-500 text-lg">
              Drag & Drop your file here, or click to select a file
            </p>
            <p className="text-gray-400 text-sm mt-2">
              Supported: PDF, DOCX, TXT. Max size: 10MB
            </p>
          </div>

          {error && (
            <div className="flex items-center text-red-600 mt-4">
              <AlertCircle className="h-5 w-5 mr-2" />
              <span>{error}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentUpload;
