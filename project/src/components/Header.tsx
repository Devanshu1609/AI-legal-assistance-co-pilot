import React from 'react';
import { Scale, Sparkles, Home, Upload } from 'lucide-react';

interface HeaderProps {
  onBackHome?: () => void;
  onUploadNew?: () => void;
  showNav?: boolean; // optional, in case you don't want nav on welcome page
}

const Header: React.FC<HeaderProps> = ({ onBackHome, onUploadNew, showNav = true }) => {
  return (
    <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200/50 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6 py-4 flex flex-col sm:flex-row items-center justify-between">
        {/* Logo */}
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Scale className="h-8 w-8 text-blue-600" />
            <Sparkles className="h-4 w-4 text-blue-400 absolute -top-1 -right-1" />
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            AI Legal Co-Pilot
          </h1>
        </div>

        {/* Navbar */}
        {showNav && (
          <nav className="flex items-center space-x-4 mt-4 sm:mt-0">
            {onBackHome && (
              <button
                onClick={onBackHome}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-xl font-medium text-gray-700 transition"
              >
                <Home className="h-4 w-4" />
                <span>Home</span>
              </button>
            )}
            {onUploadNew && (
              <button
                onClick={onUploadNew}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-xl font-medium text-white transition"
              >
                <Upload className="h-4 w-4" />
                <span>Upload Document</span>
              </button>
            )}
          </nav>
        )}
      </div>
    </header>
  );
};

export default Header;
