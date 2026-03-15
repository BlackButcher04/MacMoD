import { useState } from 'react';
import { Machine, SparePart } from '../../types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '../ui/dialog';
import { Wrench, AlertTriangle, ChevronRight, Activity, Cpu } from 'lucide-react';
import { toast } from 'sonner@2.0.3';

interface MaintenanceProps {
  machines: Machine[];
  onRepairPart: (machineId: string, partId: string, startDate?: string, endDate?: string) => void;
}

export function Maintenance({ machines, onRepairPart }: MaintenanceProps) {
  // Only show machines that have parts needing repair or suggested repair
  const machinesNeedingRepair = machines.filter(m => m.spareParts.some(p => p.needsRepair));
  
  const [selectedMachine, setSelectedMachine] = useState<Machine | null>(null);
  const [selectedPart, setSelectedPart] = useState<{machine: Machine, part: SparePart} | null>(null);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Healthy': return 'bg-green-100 text-green-800 border-green-200';
      case 'Warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'Pending Maintenance': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const handleRepairConfirm = () => {
    if (selectedPart && startDate && endDate) {
      onRepairPart(selectedPart.machine.id, selectedPart.part.id, startDate, endDate);
      toast.success(`${selectedPart.part.name} scheduled for maintenance from ${startDate} to ${endDate}.`);
      setSelectedPart(null);
      setStartDate('');
      setEndDate('');
      // Close machine dialog if no more parts need repair
      const remainingParts = selectedPart.machine.spareParts.filter(p => p.needsRepair && p.id !== selectedPart.part.id);
      if (remainingParts.length === 0) {
        setSelectedMachine(null);
      }
    } else if (selectedPart) {
      toast.error("Please select a start and end date for maintenance.");
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Maintenance Queue</h1>
        <p className="text-gray-600 mt-1">Review machines and spare parts requiring attention.</p>
      </div>

      {machinesNeedingRepair.length === 0 ? (
        <div className="mt-8 p-12 text-center border-2 border-dashed border-gray-300 rounded-lg bg-gray-50">
          <Activity className="w-12 h-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900">All Systems Operational</h3>
          <p className="text-gray-500 mt-1">No machines currently require maintenance.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {machinesNeedingRepair.map(machine => {
            const badParts = machine.spareParts.filter(p => p.needsRepair);
            return (
              <Card key={machine.id} className="hover:border-orange-300 transition-colors cursor-pointer group" onClick={() => setSelectedMachine(machine)}>
                <CardHeader className="pb-3 border-b border-gray-100">
                  <div className="flex justify-between items-start">
                    <div className="p-2 bg-orange-100 text-orange-600 rounded-lg group-hover:bg-orange-200 transition-colors">
                      <AlertTriangle className="w-6 h-6" />
                    </div>
                    <Badge variant="outline" className={getStatusColor(machine.status)}>
                      {machine.status}
                    </Badge>
                  </div>
                  <CardTitle className="mt-4 text-lg">{machine.name}</CardTitle>
                  <CardDescription>{badParts.length} parts need attention</CardDescription>
                </CardHeader>
                <CardContent className="pt-4">
                  <p className="text-sm text-gray-600 mb-3">Critical spare parts detected:</p>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {badParts.map(part => (
                      <Badge key={part.id} variant="secondary" className="bg-red-50 text-red-700 border-red-200">
                        {part.name}
                      </Badge>
                    ))}
                  </div>
                  <Button variant="ghost" className="w-full justify-between text-orange-600 hover:text-orange-700 hover:bg-orange-50">
                    Review Maintenance Required
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Machine Details Dialog */}
      <Dialog open={!!selectedMachine} onOpenChange={(open) => !open && setSelectedMachine(null)}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-xl">
              <Wrench className="w-5 h-5 text-orange-500" />
              Maintenance Required: {selectedMachine?.name}
            </DialogTitle>
            <DialogDescription>
              Select a spare part to view telemetric details and schedule repair.
            </DialogDescription>
          </DialogHeader>
          
          {/* 这里加上了 pt-2 来解决卡片 hover 向上位移被遮挡的问题 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 max-h-[60vh] overflow-y-auto pr-2 pt-2">
            {selectedMachine?.spareParts.map(part => (
              <Card key={part.id} 
                className={`cursor-pointer transition-all hover:-translate-y-1 ${part.needsRepair ? 'border-red-300 bg-red-50/20' : 'border-green-200 bg-green-50/20 opacity-60'}`}
                onClick={() => {
                  if (part.needsRepair) setSelectedPart({machine: selectedMachine, part});
                }}
              >
                <CardContent className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Cpu className={`w-8 h-8 ${part.needsRepair ? 'text-red-500' : 'text-green-500'}`} />
                    <div>
                      <h4 className="font-semibold text-gray-900">{part.name}</h4>
                      <p className="text-xs text-gray-500">Health: {part.health}%</p>
                    </div>
                  </div>
                  {part.needsRepair ? (
                    <Badge variant="destructive">Repair</Badge>
                  ) : (
                    <Badge variant="outline" className="bg-green-100 text-green-800 border-green-200">Healthy</Badge>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </DialogContent>
      </Dialog>

      {/* Spare Part Diagnostics Dialog */}
      <Dialog open={!!selectedPart} onOpenChange={(open) => !open && setSelectedPart(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Spare Part Diagnostics</DialogTitle>
            <DialogDescription>Review telemetric data for {selectedPart?.part.name}</DialogDescription>
          </DialogHeader>
          
          {selectedPart && (
            <div className="space-y-4 mt-2">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 font-medium">HEALTH SCORE</p>
                  <p className="text-2xl font-bold text-red-600">{selectedPart.part.health}%</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 font-medium">LAST REPLACED</p>
                  <p className="text-xl font-bold text-gray-900">{selectedPart.part.lastReplaced}</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 font-medium">TEMP SENSOR</p>
                  <p className="text-xl font-bold text-orange-600">{selectedPart.part.temperature} °C</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 font-medium">VIBRATION</p>
                  <p className="text-xl font-bold text-orange-600">{selectedPart.part.vibration} mm/s</p>
                </div>
              </div>
              
              <div className="bg-yellow-50 border border-yellow-200 p-3 rounded-lg text-sm text-yellow-800 mt-4">
                <AlertTriangle className="w-4 h-4 inline mr-2 -mt-0.5" />
                This part has crossed the degradation threshold. Repair or replacement required.
              </div>

              <div className="grid grid-cols-2 gap-4 mt-4">
                <div>
                  <label className="text-xs font-medium text-gray-700 mb-1 block">Maintenance Start Date</label>
                  <input 
                    type="date" 
                    className="w-full border border-gray-300 rounded-md p-2 text-sm"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-700 mb-1 block">Maintenance End Date</label>
                  <input 
                    type="date" 
                    className="w-full border border-gray-300 rounded-md p-2 text-sm"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </div>
              </div>
            </div>
          )}
          
          <DialogFooter className="mt-6">
            <Button variant="outline" onClick={() => setSelectedPart(null)}>Cancel</Button>
            <Button onClick={handleRepairConfirm} className="bg-orange-600 hover:bg-orange-700 text-white gap-2">
              <Wrench className="w-4 h-4" /> Schedule Repair
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}