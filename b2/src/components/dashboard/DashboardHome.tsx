import { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '../ui/dialog';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { toast } from 'sonner@2.0.3';
import { Machine, SparePart, LogEntry } from '../../types';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Textarea } from '../ui/textarea';
import { 
  Activity, 
  Settings, 
  Wrench,
  AlertTriangle,
  Calendar,
  TrendingDown,
  Clock,
  Database,
  CheckCircle,
  AlertCircle,
  Plus,
  Cpu,
  LineChart,
  BarChart,
  Server,
  Trash2,
  Upload
} from 'lucide-react';

interface DashboardHomeProps {
  userName: string;
  machines: Machine[];
  onAddMachine: (m: Machine) => void;
  systemLogs: LogEntry[];
  addLog: (action: string, type: LogEntry['type'], machine?: string) => void;
  maintenanceRecords: any[];
  setMaintenanceRecords: (records: any[]) => void;
}

export function DashboardHome({ userName, machines, onAddMachine, systemLogs, addLog, maintenanceRecords, setMaintenanceRecords }: DashboardHomeProps) {
  const [selectedMachine, setSelectedMachine] = useState<Machine | null>(null);
  const [showAddMachine, setShowAddMachine] = useState(false);
  
  // Upload File State
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  
  // Anomaly Threshold State
  const [showThresholdDialog, setShowThresholdDialog] = useState(false);
  const [thresholdSettings, setThresholdSettings] = useState({
    alertThreshold: 30,
    anomalyZScore: 3.5,
    agePenalty: 1.5,
    temporalWindow: 14
  });
  
  // Schedule Maintenance State
  const [showScheduleDialog, setShowScheduleDialog] = useState(false);
  const [scheduleForm, setScheduleForm] = useState({
    machine: '',
    description: '',
    scheduledDate: '',
    priority: 'medium' as 'low' | 'medium' | 'high'
  });
  
  // Add Machine Form State
  const [newMachineForm, setNewMachineForm] = useState({ name: '', type: '' });
  const [newMachineSensors, setNewMachineSensors] = useState<string[]>([]);
  const [newSensorInput, setNewSensorInput] = useState('');
  const [newSpareParts, setNewSpareParts] = useState<{name: string, sensors: string[]}[]>([]);
  const [newSparePartName, setNewSparePartName] = useState('');
  const [newSparePartSensor, setNewSparePartSensor] = useState('');
  const [currentSparePartSensors, setCurrentSparePartSensors] = useState<string[]>([]);
  // MacMod Predictive Maintenance Data
  const systemStats = {
    totalMachines: machines.length,
    activeSensors: machines.reduce((acc, m) => acc + (m.sensors?.length || 0) + m.spareParts.reduce((pAcc, p) => pAcc + (p.sensors?.length || 2), 0), 156),
    maintenancePending: machines.filter(m => m.status === 'Pending Maintenance' || m.spareParts.some(p => p.status === 'Pending Maintenance')).length,
    criticalAlerts: machines.filter(m => m.status === 'Critical').length
  };

  const handleAddMachineSubmit = () => {
    if (!newMachineForm.name || !newMachineForm.type) {
      toast.error('Please provide machine name and type.');
      return;
    }
    
    const newMachine: Machine = {
      id: `m${Date.now()}`,
      name: newMachineForm.name,
      type: newMachineForm.type,
      startDate: new Date().toISOString().split('T')[0],
      repairs: 0,
      status: 'Healthy',
      currentCycle: 0,
      failureCycle: 300,
      healthScore: 100,
      rmse: 0.5,
      regime: 'STABLE',
      alertThreshold: 40,
      sensors: newMachineSensors,
      spareParts: newSpareParts.map((sp, idx) => ({
        id: `p${Date.now()}${idx}`,
        name: sp.name,
        health: 100,
        needsRepair: false,
        status: 'Healthy',
        lastReplaced: new Date().toISOString().split('T')[0],
        temperature: 40,
        vibration: 1.0,
        sensors: sp.sensors
      }))
    };
    
    onAddMachine(newMachine);
    addLog(`Uploaded new machine: ${newMachine.name}`, 'user_action', newMachine.name);
    toast.success('Machine and spare parts added successfully!');
    setShowAddMachine(false);
    
    // Reset form
    setNewMachineForm({ name: '', type: '' });
    setNewMachineSensors([]);
    setNewSpareParts([]);
  };

  const scheduledMaintenance = [
    ...machines.flatMap(m => 
      m.spareParts
        .filter(p => p.maintenanceSchedule)
        .map(p => ({
          task: `Repair ${p.name} on ${m.name}`,
          priority: 'high',
          dueDate: p.maintenanceSchedule!.start,
          endDate: p.maintenanceSchedule!.end
        }))
    ),
    ...maintenanceRecords
  ].sort((a, b) => new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime());

  const formatTimeAgo = (timestamp: string) => {
    const diff = Date.now() - new Date(timestamp).getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return 'Just now';
  };

  const actionItems = [
    { 
      task: 'Dispatch technician for Lathe D repair', 
      priority: 'high',
      dueDate: '2023-12-14'
    },
    { 
      task: 'Order replacement bearing for Press B', 
      priority: 'medium',
      dueDate: '2023-12-15'
    },
    { 
      task: 'Review weekly RUL degradation report', 
      priority: 'low',
      dueDate: '2023-12-17'
    }
  ];

  const modelMetrics = {
    totalPredictions: '23.4k',
    accuracy: '94.2%',
    avgRmse: '1.4',
    anomaliesDetected: 18,
    preventedFailures: 5
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'alert_critical':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'maintenance_scheduled':
        return <Wrench className="w-4 h-4 text-orange-500" />;
      case 'sensor_calibrated':
        return <Settings className="w-4 h-4 text-blue-500" />;
      case 'model_updated':
        return <Database className="w-4 h-4 text-green-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'destructive';
      case 'medium': return 'secondary';
      case 'low': return 'outline';
      default: return 'secondary';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Healthy': return 'bg-green-100 text-green-800 border-green-200';
      case 'Warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'Pending Maintenance': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Welcome Header */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Welcome back, {userName}!</h1>
        <p className="text-gray-600 mt-1">Here is the real-time health overview of your industrial assets.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Machines</p>
                <p className="text-2xl font-semibold text-gray-900">{systemStats.totalMachines}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Server className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Sensors Monitored</p>
                <p className="text-2xl font-semibold text-gray-900">{systemStats.activeSensors}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Cpu className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Pending Maintenance</p>
                <p className="text-2xl font-semibold text-gray-900">{systemStats.maintenancePending}</p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Wrench className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Critical Alerts</p>
                <p className="text-2xl font-semibold text-gray-900">{systemStats.criticalAlerts}</p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
        {/* Monitored Machines */}
        <Card className="h-full flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Asset Health & RUL
            </CardTitle>
            <p className="text-sm text-gray-600">Real-time Remaining Useful Life estimates</p>
          </CardHeader>
          <CardContent className="space-y-4 flex-1">
            {machines.map((machine) => (
              <div 
                key={machine.id} 
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-blue-50 transition-colors cursor-pointer"
                onClick={() => setSelectedMachine(machine)}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium">{machine.name}</h4>
                    <Badge variant="outline" className={`text-xs ${getStatusColor(machine.status)}`}>
                      {machine.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-1">
                    Estimated RUL: <span className="font-semibold">{Math.max(0, machine.failureCycle - machine.currentCycle)} cycles</span>
                  </p>
                  <p className="text-xs text-gray-500">
                    Health: {machine.healthScore}% | Spare parts: {machine.spareParts.length}
                  </p>
                </div>
                <div className="text-right pl-4">
                  <p className="text-sm font-medium">Type</p>
                  <p className="text-xs text-gray-600 mt-1">{machine.type}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="h-full flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Plus className="w-5 h-5" />
              Quick Actions
            </CardTitle>
            <p className="text-sm text-gray-600">Common management tasks</p>
          </CardHeader>
          <CardContent className="space-y-3 flex-1 flex flex-col justify-start">
            <input 
              type="file" 
              ref={fileInputRef} 
              className="hidden" 
              onChange={(e) => {
                if (e.target.files && e.target.files.length > 0) {
                  const filename = e.target.files[0].name;
                  toast.success(`Uploading ${filename}... AI model retraining initiated.`);
                  addLog(`Uploaded raw telemetry file: ${filename}`, 'model_updated');
                  e.target.value = '';
                }
              }} 
            />
            <Button variant="outline" className="w-full justify-start gap-2" onClick={() => fileInputRef.current?.click()}>
              <Database className="w-4 h-4" />
              Upload Factory Raw Data
            </Button>
            <Button variant="outline" className="w-full justify-start gap-2" onClick={() => setShowAddMachine(true)}>
              <Cpu className="w-4 h-4" />
              Upload Machine & Spare Parts
            </Button>
            <Button variant="outline" className="w-full justify-start gap-2" onClick={() => setShowScheduleDialog(true)}>
              <Wrench className="w-4 h-4" />
              Schedule Maintenance
            </Button>
            <Button variant="outline" className="w-full justify-start gap-2" onClick={() => setShowThresholdDialog(true)}>
              <Settings className="w-4 h-4" />
              Adjust Anomaly Thresholds
            </Button>
            <Button variant="outline" className="w-full justify-start gap-2">
              <Calendar className="w-4 h-4" />
              View Facility Calendar
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activities */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              System Logs
            </CardTitle>
            <p className="text-sm text-gray-600">Recent anomaly detections and events</p>
          </CardHeader>
          <CardContent className="space-y-3">
            {systemLogs.map((log) => (
              <div key={log.id} className="flex items-start gap-3 p-3 border rounded-lg">
                <div className="mt-1">
                  {getActivityIcon(log.type)}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">{log.action}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <p className="text-xs text-gray-500">{formatTimeAgo(log.timestamp)} by {log.userName}</p>
                    {log.machine && (
                      <>
                        <span className="text-xs text-gray-400">•</span>
                        <p className="text-xs text-gray-500">{log.machine}</p>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Scheduled Maintenance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Scheduled Maintenance
            </CardTitle>
            <p className="text-sm text-gray-600">Upcoming predictive repairs</p>
          </CardHeader>
          <CardContent className="space-y-3">
            {scheduledMaintenance.length > 0 ? scheduledMaintenance.map((item, index) => (
              <div key={index} className="flex items-start justify-between p-3 border rounded-lg bg-blue-50/50">
                <div className="flex-1 pr-4">
                  <p className="text-sm font-medium">{item.task}</p>
                  <p className="text-xs text-blue-600 mt-1 font-medium">
                    Scheduled: {item.dueDate} to {item.endDate}
                  </p>
                </div>
                <Badge variant="outline" className="text-xs capitalize shrink-0 bg-blue-100 text-blue-800 border-blue-200">
                  Pending
                </Badge>
              </div>
            )) : (
              <div className="text-center p-6 text-gray-500 text-sm">
                No maintenance scheduled. All systems nominal.
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Resource Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingDown className="w-5 h-5" />
            Model Performance & Impact
          </CardTitle>
          <p className="text-sm text-gray-600">Time-series prediction metrics and ROI</p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <Database className="w-6 h-6 text-blue-600" />
              </div>
              <p className="text-lg font-semibold">{modelMetrics.totalPredictions}</p>
              <p className="text-sm text-gray-600">Predictions</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <p className="text-lg font-semibold">{modelMetrics.accuracy}</p>
              <p className="text-sm text-gray-600">Accuracy</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <BarChart className="w-6 h-6 text-purple-600" />
              </div>
              <p className="text-lg font-semibold">{modelMetrics.avgRmse}</p>
              <p className="text-sm text-gray-600">Avg RMSE</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <AlertTriangle className="w-6 h-6 text-orange-600" />
              </div>
              <p className="text-lg font-semibold">{modelMetrics.anomaliesDetected}</p>
              <p className="text-sm text-gray-600">Anomalies</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <TrendingDown className="w-6 h-6 text-red-600" />
              </div>
              <p className="text-lg font-semibold">{modelMetrics.preventedFailures}</p>
              <p className="text-sm text-gray-600">Prevented Failures</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Live Data Dialog */}
      <Dialog open={!!selectedMachine} onOpenChange={(open) => !open && setSelectedMachine(null)}>
        <DialogContent className="max-w-4xl bg-slate-900 text-white border-slate-800">
          <DialogHeader>
            <DialogTitle className="text-xl flex items-center gap-2 text-blue-400">
              <Activity className="w-5 h-5" />
              LIVE TELEMETRY: {selectedMachine?.name}
            </DialogTitle>
            <DialogDescription className="text-slate-400">
              Real-time sensor feed and diagnostic data
            </DialogDescription>
          </DialogHeader>
          {selectedMachine && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-[1fr_1fr_1fr_auto] gap-4">
                <div className="bg-slate-800 p-4 rounded-lg">
                  <p className="text-xs text-slate-400">ASSET HEALTH</p>
                  <p className="text-2xl font-bold text-emerald-400">{selectedMachine.healthScore}%</p>
                </div>
                <div className="bg-slate-800 p-4 rounded-lg">
                  <p className="text-xs text-slate-400">CURRENT CYCLE</p>
                  <p className="text-2xl font-bold text-blue-400">{selectedMachine.currentCycle}</p>
                </div>
                <div className="bg-slate-800 p-4 rounded-lg">
                  <p className="text-xs text-slate-400">ESTIMATED RUL</p>
                  <p className="text-2xl font-bold text-purple-400">{Math.max(0, selectedMachine.failureCycle - selectedMachine.currentCycle)}</p>
                </div>
                <div className="bg-slate-800 p-4 rounded-lg min-w-0">
  <p className="text-xs text-slate-400 truncate">REGIME STATE</p>
  <p 
    className={`text-lg lg:text-xl font-bold mt-1 tracking-tight truncate ${selectedMachine.regime === 'STABLE' ? 'text-emerald-400' : 'text-red-400'}`}
    title={selectedMachine.regime}
  >
    {selectedMachine.regime}
  </p>
</div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-slate-300 mb-3 border-b border-slate-700 pb-2">SPARE PARTS SUBSYSTEM LIVE DATA</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedMachine.spareParts.map((part) => (
                    <div key={part.id} className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                      <div className="flex justify-between items-center mb-3">
                        <h4 className="font-medium text-blue-300">{part.name}</h4>
                        <Badge variant="outline" className={`
                          ${part.status === 'Healthy' ? 'text-emerald-400 border-emerald-400' : 
                            part.status === 'Pending Maintenance' ? 'text-blue-400 border-blue-400' : 
                            part.status === 'Warning' ? 'text-yellow-400 border-yellow-400' : 
                            'text-red-400 border-red-400'}
                        `}>
                          {part.status}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-3 gap-2">
                        <div>
                          <p className="text-[10px] text-slate-500">HEALTH</p>
                          <p className="text-sm font-mono text-slate-200">{part.health}%</p>
                        </div>
                        <div>
                          <p className="text-[10px] text-slate-500">TEMP</p>
                          <p className="text-sm font-mono text-orange-400">{part.temperature} °C</p>
                        </div>
                        <div>
                          <p className="text-[10px] text-slate-500">VIBE</p>
                          <p className="text-sm font-mono text-cyan-400">{part.vibration} mm/s</p>
                        </div>
                      </div>
                      {part.sensors && part.sensors.length > 0 && (
                        <div className="mt-3 pt-2 border-t border-slate-700/50">
                          <p className="text-[10px] text-slate-500 mb-1">MAPPED SENSORS</p>
                          <div className="flex flex-wrap gap-1">
                            {part.sensors.map(s => (
                              <span key={s} className="text-[10px] bg-slate-900 px-1.5 py-0.5 rounded text-slate-400">{s}</span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Add Machine Dialog */}
      <Dialog open={showAddMachine} onOpenChange={setShowAddMachine}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Upload Machine & Spare Parts</DialogTitle>
            <DialogDescription>
              Register a new machine asset and map telemetry sensors to its spare parts.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 mt-4">
            {/* Machine Details */}
            <div className="space-y-4 p-4 border border-gray-100 rounded-lg bg-gray-50/50">
              <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                <Server className="w-4 h-4 text-blue-600" />
                Machine Information
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Machine Name</Label>
                  <Input placeholder="e.g. Robot Arm X1" value={newMachineForm.name} onChange={e => setNewMachineForm({...newMachineForm, name: e.target.value})} />
                </div>
                <div className="space-y-2">
                  <Label>Machine Type</Label>
                  <Input placeholder="e.g. Assembly" value={newMachineForm.type} onChange={e => setNewMachineForm({...newMachineForm, type: e.target.value})} />
                </div>
              </div>

              <div className="space-y-2 pt-2">
                <Label>Machine-Level Sensors</Label>
                <div className="flex gap-2">
                  <Input 
                    placeholder="Add sensor ID (e.g. S11)" 
                    value={newSensorInput} 
                    onChange={e => setNewSensorInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && newSensorInput) {
                        e.preventDefault();
                        setNewMachineSensors([...newMachineSensors, newSensorInput]);
                        setNewSensorInput('');
                      }
                    }}
                  />
                  <Button type="button" variant="outline" onClick={() => {
                    if (newSensorInput) {
                      setNewMachineSensors([...newMachineSensors, newSensorInput]);
                      setNewSensorInput('');
                    }
                  }}>Add</Button>
                </div>
                {newMachineSensors.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {newMachineSensors.map((s, idx) => (
                      <Badge key={idx} variant="secondary" className="gap-1">
                        {s}
                        <Trash2 className="w-3 h-3 cursor-pointer hover:text-red-500" onClick={() => setNewMachineSensors(newMachineSensors.filter((_, i) => i !== idx))} />
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Spare Parts Details */}
            <div className="space-y-4 p-4 border border-gray-100 rounded-lg bg-gray-50/50">
              <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-purple-600" />
                Spare Parts Subsystem
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-end">
                <div className="space-y-2 md:col-span-2">
                  <Label>Part Name</Label>
                  <Input placeholder="e.g. Servo Motor" value={newSparePartName} onChange={e => setNewSparePartName(e.target.value)} />
                </div>
                <Button type="button" onClick={() => {
                  if (newSparePartName) {
                    setNewSpareParts([...newSpareParts, { name: newSparePartName, sensors: currentSparePartSensors }]);
                    setNewSparePartName('');
                    setCurrentSparePartSensors([]);
                  }
                }}>Add Part</Button>
              </div>

              <div className="space-y-2">
                <Label className="text-xs text-gray-500">Sensors for {newSparePartName || 'new part'} (Optional)</Label>
                <div className="flex gap-2">
                  <Input 
                    placeholder="Add sensor (e.g. TEMP_01)" 
                    value={newSparePartSensor} 
                    onChange={e => setNewSparePartSensor(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && newSparePartSensor) {
                        e.preventDefault();
                        setCurrentSparePartSensors([...currentSparePartSensors, newSparePartSensor]);
                        setNewSparePartSensor('');
                      }
                    }}
                  />
                  <Button type="button" variant="outline" onClick={() => {
                    if (newSparePartSensor) {
                      setCurrentSparePartSensors([...currentSparePartSensors, newSparePartSensor]);
                      setNewSparePartSensor('');
                    }
                  }}>Add Sensor</Button>
                </div>
                {currentSparePartSensors.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {currentSparePartSensors.map((s, idx) => (
                      <Badge key={idx} variant="outline" className="gap-1 border-purple-200 bg-purple-50 text-purple-700">
                        {s}
                        <Trash2 className="w-3 h-3 cursor-pointer hover:text-red-500" onClick={() => setCurrentSparePartSensors(currentSparePartSensors.filter((_, i) => i !== idx))} />
                      </Badge>
                    ))}
                  </div>
                )}
              </div>

              {newSpareParts.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-sm font-medium mb-2">Added Parts:</p>
                  <div className="space-y-2">
                    {newSpareParts.map((sp, idx) => (
                      <div key={idx} className="flex justify-between items-center bg-white p-2 border rounded text-sm">
                        <div>
                          <span className="font-medium">{sp.name}</span>
                          {sp.sensors.length > 0 && (
                            <span className="text-xs text-gray-500 ml-2">({sp.sensors.join(', ')})</span>
                          )}
                        </div>
                        <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-red-500 hover:text-red-700" onClick={() => setNewSpareParts(newSpareParts.filter((_, i) => i !== idx))}>
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          <DialogFooter className="mt-4">
            <Button variant="outline" onClick={() => setShowAddMachine(false)}>Cancel</Button>
            <Button onClick={handleAddMachineSubmit} className="bg-blue-600 hover:bg-blue-700">Confirm & Upload</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Adjust Anomaly Threshold Dialog */}
      <Dialog open={showThresholdDialog} onOpenChange={setShowThresholdDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Adjust Anomaly Thresholds</DialogTitle>
            <DialogDescription>
              Configure AI detection sensitivities for predictive maintenance.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Alert Threshold (RUL Cycles)</Label>
              <Input 
                type="number" 
                value={thresholdSettings.alertThreshold}
                onChange={e => setThresholdSettings({...thresholdSettings, alertThreshold: Number(e.target.value)})}
              />
            </div>
            <div className="space-y-2">
              <Label>Anomaly Z-Score</Label>
              <Input 
                type="number" step="0.1"
                value={thresholdSettings.anomalyZScore}
                onChange={e => setThresholdSettings({...thresholdSettings, anomalyZScore: Number(e.target.value)})}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowThresholdDialog(false)}>Cancel</Button>
            <Button onClick={() => {
              toast.success('Anomaly thresholds updated successfully.');
              addLog(`Adjusted anomaly detection thresholds`, 'sensor_calibrated');
              setShowThresholdDialog(false);
            }}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      {/* Schedule Maintenance Dialog */}
      <Dialog open={showScheduleDialog} onOpenChange={setShowScheduleDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Schedule Maintenance</DialogTitle>
            <DialogDescription>
              Create a new predictive maintenance task.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Task Description</Label>
              <Input 
                value={scheduleForm.description}
                onChange={e => setScheduleForm({...scheduleForm, description: e.target.value})}
                placeholder="e.g. Replace Bearings"
              />
            </div>
            <div className="space-y-2">
              <Label>Start Date</Label>
              <Input 
                type="date"
                value={scheduleForm.scheduledDate}
                onChange={e => setScheduleForm({...scheduleForm, scheduledDate: e.target.value})}
              />
            </div>
            <div className="space-y-2">
              <Label>Priority</Label>
              <Select value={scheduleForm.priority} onValueChange={(v: any) => setScheduleForm({...scheduleForm, priority: v})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowScheduleDialog(false)}>Cancel</Button>
            <Button onClick={() => {
              if (!scheduleForm.description || !scheduleForm.scheduledDate) {
                toast.error('Please fill all required fields');
                return;
              }
              const newRecord = {
                task: scheduleForm.description,
                priority: scheduleForm.priority,
                dueDate: scheduleForm.scheduledDate,
                endDate: scheduleForm.scheduledDate
              };
              setMaintenanceRecords([...maintenanceRecords, newRecord]);
              toast.success('Maintenance task scheduled.');
              addLog(`Scheduled predictive maintenance: ${scheduleForm.description}`, 'maintenance_scheduled');
              setShowScheduleDialog(false);
              setScheduleForm({ machine: '', description: '', scheduledDate: '', priority: 'medium' });
            }}>Schedule</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}