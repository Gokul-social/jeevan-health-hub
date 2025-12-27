import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Heart, Wifi } from "lucide-react";

export default function SplashScreen() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
      navigate("/onboarding");
    }, 2500);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="min-h-screen gradient-hero flex flex-col items-center justify-center p-6">
      <div className="animate-scale-in flex flex-col items-center">
        {/* Logo */}
        <div className="relative mb-6">
          <div className="w-24 h-24 rounded-3xl gradient-primary flex items-center justify-center shadow-lg">
            <Heart className="w-12 h-12 text-primary-foreground" />
          </div>
          <div className="absolute -bottom-1 -right-1 w-8 h-8 rounded-full bg-success flex items-center justify-center border-4 border-background">
            <Wifi className="w-4 h-4 text-success-foreground" />
          </div>
        </div>

        {/* App Name */}
        <h1 className="text-4xl font-bold text-foreground mb-2">
          Jeevan<span className="text-primary">+</span>
        </h1>
        
        {/* Tagline */}
        <p className="text-muted-foreground text-center text-lg max-w-[280px]">
          Healthcare Anywhere, Even Offline
        </p>

        {/* Loading indicator */}
        {isLoading && (
          <div className="mt-12 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse delay-100" />
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse delay-200" />
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="absolute bottom-8 text-center">
        <p className="text-xs text-muted-foreground">
          Secure • Private • Accessible
        </p>
      </div>
    </div>
  );
}
