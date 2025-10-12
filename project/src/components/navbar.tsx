import React from 'react';
import { Scale, Sparkles, Upload, Home, FileText, Settings, HelpCircle } from 'lucide-react';

interface NavbarProps {
  currentPage: 'welcome' | 'upload' | 'results';
  onNavigate: (page: 'welcome' | 'upload' | 'results') => void;
  hasResults: boolean;
}

const Navbar: React.FC<NavbarProps> = ({ currentPage, onNavigate, hasResults }) => {
  const navItems = [
    {
      id: 'welcome',
      label: 'Home',
      icon: Home,
      available: true,
    },
    {
      id: 'upload',
      label: 'Upload',
      icon: Upload,
      available: true,
    },
    {
      id: 'results',
      label: 'Results',
      icon: FileText,
      available: hasResults,
    },
  ];

  const rightItems = [
    {
      id: 'help',
      label: 'Help',
      icon: HelpCircle,
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: Settings,
    },
  ];

  return (
    <nav className="bg-white/95 backdrop-blur-sm border-b border-gray-200/50 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Scale className="h-8 w-8 text-blue-600" />
              <Sparkles className="h-4 w-4 text-blue-400 absolute -top-1 -right-1" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                AI Legal Co-Pilot
              </h1>
            </div>
          </div>

          {/* Navigation Items */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              const isAvailable = item.available;
              
              return (
                <button
                  key={item.id}
                  onClick={() => isAvailable && onNavigate(item.id as any)}
                  disabled={!isAvailable}
                  className={`
                    inline-flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200
                    ${isActive 
                      ? 'bg-blue-100 text-blue-700 shadow-sm' 
                      : isAvailable 
                      ? 'text-gray-600 hover:text-gray-900 hover:bg-gray-100' 
                      : 'text-gray-400 cursor-not-allowed'
                    }
                  `}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>

          {/* Right Side Items */}
          <div className="flex items-center space-x-1">
            {rightItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  className="inline-flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-all duration-200"
                >
                  <Icon className="h-4 w-4" />
                  <span className="hidden sm:inline">{item.label}</span>
                </button>
              );
            })}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button className="inline-flex items-center justify-center p-2 rounded-xl text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-all duration-200">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden border-t border-gray-200 py-3">
          <div className="flex items-center justify-around">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              const isAvailable = item.available;
              
              return (
                <button
                  key={item.id}
                  onClick={() => isAvailable && onNavigate(item.id as any)}
                  disabled={!isAvailable}
                  className={`
                    flex flex-col items-center space-y-1 px-3 py-2 rounded-xl text-xs font-medium transition-all duration-200
                    ${isActive 
                      ? 'bg-blue-100 text-blue-700' 
                      : isAvailable 
                      ? 'text-gray-600 hover:text-gray-900 hover:bg-gray-100' 
                      : 'text-gray-400 cursor-not-allowed'
                    }
                  `}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;