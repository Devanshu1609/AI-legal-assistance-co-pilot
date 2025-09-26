import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ChevronDown, ChevronRight, FileText, AlertTriangle, CheckCircle, Info, BookOpen, Target, Shield, Lightbulb } from 'lucide-react';
import { DocumentReport } from '../types/api';

interface ReportSectionProps {
  report: DocumentReport;
}

interface CollapsibleSectionProps {
  title: string;
  content: string;
  defaultOpen?: boolean;
  className?: string;
  icon?: React.ReactNode;
  badge?: string;
}

const CollapsibleSection: React.FC<CollapsibleSectionProps> = ({
  title,
  content,
  defaultOpen = false,
  className = '',
  icon,
  badge,
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className={`bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all duration-200 ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-8 py-6 text-left bg-gradient-to-r from-gray-50/50 to-blue-50/30 hover:from-gray-100/50 hover:to-blue-100/50 transition-all duration-200 flex items-center justify-between group"
      >
        <div className="flex items-center space-x-4">
          {icon && (
            <div className="bg-white w-10 h-10 rounded-xl flex items-center justify-center shadow-sm group-hover:shadow-md transition-shadow">
              {icon}
            </div>
          )}
          <div>
            <h3 className="text-xl font-bold text-gray-900 flex items-center space-x-3">
              <span>{title}</span>
              {badge && (
                <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-medium">
                  {badge}
                </span>
              )}
            </h3>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {isOpen ? (
            <ChevronDown className="h-5 w-5 text-gray-500 group-hover:text-gray-700 transition-colors" />
          ) : (
            <ChevronRight className="h-5 w-5 text-gray-500 group-hover:text-gray-700 transition-colors" />
          )}
        </div>
      </button>
      
      {isOpen && (
        <div className="px-8 py-8 border-t border-gray-100 bg-white">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              table: ({ children }) => (
                <div className="overflow-x-auto my-6">
                  <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                    {children}
                  </table>
                </div>
              ),
              thead: ({ children }) => (
                <thead className="bg-gradient-to-r from-gray-50 to-blue-50">{children}</thead>
              ),
              tbody: ({ children }) => (
                <tbody className="bg-white divide-y divide-gray-200">
                  {children}
                </tbody>
              ),
              tr: ({ children }) => (
                <tr className="hover:bg-gray-50/50 transition-colors">{children}</tr>
              ),
              th: ({ children }) => (
                <th className="px-6 py-4 text-left text-sm font-bold text-gray-900 uppercase tracking-wider border-b border-gray-200">
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td className="px-6 py-4 text-sm text-gray-700 border-b border-gray-100">
                  {children}
                </td>
              ),
              h1: ({ children }) => (
                <h1 className="text-2xl font-bold text-gray-900 mb-4 pb-2 border-b border-gray-200">{children}</h1>
              ),
              h2: ({ children }) => (
                <h2 className="text-xl font-bold text-gray-900 mb-3 mt-6">{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-lg font-semibold text-gray-900 mb-2 mt-4">{children}</h3>
              ),
              ul: ({ children }) => (
                <ul className="space-y-2 my-4">{children}</ul>
              ),
              li: ({ children }) => (
                <li className="flex items-start space-x-2">
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                  <span>{children}</span>
                </li>
              ),
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-blue-500 pl-6 py-2 my-4 bg-blue-50/50 rounded-r-lg">
                  {children}
                </blockquote>
              ),
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
};

const ReportSection: React.FC<ReportSectionProps> = ({ report }) => {
  const sections = [
    {
      key: 'table_of_contents',
      title: 'Table of Contents',
      icon: <BookOpen className="h-5 w-5 text-blue-600" />,
      defaultOpen: true,
      badge: 'Overview',
    },
    {
      key: 'executive_summary',
      title: 'Executive Summary',
      icon: <FileText className="h-5 w-5 text-green-600" />,
      defaultOpen: true,
      badge: 'Key Insights',
    },
    {
      key: 'key_points',
      title: 'Key Points',
      icon: <Target className="h-5 w-5 text-purple-600" />,
      defaultOpen: false,
      badge: 'Important',
    },
    {
      key: 'complex_clauses',
      title: 'Complex Clauses Explained',
      icon: <Info className="h-5 w-5 text-orange-600" />,
      defaultOpen: false,
      badge: 'Analysis',
    },
    {
      key: 'risk_assessment',
      title: 'Risk Assessment',
      icon: <AlertTriangle className="h-5 w-5 text-red-600" />,
      defaultOpen: false,
      badge: 'Critical',
    },
    {
      key: 'recommendations',
      title: 'Recommendations',
      icon: <Lightbulb className="h-5 w-5 text-yellow-600" />,
      defaultOpen: false,
      badge: 'Action Items',
    },
    {
      key: 'unclear_missing',
      title: 'Unclear or Missing Information',
      icon: <AlertTriangle className="h-5 w-5 text-amber-600" />,
      defaultOpen: false,
      badge: 'Review Needed',
    },
    {
      key: 'appendix',
      title: 'Appendix (Method & Sources)',
      icon: <Shield className="h-5 w-5 text-gray-600" />,
      defaultOpen: false,
      badge: 'Reference',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl shadow-xl border border-blue-200 p-8 text-white relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute top-0 right-0 w-40 h-40 bg-white/10 rounded-full -translate-y-20 translate-x-20"></div>
        <div className="absolute bottom-0 left-0 w-32 h-32 bg-white/10 rounded-full translate-y-16 -translate-x-16"></div>
        
        <div className="relative">
          <div className="flex items-center space-x-4 mb-6">
            <div className="bg-white/20 w-16 h-16 rounded-2xl flex items-center justify-center backdrop-blur-sm">
              <CheckCircle className="h-8 w-8 text-white" />
            </div>
            <div>
              <h2 className="text-4xl font-bold mb-2">
                Analysis Complete
              </h2>
              <p className="text-blue-100 text-lg">
                Comprehensive AI-powered analysis of your legal document
              </p>
            </div>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6 mt-8">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20">
              <div className="text-2xl font-bold mb-1">{sections.filter(s => report[s.key]).length}</div>
              <div className="text-blue-100 text-sm">Sections Analyzed</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20">
              <div className="text-2xl font-bold mb-1">AI-Powered</div>
              <div className="text-blue-100 text-sm">Advanced Analysis</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20">
              <div className="text-2xl font-bold mb-1">Ready</div>
              <div className="text-blue-100 text-sm">For Review</div>
            </div>
          </div>
        </div>
      </div>

      {/* Report Sections */}
      {sections.map((section) => {
        const content = report[section.key];
        if (!content) return null;

        return (
          <CollapsibleSection
            key={section.key}
            title={section.title}
            content={content}
            defaultOpen={section.defaultOpen}
            icon={section.icon}
            badge={section.badge}
          />
        );
      })}
    </div>
  );
};

export default ReportSection;