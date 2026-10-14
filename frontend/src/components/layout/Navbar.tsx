import React from 'react';
import { Zap, Layers, UserCog, BarChart3, PanelRight, Plus, LogOut } from 'lucide-react';

interface NavbarProps {
  currentTab: 'pipeline' | 'profile' | 'analytics';
  onTabChange: (tab: 'pipeline' | 'profile' | 'analytics') => void;
  onToggleTriage: () => void;
  onImportClick: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onTabChange,
  onToggleTriage,
  onImportClick,
}) => {
  return (
    <nav className="bg-gray-900 border-b border-gray-800 h-16 flex items-center justify-between px-6 shrink-0 z-20 relative shadow-sm">
      <div className="flex items-center space-x-8">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Zap className="text-white w-4 h-4 fill-current" />
          </div>
          <span className="text-xl font-black tracking-tight text-white">Jobflow</span>
        </div>

        <div className="hidden md:flex space-x-1">
          <button
            onClick={() => onTabChange('pipeline')}
            className={`px-4 py-2 rounded-lg font-bold text-sm transition flex items-center ${
              currentTab === 'pipeline'
                ? 'bg-gray-800 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
          >
            <Layers className="w-4 h-4 mr-2" />
            Pipeline
          </button>
          <button
            onClick={() => onTabChange('profile')}
            className={`px-4 py-2 rounded-lg font-bold text-sm transition flex items-center ${
              currentTab === 'profile'
                ? 'bg-gray-800 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
          >
            <UserCog className="w-4 h-4 mr-2" />
            Master Profile
          </button>
          <button
            onClick={() => onTabChange('analytics')}
            className={`px-4 py-2 rounded-lg font-bold text-sm transition flex items-center ${
              currentTab === 'analytics'
                ? 'bg-gray-800 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            Analytics
          </button>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <button
          onClick={onToggleTriage}
          className="hidden md:flex bg-gray-800 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-lg text-sm transition shadow-sm border border-gray-700 items-center"
        >
          <PanelRight className="w-4 h-4 mr-2 text-blue-400" />
          Toggle Triage
        </button>
        <button
          onClick={onImportClick}
          className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded-lg text-sm transition shadow-lg shadow-blue-900/20 flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          Import Job
        </button>
        <div className="h-6 w-px bg-gray-700"></div>
        <a
          href="/auth/logout"
          className="text-gray-400 hover:text-white text-sm font-bold transition flex items-center"
        >
          <LogOut className="w-4 h-4 mr-1" />
          Logout
        </a>
      </div>
    </nav>
  );
};
