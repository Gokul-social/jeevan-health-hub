import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: string;
  unit?: string;
  status?: "normal" | "warning" | "critical";
  trend?: "up" | "down" | "stable";
  className?: string;
}

const statusColors = {
  normal: "text-success",
  warning: "text-warning",
  critical: "text-destructive",
};

export function StatCard({
  icon: Icon,
  label,
  value,
  unit,
  status = "normal",
  className,
}: StatCardProps) {
  return (
    <div
      className={cn(
        "bg-card rounded-2xl p-4 border border-border/50 shadow-sm",
        className
      )}
    >
      <div className="flex items-center gap-2 mb-2">
        <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center">
          <Icon className="w-4 h-4 text-muted-foreground" />
        </div>
        <span className="text-sm text-muted-foreground">{label}</span>
      </div>
      <div className="flex items-baseline gap-1">
        <span className={cn("text-2xl font-bold", statusColors[status])}>
          {value}
        </span>
        {unit && (
          <span className="text-sm text-muted-foreground">{unit}</span>
        )}
      </div>
    </div>
  );
}
