import { cn } from "@/lib/utils";
import { ChevronLeft, Settings } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { StatusBadge } from "./status-badge";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  showBack?: boolean;
  showSettings?: boolean;
  showStatus?: boolean;
  isOnline?: boolean;
  className?: string;
  rightContent?: React.ReactNode;
}

export function PageHeader({
  title,
  subtitle,
  showBack = false,
  showSettings = false,
  showStatus = false,
  isOnline = true,
  className,
  rightContent,
}: PageHeaderProps) {
  const navigate = useNavigate();

  return (
    <header
      className={cn(
        "sticky top-0 z-40 bg-background/80 backdrop-blur-lg border-b border-border/50 safe-area-inset-top",
        className
      )}
    >
      <div className="flex items-center justify-between px-4 py-4">
        <div className="flex items-center gap-3">
          {showBack && (
            <button
              onClick={() => navigate(-1)}
              className="w-10 h-10 rounded-xl bg-secondary flex items-center justify-center tap-target"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
          )}
          <div>
            <h1 className="text-xl font-bold text-foreground">{title}</h1>
            {subtitle && (
              <p className="text-sm text-muted-foreground">{subtitle}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {showStatus && (
            <StatusBadge variant={isOnline ? "online" : "offline"} />
          )}
          {rightContent}
          {showSettings && (
            <button
              onClick={() => navigate("/settings")}
              className="w-10 h-10 rounded-xl bg-secondary flex items-center justify-center tap-target"
            >
              <Settings className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
