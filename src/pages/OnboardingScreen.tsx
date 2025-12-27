import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { 
  Stethoscope, 
  WifiOff, 
  Shield, 
  Languages, 
  ChevronRight,
  Check
} from "lucide-react";
import { cn } from "@/lib/utils";

const slides = [
  {
    icon: Stethoscope,
    title: "AI-Powered Diagnosis",
    description: "Get instant symptom analysis powered by medical AI, even without internet",
    color: "bg-primary",
  },
  {
    icon: WifiOff,
    title: "Works Offline",
    description: "Access your health records, prescriptions, and AI assistance anywhere",
    color: "bg-success",
  },
  {
    icon: Shield,
    title: "Secure & Private",
    description: "Your health data is encrypted and protected with bank-grade security",
    color: "bg-accent-foreground",
  },
];

const languages = [
  { code: "en", name: "English", native: "English" },
  { code: "hi", name: "Hindi", native: "हिंदी" },
  { code: "ta", name: "Tamil", native: "தமிழ்" },
  { code: "te", name: "Telugu", native: "తెలుగు" },
  { code: "bn", name: "Bengali", native: "বাংলা" },
  { code: "mr", name: "Marathi", native: "मराठी" },
  { code: "gu", name: "Gujarati", native: "ગુજરાતી" },
  { code: "kn", name: "Kannada", native: "ಕನ್ನಡ" },
  { code: "ml", name: "Malayalam", native: "മലയാളം" },
  { code: "pa", name: "Punjabi", native: "ਪੰਜਾਬੀ" },
  { code: "or", name: "Odia", native: "ଓଡ଼ିଆ" },
];

export default function OnboardingScreen() {
  const navigate = useNavigate();
  const [currentSlide, setCurrentSlide] = useState(0);
  const [showLanguages, setShowLanguages] = useState(false);
  const [selectedLang, setSelectedLang] = useState("en");

  const handleNext = () => {
    if (currentSlide < slides.length - 1) {
      setCurrentSlide(currentSlide + 1);
    } else {
      setShowLanguages(true);
    }
  };

  const handleLanguageSelect = (code: string) => {
    setSelectedLang(code);
  };

  const handleGetStarted = () => {
    navigate("/auth");
  };

  if (showLanguages) {
    return (
      <div className="min-h-screen bg-background p-6 flex flex-col">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-xl bg-primary-light flex items-center justify-center">
              <Languages className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">Select Language</h1>
              <p className="text-sm text-muted-foreground">Choose your preferred language</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {languages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => handleLanguageSelect(lang.code)}
                className={cn(
                  "p-4 rounded-2xl border-2 text-left transition-all tap-target",
                  selectedLang === lang.code
                    ? "border-primary bg-primary-light"
                    : "border-border bg-card hover:border-primary/50"
                )}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-foreground">{lang.native}</p>
                    <p className="text-sm text-muted-foreground">{lang.name}</p>
                  </div>
                  {selectedLang === lang.code && (
                    <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center">
                      <Check className="w-4 h-4 text-primary-foreground" />
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>

        <Button 
          onClick={handleGetStarted} 
          size="lg" 
          className="w-full h-14 text-lg rounded-2xl mt-6"
        >
          Get Started
          <ChevronRight className="w-5 h-5 ml-2" />
        </Button>
      </div>
    );
  }

  const slide = slides[currentSlide];
  const Icon = slide.icon;

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Skip button */}
      <div className="p-4 flex justify-end">
        <button
          onClick={() => setShowLanguages(true)}
          className="text-muted-foreground text-sm font-medium tap-target"
        >
          Skip
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-8">
        <div className="animate-scale-in">
          <div className={cn(
            "w-32 h-32 rounded-3xl flex items-center justify-center mb-8 mx-auto",
            slide.color
          )}>
            <Icon className="w-16 h-16 text-primary-foreground" />
          </div>
          
          <h2 className="text-2xl font-bold text-foreground text-center mb-4">
            {slide.title}
          </h2>
          
          <p className="text-muted-foreground text-center max-w-[300px] mx-auto text-lg">
            {slide.description}
          </p>
        </div>
      </div>

      {/* Navigation */}
      <div className="p-6">
        {/* Dots */}
        <div className="flex justify-center gap-2 mb-6">
          {slides.map((_, index) => (
            <div
              key={index}
              className={cn(
                "h-2 rounded-full transition-all duration-300",
                index === currentSlide
                  ? "w-8 bg-primary"
                  : "w-2 bg-muted"
              )}
            />
          ))}
        </div>

        <Button 
          onClick={handleNext} 
          size="lg" 
          className="w-full h-14 text-lg rounded-2xl"
        >
          {currentSlide === slides.length - 1 ? "Choose Language" : "Next"}
          <ChevronRight className="w-5 h-5 ml-2" />
        </Button>
      </div>
    </div>
  );
}
