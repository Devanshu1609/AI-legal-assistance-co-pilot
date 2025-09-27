import React from 'react';
import { FileText, MessageSquare, Shield, Zap, Upload, ArrowRight, Sparkles, Brain, CheckCircle } from 'lucide-react';

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
    <div className="min-h-[calc(100vh-80px)] bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 to-purple-600/5"></div>
        <div className="relative max-w-7xl mx-auto px-6 py-20 sm:py-24 lg:py-32">
          <div className="text-center space-y-8">
            {/* Badge */}
            <div className="inline-flex items-center space-x-2 bg-blue-50 border border-blue-200 text-blue-700 px-4 py-2 rounded-full text-sm font-medium shadow-sm">
              <Sparkles className="h-4 w-4" />
              <span>Powered by Advanced AI Technology</span>
            </div>
            
            {/* Main Heading */}
            <div className="space-y-6">
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900 leading-tight tracking-tight">
                Your AI-Powered
                <span className="block bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent pb-3">
                  Legal Assistant
                </span>
              </h1>
              
              <p className="text-xl sm:text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed font-light">
                Transform complex legal documents into clear, actionable insights. 
                Upload, analyze, and get instant answers with AI precision.
              </p>
            </div>

            {/* CTA Section */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8">
              <button
                onClick={onGetStarted}
                className="group inline-flex items-center space-x-3 bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-2xl text-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
              >
                <Upload className="h-5 w-5" />
                <span>Start Analysis</span>
                <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </button>
              
              <div className="text-sm text-gray-500 flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span>Free to try • No signup required</span>
              </div>
            </div>

            {/* Supported Formats */}
            <div className="flex items-center justify-center space-x-6 pt-6 text-sm text-gray-500">
              <div className="flex items-center space-x-2">
                <FileText className="h-4 w-4" />
                <span>PDF</span>
              </div>
              <div className="flex items-center space-x-2">
                <FileText className="h-4 w-4" />
                <span>DOCX</span>
              </div>
              <div className="flex items-center space-x-2">
                <FileText className="h-4 w-4" />
                <span>TXT</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Why Choose AI Legal Co-Pilot?
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Experience the future of legal document analysis with cutting-edge AI technology
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group bg-white p-8 rounded-3xl shadow-sm border border-gray-100 hover:shadow-lg hover:border-blue-200 transition-all duration-300 hover:-translate-y-1"
            >
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 w-14 h-14 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <feature.icon className="h-7 w-7 text-blue-600" />
              </div>
              <h3 className="font-bold text-gray-900 mb-3 text-lg">{feature.title}</h3>
              <p className="text-gray-600 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Capabilities Section */}
      <div className="bg-white/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-20">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
                Comprehensive Legal Analysis
              </h2>
              <p className="text-xl text-gray-600 mb-8 leading-relaxed">
                Our AI understands legal language and provides detailed analysis across multiple dimensions of your documents.
              </p>
              
              <div className="space-y-4">
                {capabilities.map((capability, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                    <span className="text-gray-700 font-medium">{capability}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-gray-50 to-blue-50/30 rounded-3xl p-8 border border-gray-200">
              <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
                <MessageSquare className="h-5 w-5 text-blue-600" />
                <span>Ask Anything About Your Document</span>
              </h3>
              <div className="space-y-4">
                {exampleQuestions.map((question, index) => (
                  <div
                    key={index}
                    className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-200"
                  >
                    <p className="text-gray-700 font-medium">"{question}"</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Final CTA Section */}
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-3xl p-12 text-center text-white relative overflow-hidden">
          <div className="absolute inset-0 bg-black/10"></div>
          <div className="relative">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Ready to Transform Your Legal Workflow?
            </h2>
            <p className="text-xl mb-8 text-blue-100 max-w-2xl mx-auto">
              Join thousands of legal professionals who trust AI Legal Co-Pilot for document analysis
            </p>
            <button
              onClick={onGetStarted}
              className="inline-flex items-center space-x-3 bg-white text-blue-600 px-8 py-4 rounded-2xl text-lg font-semibold hover:bg-gray-50 transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              <Upload className="h-5 w-5" />
              <span>Upload Your First Document</span>
              <ArrowRight className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen;