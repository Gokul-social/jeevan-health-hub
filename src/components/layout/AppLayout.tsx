import { ReactNode } from "react";
import { BottomNav } from "@/components/ui/bottom-nav";

interface AppLayoutProps {
  children: ReactNode;
  hideNav?: boolean;
}

export function AppLayout({ children, hideNav = false }: AppLayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      <main className={!hideNav ? "pb-24" : ""}>
        {children}
      </main>
      {!hideNav && <BottomNav />}
    </div>
  );
}
