import { cn } from '../ui/utils';
import { Button } from '../ui/button';
import { 
  Home, 
  Settings,
  Activity,
  LogOut,
  Wrench,
  BarChart3,
  MonitorPlay
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  onLogout: () => void;
  userName: string;
  userPosition: string;
  onAddAccount: () => void;
}

const navigation = [
  { id: 'home', label: 'Dashboard', icon: Home },
  { id: 'machines', label: 'Machines', icon: MonitorPlay },
  { id: 'maintenance', label: 'Maintenance', icon: Wrench },
  { id: 'reports', label: 'Reports', icon: BarChart3 },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export function Sidebar({ activeTab, onTabChange, onLogout, userName, userPosition, onAddAccount }: SidebarProps) {
  return (
    <div className="w-64 bg-slate-900 text-white flex flex-col h-full">
      {/* Logo and Brand */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg relative overflow-hidden">
            <Activity className="w-5 h-5 text-white absolute" strokeWidth={3} />
          </div>
          <div>
            <h1 className="font-bold text-lg leading-tight tracking-tight">MacMod</h1>
            <p className="text-xs text-blue-400 font-medium">Predictive Maintenance</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.id}>
                <Button
                  variant="ghost"
                  className={cn(
                    "w-full justify-start gap-3 h-10 text-slate-300 hover:text-white hover:bg-slate-800",
                    activeTab === item.id && "bg-slate-800 text-white"
                  )}
                  onClick={() => onTabChange(item.id)}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* User Profile and Logout */}
      <div className="p-4 border-t border-slate-700">
        <div 
          className="flex items-center gap-3 mb-4 cursor-pointer hover:bg-slate-800 p-2 rounded-lg transition-colors w-full text-left"
          onClick={() => onTabChange('account')}
        >
          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center shrink-0">
            <span className="text-sm font-bold text-white">
              {userName.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2)}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate text-slate-200">{userName}</p>
            <p className="text-xs text-blue-400 font-medium truncate">{userPosition}</p>
          </div>
        </div>

        <Button
          variant="ghost"
          className="w-full justify-start gap-3 h-10 text-slate-300 hover:text-white hover:bg-slate-800"
          onClick={onLogout}
        >
          <LogOut className="w-4 h-4" />
          Logout
        </Button>
      </div>
    </div>
  );
}