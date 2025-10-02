// src/components/DocumentUpload.tsx
import React, { useCallback, useState } from "react";
import {
  Upload,
  FileText,
  Loader2,
  ArrowLeft,
  AlertCircle,
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

      try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch("https://ai-legal-assistance-co-pilot.onrender.com/upload", {
          method: "POST",
          body: formData,
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.status}`);
        }

        const result = await response.json();

        // Ensure report_markdown exists
        const markdown = result?.report?.report_markdown || "";

        // Transform backend response to frontend structure
        const transformedReport = {
          document_id: result.document_id || "",
          table_of_contents: extractSection(markdown, "Table of Contents"),
          executive_summary: extractSection(markdown, "1. Executive Summary"),
          key_points: extractSection(markdown, "2. Key Points"),
          complex_clauses: extractSection(markdown, "3. Complex Clauses Explained"),
          risk_assessment: extractSection(markdown, "4. Risk Assessment"),
          recommendations: extractSection(markdown, "5. Recommendations"),
          unclear_missing: extractSection(markdown, "6. Unclear or Missing Information"),
          appendix: extractSection(markdown, "7. Appendix (Method & Sources)"),
          overall_risk_level: result?.report?.overall_risk_level || "",
          overall_risk_score: result?.report?.overall_risk_score ?? null,
          highlights: result?.report?.highlights || [],
          risks_count: result?.report?.risks_count ?? 0,
          file_name: result?.report?.file_name || file.name,
        };

        console.log("transformed report :- ", transformedReport);

        onUploadSuccess(transformedReport, result.document_id || "");
      } catch (err) {
        setError("Failed to upload and analyze document. Please try again.");
        console.error("Upload error:", err);
      } finally {
        setIsLoading(false);
      }
    },
    [onUploadSuccess, setIsLoading]
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
    return (
      <div className="min-h-[calc(100vh-80px)] bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20 flex items-center justify-center px-6">
        <div className="max-w-lg mx-auto text-center">
          <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-12 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-indigo-50/50"></div>
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-100/30 to-purple-100/30 rounded-full -translate-y-16 translate-x-16"></div>
            <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-indigo-100/30 to-blue-100/30 rounded-full translate-y-12 -translate-x-12"></div>

            <div className="relative">
              <div className="relative mb-8">
                <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto shadow-lg">
                  <Loader2 className="h-12 w-12 animate-spin text-white" />
                </div>
                <div className="absolute inset-0 rounded-full border-4 border-blue-200 animate-pulse"></div>
                <div className="absolute inset-0 rounded-full border-4 border-blue-300 animate-ping"></div>
              </div>

              <h3 className="text-3xl font-bold text-gray-900 mb-4">
                Analyzing Your Document
              </h3>
              <p className="text-gray-600 leading-relaxed text-lg mb-8">
                Our advanced AI is carefully reviewing your document to provide
                comprehensive insights. This process typically takes 30–60
                seconds.
              </p>

              <div className="flex justify-center mb-6">
                <div className="flex space-x-2">
                  <div className="w-3 h-3 bg-blue-600 rounded-full animate-bounce"></div>
                  <div
                    className="w-3 h-3 bg-blue-600 rounded-full animate-bounce"
                    style={{ animationDelay: "0.1s" }}
                  ></div>
                  <div
                    className="w-3 h-3 bg-blue-600 rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  ></div>
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4">
                <p className="text-blue-700 text-sm font-medium">
                  💡 While you wait: Our AI analyzes document structure,
                  identifies key clauses, assesses risks, and prepares actionable
                  recommendations.
                </p>
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