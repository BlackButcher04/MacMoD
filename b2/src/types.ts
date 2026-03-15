export interface UserAccount {
  id: string;
  name: string;
  email: string;
  position: string;
  registeredDate?: string;
}

export interface MaintenanceRecord {
  id: string;
  machineId: string;
  machineName: string;
  partId?: string;
  partName?: string;
  description: string;
  scheduledDate: string;
  priority: 'low' | 'medium' | 'high';
  status: 'scheduled' | 'completed' | 'cancelled';
  createdAt: string;
}

export interface AnomalyThresholdSettings {
  alertThreshold: number;
  anomalyZScore: number;
  agePenalty: number;
  temporalWindow: number;
}

export interface LogEntry {
  id: string;
  userId: string;
  userName: string;
  action: string;
  timestamp: string;
  type: 'alert_critical' | 'maintenance_scheduled' | 'sensor_calibrated' | 'model_updated' | 'user_action';
  machine?: string;
}