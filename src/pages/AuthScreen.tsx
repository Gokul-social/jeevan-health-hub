import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Phone, 
  Mail, 
  ArrowRight, 
  Heart,
  User,
  Stethoscope,
  WifiOff
} from "lucide-react";
import { cn } from "@/lib/utils";

type AuthMethod = "phone" | "email";
type UserRole = "patient" | "doctor";

export default function AuthScreen() {
  const navigate = useNavigate();
  const [authMethod, setAuthMethod] = useState<AuthMethod>("phone");
  const [role, setRole] = useState<UserRole>("patient");
  const [inputValue, setInputValue] = useState("");
  const [isOfflineMode, setIsOfflineMode] = useState(false);

  const handleLogin = () => {
    // Mock login - in real app would verify JWT
    navigate("/");
  };

  const handleOfflineAccess = () => {
    setIsOfflineMode(true);
    setTimeout(() => navigate("/"), 1000);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <div className="p-6 pt-12">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl gradient-primary flex items-center justify-center">
            <Heart className="w-5 h-5 text-primary-foreground" />
          </div>
          <span className="text-xl font-bold text-foreground">
            Jeevan<span className="text-primary">+</span>
          </span>
        </div>
        <h1 className="text-3xl font-bold text-foreground mt-6">Welcome back</h1>
        <p className="text-muted-foreground mt-1">Sign in to access your health dashboard</p>
      </div>

      {/* Role Toggle */}
      <div className="px-6 mb-6">
        <p className="text-sm font-medium text-muted-foreground mb-3">I am a</p>
        <div className="flex gap-3">
          <button
            onClick={() => setRole("patient")}
            className={cn(
              "flex-1 p-4 rounded-2xl border-2 flex items-center gap-3 transition-all tap-target",
              role === "patient"
                ? "border-primary bg-primary-light"
                : "border-border bg-card"
            )}
          >
            <div className={cn(
              "w-10 h-10 rounded-xl flex items-center justify-center",
              role === "patient" ? "bg-primary" : "bg-secondary"
            )}>
              <User className={cn(
                "w-5 h-5",
                role === "patient" ? "text-primary-foreground" : "text-muted-foreground"
              )} />
            </div>
            <span className="font-semibold text-foreground">Patient</span>
          </button>
          
          <button
            onClick={() => setRole("doctor")}
            className={cn(
              "flex-1 p-4 rounded-2xl border-2 flex items-center gap-3 transition-all tap-target",
              role === "doctor"
                ? "border-primary bg-primary-light"
                : "border-border bg-card"
            )}
          >
            <div className={cn(
              "w-10 h-10 rounded-xl flex items-center justify-center",
              role === "doctor" ? "bg-primary" : "bg-secondary"
            )}>
              <Stethoscope className={cn(
                "w-5 h-5",
                role === "doctor" ? "text-primary-foreground" : "text-muted-foreground"
              )} />
            </div>
            <span className="font-semibold text-foreground">Doctor</span>
          </button>
        </div>
      </div>

      {/* Auth Method Toggle */}
      <div className="px-6 mb-4">
        <div className="flex bg-secondary rounded-2xl p-1">
          <button
            onClick={() => setAuthMethod("phone")}
            className={cn(
              "flex-1 py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all font-medium tap-target",
              authMethod === "phone"
                ? "bg-card shadow-sm text-foreground"
                : "text-muted-foreground"
            )}
          >
            <Phone className="w-4 h-4" />
            Phone
          </button>
          <button
            onClick={() => setAuthMethod("email")}
            className={cn(
              "flex-1 py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all font-medium tap-target",
              authMethod === "email"
                ? "bg-card shadow-sm text-foreground"
                : "text-muted-foreground"
            )}
          >
            <Mail className="w-4 h-4" />
            Email
          </button>
        </div>
      </div>

      {/* Input */}
      <div className="px-6 flex-1">
        <div className="relative">
          <Input
            type={authMethod === "phone" ? "tel" : "email"}
            placeholder={authMethod === "phone" ? "+91 Enter phone number" : "Enter your email"}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            className="h-14 text-lg rounded-2xl pl-4 pr-12 bg-card border-border"
          />
        </div>

        <Button
          onClick={handleLogin}
          size="lg"
          className="w-full h-14 text-lg rounded-2xl mt-4"
          disabled={!inputValue}
        >
          Continue
          <ArrowRight className="w-5 h-5 ml-2" />
        </Button>

        {/* Divider */}
        <div className="flex items-center gap-4 my-6">
          <div className="flex-1 h-px bg-border" />
          <span className="text-sm text-muted-foreground">or</span>
          <div className="flex-1 h-px bg-border" />
        </div>

        {/* Offline Access */}
        <button
          onClick={handleOfflineAccess}
          className="w-full p-4 rounded-2xl border-2 border-dashed border-border bg-offline-light flex items-center justify-center gap-3 tap-target transition-all hover:border-offline"
        >
          <WifiOff className="w-5 h-5 text-offline" />
          <span className="font-medium text-offline">Continue Offline</span>
        </button>

        {isOfflineMode && (
          <p className="text-center text-sm text-muted-foreground mt-4 animate-fade-in">
            Accessing cached data...
          </p>
        )}
      </div>

      {/* Footer */}
      <div className="p-6 text-center">
        <p className="text-xs text-muted-foreground">
          By continuing, you agree to our{" "}
          <span className="text-primary">Terms of Service</span> and{" "}
          <span className="text-primary">Privacy Policy</span>
        </p>
      </div>
    </div>
  );
}
