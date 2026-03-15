import { useState, useMemo } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "../ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "../ui/dialog";
import {
  Server,
  Wrench,
  AlertTriangle,
  Activity,
  Database,
  Calendar,
  ChevronRight,
  Cpu,
} from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Step,
} from "recharts";
import { Machine, SparePart } from "../../types";

interface MachineFleetProps {
  machines: Machine[];
  onRepairPart: (machineId: string, partId: string) => void;
}

// Generate data for 6 charts
const generateTelemetryData = (
  currentCycle: number,
  failureCycle: number,
) => {
  const data = [];
  for (
    let i = Math.max(0, currentCycle - 60);
    i <= currentCycle + 15;
    i += 2
  ) {
    const trueRUL = Math.max(0, failureCycle - i);
    const aiRUL = Math.max(
      0,
      trueRUL +
        (Math.random() - 0.5) *
          15 *
          (1 - trueRUL / failureCycle),
    );

    data.push({
      cycle: i,
      s11:
        45 +
        Math.sin(i / 10) * 15 +
        Math.random() * 5 +
        (i > failureCycle - 20 ? 20 : 0),
      s12: 8000 - (i / failureCycle) * 400 + Math.random() * 50,
      rsi: Math.max(
        0,
        Math.min(
          100,
          50 +
            Math.sin(i / 5) * 30 +
            (i > failureCycle - 20 ? 30 : 0),
        ),
      ),
      momentum:
        Math.cos(i / 3) * 5 + (i > failureCycle - 20 ? -10 : 0),
      regime: i > failureCycle - 40 ? 1 : 0, // 0 = STABLE, 1 = IMPAIRED
      trueRUL: Math.round(trueRUL),
      aiRUL: Math.round(aiRUL),
    });
  }
  return data;
};

