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
      icon: <FileText className="h-4 w-4 text-green-400" />,
    },
    {
      key: "key_points",
      title: "Key Points",
      icon: <Target className="h-4 w-4 text-purple-400" />,
    },
    {
      key: "complex_clauses",
      title: "Complex Clauses Explained",
      icon: <Info className="h-4 w-4 text-orange-400" />,
    },
    {
      key: "risk_assessment",
      title: "Risk Assessment",
      icon: <AlertTriangle className="h-4 w-4 text-red-400" />,
    },
    {
      key: "recommendations",
      title: "Recommendations",
      icon: <Lightbulb className="h-4 w-4 text-yellow-400" />,
    },
    {
      key: "unclear_missing",
      title: "Unclear or Missing Information",
      icon: <AlertTriangle className="h-4 w-4 text-amber-400" />,
    },
    {
      key: "appendix",
      title: "Appendix",
      icon: <Shield className="h-4 w-4 text-gray-400" />,
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
    <div className="flex gap-10 ">

      {/* SIDEBAR */}
      <div className="hidden lg:block w-64 flex-shrink-0 ">

        <div className="sticky top-28 bg-[#21262d] border border-gray-800 rounded-2xl p-6">

          <h3 className="text-xs font-mono text-gray-500 uppercase tracking-wider mb-4">
            Report Sections
          </h3>

          <div className="space-y-2">
            {sections.map((section) => {
              if (!report[section.key]) return null;

              return (
                <button
                  key={section.key}
                  onClick={() => scrollToSection(section.key)}
                  className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-all
                  text-gray-400 hover:text-white hover:bg-gray-800/60"
                >
                  {section.icon}
                  <span className="text-sm">{section.title}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* CONTENT */}
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
              {/* HEADER */}
              <div className="flex items-center space-x-3 mb-5">
                {section.icon}
                <h2 className="text-2xl font-semibold text-white">
                  {section.title}
                </h2>
              </div>

              {/* CARD */}
              <div className="text-sm">

                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    hr: () => null,

                    table: ({ children }) => (
                      <div className="overflow-x-auto my-6">
                        <table className="min-w-full border border-gray-700 rounded-xl overflow-hidden">
                          {children}
                        </table>
                      </div>
                    ),

                    th: ({ children }) => (
                      <th className="px-5 py-3 text-left text-sm font-semibold text-gray-300 bg-[#0a0e1a]">
                        {children}
                      </th>
                    ),

                    td: ({ children }) => (
                      <td className="px-5 py-3 text-sm text-gray-400 border-t border-gray-800">
                        {children}
                      </td>
                    ),

                    ul: ({ children }) => (
                      <ul className="space-y-2 my-4">{children}</ul>
                    ),

                    li: ({ children }) => (
                      <li className="flex items-start space-x-2">
                        <span className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-2"></span>
                        <span className="text-gray-300">{children}</span>
                      </li>
                    ),

                    p: ({ children }) => (
                      <p className="text-gray-300 leading-relaxed mb-4">
                        {children}
                      </p>
                    ),

                    strong: ({ children }) => (
                      <strong className="text-white font-semibold">
                        {children}
                      </strong>
                    ),

                    h3: ({ children }) => (
                      <h3 className="text-lg font-semibold text-white mt-6 mb-3">
                        {children}
                      </h3>
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
