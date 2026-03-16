import React, { useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  FileText,
  AlertTriangle,
  Info,
  Target,
  Shield,
  Lightbulb
} from "lucide-react";
import { DocumentReport } from "../types/api";

interface ReportSectionProps {
  report: DocumentReport;
}

const ReportSection: React.FC<ReportSectionProps> = ({ report }) => {

  const sections = [
    {
      key: "executive_summary",
      title: "Executive Summary",
      icon: <FileText className="h-4 w-4 text-green-600" />,
    },
    {
      key: "key_points",
      title: "Key Points",
      icon: <Target className="h-4 w-4 text-purple-600" />,
    },
    {
      key: "complex_clauses",
      title: "Complex Clauses Explained",
      icon: <Info className="h-4 w-4 text-orange-600" />,
    },
    {
      key: "risk_assessment",
      title: "Risk Assessment",
      icon: <AlertTriangle className="h-4 w-4 text-red-600" />,
    },
    {
      key: "recommendations",
      title: "Recommendations",
      icon: <Lightbulb className="h-4 w-4 text-yellow-600" />,
    },
    {
      key: "unclear_missing",
      title: "Unclear or Missing Information",
      icon: <AlertTriangle className="h-4 w-4 text-amber-600" />,
    },
    {
      key: "appendix",
      title: "Appendix",
      icon: <Shield className="h-4 w-4 text-gray-600" />,
    },
  ];

  const sectionRefs: Record<string, any> = {};
  sections.forEach((s) => (sectionRefs[s.key] = useRef<HTMLDivElement>(null)));

  const scrollToSection = (key: string) => {
    sectionRefs[key]?.current?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  };

  return (
    <div className="flex gap-10">

      {/* LEFT SIDEBAR */}
      <div className="hidden lg:block w-64 flex-shrink-0">

        <div className="sticky top-28 bg-white rounded-2xl border border-gray-200 shadow-sm p-6">

          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
            Report Sections
          </h3>

          <div className="space-y-2">
            {sections.map((section) => {
              if (!report[section.key]) return null;

              return (
                <button
                  key={section.key}
                  onClick={() => scrollToSection(section.key)}
                  className="w-full flex items-center space-x-3 text-left px-3 py-2 rounded-lg hover:bg-blue-50 transition-colors group"
                >
                  {section.icon}

                  <span className="text-sm font-medium text-gray-700 group-hover:text-blue-600">
                    {section.title}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* RIGHT CONTENT */}
      <div className="flex-1 max-w-6xl">

        {sections.map((section) => {
          const content = report[section.key];
          if (!content) return null;

          return (
            <div
              key={section.key}
              ref={sectionRefs[section.key]}
              className="mb-16 scroll-mt-28"
            >
              <div className="flex items-center space-x-3 mb-6">
                {section.icon}
                <h2 className="text-2xl font-bold text-gray-900">
                  {section.title}
                </h2>
              </div>

              <div className="bg-white text-m border border-gray-200 rounded-2xl p-8 shadow-sm">

                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    table: ({ children }) => (
                      <div className="overflow-x-auto my-6">
                        <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-xl">
                          {children}
                        </table>
                      </div>
                    ),
                    th: ({ children }) => (
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900 bg-gray-50">
                        {children}
                      </th>
                    ),
                    td: ({ children }) => (
                      <td className="px-6 py-3 text-sm text-gray-700 border-t">
                        {children}
                      </td>
                    ),
                    ul: ({ children }) => (
                      <ul className="space-y-2  my-4">{children}</ul>
                    ),
                    li: ({ children }) => (
                      <li className="flex  items-start space-x-2">
                        <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2"></span>
                        <span>{children}</span>
                      </li>
                    ),
                  }}
                >
                  {content}
                </ReactMarkdown>

              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ReportSection;