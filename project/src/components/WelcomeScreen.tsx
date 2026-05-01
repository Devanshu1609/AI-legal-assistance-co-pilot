import React from 'react';
import {
  FileText,
  MessageSquare,
  Shield,
  Zap,
  Upload,
  ArrowRight,
  Sparkles,
  Brain,
  CheckCircle
} from 'lucide-react';

interface WelcomeScreenProps {
  onGetStarted: () => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onGetStarted }) => {

  const features = [
    {
      icon: Brain,
      title: "AI-Powered Analysis",
      description: "Advanced AI technology analyzes your legal documents with precision and speed"
    },
    {
      icon: Shield,
      title: "Risk Assessment",
      description: "Identify potential legal risks and get actionable recommendations"
    },
    {
      icon: MessageSquare,
      title: "Interactive Q&A",
      description: "Ask questions about your documents and get instant, detailed answers"
    },
    {
      icon: Zap,
      title: "Instant Processing",
      description: "Get comprehensive analysis in minutes, not hours"
    }
  ];

  const capabilities = [
    "Contract analysis and review",
    "Risk identification and assessment",
    "Complex clause explanation",
    "Legal document summarization",
    "Compliance checking",
    "Interactive document Q&A"
  ];

  const exampleQuestions = [
    "What are the key terms and conditions?",
    "Are there any potential legal risks?",
    "Can you explain the complex clauses?",
    "What are your recommendations?"
  ];

  return (
    <div className="min-h-[calc(100vh-80px)] bg-[#0a0e1a] text-white">

      {/* HERO */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[#0a0e1a]"></div>

        <div className="relative max-w-7xl mx-auto px-6 py-24 text-center space-y-8">

          {/* Badge */}
          <div className="inline-flex items-center space-x-2 bg-blue-500/10 border border-blue-500/30 text-blue-400 px-4 py-1.5 rounded-full text-xs font-mono">
            <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse"></span>
            <Sparkles className="h-4 w-4" />
            <span>AI LEGAL AGENT</span>
          </div>

          {/* Heading */}
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold leading-tight tracking-tight">
            Your AI-Powered
            <span className="block bg-gradient-to-r from-blue-500 to-cyan-400 bg-clip-text text-transparent">
              Legal Assistant
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-lg sm:text-xl text-gray-400 max-w-3xl mx-auto leading-relaxed">
            Transform complex legal documents into clear, actionable insights.
            Upload, analyze, and get instant answers with AI precision.
          </p>

          {/* CTA */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-6">
            <button
              onClick={onGetStarted}
className="group inline-flex items-center space-x-3 
bg-[#0f172a] hover:bg-[#111827] 
border border-blue-500/30 
text-blue-400 
px-8 py-4 rounded-2xl text-lg font-semibold 
transition-all duration-300 transform hover:scale-105 
shadow-lg shadow-blue-500/10 hover:shadow-blue-500/20"            >
              <Upload className="h-5 w-5" />
              <span>Start Analysis</span>
              <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </button>

            <div className="text-sm text-gray-500 flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-400" />
              <span>Free • No signup required</span>
            </div>
          </div>

          {/* Formats */}
          <div className="flex justify-center gap-6 pt-6 text-sm text-gray-500">
            <span>PDF</span>
            <span>DOCX</span>
            <span>TXT</span>
          </div>
        </div>
      </div>

      {/* FEATURES */}
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-14">
          <h2 className="text-3xl sm:text-4xl font-bold mb-3">
            Why Choose AI Legal Co-Pilot?
          </h2>
          <p className="text-gray-400">
            Experience the future of legal document analysis
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group bg-[#0f1629] border border-gray-800 p-6 rounded-2xl hover:border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/10 transition-all duration-300"
            >
              <div className="w-12 h-12 flex items-center justify-center rounded-xl bg-blue-500/10 border border-blue-500/20 mb-4 group-hover:scale-110 transition">
                <feature.icon className="h-5 w-5 text-blue-400" />
              </div>
              <h3 className="font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-gray-400 text-sm">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* CAPABILITIES */}
      <div className="bg-[#0a0e1a]/80 border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-6 py-20 grid lg:grid-cols-2 gap-12">

          {/* LEFT */}
          <div>
            <h2 className="text-3xl font-bold mb-6">
              Comprehensive Legal Analysis
            </h2>

            <p className="text-gray-400 mb-6">
              Our AI understands legal language and provides deep insights.
            </p>

            <div className="space-y-3">
              {capabilities.map((item, i) => (
                <div key={i} className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-400" />
                  <span className="text-gray-300 text-sm">{item}</span>
                </div>
              ))}
            </div>
          </div>

          {/* RIGHT */}
          <div className="bg-[#0f1629] border border-gray-800 rounded-2xl p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-blue-400" />
              Ask Anything
            </h3>

            <div className="space-y-3">
              {exampleQuestions.map((q, i) => (
                <div
                  key={i}
                  className="bg-[#0a0e1a] border border-gray-800 p-3 rounded-lg text-sm text-gray-300 hover:border-blue-500/30 transition"
                >
                  "{q}"
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>

      {/* FINAL CTA */}
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="bg-[#0f172a] rounded-3xl p-12 text-center relative overflow-hidden">
          <div className="absolute inset-0 bg-black/10"></div>

          <div className="relative">
            <h2 className="text-3xl font-bold mb-3">
              Ready to Analyze Your Document?
            </h2>

            <p className="text-blue-100 mb-6">
              Upload now and get AI-powered insights instantly
            </p>

            <button
              onClick={onGetStarted}
              className="inline-flex items-center gap-3 bg-blue-500/10 border border-blue-500/30 text-blue-400 px-6 py-3 rounded-xl font-semibold hover:bg-gray-100 transition transform hover:scale-105"
            >
              <Upload className="h-4 w-4" />
              Upload Document
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

    </div>
  );
};

export default WelcomeScreen;
