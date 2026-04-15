import React from 'react';
import {
  Scale,
  Sparkles,
  Upload,
  Home,
  FileText,
  Settings,
  HelpCircle
} from 'lucide-react';

interface NavbarProps {
  currentPage: 'welcome' | 'upload' | 'results';
  onNavigate: (page: 'welcome' | 'upload' | 'results') => void;
  hasResults: boolean;
}

const Navbar: React.FC<NavbarProps> = ({ currentPage, onNavigate, hasResults }) => {

  const navItems = [
    { id: 'welcome', label: 'Home', icon: Home, available: true },
    { id: 'upload', label: 'Upload', icon: Upload, available: true },
    { id: 'results', label: 'Results', icon: FileText, available: hasResults },
  ];

  const rightItems = [
    { id: 'help', label: 'Help', icon: HelpCircle },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <nav className="bg-[#0a0e1a]/80 backdrop-blur-md border-b border-gray-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        <div className="flex items-center justify-between h-16">

          {/* LOGO */}
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Scale className="h-7 w-7 text-blue-400" />
              <Sparkles className="h-3 w-3 text-cyan-400 absolute -top-1 -right-1" />
            </div>

            <h1 className="text-lg font-semibold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              AI Legal Co-Pilot
            </h1>
          </div>

          {/* NAV ITEMS */}
          <div className="hidden md:flex items-center space-x-2">
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
                      ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30 shadow-sm'
                      : isAvailable
                        ? 'text-gray-400 hover:text-white hover:bg-gray-800/60'
                        : 'text-gray-600 cursor-not-allowed'
                    }
                  `}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>

          {/* RIGHT SIDE */}
          <div className="flex items-center space-x-2">
            {rightItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  className="inline-flex items-center space-x-2 px-3 py-2 rounded-xl text-sm text-gray-400 hover:text-white hover:bg-gray-800/60 transition-all duration-200"
                >
                  <Icon className="h-4 w-4" />
                  <span className="hidden sm:inline">{item.label}</span>
                </button>
              );
            })}
          </div>

          {/* MOBILE BUTTON */}
          <div className="md:hidden">
            <button className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800 transition">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* MOBILE NAV */}
        <div className="md:hidden border-t border-gray-800 py-3">
          <div className="flex justify-around">
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
                    flex flex-col items-center space-y-1 px-3 py-2 rounded-xl text-xs transition-all
                    ${isActive
                      ? 'text-blue-400'
                      : isAvailable
                        ? 'text-gray-400 hover:text-white'
                        : 'text-gray-600'
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

