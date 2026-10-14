import React from 'react';
import { Zap, Layers, UserCog, LogOut } from 'lucide-react';

interface NavbarProps {
  currentTab: 'dashboard' | 'profile';
  onTabChange: (tab: 'dashboard' | 'profile') => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onTabChange,
}) => {
  return (
    <nav className="bg-[#111625] border-b border-neutral-800 h-15 flex items-center justify-between px-6 shrink-0 z-30 relative shadow-sm">
      <div className="flex items-center space-x-8">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25">
            <Zap className="text-white w-4 h-4 fill-current" />
          </div>
          <span className="text-lg font-black tracking-tight text-white">Jobflow</span>
        </div>

        <div className="flex space-x-1.5">
          <button
            onClick={() => onTabChange('dashboard')}
            className={`px-3.5 py-1.5 rounded-xl font-bold text-xs transition flex items-center ${
              currentTab === 'dashboard'
                ? 'bg-blue-600/15 border border-blue-500/40 text-blue-400'
                : 'text-neutral-400 hover:text-white hover:bg-neutral-800/60'
            }`}
          >
            <Layers className="w-4 h-4 mr-1.5" />
            Dashboard & Jobs
          </button>
          <button
            onClick={() => onTabChange('profile')}
            className={`px-3.5 py-1.5 rounded-xl font-bold text-xs transition flex items-center ${
              currentTab === 'profile'
                ? 'bg-blue-600/15 border border-blue-500/40 text-blue-400'
                : 'text-neutral-400 hover:text-white hover:bg-neutral-800/60'
            }`}
          >
            <UserCog className="w-4 h-4 mr-1.5" />
            Master Profile
          </button>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <a
          href="/auth/logout"
          className="text-neutral-400 hover:text-red-400 text-xs font-semibold transition flex items-center p-1.5 rounded-lg hover:bg-neutral-800"
          title="Sign out of Jobflow"
        >
          <LogOut className="w-4 h-4 mr-1.5" />
          Logout
        </a>
      </div>
    </nav>
  );
};
