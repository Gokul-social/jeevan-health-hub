import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { 
  User,
  Languages,
  HardDrive,
  Shield,
  Bell,
  Moon,
  HelpCircle,
  LogOut,
  ChevronRight,
  Check,
  Lock,
  Smartphone
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SettingItem {
  icon: React.ElementType;
  label: string;
  value?: string;
  onClick?: () => void;
  danger?: boolean;
}

export default function SettingsScreen() {
  const navigate = useNavigate();
  const [showLanguageModal, setShowLanguageModal] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState("English");

  const storageUsed = 245; // MB
  const storageTotal = 500; // MB

  const settingsGroups: { title: string; items: SettingItem[] }[] = [
    {
      title: "Account",
      items: [
        {
          icon: User,
          label: "Profile",
          value: "Rahul Kumar",
          onClick: () => {},
        },
        {
          icon: Bell,
          label: "Notifications",
          value: "Enabled",
          onClick: () => {},
        },
      ],
    },
    {
      title: "Preferences",
      items: [
        {
          icon: Languages,
          label: "Language",
          value: selectedLanguage,
          onClick: () => setShowLanguageModal(true),
        },
        {
          icon: Moon,
          label: "Appearance",
          value: "System",
          onClick: () => {},
        },
      ],
    },
    {
      title: "Data & Storage",
      items: [
        {
          icon: HardDrive,
          label: "Offline Storage",
          value: `${storageUsed} MB / ${storageTotal} MB`,
          onClick: () => {},
        },
        {
          icon: Smartphone,
          label: "Sync Settings",
          value: "Auto-sync enabled",
          onClick: () => {},
        },
      ],
    },
    {
      title: "Security",
      items: [
        {
          icon: Shield,
          label: "Security Info",
          onClick: () => {},
        },
        {
          icon: Lock,
          label: "Privacy",
          onClick: () => {},
        },
      ],
    },
    {
      title: "Support",
      items: [
        {
          icon: HelpCircle,
          label: "Help & FAQ",
          onClick: () => {},
        },
      ],
    },
  ];

  const languages = [
    { code: "en", name: "English" },
    { code: "hi", name: "हिंदी (Hindi)" },
    { code: "ta", name: "தமிழ் (Tamil)" },
    { code: "te", name: "తెలుగు (Telugu)" },
    { code: "bn", name: "বাংলা (Bengali)" },
  ];

  return (
    <AppLayout>
      <PageHeader title="Settings" showBack />

      <div className="px-4 py-4 space-y-6">
        {/* Profile card */}
        <div className="bg-card rounded-2xl p-5 border border-border/50 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl gradient-primary flex items-center justify-center">
              <span className="text-2xl font-bold text-primary-foreground">RK</span>
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-bold text-foreground">Rahul Kumar</h2>
              <p className="text-muted-foreground">+91 98765 43210</p>
            </div>
            <ChevronRight className="w-5 h-5 text-muted-foreground" />
          </div>
        </div>

        {/* Storage indicator */}
        <div className="bg-card rounded-2xl p-4 border border-border/50 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary-light flex items-center justify-center">
                <HardDrive className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="font-semibold text-foreground">Offline Storage</p>
                <p className="text-xs text-muted-foreground">
                  {storageUsed} MB used of {storageTotal} MB
                </p>
              </div>
            </div>
          </div>
          <div className="h-2 bg-secondary rounded-full overflow-hidden">
            <div
              className="h-full bg-primary rounded-full transition-all"
              style={{ width: `${(storageUsed / storageTotal) * 100}%` }}
            />
          </div>
        </div>

        {/* Security badges */}
        <div className="bg-success-light rounded-2xl p-4">
          <div className="flex items-start gap-3">
            <Shield className="w-5 h-5 text-success mt-0.5" />
            <div>
              <p className="font-semibold text-foreground mb-2">Security & Privacy</p>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-card rounded-full text-xs font-medium text-foreground">
                  AES-256 Encryption
                </span>
                <span className="px-3 py-1 bg-card rounded-full text-xs font-medium text-foreground">
                  TLS 1.3
                </span>
                <span className="px-3 py-1 bg-card rounded-full text-xs font-medium text-foreground">
                  Zero-Knowledge
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Settings groups */}
        {settingsGroups.map((group) => (
          <div key={group.title}>
            <h3 className="text-sm font-semibold text-muted-foreground mb-2 px-1">
              {group.title}
            </h3>
            <div className="bg-card rounded-2xl border border-border/50 overflow-hidden">
              {group.items.map((item, index) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.label}
                    onClick={item.onClick}
                    className={cn(
                      "w-full flex items-center gap-4 p-4 tap-target text-left transition-colors hover:bg-secondary/50",
                      index > 0 && "border-t border-border/50",
                      item.danger && "text-destructive"
                    )}
                  >
                    <div
                      className={cn(
                        "w-10 h-10 rounded-xl flex items-center justify-center",
                        item.danger ? "bg-destructive-light" : "bg-secondary"
                      )}
                    >
                      <Icon
                        className={cn(
                          "w-5 h-5",
                          item.danger ? "text-destructive" : "text-muted-foreground"
                        )}
                      />
                    </div>
                    <div className="flex-1">
                      <p
                        className={cn(
                          "font-medium",
                          item.danger ? "text-destructive" : "text-foreground"
                        )}
                      >
                        {item.label}
                      </p>
                    </div>
                    {item.value && (
                      <span className="text-sm text-muted-foreground">{item.value}</span>
                    )}
                    <ChevronRight
                      className={cn(
                        "w-5 h-5",
                        item.danger ? "text-destructive" : "text-muted-foreground"
                      )}
                    />
                  </button>
                );
              })}
            </div>
          </div>
        ))}

        {/* Logout */}
        <Button
          variant="outline"
          className="w-full h-14 rounded-2xl border-destructive text-destructive hover:bg-destructive hover:text-destructive-foreground"
          onClick={() => navigate("/splash")}
        >
          <LogOut className="w-5 h-5 mr-2" />
          Log Out
        </Button>

        {/* Version */}
        <p className="text-center text-xs text-muted-foreground">
          Jeevan+ v1.0.0 • Made with ❤️ in India
        </p>
      </div>

      {/* Language Modal */}
      {showLanguageModal && (
        <div className="fixed inset-0 z-50 bg-foreground/50 flex items-end">
          <div className="w-full bg-background rounded-t-3xl p-6 animate-slide-in-bottom safe-area-inset-bottom">
            <h2 className="text-xl font-bold text-foreground mb-4">Select Language</h2>
            <div className="space-y-2">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => {
                    setSelectedLanguage(lang.name.split(" ")[0]);
                    setShowLanguageModal(false);
                  }}
                  className={cn(
                    "w-full p-4 rounded-xl flex items-center justify-between tap-target",
                    selectedLanguage === lang.name.split(" ")[0]
                      ? "bg-primary-light border-2 border-primary"
                      : "bg-secondary"
                  )}
                >
                  <span className="font-medium text-foreground">{lang.name}</span>
                  {selectedLanguage === lang.name.split(" ")[0] && (
                    <Check className="w-5 h-5 text-primary" />
                  )}
                </button>
              ))}
            </div>
            <Button
              variant="outline"
              className="w-full h-12 rounded-xl mt-4"
              onClick={() => setShowLanguageModal(false)}
            >
              Cancel
            </Button>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
