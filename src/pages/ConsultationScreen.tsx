import { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { PageHeader } from "@/components/ui/page-header";
import { StatusBadge } from "@/components/ui/status-badge";
import { Button } from "@/components/ui/button";
import { 
  Video,
  Phone,
  MessageSquare,
  Mic,
  MicOff,
  Camera,
  CameraOff,
  PhoneOff,
  RotateCcw,
  Wifi,
  Shield,
  Clock,
  Star
} from "lucide-react";
import { cn } from "@/lib/utils";

type ConsultMode = "list" | "video";

interface Doctor {
  id: number;
  name: string;
  specialty: string;
  rating: number;
  experience: string;
  isOnline: boolean;
  nextAvailable: string;
  image: string;
}

const doctors: Doctor[] = [
  {
    id: 1,
    name: "Dr. Priya Sharma",
    specialty: "General Physician",
    rating: 4.8,
    experience: "12 years",
    isOnline: true,
    nextAvailable: "Available now",
    image: "PS",
  },
  {
    id: 2,
    name: "Dr. Rajesh Kumar",
    specialty: "Cardiologist",
    rating: 4.9,
    experience: "15 years",
    isOnline: true,
    nextAvailable: "Available now",
    image: "RK",
  },
  {
    id: 3,
    name: "Dr. Anjali Patel",
    specialty: "Pediatrician",
    rating: 4.7,
    experience: "8 years",
    isOnline: false,
    nextAvailable: "2:30 PM",
    image: "AP",
  },
];

export default function ConsultationScreen() {
  const [mode, setMode] = useState<ConsultMode>("list");
  const [isMuted, setIsMuted] = useState(false);
  const [isCameraOff, setIsCameraOff] = useState(false);
  const [bandwidth, setBandwidth] = useState<"high" | "medium" | "low">("high");

  if (mode === "video") {
    return (
      <div className="min-h-screen bg-foreground relative">
        {/* Video feed placeholder */}
        <div className="absolute inset-0 bg-gradient-to-b from-foreground/80 to-foreground flex items-center justify-center">
          <div className="text-center">
            <div className="w-24 h-24 rounded-full bg-primary/20 flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl font-bold text-primary-foreground">PS</span>
            </div>
            <p className="text-primary-foreground/80 text-lg">Dr. Priya Sharma</p>
            <p className="text-primary-foreground/60 text-sm">Connecting...</p>
          </div>
        </div>

        {/* Self view */}
        <div className="absolute top-20 right-4 w-28 h-36 rounded-2xl bg-primary/30 border-2 border-primary-foreground/20 overflow-hidden">
          {isCameraOff ? (
            <div className="w-full h-full flex items-center justify-center bg-muted">
              <CameraOff className="w-8 h-8 text-muted-foreground" />
            </div>
          ) : (
            <div className="w-full h-full bg-secondary flex items-center justify-center">
              <span className="text-lg font-semibold text-foreground">You</span>
            </div>
          )}
        </div>

        {/* Top bar */}
        <div className="absolute top-0 left-0 right-0 p-4 flex items-center justify-between safe-area-inset-top">
          <div className="flex items-center gap-2">
            <StatusBadge variant="secure" label="E2E Encrypted" />
          </div>
          <div className="flex items-center gap-2">
            <div className={cn(
              "flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium",
              bandwidth === "high" 
                ? "bg-success-light text-success"
                : bandwidth === "medium"
                ? "bg-warning-light text-warning"
                : "bg-destructive-light text-destructive"
            )}>
              <Wifi className="w-3 h-3" />
              {bandwidth === "high" ? "HD" : bandwidth === "medium" ? "SD" : "Audio"}
            </div>
          </div>
        </div>

        {/* Mode switch indicator */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
          <div className="flex gap-2 bg-background/20 backdrop-blur-sm rounded-full p-1">
            <button className="p-3 rounded-full bg-primary">
              <Video className="w-5 h-5 text-primary-foreground" />
            </button>
            <button className="p-3 rounded-full text-primary-foreground/60">
              <Phone className="w-5 h-5" />
            </button>
            <button className="p-3 rounded-full text-primary-foreground/60">
              <MessageSquare className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Controls */}
        <div className="absolute bottom-0 left-0 right-0 p-6 safe-area-inset-bottom">
          <div className="flex items-center justify-center gap-4">
            <button
              onClick={() => setIsMuted(!isMuted)}
              className={cn(
                "w-14 h-14 rounded-full flex items-center justify-center tap-target",
                isMuted ? "bg-destructive" : "bg-background/20 backdrop-blur-sm"
              )}
            >
              {isMuted ? (
                <MicOff className="w-6 h-6 text-destructive-foreground" />
              ) : (
                <Mic className="w-6 h-6 text-primary-foreground" />
              )}
            </button>

            <button
              onClick={() => setMode("list")}
              className="w-16 h-16 rounded-full bg-destructive flex items-center justify-center tap-target"
            >
              <PhoneOff className="w-7 h-7 text-destructive-foreground" />
            </button>

            <button
              onClick={() => setIsCameraOff(!isCameraOff)}
              className={cn(
                "w-14 h-14 rounded-full flex items-center justify-center tap-target",
                isCameraOff ? "bg-destructive" : "bg-background/20 backdrop-blur-sm"
              )}
            >
              {isCameraOff ? (
                <CameraOff className="w-6 h-6 text-destructive-foreground" />
              ) : (
                <Camera className="w-6 h-6 text-primary-foreground" />
              )}
            </button>

            <button className="w-14 h-14 rounded-full bg-background/20 backdrop-blur-sm flex items-center justify-center tap-target">
              <RotateCcw className="w-6 h-6 text-primary-foreground" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <AppLayout>
      <PageHeader
        title="Consult Doctor"
        subtitle="Connect with specialists"
        showBack
      />

      <div className="px-4 py-4 space-y-4">
        {/* Connection modes */}
        <div className="flex gap-3">
          <div className="flex-1 p-4 rounded-2xl bg-primary-light border border-primary/20">
            <Video className="w-6 h-6 text-primary mb-2" />
            <p className="font-semibold text-foreground">Video Call</p>
            <p className="text-xs text-muted-foreground mt-1">Best for detailed consultation</p>
          </div>
          <div className="flex-1 p-4 rounded-2xl bg-secondary border border-border/50">
            <Phone className="w-6 h-6 text-muted-foreground mb-2" />
            <p className="font-semibold text-foreground">Audio Call</p>
            <p className="text-xs text-muted-foreground mt-1">Low bandwidth mode</p>
          </div>
          <div className="flex-1 p-4 rounded-2xl bg-secondary border border-border/50">
            <MessageSquare className="w-6 h-6 text-muted-foreground mb-2" />
            <p className="font-semibold text-foreground">Chat</p>
            <p className="text-xs text-muted-foreground mt-1">Works offline</p>
          </div>
        </div>

        {/* Available doctors */}
        <div>
          <h2 className="text-lg font-semibold text-foreground mb-3">Available Doctors</h2>
          <div className="space-y-3">
            {doctors.map((doctor) => (
              <div
                key={doctor.id}
                className="bg-card rounded-2xl p-4 border border-border/50 shadow-sm"
              >
                <div className="flex gap-4">
                  <div className="w-14 h-14 rounded-xl bg-primary-light flex items-center justify-center flex-shrink-0">
                    <span className="text-lg font-bold text-primary">{doctor.image}</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-foreground">{doctor.name}</h3>
                      {doctor.isOnline && (
                        <div className="w-2 h-2 rounded-full bg-success" />
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{doctor.specialty}</p>
                    <div className="flex items-center gap-3 mt-2">
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 text-warning fill-warning" />
                        <span className="text-sm font-medium">{doctor.rating}</span>
                      </div>
                      <span className="text-muted-foreground">•</span>
                      <div className="flex items-center gap-1 text-sm text-muted-foreground">
                        <Clock className="w-3 h-3" />
                        {doctor.experience}
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between mt-4 pt-4 border-t border-border/50">
                  <span className={cn(
                    "text-sm font-medium",
                    doctor.isOnline ? "text-success" : "text-muted-foreground"
                  )}>
                    {doctor.nextAvailable}
                  </span>
                  <Button
                    size="sm"
                    className="rounded-xl"
                    onClick={() => setMode("video")}
                  >
                    <Video className="w-4 h-4 mr-2" />
                    Consult Now
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Security note */}
        <div className="flex items-center gap-3 p-4 bg-success-light rounded-2xl">
          <Shield className="w-5 h-5 text-success" />
          <p className="text-sm text-success">
            All consultations are end-to-end encrypted with AES-256 & TLS 1.3
          </p>
        </div>
      </div>
    </AppLayout>
  );
}
