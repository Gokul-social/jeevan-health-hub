import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface ActionCardProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  onClick?: () => void;
  variant?: "default" | "primary" | "success" | "warning";
  className?: string;
  badge?: React.ReactNode;
}

const variants = {
  default: {
    container: "bg-card hover:bg-secondary/50",
    icon: "bg-secondary text-foreground",
  },
  primary: {
    container: "bg-primary-light hover:bg-primary-light/80",
    icon: "bg-primary text-primary-foreground",
  },
  success: {
    container: "bg-success-light hover:bg-success-light/80",
    icon: "bg-success text-success-foreground",
  },
  warning: {
    container: "bg-warning-light hover:bg-warning-light/80",
    icon: "bg-warning text-warning-foreground",
  },
};

export function ActionCard({
  icon: Icon,
  title,
  description,
  onClick,
  variant = "default",
  className,
  badge,
}: ActionCardProps) {
  const config = variants[variant];

  return (
    <button
      onClick={onClick}
      className={cn(
        "relative w-full p-4 rounded-2xl border border-border/50 transition-all duration-200",
        "active:scale-[0.98] tap-target text-left",
        "shadow-sm hover:shadow-md",
        config.container,
        className
      )}
    >
      {badge && (
        <div className="absolute top-3 right-3">{badge}</div>
      )}
      <div className={cn(
        "w-12 h-12 rounded-xl flex items-center justify-center mb-3",
        config.icon
      )}>
        <Icon className="w-6 h-6" />
      </div>
      <h3 className="font-semibold text-foreground">{title}</h3>
      {description && (
        <p className="text-sm text-muted-foreground mt-1">{description}</p>
      )}
    </button>
  );
}
