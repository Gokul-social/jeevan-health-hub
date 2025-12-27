import { AppLayout } from "@/components/layout/AppLayout";
import { PageHeader } from "@/components/ui/page-header";
import { ActionCard } from "@/components/ui/action-card";
import { StatCard } from "@/components/ui/stat-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { useNavigate } from "react-router-dom";
import { 
  Stethoscope, 
  Video, 
  FileText, 
  MapPin,
  Heart,
  Activity,
  Thermometer,
  Droplets,
  Bell
} from "lucide-react";

export default function HomeScreen() {
  const navigate = useNavigate();
  const isOnline = true; // Mock online status

  return (
    <AppLayout>
      <PageHeader
        title="Hi, Rahul"
        subtitle="How are you feeling today?"
        showSettings
        showStatus
        isOnline={isOnline}
      />

      <div className="px-4 py-4 space-y-6">
        {/* Quick Actions */}
        <section>
          <h2 className="text-lg font-semibold text-foreground mb-3">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-3">
            <ActionCard
              icon={Stethoscope}
              title="AI Symptom Checker"
              description="Get instant analysis"
              variant="primary"
              onClick={() => navigate("/symptoms")}
              badge={<StatusBadge variant="local" label="TinyML" showIcon={false} />}
            />
            <ActionCard
              icon={Video}
              title="Video Consult"
              description="Talk to a doctor"
              onClick={() => navigate("/consult")}
            />
            <ActionCard
              icon={FileText}
              title="Prescriptions"
              description="View your medicines"
              onClick={() => navigate("/records")}
            />
            <ActionCard
              icon={MapPin}
              title="Nearby Pharmacy"
              description="Find medicines"
              onClick={() => navigate("/pharmacy")}
            />
          </div>
        </section>

        {/* Health Stats */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-foreground">Today's Vitals</h2>
            <button className="text-sm text-primary font-medium tap-target">
              Update
            </button>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <StatCard
              icon={Heart}
              label="Heart Rate"
              value="72"
              unit="bpm"
              status="normal"
            />
            <StatCard
              icon={Activity}
              label="Blood Pressure"
              value="120/80"
              unit="mmHg"
              status="normal"
            />
            <StatCard
              icon={Thermometer}
              label="Temperature"
              value="98.4"
              unit="°F"
              status="normal"
            />
            <StatCard
              icon={Droplets}
              label="SpO2"
              value="98"
              unit="%"
              status="normal"
            />
          </div>
        </section>

        {/* Upcoming */}
        <section>
          <h2 className="text-lg font-semibold text-foreground mb-3">Upcoming</h2>
          <div className="bg-card rounded-2xl p-4 border border-border/50 shadow-sm">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-primary-light flex items-center justify-center flex-shrink-0">
                <Video className="w-6 h-6 text-primary" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold text-foreground">Dr. Priya Sharma</h3>
                  <StatusBadge variant="online" label="Online" showIcon={false} />
                </div>
                <p className="text-sm text-muted-foreground">General Physician</p>
                <p className="text-sm text-primary font-medium mt-2">Today, 4:30 PM</p>
              </div>
              <button className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center tap-target">
                <Bell className="w-5 h-5 text-primary-foreground" />
              </button>
            </div>
          </div>
        </section>

        {/* Health Tips */}
        <section>
          <h2 className="text-lg font-semibold text-foreground mb-3">Health Tips</h2>
          <div className="bg-gradient-to-br from-primary to-primary-dark rounded-2xl p-5 text-primary-foreground">
            <p className="text-sm opacity-80 mb-1">Daily Tip</p>
            <p className="font-medium">
              Stay hydrated! Drink at least 8 glasses of water daily for better immunity and energy.
            </p>
          </div>
        </section>
      </div>
    </AppLayout>
  );
}
