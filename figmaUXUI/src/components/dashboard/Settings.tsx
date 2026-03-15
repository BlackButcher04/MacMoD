import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';
import { Save, Shield, Bell, Database } from 'lucide-react';
import { toast } from 'sonner@2.0.3';

export function Settings() {
  const handleSave = () => {
    toast.success('System configuration saved successfully.');
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">System Configuration</h1>
        <p className="text-gray-600 mt-1">Adjust AI thresholds, operational parameters, and alert rules.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-blue-500" />
                Advanced AI Tuning
              </CardTitle>
              <CardDescription>Configure machine learning and degradation regression parameters.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label>Default Alert Threshold (Cycles)</Label>
                  <Input type="number" defaultValue="30" />
                  <p className="text-xs text-gray-500">Triggers 'Action Required' status.</p>
                </div>
                <div className="space-y-2">
                  <Label>Anomaly Z-Score Limit</Label>
                  <Input type="number" step="0.1" defaultValue="3.5" />
                  <p className="text-xs text-gray-500">Threshold for regime switching detection.</p>
                </div>
                <div className="space-y-2">
                  <Label>Age Penalty Multiplier</Label>
                  <Input type="number" step="0.1" defaultValue="1.5" />
                  <p className="text-xs text-gray-500">Applied to baseline RUL predictions.</p>
                </div>
                <div className="space-y-2">
                  <Label>Temporal Window Size (Cycles)</Label>
                  <Input type="number" defaultValue="14" />
                  <p className="text-xs text-gray-500">Rolling window for RSI calculation.</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="w-5 h-5 text-purple-500" />
                Data & Telemetry
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">High-Frequency UDP Ingestion</Label>
                  <p className="text-sm text-gray-500">Allow continuous raw sensor data stream.</p>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Auto-Retrain Models</Label>
                  <p className="text-sm text-gray-500">Update regression weights nightly.</p>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="space-y-2">
                <Label>Dataset Environment Priority</Label>
                <Select defaultValue="FD001">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="FD001">FD001: Standard Ops</SelectItem>
                    <SelectItem value="FD002">FD002: Complex Ops</SelectItem>
                    <SelectItem value="FD003">FD003: Extreme Ops</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="w-5 h-5 text-orange-500" />
                Notifications
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label>Critical RUL Alerts</Label>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <Label>Regime State Changes</Label>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <Label>Maintenance Reminders</Label>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <Label>Weekly PDF Reports</Label>
                <Switch />
              </div>
            </CardContent>
          </Card>

          <Button className="w-full gap-2 bg-blue-600 hover:bg-blue-700" onClick={handleSave}>
            <Save className="w-4 h-4" /> Save Configuration
          </Button>
        </div>
      </div>
    </div>
  );
}