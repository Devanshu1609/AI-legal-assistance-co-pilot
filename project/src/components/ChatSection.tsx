import React, { useState, useRef, useEffect } from 'react';
import { Send, MessageCircle, Loader2, Bot, User, Sparkles } from 'lucide-react';
import { ChatMessage } from '../types/api';

interface ChatSectionProps {
  documentId: string;
}

const ChatSection: React.FC<ChatSectionProps> = ({ documentId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentQuestion.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      type: 'user',
      content: currentQuestion.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setCurrentQuestion('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('https://ai-legal-assistance-co-pilot.onrender.com/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: documentId,
          question: userMessage.content,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get answer');
      }

      const result = await response.json();
      const aiMessage: ChatMessage = {
        type: 'ai',
        content: result.answer,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      setError('Failed to get answer. Please try again.');
      console.error('Chat error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const suggestedQuestions = [
    "What are the key terms and conditions?",
    "Are there any potential legal risks?",
    "Can you explain the complex clauses?",
    "What are your recommendations?",
  ];

  const handleSuggestedQuestion = (question: string) => {
    setCurrentQuestion(question);
  };

  return (
    <div className="bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden sticky top-24">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-8 py-6 border-b border-gray-100">
        <div className="flex items-center space-x-4">
          <div className="bg-gradient-to-br from-blue-500 to-indigo-600 w-12 h-12 rounded-2xl flex items-center justify-center shadow-lg">
            <MessageCircle className="h-6 w-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">
              Ask Questions About Your Document
            </h3>
            <p className="text-gray-600 text-sm">
              Get instant answers powered by AI analysis
            </p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="h-96 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 relative">
              <Bot className="h-10 w-10 text-blue-600" />
              <Sparkles className="h-4 w-4 text-blue-400 absolute -top-1 -right-1" />
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Ready to help!</h4>
            <p className="text-gray-500 leading-relaxed mb-6">
              Ask any questions about your uploaded document. I'll provide detailed answers based on the analysis.
            </p>
            
            {/* Suggested Questions */}
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700 mb-3">Try asking:</p>
              {suggestedQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestedQuestion(question)}
                  className="block w-full text-left p-3 bg-gray-50 hover:bg-blue-50 rounded-xl transition-colors duration-200 text-sm text-gray-700 hover:text-blue-700 border border-gray-200 hover:border-blue-200"
                >
                  "{question}"
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.type === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[85%] flex items-start space-x-3 ${
                message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.type === 'user'
                    ? 'bg-blue-600'
                    : 'bg-gradient-to-br from-gray-100 to-gray-200'
                }`}
              >
                {message.type === 'user' ? (
                  <User className="h-4 w-4 text-white" />
                ) : (
                  <Bot className="h-4 w-4 text-gray-600" />
                )}
              </div>
              
              {/* Message Content */}
              <div
                className={`px-4 py-3 rounded-2xl ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white rounded-br-md'
                    : 'bg-gray-100 text-gray-900 rounded-bl-md'
                }`}
              >
                <div className={`font-medium mb-1 text-xs opacity-75 ${
                  message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}>
                  {message.type === 'user' ? 'You' : 'AI Legal Co-Pilot'}
                </div>
                <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                <Bot className="h-4 w-4 text-gray-600" />
              </div>
              <div className="bg-gray-100 text-gray-900 px-4 py-3 rounded-2xl rounded-bl-md flex items-center space-x-2">
                <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                <span>AI Legal Co-Pilot is thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Message */}
      {error && (
        <div className="px-6 pb-4">
          <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-gray-100 p-6 bg-gray-50/50">
        <form onSubmit={handleSubmit} className="flex space-x-4">
          <div className="flex-1 relative">
            <input
              type="text"
              value={currentQuestion}
              onChange={(e) => setCurrentQuestion(e.target.value)}
              placeholder="Ask a question about your document..."
              className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-white shadow-sm"
              disabled={isLoading}
            />
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
              <MessageCircle className="h-5 w-5 text-gray-400" />
            </div>
          </div>
          <button
            type="submit"
            disabled={!currentQuestion.trim() || isLoading}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-all duration-200 font-medium shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none"
          >
            <Send className="h-4 w-4" />
            <span>Ask</span>
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatSection;