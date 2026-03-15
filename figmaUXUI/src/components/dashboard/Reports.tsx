import { useState } from 'react';
import { Machine } from '../../types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { BarChart3, Download, FileText, Filter, Activity } from 'lucide-react';
import { toast } from 'sonner@2.0.3';

interface ReportsProps {
  machines: Machine[];
}

export function Reports({ machines }: ReportsProps) {
  const [year, setYear] = useState('2024');
  const [month, setMonth] = useState('03');
  const [machineId, setMachineId] = useState('all');
  const [isGenerating, setIsGenerating] = useState(false);
  const [reportGenerated, setReportGenerated] = useState(false);

  const handleGenerate = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setIsGenerating(false);
      setReportGenerated(true);
      toast.success('Machine health report generated successfully.');
    }, 1500);
  };

  const handleDownload = () => {
    toast.success('Downloading report as PDF...');
  };

  const months = [
    { value: '01', label: 'January' }, { value: '02', label: 'February' },
    { value: '03', label: 'March' }, { value: '04', label: 'April' },
    { value: '05', label: 'May' }, { value: '06', label: 'June' },
    { value: '07', label: 'July' }, { value: '08', label: 'August' },
    { value: '09', label: 'September' }, { value: '10', label: 'October' },
    { value: '11', label: 'November' }, { value: '12', label: 'December' }
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Analytics & Reports</h1>
        <p className="text-gray-600 mt-1">Generate comprehensive health and maintenance reports for your fleet.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="w-5 h-5" />
            Report Parameters
          </CardTitle>
          <CardDescription>Select filters to compile historical telemetry data.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Year</label>
              <Select value={year} onValueChange={setYear}>
                <SelectTrigger>
                  <SelectValue placeholder="Select Year" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="2022">2022</SelectItem>
                  <SelectItem value="2023">2023</SelectItem>
                  <SelectItem value="2024">2024</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Month</label>
              <Select value={month} onValueChange={setMonth}>
                <SelectTrigger>
                  <SelectValue placeholder="Select Month" />
                </SelectTrigger>
                <SelectContent>
                  {months.map(m => (
                    <SelectItem key={m.value} value={m.value}>{m.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Machine Target</label>
              <Select value={machineId} onValueChange={setMachineId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select Machine" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Machines (Fleet Overview)</SelectItem>
                  {machines.map(m => (
                    <SelectItem key={m.id} value={m.id}>{m.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <Button 
            onClick={handleGenerate} 
            disabled={isGenerating}
            className="w-full md:w-auto gap-2 bg-blue-600 hover:bg-blue-700"
          >
            {isGenerating ? <Activity className="w-4 h-4 animate-spin" /> : <BarChart3 className="w-4 h-4" />}
            {isGenerating ? 'Compiling Telemetry...' : 'Generate Report'}
          </Button>
        </CardContent>
      </Card>

      {reportGenerated && (
        <Card className="border-green-200 shadow-sm overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="bg-green-50 p-4 border-b border-green-200 flex justify-between items-center">
            <div className="flex items-center gap-3 text-green-800">
              <FileText className="w-6 h-6" />
              <div>
                <h3 className="font-semibold">Condition Monitoring Report</h3>
                <p className="text-xs opacity-80">Period: {months.find(m => m.value === month)?.label} {year}</p>
              </div>
            </div>
            <Button onClick={handleDownload} variant="outline" className="gap-2 border-green-300 text-green-700 hover:bg-green-100">
              <Download className="w-4 h-4" /> Download PDF
            </Button>
          </div>
          <CardContent className="p-8">
            <div className="space-y-8">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Average RUL</p>
                  <p className="text-2xl font-bold text-gray-900">184 Cycles</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1">Anomalies Detected</p>
                  <p className="text-2xl font-bold text-red-600">12</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1">Repairs Conducted</p>
                  <p className="text-2xl font-bold text-blue-600">3</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1">Fleet Health Score</p>
                  <p className="text-2xl font-bold text-green-600">88%</p>
                </div>
              </div>
              
              <div className="border-t border-gray-100 pt-6">
                <h4 className="font-medium text-gray-900 mb-4">Executive Summary</h4>
                <p className="text-sm text-gray-600 leading-relaxed">
                  During the designated period, the temporal feature engineering model recorded stable operational cycles 
                  across 80% of the fleet. However, hydraulic assets showed a {Math.random() > 0.5 ? '14%' : '9%'} increase in acoustic emission 
                  anomalies. The age-adjusted RUL regression successfully predicted imminent failures, allowing for 
                  proactive maintenance without unplanned downtime. We recommend recalibrating the baseline Z-score limits 
                  for high-load machinery components.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}