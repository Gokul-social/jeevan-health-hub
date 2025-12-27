import { cn } from "@/lib/utils";
import { Wifi, WifiOff, Cloud, Cpu, Shield, AlertTriangle } from "lucide-react";

interface StatusBadgeProps {
  variant: "online" | "offline" | "cloud" | "local" | "secure" | "warning";
  label?: string;
  className?: string;
  showIcon?: boolean;
}

const variants = {
  online: {
    bg: "bg-success-light",
    text: "text-success",
    icon: Wifi,
    defaultLabel: "Online",
  },
  offline: {
    bg: "bg-offline-light",
    text: "text-offline",
    icon: WifiOff,
    defaultLabel: "Offline",
  },
  cloud: {
    bg: "bg-primary-light",
    text: "text-primary",
    icon: Cloud,
    defaultLabel: "Cloud AI",
  },
  local: {
    bg: "bg-accent",
    text: "text-accent-foreground",
    icon: Cpu,
    defaultLabel: "On-Device",
  },
  secure: {
    bg: "bg-success-light",
    text: "text-success",
    icon: Shield,
    defaultLabel: "Encrypted",
  },
  warning: {
    bg: "bg-warning-light",
    text: "text-warning",
    icon: AlertTriangle,
    defaultLabel: "Low Stock",
  },
};

export function StatusBadge({ 
  variant, 
  label, 
  className, 
  showIcon = true 
}: StatusBadgeProps) {
  const config = variants[variant];
  const Icon = config.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold",
        config.bg,
        config.text,
        className
      )}
    >
      {showIcon && <Icon className="w-3 h-3" />}
      {label || config.defaultLabel}
    </span>
  );
}
