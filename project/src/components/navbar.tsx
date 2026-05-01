import React, { useState } from "react";
import {
  Scale,
  Sparkles,
  Upload,
  Home,
  FileText,
  Settings,
  HelpCircle,
  LogOut,
  MessageSquare,
} from "lucide-react";

interface NavbarProps {
  currentPage: "welcome" | "upload" | "results" | "chat";
  onNavigate: (
    page: "welcome" | "upload" | "results" | "chat"
  ) => void;
  hasResults: boolean;
  isLoggedIn: boolean;
  user: any;
  onLogout: () => void;
}

const Navbar: React.FC<NavbarProps> = ({
  currentPage,
  onNavigate,
  hasResults,
  isLoggedIn,
  user,
  onLogout,
}) => {
  const [showSettings, setShowSettings] = useState(false);

  const navItems = [
    {
      id: "welcome",
      label: "Home",
      icon: Home,
      available: true,
    },
    {
      id: "upload",
      label: "Workspace",
      icon: Upload,
      available: isLoggedIn,
    },
    {
      id: "results",
      label: "Analysis",
      icon: FileText,
      available: isLoggedIn && hasResults,
    },
    {
      id: "chat",
      label: "Assistant",
      icon: MessageSquare,
      available: isLoggedIn,
    },
  ];

  return (
    <nav className="bg-[#0a0e1a]/80 backdrop-blur-md border-b border-gray-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">

          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Scale className="h-7 w-7 text-blue-400" />
              <Sparkles className="h-3 w-3 text-cyan-400 absolute -top-1 -right-1" />
            </div>

            <h1 className="text-lg font-semibold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              AI Legal Co-Pilot
            </h1>
          </div>

          {/* Navigation */}
          <div className="hidden md:flex items-center space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;

              return (
                <button
                  key={item.id}
                  onClick={() =>
                    item.available &&
                    onNavigate(item.id as any)
                  }
                  disabled={!item.available}
                  className={`px-4 py-2 rounded-xl transition
                  ${
                    currentPage === item.id
                      ? "bg-blue-500/10 text-blue-400 border border-blue-500/30"
                      : item.available
                      ? "text-gray-400 hover:text-white hover:bg-gray-800/60"
                      : "text-gray-600 cursor-not-allowed"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-3 relative">

            {/* Profile */}
            {isLoggedIn && user?.photoURL && (
              <img
                src={user.photoURL}
                alt="profile"
                className="w-9 h-9 rounded-full border border-blue-500"
              />
            )}

            {/* Settings */}
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="text-gray-400 hover:text-white"
            >
              <Settings className="h-5 w-5" />
            </button>

            {/* Settings Dropdown */}
            {showSettings && isLoggedIn && (
              <div className="absolute top-14 right-0 w-44 bg-[#111827] border border-gray-700 rounded-xl shadow-xl p-2 z-50">
                <button
                  onClick={onLogout}
                  className="w-full flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-700 transition"
                >
                  <LogOut className="h-4 w-4 text-red-400" />
                  Logout
                </button>
              </div>
            )}

            {/* Help */}
            <button className="text-gray-400 hover:text-white">
              <HelpCircle className="h-5 w-5" />
            </button>

          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;