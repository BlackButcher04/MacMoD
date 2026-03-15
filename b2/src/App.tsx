import { useState } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { DashboardHome } from './components/dashboard/DashboardHome';
import { MachineFleet } from './components/dashboard/MachineFleet';
import { Maintenance } from './components/dashboard/Maintenance';
import { Reports } from './components/dashboard/Reports';
import { Settings } from './components/dashboard/Settings';
import { Account } from './components/dashboard/Account';
import { Toaster } from './components/ui/sonner';
import { toast } from 'sonner@2.0.3';
import { Machine, UserAccount, MaintenanceRecord, AnomalyThresholdSettings, LogEntry } from './types';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from './components/ui/dialog';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Button } from './components/ui/button';
import { LoginForm } from './components/auth/LoginForm';

type ActiveTab = 'home' | 'machines' | 'maintenance' | 'reports' | 'settings' | 'account';

const INITIAL_MACHINES: Machine[] = [
  {
    id: 'm1',
    name: 'CNC Milling Machine Alpha',
    type: 'Milling',
    startDate: '2020-05-12',
    repairs: 2,
    status: 'Warning',
    currentCycle: 220,
    failureCycle: 250,
    healthScore: 45,
    rmse: 1.24,
    regime: 'STABLE',
    alertThreshold: 30,
    spareParts: [
      { id: 'p1', name: 'Spindle Bearing', health: 85, needsRepair: false, status: 'Healthy', lastReplaced: '2023-01-15', temperature: 45, vibration: 2.1 },
      { id: 'p2', name: 'Coolant Pump', health: 18, needsRepair: true, status: 'Warning', lastReplaced: '2021-11-20', temperature: 78, vibration: 5.4 },
    ]
  },
  {
    id: 'm2',
    name: 'Hydraulic Press Beta',
    type: 'Press',
    startDate: '2018-11-23',
    repairs: 5,
    status: 'Critical',
    currentCycle: 310,
    failureCycle: 325,
    healthScore: 12,
    rmse: 2.15,
    regime: 'IMPAIRED',
    alertThreshold: 40,
    spareParts: [
      { id: 'p3', name: 'Hydraulic Seal', health: 5, needsRepair: true, status: 'Critical', lastReplaced: '2022-04-10', temperature: 85, vibration: 1.2 },
      { id: 'p4', name: 'Pressure Valve', health: 92, needsRepair: false, status: 'Healthy', lastReplaced: '2023-08-05', temperature: 50, vibration: 0.8 },
      { id: 'p5', name: 'Control Board', health: 15, needsRepair: true, status: 'Critical', lastReplaced: '2019-02-28', temperature: 65, vibration: 0.5 },
    ]
  },
  {
    id: 'm3',
    name: 'Industrial Lathe Gamma',
    type: 'Lathe',
    startDate: '2021-02-10',
    repairs: 1,
    status: 'Healthy',
    currentCycle: 120,
    failureCycle: 280,
    healthScore: 88,
    rmse: 0.95,
    regime: 'STABLE',
    alertThreshold: 50,
    spareParts: [
      { id: 'p6', name: 'Chuck Jaw', health: 90, needsRepair: false, status: 'Healthy', lastReplaced: '2023-05-12', temperature: 38, vibration: 1.5 },
      { id: 'p7', name: 'Tailstock Quill', health: 85, needsRepair: false, status: 'Healthy', lastReplaced: '2022-09-18', temperature: 40, vibration: 1.1 },
    ]
  }
];

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activeTab, setActiveTab] = useState<ActiveTab>('home');
  const [machines, setMachines] = useState<Machine[]>(INITIAL_MACHINES);
  
  // Account State
  const [accounts, setAccounts] = useState<UserAccount[]>([
    { id: '1', name: 'Factory Manager', email: 'manager@sme-factory.com', position: 'Factory Admin' }
  ]);
  const [activeAccountId, setActiveAccountId] = useState('1');
  const [showAddAccount, setShowAddAccount] = useState(false);
  const [newAccountForm, setNewAccountForm] = useState({ username: '', email: '', password: '', position: '' });
  const [systemLogs, setSystemLogs] = useState<LogEntry[]>([
    { id: 'l1', userId: 'system', userName: 'System', action: 'Lathe D crossed vibration threshold', timestamp: new Date(Date.now() - 7200000).toISOString(), type: 'alert_critical', machine: 'Industrial Lathe D' },
    { id: 'l2', userId: '1', userName: 'Factory Manager', action: 'Scheduled predictive maintenance', timestamp: new Date(Date.now() - 14400000).toISOString(), type: 'maintenance_scheduled', machine: 'Hydraulic Press B' },
    { id: 'l3', userId: 'system', userName: 'System', action: 'RUL estimation model retrained (RMSE: 1.2)', timestamp: new Date(Date.now() - 172800000).toISOString(), type: 'model_updated', machine: 'System Core' }
  ]);
  const [maintenanceRecords, setMaintenanceRecords] = useState<any[]>([]);

  const addLog = (action: string, type: LogEntry['type'], machine?: string) => {
    const newLog: LogEntry = {
      id: `l${Date.now()}`,
      userId: activeAccount.id,
      userName: activeAccount.name,
      action,
      timestamp: new Date().toISOString(),
      type,
      machine
    };
    setSystemLogs(prev => [newLog, ...prev]);
  };

  const activeAccount = accounts.find(a => a.id === activeAccountId) || accounts[0];

  const handleLogin = (accountId: string) => {
    setActiveAccountId(accountId);
    setIsAuthenticated(true);
    
    const acc = accounts.find(a => a.id === accountId);
    
    // Add login log
    if (acc) {
      const newLog: LogEntry = {
        id: `l${Date.now()}`,
        userId: acc.id,
        userName: acc.name,
        action: 'Logged into MacMod Dashboard',
        timestamp: new Date().toISOString(),
        type: 'user_action'
      };
      setSystemLogs(prev => [newLog, ...prev]);
    }
    
    if (acc && acc.position === 'Factory Admin') {
      setActiveTab('account');
    } else {
      setActiveTab('home');
    }
  };

  const handleRegister = (newAccount: UserAccount) => {
    setAccounts(prev => [...prev, newAccount]);
    setActiveAccountId(newAccount.id);
    setIsAuthenticated(true);
    
    const newLog: LogEntry = {
      id: `l${Date.now()}`,
      userId: newAccount.id,
      userName: newAccount.name,
      action: 'Registered new MacMod account',
      timestamp: new Date().toISOString(),
      type: 'user_action'
    };
    setSystemLogs(prev => [newLog, ...prev]);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setActiveTab('home');
    toast.success('Logged out successfully.');
  };

  const handleTabChange = (tab: string) => {
    setActiveTab(tab as ActiveTab);
  };

  const handleRepairPart = (machineId: string, partId: string, startDate?: string, endDate?: string) => {
    setMachines(prev => prev.map(m => {
      if (m.id !== machineId) return m;
      
      const updatedParts = m.spareParts.map(p => 
        p.id === partId ? { 
          ...p, 
          needsRepair: false, 
          health: 100, 
          status: 'Pending Maintenance' as const, 
          maintenanceSchedule: startDate && endDate ? { start: startDate, end: endDate } : undefined
        } : p
      );

      // If parts still need repair, keep current status, otherwise "Pending Maintenance"
      const stillNeedsRepair = updatedParts.some(p => p.needsRepair);
      const isPending = updatedParts.some(p => p.status === 'Pending Maintenance');
      
      return {
        ...m,
        spareParts: updatedParts,
        status: stillNeedsRepair ? m.status : (isPending ? 'Pending Maintenance' : 'Healthy')
      };
    }));
  };

  const handleAddMachine = (newMachine: Machine) => {
    setMachines(prev => [...prev, newMachine]);
  };

  const handleAddAccount = (e: React.FormEvent) => {
    e.preventDefault();
    const newAccount: UserAccount = {
      id: Date.now().toString(),
      name: newAccountForm.username || newAccountForm.email.split('@')[0],
      email: newAccountForm.email,
      position: newAccountForm.position || 'Operator',
      registeredDate: new Date().toISOString().split('T')[0]
    };
    setAccounts([...accounts, newAccount]);
    
    // Add log before changing active account so it belongs to the previous user?
    // Actually, "New account created and switched" means the new account logs in.
    const newLog: LogEntry = {
      id: `l${Date.now()}`,
      userId: newAccount.id,
      userName: newAccount.name,
      action: 'Account registered and logged in',
      timestamp: new Date().toISOString(),
      type: 'user_action'
    };
    setSystemLogs(prev => [newLog, ...prev]);

    setActiveAccountId(newAccount.id);
    setShowAddAccount(false);
    setNewAccountForm({ username: '', email: '', password: '', position: '' });
    toast.success('New account created and switched successfully.');
  };

  const renderMainContent = () => {
    switch (activeTab) {
      case 'home':
        return <DashboardHome userName={activeAccount.name} machines={machines} onAddMachine={handleAddMachine} systemLogs={systemLogs} addLog={addLog} maintenanceRecords={maintenanceRecords} setMaintenanceRecords={setMaintenanceRecords} />;
      case 'machines':
        return <MachineFleet machines={machines} onRepairPart={handleRepairPart} />;
      case 'maintenance':
        return <Maintenance machines={machines} onRepairPart={handleRepairPart} />;
      case 'reports':
        return <Reports machines={machines} />;
      case 'settings':
        return <Settings />;
      case 'account':
        return <Account account={activeAccount} onAddAccountClick={() => setShowAddAccount(true)} userLogs={systemLogs.filter(l => l.userId === activeAccount.id)} />;
      default:
        return <DashboardHome userName={activeAccount.name} machines={machines} onAddMachine={handleAddMachine} systemLogs={systemLogs} addLog={addLog} maintenanceRecords={maintenanceRecords} setMaintenanceRecords={setMaintenanceRecords} />;
    }
  };

  if (!isAuthenticated) {
    return (
      <>
        <LoginForm accounts={accounts} onLogin={handleLogin} onRegister={handleRegister} />
        <Toaster position="top-right" />
      </>
    );
  }

  return (
    <div className="h-screen flex bg-gray-50">
      <Sidebar
        activeTab={activeTab}
        onTabChange={handleTabChange}
        onLogout={handleLogout}
        userName={activeAccount.name}
        userPosition={activeAccount.position}
        onAddAccount={() => setShowAddAccount(true)}
      />

      <div className="flex-1 overflow-auto">
        {renderMainContent()}
      </div>

      <Toaster position="top-right" />

      <Dialog open={showAddAccount} onOpenChange={setShowAddAccount}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Register New Account</DialogTitle>
            <DialogDescription>Create a new sub-account for another operator or manager.</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleAddAccount} className="space-y-4 mt-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input 
                id="username" 
                type="text" 
                required 
                value={newAccountForm.username}
                onChange={e => setNewAccountForm({...newAccountForm, username: e.target.value})}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input 
                id="email" 
                type="email" 
                required 
                value={newAccountForm.email}
                onChange={e => setNewAccountForm({...newAccountForm, email: e.target.value})}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input 
                id="password" 
                type="password" 
                required 
                value={newAccountForm.password}
                onChange={e => setNewAccountForm({...newAccountForm, password: e.target.value})}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="position">Job Position</Label>
              <Input 
                id="position" 
                placeholder="e.g. Maintenance Technician" 
                required 
                value={newAccountForm.position}
                onChange={e => setNewAccountForm({...newAccountForm, position: e.target.value})}
              />
            </div>
            <DialogFooter className="pt-4">
              <Button type="button" variant="outline" onClick={() => setShowAddAccount(false)}>Cancel</Button>
              <Button type="submit" className="bg-blue-600 hover:bg-blue-700">Create Account</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}