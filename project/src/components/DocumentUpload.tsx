import React, { useCallback, useState, useEffect, useRef } from "react";
import {
  Upload,
  FileText,
  ArrowLeft,
  AlertCircle,
  BookOpen,
  Info,
  AlertTriangle,
  CheckCircle,
  Brain,
  Shield,
  Zap,
  File,
  X,
  Sparkles,
  Bot,
  Terminal,
  Cpu,
} from "lucide-react";

interface DocumentUploadProps {
  onUploadSuccess: (report: any, documentId: string) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  onBack: () => void;
}

interface SelectedFile {
  file: File;
  name: string;
  size: string;
  type: string;
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const getFileIcon = (extension: string) => {
  switch (extension) {
    case ".pdf": return { label: "PDF", color: "text-red-400", bg: "bg-red-500/10 border-red-500/20" };
    case ".docx": return { label: "DOCX", color: "text-blue-400", bg: "bg-blue-500/10 border-blue-500/20" };
    case ".txt": return { label: "TXT", color: "text-green-400", bg: "bg-green-500/10 border-green-500/20" };
    default: return { label: "FILE", color: "text-gray-400", bg: "bg-gray-500/10 border-gray-500/20" };
  }
};

const AgentProcessingView: React.FC<{ currentStatus: string; completedSteps: string[]; fileName: string }> = ({
  currentStatus,
  completedSteps,
  fileName,
}) => {
  const [typedLines, setTypedLines] = useState<string[]>([]);
  const [dots, setDots] = useState(".");
  const logRef = useRef<HTMLDivElement>(null);

  const steps = [
    { id: "uploaded", label: "Document Uploaded", icon: Upload, log: `[AGENT] File received: ${fileName}` },
    { id: "parsed", label: "Text Extracted", icon: FileText, log: "[AGENT] Parsing document structure..." },
    { id: "summarized", label: "Document Summarized", icon: BookOpen, log: "[AGENT] Generating executive summary..." },
    { id: "clauses_explained", label: "Clauses Analyzed", icon: Info, log: "[AGENT] Interpreting complex clauses..." },
    { id: "risk_calculated", label: "Risk Assessment", icon: AlertTriangle, log: "[AGENT] Running risk model..." },
    { id: "completed", label: "Report Generated", icon: CheckCircle, log: "[AGENT] Compiling final report..." },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setDots((d) => (d.length >= 3 ? "." : d + "."));
    }, 500);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const newLines: string[] = [];
    completedSteps.forEach((stepId) => {
      const step = steps.find((s) => s.id === stepId);
      if (step) newLines.push(step.log);
    });
    setTypedLines(newLines);
  }, [completedSteps, fileName]);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [typedLines]);

  const progressPercentage = Math.round((completedSteps.length / steps.length) * 100);
  const activeStepIndex = completedSteps.length;

  return (
    <div className="min-h-[calc(100vh-64px)] bg-[#0a0e1a] flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-3xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center space-x-2 bg-blue-500/10 border border-blue-500/30 text-blue-400 px-4 py-1.5 rounded-full text-xs font-mono mb-4">
            <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse"></span>
            <span>AI AGENT PROCESSING</span>
          </div>
          <h2 className="text-2xl font-bold text-white mb-1">Analyzing Document</h2>
          <p className="text-gray-500 text-sm font-mono">{fileName}</p>
        </div>

        {/* Main Card */}
        <div className="bg-[#0f1629] border border-gray-800 rounded-2xl overflow-hidden shadow-2xl">
          {/* Terminal Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800 bg-[#0a0e1a]">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-red-500/70"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500/70"></div>
              <div className="w-3 h-3 rounded-full bg-green-500/70"></div>
            </div>
            <div className="flex items-center space-x-2 text-gray-500 text-xs font-mono">
              <Terminal className="h-3 w-3" />
              <span>legal-agent — analysis</span>
            </div>
            <div className="flex items-center space-x-1">
              <Cpu className="h-3 w-3 text-blue-400 animate-pulse" />
              <span className="text-blue-400 text-xs font-mono">{progressPercentage}%</span>
            </div>
          </div>

          {/* Log Output */}
          <div
            ref={logRef}
            className="h-36 overflow-y-auto px-5 py-4 font-mono text-xs space-y-1.5 bg-[#0a0e1a]/60"
          >
            <div className="text-gray-600">$ legal-agent start --file "{fileName}"</div>
            <div className="text-gray-600">$ Initializing AI agents{dots}</div>
            {typedLines.map((line, i) => (
              <div key={i} className="text-green-400">{line}</div>
            ))}
            {completedSteps.length < steps.length && (
              <div className="text-blue-400 flex items-center space-x-1">
                <span className="animate-pulse">▋</span>
                <span>{currentStatus || "Processing"}{dots}</span>
              </div>
            )}
          </div>

          {/* Progress Bar */}
          <div className="px-5 py-3 border-t border-gray-800 bg-[#0a0e1a]/80">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-500 text-xs font-mono">Progress</span>
              <span className="text-blue-400 text-xs font-mono font-bold">{progressPercentage}%</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full transition-all duration-700 ease-out relative"
                style={{ width: `${progressPercentage}%` }}
              >
                <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-cyan-300 rounded-full shadow-lg shadow-cyan-400/50"></div>
              </div>
            </div>
          </div>

          {/* Steps Grid */}
          <div className="grid grid-cols-3 gap-px bg-gray-800 border-t border-gray-800">
            {steps.map((step, index) => {
              const isCompleted = completedSteps.includes(step.id);
              const isActive = activeStepIndex === index;
              const StepIcon = step.icon;

              return (
                <div
                  key={step.id}
                  className={`flex flex-col items-center justify-center p-4 transition-all duration-500 ${isCompleted
                    ? "bg-[#0a1a12]"
                    : isActive
                      ? "bg-[#0a0f1e]"
                      : "bg-[#0a0e1a]"
                    }`}
                >
                  <div
                    className={`w-9 h-9 rounded-xl flex items-center justify-center mb-2 transition-all duration-500 ${isCompleted
                      ? "bg-green-500/20 border border-green-500/30"
                      : isActive
                        ? "bg-blue-500/20 border border-blue-500/40"
                        : "bg-gray-800 border border-gray-700"
                      }`}
                  >
                    {isCompleted ? (
                      <CheckCircle className="h-4 w-4 text-green-400" />
                    ) : isActive ? (
                      <StepIcon className="h-4 w-4 text-blue-400 animate-pulse" />
                    ) : (
                      <StepIcon className="h-4 w-4 text-gray-600" />
                    )}
                  </div>
                  <span
                    className={`text-xs font-medium text-center leading-tight ${isCompleted
                      ? "text-green-400"
                      : isActive
                        ? "text-blue-400"
                        : "text-gray-600"
                      }`}
                  >
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Info Row */}
        <div className="grid grid-cols-3 gap-3 mt-4">
          {[
            { icon: Brain, label: "AI Analysis", desc: "Multi-agent processing", color: "blue" },
            { icon: Shield, label: "Encrypted", desc: "Enterprise-grade security", color: "green" },
            { icon: Zap, label: "Real-time", desc: "Live progress updates", color: "amber" },
          ].map((item, i) => {
            const Icon = item.icon;
            return (
              <div key={i} className="bg-[#0f1629] border border-gray-800 rounded-xl p-3 flex items-center space-x-3">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${item.color === "blue" ? "bg-blue-500/10" : item.color === "green" ? "bg-green-500/10" : "bg-amber-500/10"
                  }`}>
                  <Icon className={`h-4 w-4 ${item.color === "blue" ? "text-blue-400" : item.color === "green" ? "text-green-400" : "text-amber-400"
                    }`} />
                </div>
                <div>
                  <div className="text-white text-xs font-semibold">{item.label}</div>
                  <div className="text-gray-600 text-xs">{item.desc}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUploadSuccess,
  isLoading,
  setIsLoading,
  onBack,
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStatus, setCurrentStatus] = useState<string>("");
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  const [selectedFile, setSelectedFile] = useState<SelectedFile | null>(null);
  const [processingFileName, setProcessingFileName] = useState("");

  // const extractSection = (markdown: string | undefined, sectionTitle: string): string => {
  //   if (!markdown || typeof markdown !== "string") return "";

  //   const lines = markdown.split("\n");
  //   let sectionStart = -1;
  //   let sectionEnd = -1;

  //   for (let i = 0; i < lines.length; i++) {
  //     if (lines[i].trim() === `## ${sectionTitle}`) {
  //       sectionStart = i;
  //       break;
  //     }
  //   }

  //   if (sectionStart === -1) return "";

  //   for (let i = sectionStart + 1; i < lines.length; i++) {
  //     if (lines[i].startsWith("## ") && i !== sectionStart) {
  //       sectionEnd = i;
  //       break;
  //     }
  //   }

  //   if (sectionEnd === -1) sectionEnd = lines.length;

  //   return lines.slice(sectionStart + 1, sectionEnd).join("\n").trim() || "";
  // };

  const extractSection = (markdown: string | undefined, sectionTitle: string): string => {
  if (!markdown || typeof markdown !== "string") return "";

  const regex = new RegExp(`##\\s*${sectionTitle}\\s*([\\s\\S]*?)(?=\\n##\\s|$)`, "i");
  const match = markdown.match(regex);

  return match ? match[1].trim() : "";
};

  const processFile = useCallback(
    async (file: File) => {
      const validTypes = [".pdf", ".docx", ".txt"];
      const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf("."));

      if (!validTypes.includes(fileExtension)) {
        setError("Please upload a PDF, DOCX, or TXT file.");
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        setError("File size must be less than 10MB.");
        return;
      }

      setError(null);
      setProcessingFileName(file.name);
      setIsLoading(true);
      setCurrentStatus("Starting analysis...");
      setCompletedSteps([]);

      try {
        const formData = new FormData();
        formData.append("file", file);

        // 🚀 FAKE PROGRESS STEPS (matches your UI)
        const steps = [
          { id: "uploaded", text: "Document uploaded successfully" },
          { id: "parsed", text: "Document parsed and text extracted" },
          { id: "summarized", text: "Document summarized" },
          { id: "clauses_explained", text: "Complex clauses explained" },
          { id: "risk_calculated", text: "Risk analysis completed" },
          { id: "completed", text: "Report generation completed" },
        ];

        let stepIndex = 0;

        const interval = setInterval(() => {
          if (stepIndex >= steps.length) {
            clearInterval(interval); // ✅ STOP when done
            return;
          }

          const step = steps[stepIndex];

          if (step) {
            setCurrentStatus(step.text);
            setCompletedSteps((prev) => [...prev, step.id]);
          }

          stepIndex++;
        }, 700);

        const response = await fetch("http://127.0.0.1:8000/upload-document", {
          method: "POST",
          body: formData,
        });
        console.log("API Response:", response);

        if (!response.ok) throw new Error(`Upload failed: ${response.status}`);

        const finalReport = await response.json();
        console.log("Final Report from API:", finalReport);
        console.log("TYPE OF finalReport.report:", typeof finalReport.report);
        console.log("FULL finalReport:", finalReport);

        clearInterval(interval);

        // Ensure all steps complete visually
        setCompletedSteps(steps.map((s) => s.id));
        setCurrentStatus("Finalizing report...");

        const markdown =
          typeof finalReport?.report === "string"
            ? finalReport.report
            : finalReport?.report?.report || "";

        console.log("Received Markdown Report:", markdown);
        const documentId = file.name;
        console.log("Generated Document ID:", documentId);

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
          file_name: file.name,
        };

        console.log("Transformed Report Object:", transformedReport);

        setTimeout(() => {
          onUploadSuccess(transformedReport, documentId);
        }, 800);

      } catch (err) {
        console.error(err);
        setError("Failed to upload and analyze document. Please try again.");
      } finally {
        setTimeout(() => {
          setIsLoading(false);
          setCurrentStatus("");
          setCompletedSteps([]);
        }, 1200);
      }
    },
    [onUploadSuccess, setIsLoading, extractSection]
  );

  const handleFiles = useCallback(
    (files: FileList | File[]) => {
      const file = files[0];
      if (!file) return;

      const validTypes = [".pdf", ".docx", ".txt"];
      const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf("."));

      if (!validTypes.includes(fileExtension)) {
        setError("Please upload a PDF, DOCX, or TXT file.");
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        setError("File size must be less than 10MB.");
        return;
      }

      setError(null);
      setSelectedFile({
        file,
        name: file.name,
        size: formatFileSize(file.size),
        type: fileExtension,
      });
    },
    []
  );

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);
      if (e.dataTransfer.files?.[0]) handleFiles(e.dataTransfer.files);
    },
    [handleFiles]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      e.preventDefault();
      if (e.target.files?.[0]) handleFiles(e.target.files);
    },
    [handleFiles]
  );

  const handleAnalyze = () => {
    if (selectedFile) processFile(selectedFile.file);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setError(null);
  };

  if (isLoading) {
    return (
      <AgentProcessingView
        currentStatus={currentStatus}
        completedSteps={completedSteps}
        fileName={processingFileName}
      />
    );
  }

  const fileInfo = selectedFile ? getFileIcon(selectedFile.type) : null;

  return (
    <div className="min-h-[calc(100vh-64px)] bg-[#0a0e1a] flex flex-col">
      {/* Top Bar */}
      <div className="border-b border-gray-800/60 px-6 py-3 flex items-center justify-between">
        <button
          onClick={onBack}
          className="group inline-flex items-center space-x-2 text-gray-500 hover:text-gray-300 transition-all duration-200 text-sm"
        >
          <ArrowLeft className="h-4 w-4 group-hover:-translate-x-0.5 transition-transform" />
          <span>Back</span>
        </button>
        <div className="flex items-center space-x-2 text-gray-600 text-xs font-mono">
          <Bot className="h-3.5 w-3.5" />
          <span>legal-agent v2.0</span>
        </div>
        <div className="w-16"></div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-10">
        <div className="w-full max-w-2xl">
          {/* Header */}
          <div className="text-center mb-10">
            {/* <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-500/10 border border-blue-500/20 mb-5 mx-auto">
              <Sparkles className="h-7 w-7 text-blue-400" />
            </div> */}
            <h1 className="text-3xl font-bold text-white mb-3 tracking-tight">
              Upload Legal Document
            </h1>
            <p className="text-gray-500 text-base max-w-md mx-auto leading-relaxed">
              Drop your document and our AI agents will analyze it for risks, key clauses, and actionable recommendations.
            </p>
          </div>

          {/* Upload Zone */}
          {!selectedFile ? (
            <div
              className={`relative rounded-3xl overflow-hidden cursor-pointer transition-all duration-500 ${dragActive ? "scale-[1.02]" : "scale-100"
                }`}
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-50"
                onChange={handleChange}
              />

              {/* Animated Background */}
              <div className="absolute inset-0 bg-[#0f1629] z-0">
                {/* Gradient Orbs */}
                <div className={`absolute -top-1/2 -right-1/4 w-96 h-96 bg-gradient-to-br from-blue-600/30 to-cyan-600/20 rounded-full blur-3xl transition-all duration-700 ${dragActive ? "scale-150 opacity-100" : "scale-100 opacity-50"
                  }`}></div>
                <div className={`absolute -bottom-1/3 -left-1/4 w-80 h-80 bg-gradient-to-tr from-purple-600/20 to-blue-600/20 rounded-full blur-3xl transition-all duration-700 ${dragActive ? "scale-150 opacity-100" : "scale-100 opacity-50"
                  }`}></div>

                {/* Grid Pattern */}
                <div className="absolute inset-0 opacity-[0.03]" style={{
                  backgroundImage: `
                    linear-gradient(0deg, transparent 24%, rgba(255,255,255,.05) 25%, rgba(255,255,255,.05) 26%, transparent 27%, transparent 74%, rgba(255,255,255,.05) 75%, rgba(255,255,255,.05) 76%, transparent 77%, transparent),
                    linear-gradient(90deg, transparent 24%, rgba(255,255,255,.05) 25%, rgba(255,255,255,.05) 26%, transparent 27%, transparent 74%, rgba(255,255,255,.05) 75%, rgba(255,255,255,.05) 76%, transparent 77%, transparent)
                  `,
                  backgroundSize: '50px 50px'
                }}></div>

                {/* Animated Particles */}
                <div className="absolute inset-0 overflow-hidden">
                  {[...Array(4)].map((_, i) => (
                    <div
                      key={i}
                      className="absolute w-1 h-1 bg-blue-400 rounded-full opacity-60 animate-pulse"
                      style={{
                        left: `${25 + i * 20}%`,
                        top: `${30 + i * 15}%`,
                        animation: `float ${3 + i}s ease-in-out infinite`,
                      }}
                    ></div>
                  ))}
                </div>
              </div>

              {/* Border */}
              <div className={`absolute inset-0 rounded-3xl border-2 pointer-events-none transition-all duration-300 ${dragActive
                ? "border-blue-400 shadow-xl shadow-blue-500/20"
                : "border-gray-700 group-hover:border-gray-600"
                }`}></div>

              {/* Content */}
              <div className="relative z-20 px-8 py-8 text-center">
                {/* Icon Container */}
                <div className="flex justify-center mb-8">
                  <div className={`relative transition-all duration-500 ${dragActive ? "scale-110" : "scale-100"
                    }`}>
                    {/* Icon Background Circle */}
                    <div className={`absolute inset-0 rounded-3xl blur-2xl transition-all duration-500 ${dragActive
                      ? "bg-gradient-to-r from-blue-500 to-cyan-500 opacity-40 scale-125"
                      : "bg-gradient-to-r from-blue-400 to-cyan-400 opacity-0"
                      }`}></div>

                    {/* Icon Box */}
                    <div className={`relative w-20 h-20 rounded-2xl flex items-center justify-center transition-all duration-500 ${dragActive
                      ? "bg-gradient-to-br from-blue-500/30 to-cyan-500/20 border border-blue-400/50"
                      : "bg-gradient-to-br from-gray-700/50 to-gray-800/50 border border-gray-600/50"
                      }`}>
                      <Upload className={`h-8 w-8 transition-all duration-500 ${dragActive ? "text-blue-300 scale-125" : "text-gray-400"
                        }`} />
                    </div>
                  </div>
                </div>

                {/* Text */}
                <div className="mb-8">
                  <p className={`text-2xl font-bold transition-all duration-300 mb-2 ${dragActive ? "text-blue-300" : "text-white"
                    }`}>
                    {dragActive ? "Drop your document here" : "Upload Your Legal Document"}
                  </p>
                  <p className="text-gray-500 text-sm leading-relaxed max-w-sm mx-auto">
                    {dragActive
                      ? "Release to start analysis"
                      : "Drag and drop your file, or click to browse. We'll analyze it in seconds."}
                  </p>
                </div>

                {/* File Types & Size */}
                <div className="flex flex-col items-center space-y-4">
                  <div className="flex items-center justify-center gap-2">
                    {[
                      { icon: "📄", label: "PDF" },
                      { icon: "📝", label: "DOCX" },
                      { icon: "📋", label: "TXT" },
                    ].map((type, i) => (
                      <div
                        key={i}
                        className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-gray-800/60 border border-gray-700 text-gray-400 text-xs font-medium transition-all duration-300 hover:border-gray-600 hover:bg-gray-800"
                      >
                        <span>{type.icon}</span>
                        <span>{type.label}</span>
                      </div>
                    ))}
                  </div>
                  <p className="text-gray-600 text-xs">
                    Maximum file size: <span className="text-blue-400 font-semibold">10MB</span>
                  </p>
                </div>
              </div>

              {/* Animated Corners */}
              <div className="absolute top-0 left-0 w-px h-8 bg-gradient-to-b from-blue-500 to-transparent opacity-0 group-hover:opacity-50 transition-opacity duration-300 pointer-events-none"></div>
              <div className="absolute top-0 right-0 w-px h-8 bg-gradient-to-b from-blue-500 to-transparent opacity-0 group-hover:opacity-50 transition-opacity duration-300 pointer-events-none"></div>
              <div className="absolute bottom-0 left-0 w-px h-8 bg-gradient-to-t from-blue-500 to-transparent opacity-0 group-hover:opacity-50 transition-opacity duration-300 pointer-events-none"></div>
              <div className="absolute bottom-0 right-0 w-px h-8 bg-gradient-to-t from-blue-500 to-transparent opacity-0 group-hover:opacity-50 transition-opacity duration-300 pointer-events-none"></div>
            </div>
          ) : (
            <div className="bg-[#0f1629] border border-gray-700 rounded-2xl overflow-hidden">
              {/* File Preview */}
              <div className="p-5 flex items-center space-x-4">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center border flex-shrink-0 ${fileInfo?.bg}`}>
                  <span className={`text-xs font-bold font-mono ${fileInfo?.color}`}>{fileInfo?.label}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-white font-medium text-sm truncate">{selectedFile.name}</p>
                  <p className="text-gray-600 text-xs mt-0.5">{selectedFile.size} — Ready to analyze</p>
                </div>
                <button
                  onClick={handleRemoveFile}
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-gray-600 hover:text-gray-400 hover:bg-gray-800 transition-colors flex-shrink-0"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Divider */}
              <div className="border-t border-gray-800 mx-5"></div>

              {/* Agent Preview */}
              <div className="px-5 py-4">
                <p className="text-gray-600 text-xs font-mono mb-3">AI agents will run:</p>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { icon: FileText, label: "Document Parsing" },
                    { icon: Brain, label: "AI Summarization" },
                    { icon: Info, label: "Clause Analysis" },
                    { icon: AlertTriangle, label: "Risk Assessment" },
                    { icon: Zap, label: "Recommendations" },
                    { icon: BookOpen, label: "Report Generation" },
                  ].map((item, i) => {
                    const Icon = item.icon;
                    return (
                      <div key={i} className="flex items-center space-x-2 text-gray-500 text-xs">
                        <Icon className="h-3 w-3 text-blue-500/70 flex-shrink-0" />
                        <span>{item.label}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Action */}
              <div className="px-5 pb-5">
                <button
                  onClick={handleAnalyze}
                  className="w-full py-3.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 group"
                >
                  <Sparkles className="h-4 w-4 group-hover:rotate-12 transition-transform" />
                  <span>Analyze Document</span>
                </button>
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mt-4 flex items-center space-x-2 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl px-4 py-3 text-sm">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Feature Pills */}
          <div className="flex flex-wrap items-center justify-center gap-2 mt-8">
            {[
              { icon: Shield, label: "End-to-end encrypted" },
              { icon: Zap, label: "Real-time analysis" },
              { icon: Bot, label: "Multi-agent AI" },
              { icon: File, label: "No data stored" },
            ].map((item, i) => {
              const Icon = item.icon;
              return (
                <div key={i} className="inline-flex items-center space-x-1.5 bg-gray-900/60 border border-gray-800 text-gray-600 text-xs px-3 py-1.5 rounded-full">
                  <Icon className="h-3 w-3" />
                  <span>{item.label}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentUpload;
