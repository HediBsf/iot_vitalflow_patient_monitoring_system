import React from 'react';
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function Card({ className, children }: { className?: string, children: React.ReactNode }) {
  return (
    <div className={cn("rounded-xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur-sm", className)}>
      {children}
    </div>
  );
}

export function MetricCard({ title, value, unit, icon: Icon, color }: any) {
  const colorStyles = {
    red: "text-red-400 border-red-500/20 bg-red-500/10",
    blue: "text-blue-400 border-blue-500/20 bg-blue-500/10",
    green: "text-emerald-400 border-emerald-500/20 bg-emerald-500/10",
    yellow: "text-amber-400 border-amber-500/20 bg-amber-500/10",
  };

  const style = colorStyles[color as keyof typeof colorStyles] || colorStyles.blue;

  return (
    <div className={cn("relative overflow-hidden rounded-xl border p-4 transition-all hover:scale-[1.02]", style)}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-80">{title}</p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold tracking-tight">{value || "--"}</span>
            <span className="text-sm opacity-60">{unit}</span>
          </div>
        </div>
        <div className="rounded-full bg-white/10 p-2">
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  );
}

export function AlertItem({ alert }: any) {
  return (
    <div className="mb-3 rounded-lg border border-red-500/20 bg-red-500/5 p-3 transition-colors hover:bg-red-500/10">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 animate-pulse rounded-full bg-red-500" />
          <span className="font-semibold text-red-200">Patient {alert.subject_id}</span>
        </div>
        <span className="text-xs text-red-300/60">
            {new Date(alert.timestamp).toLocaleTimeString()}
        </span>
      </div>
      <div className="mt-1 pl-4">
        <p className="text-sm text-red-200/80">
          {alert.metric}: <span className="font-bold">{alert.avg_value.toFixed(1)}</span>
        </p>
        {alert.device_id && (
          <p className="text-xs text-slate-500 mt-0.5">
            Device: {alert.device_id}
          </p>
        )}
        <p className="text-xs text-red-400/60 mt-1 uppercase tracking-wider font-bold">
          {alert.message}
        </p>
      </div>
    </div>
  );
}
