import { cn } from "@/lib/utils";

interface SkeletonCardProps {
  className?: string;
  lines?: number;
  showIcon?: boolean;
}

export function SkeletonCard({ 
  className, 
  lines = 2, 
  showIcon = true 
}: SkeletonCardProps) {
  return (
    <div
      className={cn(
        "bg-card rounded-2xl p-4 border border-border/50 animate-pulse",
        className
      )}
    >
      {showIcon && (
        <div className="w-12 h-12 rounded-xl bg-muted mb-3" />
      )}
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={cn(
            "h-4 bg-muted rounded-md",
            i === 0 ? "w-3/4" : "w-1/2",
            i > 0 && "mt-2"
          )}
        />
      ))}
    </div>
  );
}

export function SkeletonList({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}
