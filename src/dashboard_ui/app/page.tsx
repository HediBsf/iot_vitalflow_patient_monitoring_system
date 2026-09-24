"use client";

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Activity, Heart, Wind, Droplets, AlertTriangle, User } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, MetricCard, AlertItem } from '../components/ui-components';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Dashboard() {
  const [patients, setPatients] = useState<number[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<number | null>(null);
  const [selectedMetric, setSelectedMetric] = useState('HeartRate');
  const [vitalsHistory, setVitalsHistory] = useState<any[]>([]);
  const [latestVitals, setLatestVitals] = useState<any>({});
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch Patients List
  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const res = await axios.get(`${API_URL}/patients`);
        setPatients(res.data.patients);
        if (res.data.patients.length > 0 && !selectedPatient) {
          setSelectedPatient(res.data.patients[0]);
        }
      } catch (err) {
        console.error("Failed to fetch patients", err);
      }
    };
    fetchPatients();
    const interval = setInterval(fetchPatients, 10000);
    return () => clearInterval(interval);
  }, []);

  // Fetch Data Loop
  useEffect(() => {
    const fetchData = async () => {
      if (!selectedPatient) return;

      try {
        // 1. History for Graph
        const historyRes = await axios.get(`${API_URL}/vitals/${selectedPatient}`, {
          params: { metric: selectedMetric, limit: 50 }
        });
        setVitalsHistory(historyRes.data);

        // 2. Latest Vitals for Cards
        const latestRes = await axios.get(`${API_URL}/latest/${selectedPatient}`);
        setLatestVitals(latestRes.data);

        // 3. Alerts
        const alertsRes = await axios.get(`${API_URL}/alerts`);
        setAlerts(alertsRes.data);
        
        setLoading(false);
      } catch (err) {
        console.error("Error fetching dashboard data", err);
      }
    };

    if (selectedPatient) {
      fetchData();
      const interval = setInterval(fetchData, 2000);
      return () => clearInterval(interval);
    }
  }, [selectedPatient, selectedMetric]);

  const getMetricColor = (metric: string) => {
    switch(metric) {
      case 'HeartRate': return '#ef4444'; // red
      case 'O2Sat': return '#3b82f6'; // blue
      case 'RespRate': return '#10b981'; // green
      case 'SysBP': return '#f59e0b'; // yellow
      default: return '#8884d8';
    }
  };

  return (
    <div className="min-h-screen bg-[#0B1120] text-slate-200 p-6">
      {/* Header */}
      <header className="mb-8 flex items-center justify-between border-b border-white/10 pb-6">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-blue-600/20 p-2">
            <Activity className="h-6 w-6 text-blue-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">ICU Command Center</h1>
            <p className="text-sm text-slate-400">Real-time Patient Monitoring System</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 rounded-full bg-emerald-500/10 px-3 py-1 text-sm font-medium text-emerald-400 border border-emerald-500/20">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            System Online
          </div>
        </div>
      </header>

      {/* Controls */}
      <div className="mb-8 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-400">Select Patient</label>
          <select 
            className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none"
            value={selectedPatient || ''}
            onChange={(e) => setSelectedPatient(Number(e.target.value))}
          >
            {patients.map(p => (
              <option key={p} value={p}>Patient {p}</option>
            ))}
          </select>
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-400">Graph Metric</label>
          <div className="flex rounded-lg border border-white/10 bg-white/5 p-1">
            {['HeartRate', 'O2Sat', 'RespRate', 'SysBP'].map((m) => (
              <button
                key={m}
                onClick={() => setSelectedMetric(m)}
                className={`flex-1 rounded-md px-3 py-1.5 text-xs font-medium transition-all ${
                  selectedMetric === m 
                    ? 'bg-blue-600 text-white shadow-lg' 
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {m}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="mb-8 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard 
          title="Heart Rate" 
          value={latestVitals.HeartRate?.toFixed(0)} 
          unit="BPM" 
          icon={Heart} 
          color="red" 
        />
        <MetricCard 
          title="O2 Saturation" 
          value={latestVitals.O2Sat?.toFixed(0)} 
          unit="%" 
          icon={Droplets} 
          color="blue" 
        />
        <MetricCard 
          title="Blood Pressure" 
          value={latestVitals.SysBP?.toFixed(0)} 
          unit="mmHg" 
          icon={Activity} 
          color="yellow" 
        />
        <MetricCard 
          title="Resp. Rate" 
          value={latestVitals.RespRate?.toFixed(0)} 
          unit="bpm" 
          icon={Wind} 
          color="green" 
        />
      </div>

      {/* Main Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Graph Section */}
        <Card className="lg:col-span-2 min-h-[500px]">
          <div className="mb-6 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Real-time Trends</h3>
            <span className="text-sm text-slate-400">Last 50 readings</span>
          </div>
          <div className="h-[400px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={vitalsHistory}>
                <defs>
                  <linearGradient id="colorMetric" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={getMetricColor(selectedMetric)} stopOpacity={0.3}/>
                    <stop offset="95%" stopColor={getMetricColor(selectedMetric)} stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis 
                  dataKey="timestamp" 
                  hide={true} 
                />
                <YAxis 
                  stroke="#94a3b8" 
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                  domain={['auto', 'auto']}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="value" 
                  stroke={getMetricColor(selectedMetric)} 
                  strokeWidth={3}
                  fillOpacity={1} 
                  fill="url(#colorMetric)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Alerts Section */}
        <Card className="h-[500px] flex flex-col">
          <div className="mb-4 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-400" />
            <h3 className="text-lg font-semibold text-white">Critical Alerts</h3>
          </div>
          <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
            {alerts.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center text-slate-500">
                <p>No active alerts</p>
              </div>
            ) : (
              alerts.map((alert, i) => (
                <AlertItem key={i} alert={alert} />
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
