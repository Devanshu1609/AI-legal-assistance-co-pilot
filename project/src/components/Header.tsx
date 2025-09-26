import React from 'react';
import { Scale, Sparkles } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200/50 sticky top-0 z-50">
      <div className="max-w-4xl mx-auto px-6 py-4">
        <div className="flex items-center justify-center space-x-3">
          <div className="relative">
            <Scale className="h-8 w-8 text-blue-600" />
            <Sparkles className="h-4 w-4 text-blue-400 absolute -top-1 -right-1" />
          </div>
          <div className="text-center">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              AI Legal Co-Pilot
            </h1>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;