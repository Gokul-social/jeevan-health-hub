import { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { PageHeader } from "@/components/ui/page-header";
import { StatusBadge } from "@/components/ui/status-badge";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { 
  FileText,
  Pill,
  TestTube,
  Calendar,
  Download,
  Upload,
  Cloud,
  Check,
  ChevronRight,
  Clock
} from "lucide-react";
import { cn } from "@/lib/utils";

type Tab = "prescriptions" | "labReports" | "visits";

interface Record {
  id: number;
  title: string;
  doctor: string;
  date: string;
  type: string;
  synced: boolean;
}

const prescriptions: Record[] = [
  {
    id: 1,
    title: "Common Cold Treatment",
    doctor: "Dr. Priya Sharma",
    date: "Dec 25, 2024",
    type: "prescription",
    synced: true,
  },
  {
    id: 2,
    title: "Vitamin D Supplement",
    doctor: "Dr. Rajesh Kumar",
    date: "Dec 20, 2024",
    type: "prescription",
    synced: true,
  },
  {
    id: 3,
    title: "Allergy Medication",
    doctor: "Dr. Anjali Patel",
    date: "Dec 15, 2024",
    type: "prescription",
    synced: false,
  },
];

const labReports: Record[] = [
  {
    id: 1,
    title: "Complete Blood Count",
    doctor: "City Lab",
    date: "Dec 22, 2024",
    type: "lab",
    synced: true,
  },
  {
    id: 2,
    title: "Thyroid Profile",
    doctor: "City Lab",
    date: "Dec 10, 2024",
    type: "lab",
    synced: true,
  },
];

const visits: Record[] = [
  {
    id: 1,
    title: "General Checkup",
    doctor: "Dr. Priya Sharma",
    date: "Dec 25, 2024",
    type: "visit",
    synced: true,
  },
  {
    id: 2,
    title: "Follow-up Consultation",
    doctor: "Dr. Rajesh Kumar",
    date: "Dec 18, 2024",
    type: "visit",
    synced: true,
  },
];

export default function HealthRecordsScreen() {
  const [activeTab, setActiveTab] = useState<Tab>("prescriptions");

  const tabs = [
    { id: "prescriptions" as Tab, label: "Prescriptions", icon: Pill, count: prescriptions.length },
    { id: "labReports" as Tab, label: "Lab Reports", icon: TestTube, count: labReports.length },
    { id: "visits" as Tab, label: "Visits", icon: Calendar, count: visits.length },
  ];

  const getRecords = () => {
    switch (activeTab) {
      case "prescriptions":
        return prescriptions;
      case "labReports":
        return labReports;
      case "visits":
        return visits;
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case "prescription":
        return Pill;
      case "lab":
        return TestTube;
      case "visit":
        return Calendar;
      default:
        return FileText;
    }
  };

  return (
    <AppLayout>
      <PageHeader
        title="Health Records"
        subtitle="Your medical history"
        showBack
        rightContent={
          <StatusBadge variant="secure" label="Encrypted" />
        }
      />

      <div className="px-4 py-4 space-y-4">
        {/* Sync status */}
        <div className="flex items-center justify-between p-4 bg-success-light rounded-2xl">
          <div className="flex items-center gap-3">
            <Cloud className="w-5 h-5 text-success" />
            <div>
              <p className="font-medium text-foreground">All synced</p>
              <p className="text-xs text-muted-foreground">Last sync: 2 mins ago</p>
            </div>
          </div>
          <div className="w-8 h-8 rounded-full bg-success flex items-center justify-center">
            <Check className="w-4 h-4 text-success-foreground" />
          </div>
        </div>

        {/* Upload/Download */}
        <div className="flex gap-3">
          <Button variant="outline" className="flex-1 h-12 rounded-xl">
            <Upload className="w-4 h-4 mr-2" />
            Upload
          </Button>
          <Button variant="outline" className="flex-1 h-12 rounded-xl">
            <Download className="w-4 h-4 mr-2" />
            Download All
          </Button>
        </div>

        {/* Tabs */}
        <div className="flex bg-secondary rounded-2xl p-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex-1 py-3 px-2 rounded-xl flex items-center justify-center gap-2 transition-all font-medium tap-target",
                  activeTab === tab.id
                    ? "bg-card shadow-sm text-foreground"
                    : "text-muted-foreground"
                )}
              >
                <Icon className="w-4 h-4" />
                <span className="text-sm">{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Records list */}
        <div className="space-y-3">
          {getRecords().length === 0 ? (
            <EmptyState
              icon={FileText}
              title="No records yet"
              description="Your medical records will appear here once added"
              actionLabel="Upload Record"
              onAction={() => {}}
            />
          ) : (
            getRecords().map((record) => {
              const Icon = getIcon(record.type);
              return (
                <button
                  key={record.id}
                  className="w-full bg-card rounded-2xl p-4 border border-border/50 shadow-sm text-left tap-target"
                >
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-primary-light flex items-center justify-center flex-shrink-0">
                      <Icon className="w-6 h-6 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-semibold text-foreground truncate pr-2">
                          {record.title}
                        </h3>
                        <ChevronRight className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                      </div>
                      <p className="text-sm text-muted-foreground">{record.doctor}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                          <Clock className="w-3 h-3" />
                          {record.date}
                        </div>
                        {record.synced ? (
                          <StatusBadge variant="online" label="Synced" showIcon={false} />
                        ) : (
                          <StatusBadge variant="offline" label="Pending" showIcon={false} />
                        )}
                      </div>
                    </div>
                  </div>
                </button>
              );
            })
          )}
        </div>
      </div>
    </AppLayout>
  );
}