export function MachineFleet({
  machines,
  onRepairPart,
}: MachineFleetProps) {
  const [selectedMachine, setSelectedMachine] = useState<Machine | null>(null);
  const [selectedPart, setSelectedPart] = useState<SparePart | null>(null);
  const [dataSource, setDataSource] = useState("system");
  const [expandedChart, setExpandedChart] = useState<string | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Healthy":
        return "bg-green-100 text-green-800 border-green-200";
      case "Warning":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "Critical":
        return "bg-red-100 text-red-800 border-red-200";
      case "Pending Maintenance":
        return "bg-blue-100 text-blue-800 border-blue-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  // 使用 useMemo 缓存数据，防止点击零件时图表乱跳
  const chartData = useMemo(() => {
    return selectedMachine
      ? generateTelemetryData(
          selectedMachine.currentCycle,
          selectedMachine.failureCycle,
        )
      : [];
  }, [selectedMachine?.id]);

  const currentRUL = selectedMachine
    ? Math.max(
        0,
        selectedMachine.failureCycle -
          selectedMachine.currentCycle,
      )
    : 0;

  // 渲染放大的图表组件（已修复动画期间 null child 的报错）
  const renderExpandedChart = () => {
    if (!expandedChart || !chartData.length) return null;

    const commonMargin = { top: 30, right: 40, left: 10, bottom: 20 };
    const axisProps = { stroke: "#475569", tick: { fontSize: 14, fill: "#94a3b8" } };
    const tooltipProps = {
      contentStyle: {
        backgroundColor: "#0f172a",
        border: "1px solid #1e293b",
        borderRadius: "8px",
        color: "#f8fafc",
        fontSize: "14px",
        padding: "12px",
        boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.5)",
      },
    };

    let chartComponent = null;

    switch (expandedChart) {
      case "S11 THROTTLE POSITION":
        chartComponent = (
          <LineChart data={chartData} margin={commonMargin}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="cycle" {...axisProps} />
            <YAxis {...axisProps} domain={["auto", "auto"]} />
            <Tooltip {...tooltipProps} />
            <Line type="monotone" dataKey="s11" stroke="#3b82f6" strokeWidth={3} dot={false} activeDot={{ r: 6, fill: "#3b82f6" }} isAnimationActive={false} />
          </LineChart>
        );
        break;
      case "S12 CORE SPEED":
        chartComponent = (
          <LineChart data={chartData} margin={commonMargin}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="cycle" {...axisProps} />
            <YAxis {...axisProps} domain={["auto", "auto"]} />
            <Tooltip {...tooltipProps} />
            <Line type="monotone" dataKey="s12" stroke="#ef4444" strokeWidth={3} dot={false} activeDot={{ r: 6, fill: "#ef4444" }} isAnimationActive={false} />
          </LineChart>
        );
        break;
      case "S11 RELATIVE STRENGTH":
        chartComponent = (
          <LineChart data={chartData} margin={commonMargin}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="cycle" {...axisProps} />
            <YAxis {...axisProps} domain={[0, 100]} />
            <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" strokeOpacity={0.6} />
            <ReferenceLine y={30} stroke="#22c55e" strokeDasharray="3 3" strokeOpacity={0.6} />
            <Tooltip {...tooltipProps} />
            <Line type="monotone" dataKey="rsi" stroke="#eab308" strokeWidth={3} dot={false} activeDot={{ r: 6, fill: "#eab308" }} isAnimationActive={false} />
          </LineChart>
        );
        break;
      case "S11 DECAY MOMENTUM":
        chartComponent = (
          <BarChart data={chartData} margin={commonMargin}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="cycle" {...axisProps} />
            <YAxis {...axisProps} />
            <ReferenceLine y={0} stroke="#475569" strokeOpacity={0.5} />
            <Tooltip cursor={{ fill: "#1e293b", opacity: 0.4 }} {...tooltipProps} />
            <Bar dataKey="momentum" fill="#8b5cf6" radius={[4, 4, 0, 0]} isAnimationActive={false} />
          </BarChart>
        );
        break;
      case "SYSTEM REGIME STATE":
        chartComponent = (
          <LineChart data={chartData} margin={commonMargin}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="cycle" {...axisProps} />
            <YAxis {...axisProps} domain={[-0.2, 1.2]} ticks={[0, 1]} />
            <Tooltip {...tooltipProps} />
            <Line type="stepAfter" dataKey="regime" stroke="#06b6d4" strokeWidth={3} dot={false} isAnimationActive={false} />
          </LineChart>
        );
        break;
      case "PROGNOSTICS: RUL AI":
        chartComponent = (
          <LineChart data={chartData} margin={commonMargin}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="cycle" {...axisProps} />
            <YAxis {...axisProps} domain={[0, 300]} />
            <Tooltip {...tooltipProps} />
            <ReferenceLine y={selectedMachine?.alertThreshold || 50} stroke="#eab308" strokeDasharray="3 3" label={{ position: "insideTopLeft", fill: "#eab308", fontSize: 14, value: "ALERT THRESHOLD", dy: -10 }} strokeOpacity={0.8} />
            <Line type="monotone" name="TRUTH" dataKey="trueRUL" stroke="#10b981" strokeWidth={3} dot={false} isAnimationActive={false} />
            <Line type="monotone" name="AI PRED" dataKey="aiRUL" stroke="#ec4899" strokeWidth={3} strokeDasharray="5 5" dot={false} isAnimationActive={false} />
          </LineChart>
        );
        break;
      default:
        return null;
    }

    return (
      <ResponsiveContainer width="100%" height="100%">
        {chartComponent}
      </ResponsiveContainer>
    );
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">
            Machine Fleet AI Monitor
          </h1>
          <p className="text-gray-600 mt-1">
            Predictive maintenance terminal and RUL diagnostics.
          </p>
        </div>

        <Tabs
          value={dataSource}
          onValueChange={setDataSource}
          className="w-[400px]"
        >
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger
              value="system"
              className="flex items-center gap-2"
            >
              <Database className="w-4 h-4" />
              System Data
            </TabsTrigger>
            <TabsTrigger
              value="custom"
              className="flex items-center gap-2"
            >
              <Activity className="w-4 h-4" />
              Custom Data
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {dataSource === "custom" && (
        <div className="bg-blue-50 border border-blue-200 text-blue-800 px-4 py-3 rounded-lg flex items-start gap-3">
          <Activity className="w-5 h-5 mt-0.5 text-blue-600" />
          <div>
            <h4 className="font-semibold text-sm">
              Custom Data Mode Active
            </h4>
            <p className="text-sm mt-1">
              AI models are currently inferring RUL using the
              custom raw telemetry data uploaded from your
              factory.
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {machines.map((machine) => (
          <Card
            key={machine.id}
            className="hover:border-blue-300 hover:shadow-md transition-all cursor-pointer overflow-hidden group"
            onClick={() => setSelectedMachine(machine)}
          >
            <div className="h-2 bg-slate-900 w-full" />
            <CardHeader className="pb-3">
              <div className="flex justify-between items-start">
                <div className="p-2 bg-slate-100 rounded-lg group-hover:bg-blue-50 group-hover:text-blue-600 transition-colors">
                  <Server className="w-6 h-6" />
                </div>
                <Badge
                  variant="outline"
                  className={getStatusColor(machine.status)}
                >
                  {machine.status}
                </Badge>
              </div>
              <CardTitle className="mt-4 text-lg">
                {machine.name}
              </CardTitle>
              <CardDescription>
                Type: {machine.type}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500 flex items-center gap-2">
                    <Calendar className="w-4 h-4" /> Started
                  </span>
                  <span className="font-medium text-gray-900">
                    {machine.startDate}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500 flex items-center gap-2">
                    <Wrench className="w-4 h-4" /> Prior Repairs
                  </span>
                  <span className="font-medium text-gray-900">
                    {machine.repairs}
                  </span>
                </div>
                <div className="pt-4 border-t border-gray-100 mt-2">
                  <Button
                    variant="ghost"
                    className="w-full justify-between text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                  >
                    Open Predictive Terminal
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 主控制台弹窗 */}
      <Dialog
        open={!!selectedMachine}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedMachine(null);
            setSelectedPart(null);
            setExpandedChart(null); // 关闭主弹窗时顺便清理大图状态
          }
        }}
      >
        <DialogContent className="max-w-[85vw] xl:max-w-[1200px] w-full h-[95vh] flex flex-col bg-[#0b1121] text-slate-50 border-slate-800 p-0 overflow-hidden shadow-2xl rounded-xl">
          <DialogHeader className="p-4 md:p-6 border-b border-slate-800/80 shrink-0 bg-slate-900/50 flex flex-col md:flex-row items-start justify-between gap-4">
            <div className="space-y-1.5 w-full md:w-auto">
              <DialogTitle className="text-lg md:text-2xl font-mono tracking-wide text-blue-400 flex items-center gap-2 md:gap-4 flex-wrap">
                <Activity className="w-5 h-5 md:w-6 md:h-6 text-blue-500 shrink-0" />
                <span className="truncate">SMART HARVESTER // PREDICTIVE MAINTENANCE TERMINAL</span>
              </DialogTitle>
              <DialogDescription className="text-slate-400 font-mono text-xs md:text-sm uppercase tracking-wider flex items-center gap-2 md:gap-3 flex-wrap">
                <span>Autonomous telemetric diagnostics</span>
                <span className="text-slate-600 hidden md:inline">|</span>
                <span>
                  Asset:{" "}
                  <span className="text-slate-200">
                    {selectedMachine?.name}
                  </span>
                </span>
                <span className="text-slate-600 hidden md:inline">|</span>
                <span>
                  ID: {selectedMachine?.id.toUpperCase()}
                </span>
              </DialogDescription>
            </div>

            {/* KPI Strip */}
            {selectedMachine && (
              <div className="flex items-center gap-8 pr-4 hidden lg:flex">
                <div className="flex flex-col items-center justify-center">
                  <p className="text-[11px] text-slate-400 font-mono mb-1.5 uppercase tracking-wider font-semibold text-center">
                    System Health
                  </p>
                  <p className="text-3xl font-bold font-mono text-blue-400 leading-none text-center">
                    {selectedMachine.healthScore}%
                  </p>
                </div>
                
                <div className="w-px h-10 bg-slate-800"></div>
                
                <div className="flex flex-col items-center justify-center">
                  <p className="text-[11px] text-slate-400 font-mono mb-1.5 uppercase tracking-wider font-semibold text-center">
                    Adj RUL
                  </p>
                  <p
                    className={`text-3xl font-bold font-mono leading-none text-center ${currentRUL < selectedMachine.alertThreshold ? "text-yellow-400" : "text-emerald-400"}`}
                  >
                    {currentRUL}{" "}
                    <span className="text-sm text-slate-500 font-normal">
                      CYC
                    </span>
                  </p>
                </div>
                
                <div className="w-px h-10 bg-slate-800"></div>
                
                <div className="flex flex-col items-center justify-center">
                  <p className="text-[11px] text-slate-400 font-mono mb-1.5 uppercase tracking-wider font-semibold text-center">
                    Regime State
                  </p>
                  <span
                    className={`inline-flex items-center px-2.5 py-1 text-sm font-bold font-mono rounded ${selectedMachine.regime === "STABLE" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-red-500/10 text-red-400 border border-red-500/20"}`}
                  >
                    {selectedMachine.regime}
                  </span>
                </div>
                
                <div className="w-px h-10 bg-slate-800"></div>
                
                <div className="flex flex-col items-center justify-center">
                  <p className="text-[11px] text-slate-400 font-mono mb-1.5 uppercase tracking-wider font-semibold text-center">
                    Status
                  </p>
                  <span
                    className={`inline-flex items-center px-2.5 py-1 text-sm font-bold font-mono rounded ${currentRUL <= 0 ? "bg-red-500/10 text-red-400 border border-red-500/20" : currentRUL < selectedMachine.alertThreshold ? "bg-yellow-500/10 text-yellow-400 border border-yellow-500/20" : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"}`}
                  >
                    {currentRUL <= 0
                      ? "SHUTDOWN"
                      : currentRUL < selectedMachine.alertThreshold
                        ? "WARNING"
                        : "OPTIMAL"}
                  </span>
                </div>
              </div>
            )}
          </DialogHeader>

          {selectedMachine && (
            <div className="flex-1 min-h-0 flex flex-col lg:flex-row gap-0 bg-[#0b1121]">
              {/* Left Main: 6 Telemetry Charts Grid */}
              <div className="w-full lg:w-[78%] h-full overflow-y-auto border-r border-slate-800/80 p-6 pb-20">
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  
                  {/* 1. S11 Throttle */}
                  <div 
                    className="h-full min-h-[240px] flex flex-col bg-[#111827] p-5 rounded-xl border border-slate-800/60 shadow-sm relative overflow-hidden group cursor-pointer hover:border-slate-500 hover:bg-slate-800/50 transition-all"
                    onClick={() => setExpandedChart("S11 THROTTLE POSITION")}
                  >
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500/40 to-transparent opacity-50"></div>
                    <div className="flex justify-between items-center mb-4">
                      <p className="text-xs font-mono text-slate-400 tracking-wider">
                        S11 THROTTLE POSITION
                      </p>
                      <Activity className="w-4 h-4 text-blue-500/50 group-hover:text-blue-400 transition-colors" />
                    </div>
                    <div className="flex-1 min-h-0 pointer-events-none">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                          <XAxis dataKey="cycle" stroke="#475569" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} />
                          <YAxis stroke="#475569" tick={{ fontSize: 10, fill: "#64748b" }} domain={["auto", "auto"]} axisLine={false} tickLine={false} />
                          <Line type="monotone" dataKey="s11" stroke="#3b82f6" strokeWidth={2} dot={false} isAnimationActive={false} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* 2. S12 Core Speed */}
                  <div 
                    className="h-full min-h-[240px] flex flex-col bg-[#111827] p-5 rounded-xl border border-slate-800/60 shadow-sm relative overflow-hidden group cursor-pointer hover:border-slate-500 hover:bg-slate-800/50 transition-all"
                    onClick={() => setExpandedChart("S12 CORE SPEED")}
                  >
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-500/40 to-transparent opacity-50"></div>
                    <div className="flex justify-between items-center mb-4">
                      <p className="text-xs font-mono text-slate-400 tracking-wider">
                        S12 CORE SPEED
                      </p>
                      <Activity className="w-4 h-4 text-red-500/50 group-hover:text-red-400 transition-colors" />
                    </div>
                    <div className="flex-1 min-h-0 pointer-events-none">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                          <XAxis dataKey="cycle" stroke="#475569" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} />
                          <YAxis stroke="#475569" tick={{ fontSize: 10, fill: "#64748b" }} domain={["auto", "auto"]} axisLine={false} tickLine={false} />
                          <Line type="monotone" dataKey="s12" stroke="#ef4444" strokeWidth={2} dot={false} isAnimationActive={false} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* 3. S11 RSI */}
                  <div 
                    className="h-full min-h-[240px] flex flex-col bg-[#111827] p-5 rounded-xl border border-slate-800/60 shadow-sm relative overflow-hidden group cursor-pointer hover:border-slate-500 hover:bg-slate-800/50 transition-all"
                    onClick={() => setExpandedChart("S11 RELATIVE STRENGTH")}
                  >
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-yellow-500/40 to-transparent opacity-50"></div>
                    <div className="flex justify-between items-center mb-4">
                      <p className="text-xs font-mono text-slate-400 tracking-wider">
                        S11 RELATIVE STRENGTH
                      </p>
                      <Activity className="w-4 h-4 text-yellow-500/50 group-hover:text-yellow-400 transition-colors" />
                    </div>
                    <div className="flex-1 min-h-0 pointer-events-none">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                          <XAxis dataKey="cycle" stroke="#475569" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} />
                          <YAxis stroke="#475569" tick={{ fontSize: 10, fill: "#64748b" }} domain={[0, 100]} axisLine={false} tickLine={false} />
                          <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" strokeOpacity={0.6} />
                          <ReferenceLine y={30} stroke="#22c55e" strokeDasharray="3 3" strokeOpacity={0.6} />
                          <Line type="monotone" dataKey="rsi" stroke="#eab308" strokeWidth={2} dot={false} isAnimationActive={false} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* 4. S11 Decay Momentum */}
                  <div 
                    className="h-full min-h-[240px] flex flex-col bg-[#111827] p-5 rounded-xl border border-slate-800/60 shadow-sm relative overflow-hidden group cursor-pointer hover:border-slate-500 hover:bg-slate-800/50 transition-all"
                    onClick={() => setExpandedChart("S11 DECAY MOMENTUM")}
                  >
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-500/40 to-transparent opacity-50"></div>
                    <div className="flex justify-between items-center mb-4">
                      <p className="text-xs font-mono text-slate-400 tracking-wider">
                        S11 DECAY MOMENTUM
                      </p>
                      <Activity className="w-4 h-4 text-purple-500/50 group-hover:text-purple-400 transition-colors" />
                    </div>
                    <div className="flex-1 min-h-0 pointer-events-none">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                          <XAxis dataKey="cycle" stroke="#475569" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} />
                          <YAxis stroke="#475569" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} />
                          <ReferenceLine y={0} stroke="#475569" strokeOpacity={0.5} />
                          <Bar dataKey="momentum" fill="#8b5cf6" radius={[2, 2, 0, 0]} isAnimationActive={false} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* 5. Regime State */}
                  <div 
                    className="h-full min-h-[240px] flex flex-col bg-[#111827] p-5 rounded-xl border border-slate-800/60 shadow-sm relative overflow-hidden group cursor-pointer hover:border-slate-500 hover:bg-slate-800/50 transition-all"
                    onClick={() => setExpandedChart("SYSTEM REGIME STATE")}
                  >
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500/40 to-transparent opacity-50"></div>
                    <div className="flex justify-between items-center mb-4">
                      <p className="text-xs font-mono text-slate-400 tracking-wider">
                        SYSTEM REGIME STATE
                      </p>
                      <Activity className="w-4 h-4 text-cyan-500/50 group-hover:text-cyan-400 transition-colors" />
                    </div>
                    <div className="flex-1 min-h-0 pointer-events-none">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                          <XAxis dataKey="cycle" stroke="#475569" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} />
                          <YAxis stroke="#475569" tick={{ fontSize: 10, fill: "#64748b" }} domain={[-0.2, 1.2]} ticks={[0, 1]} axisLine={false} tickLine={false} />
                          <Line type="stepAfter" dataKey="regime" stroke="#06b6d4" strokeWidth={2} dot={false} isAnimationActive={false} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* 6. RUL AI Regression */}
                  <div 
                    className="h-full min-h-[240px] flex flex-col bg-[#111827] p-5 rounded-xl border border-slate-800/60 shadow-sm relative overflow-hidden group cursor-pointer hover:border-slate-500 hover:bg-slate-800/50 transition-all"
                    onClick={() => setExpandedChart("PROGNOSTICS: RUL AI")}
                  >
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-pink-500/40 to-transparent opacity-50"></div>
                    <div className="flex justify-between items-center mb-4">
                      <p className="text-xs font-mono text-slate-400 tracking-wider">
                        PROGNOSTICS: RUL AI
                      </p>
                      <Activity className="w-4 h-4 text-pink-500/50 group-hover:text-pink-400 transition-colors" />
                    </div>
                    <div className="flex-1 min-h-0 relative pointer-events-none">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData} margin={{ top: 20, right: 10, left: -20, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                          <XAxis dataKey="cycle" stroke="#475569" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} />
                          <YAxis stroke="#475569" tick={{ fontSize: 10, fill: "#64748b" }} domain={[0, 300]} axisLine={false} tickLine={false} />
                          <ReferenceLine y={selectedMachine.alertThreshold} stroke="#eab308" strokeDasharray="3 3" strokeOpacity={0.8} />
                          <Line type="monotone" name="TRUTH" dataKey="trueRUL" stroke="#10b981" strokeWidth={2} dot={false} isAnimationActive={false} />
                          <Line type="monotone" name="AI PRED" dataKey="aiRUL" stroke="#ec4899" strokeWidth={2} strokeDasharray="5 5" dot={false} isAnimationActive={false} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                </div>
              </div>

              {/* Right Column: Metrics & Spare Parts */}
              <div className="w-full lg:w-[22%] h-full overflow-y-auto bg-[#111827]/50 flex flex-col p-6">
                <div className="flex-1">
                  <h3 className="text-xs font-mono font-semibold text-slate-300 mb-4 tracking-wider flex items-center gap-2 uppercase pb-3 border-b border-slate-800/80">
                    <Wrench className="w-4 h-4 text-slate-500" />
                    Spare Parts Subsystem
                  </h3>

                  <div className="flex flex-col gap-3">
                    {selectedMachine.spareParts.map((part) => {
                      const isCritical = part.health < 6;
                      const isWarning = part.needsRepair && !isCritical;
                      const isPending = part.status === "Pending Maintenance";

                      return (
                        <div
                          key={part.id}
                          onClick={() => setSelectedPart(selectedPart?.id === part.id ? null : part)}
                          className={`p-3.5 rounded-xl border transition-all cursor-pointer shadow-sm relative overflow-hidden group ${
                            isCritical ? "bg-red-500/5 border-red-500/30 hover:bg-red-500/10" : isWarning ? "bg-yellow-500/5 border-yellow-500/30 hover:bg-yellow-500/10" : isPending ? "bg-blue-500/5 border-blue-500/30 hover:bg-blue-500/10" : "bg-slate-800/40 border-slate-700/60 hover:bg-slate-800/70 hover:border-slate-600"
                          } ${selectedPart?.id === part.id ? `ring-1 ${isCritical ? "ring-red-500/50 shadow-[0_0_15px_rgba(239,68,68,0.15)]" : "ring-blue-500/50 shadow-[0_0_15px_rgba(59,130,246,0.15)]"}` : ""}`}
                        >
                          {isCritical && <div className="absolute top-0 left-0 w-1 h-full bg-red-500"></div>}
                          {isWarning && <div className="absolute top-0 left-0 w-1 h-full bg-yellow-500"></div>}
                          {isPending && <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>}
                          {!isCritical && !isWarning && !isPending && <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500/50 opacity-0 group-hover:opacity-100 transition-opacity"></div>}

                          <div className="flex justify-between items-center relative z-10 pl-1">
                            <div className="flex items-center gap-3">
                              <div className={`p-1.5 rounded-lg ${isCritical ? "bg-red-500/20 text-red-400" : isWarning ? "bg-yellow-500/20 text-yellow-400" : isPending ? "bg-blue-500/20 text-blue-400" : "bg-slate-700/50 text-slate-300"}`}>
                                <Cpu className="w-4 h-4" />
                              </div>
                              <div>
                                <p className="font-medium text-sm text-slate-200 tracking-wide">{part.name}</p>
                                <p className={`text-[10px] font-mono mt-0.5 ${isCritical ? "text-red-400" : isWarning ? "text-yellow-400" : isPending ? "text-blue-400" : "text-slate-500"}`}>
                                  {isPending ? "PENDING MAINTENANCE" : isCritical ? "CRITICAL" : isWarning ? "REPAIR" : "OPTIMAL"}
                                </p>
                              </div>
                            </div>
                            <div className="text-right">
                              <span className={`font-mono text-lg font-bold ${isCritical ? "text-red-400" : isWarning ? "text-yellow-400" : isPending ? "text-blue-400" : "text-emerald-400"}`}>
                                {part.health}%
                              </span>
                            </div>
                          </div>

                          {selectedPart?.id === part.id && (
                            <div className="mt-4 pt-4 border-t border-slate-700/50 animate-in slide-in-from-top-2 relative z-10">
                              <div className="grid grid-cols-2 gap-3 mb-2">
                                <div className="bg-[#0b1121] p-2.5 rounded-lg border border-slate-800">
                                  <p className="text-[10px] text-slate-500 font-mono tracking-wider mb-0.5">TEMPERATURE</p>
                                  <p className="text-sm text-orange-400 font-mono font-medium">{part.temperature} <span className="text-xs text-orange-400/60">°C</span></p>
                                </div>
                                <div className="bg-[#0b1121] p-2.5 rounded-lg border border-slate-800">
                                  <p className="text-[10px] text-slate-500 font-mono tracking-wider mb-0.5">VIBRATION</p>
                                  <p className="text-sm text-cyan-400 font-mono font-medium">{part.vibration} <span className="text-xs text-cyan-400/60">mm/s</span></p>
                                </div>
                                <div className="bg-[#0b1121] p-2.5 rounded-lg border border-slate-800 col-span-2">
                                  <p className="text-[10px] text-slate-500 font-mono tracking-wider mb-0.5 flex justify-between">
                                    <span>LAST REPLACED</span>
                                    {part.sensors && part.sensors.length > 0 && <span>SENSORS: {part.sensors.join(", ")}</span>}
                                  </p>
                                  <p className="text-sm text-slate-300 font-mono font-medium">{part.lastReplaced}</p>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* 点击放大后的独立图表查看器 */}
      <Dialog open={!!expandedChart} onOpenChange={(open) => !open && setExpandedChart(null)}>
        <DialogContent className="max-w-[75vw] xl:max-w-[1000px] w-full h-[65vh] bg-[#0b1121] border-slate-800 p-6 flex flex-col shadow-2xl rounded-xl">
          <DialogHeader className="shrink-0 mb-4">
            <DialogTitle className="text-xl font-mono text-blue-400 flex items-center gap-3 uppercase tracking-widest">
              <Activity className="w-6 h-6" />
              {expandedChart} - DETAILED ANALYSIS
            </DialogTitle>
            <DialogDescription className="text-slate-500 font-mono text-sm mt-2">
              High-resolution telemetric data view. Hover over data points for specific cycle values.
            </DialogDescription>
          </DialogHeader>
          
          <div className="flex-1 w-full min-h-0 bg-[#111827] rounded-xl border border-slate-800/80 p-6">
            {renderExpandedChart()}
          </div>
        </DialogContent>
      </Dialog>

    </div>
  );
}