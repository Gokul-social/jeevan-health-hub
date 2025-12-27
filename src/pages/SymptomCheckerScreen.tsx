import { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { PageHeader } from "@/components/ui/page-header";
import { ChatBubble } from "@/components/ui/chat-bubble";
import { StatusBadge } from "@/components/ui/status-badge";
import { Button } from "@/components/ui/button";
import { 
  Send, 
  Mic, 
  AlertCircle,
  Stethoscope,
  Home
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Message {
  id: number;
  text: string;
  isBot: boolean;
  timestamp: string;
}

const symptomOptions = [
  "Headache",
  "Fever",
  "Cough",
  "Fatigue",
  "Body Pain",
  "Nausea",
];

export default function SymptomCheckerScreen() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hello! I'm your AI health assistant. Tell me, what symptoms are you experiencing today?",
      isBot: true,
      timestamp: "10:30 AM",
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const isOnline = true;

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: messages.length + 1,
      text: input,
      isBot: false,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages([...messages, userMessage]);
    setInput("");
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      setIsTyping(false);
      const botMessage: Message = {
        id: messages.length + 2,
        text: "I understand you're experiencing those symptoms. Let me analyze this for you...",
        isBot: true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, botMessage]);
      
      setTimeout(() => setShowResult(true), 1500);
    }, 2000);
  };

  const handleSymptomClick = (symptom: string) => {
    setInput((prev) => (prev ? `${prev}, ${symptom}` : symptom));
  };

  return (
    <AppLayout>
      <PageHeader
        title="Symptom Checker"
        showBack
        rightContent={
          <StatusBadge 
            variant={isOnline ? "cloud" : "local"} 
            label={isOnline ? "Cloud AI" : "Offline AI"} 
          />
        }
      />

      <div className="flex flex-col h-[calc(100vh-180px)]">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
          {messages.map((msg) => (
            <ChatBubble
              key={msg.id}
              message={msg.text}
              isBot={msg.isBot}
              timestamp={msg.timestamp}
            />
          ))}
          
          {isTyping && (
            <ChatBubble message="" isBot isTyping />
          )}

          {/* Result Card */}
          {showResult && (
            <div className="bg-card rounded-2xl p-5 border border-border/50 shadow-md animate-slide-up">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-10 h-10 rounded-xl bg-warning-light flex items-center justify-center">
                  <AlertCircle className="w-5 h-5 text-warning" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">Possible Condition</h3>
                  <p className="text-sm text-muted-foreground">Based on your symptoms</p>
                </div>
              </div>

              <div className="space-y-3">
                <div className="p-3 bg-secondary rounded-xl">
                  <p className="font-medium text-foreground">Common Cold / Viral Infection</p>
                  <div className="flex items-center gap-2 mt-2">
                    <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                      <div className="h-full w-[75%] bg-primary rounded-full" />
                    </div>
                    <span className="text-sm font-semibold text-primary">75%</span>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button variant="outline" className="flex-1 h-12 rounded-xl">
                    <Home className="w-4 h-4 mr-2" />
                    Home Care
                  </Button>
                  <Button className="flex-1 h-12 rounded-xl">
                    <Stethoscope className="w-4 h-4 mr-2" />
                    Consult Doctor
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Quick Symptoms */}
        <div className="px-4 py-3 border-t border-border/50 bg-background">
          <div className="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4 scrollbar-hide">
            {symptomOptions.map((symptom) => (
              <button
                key={symptom}
                onClick={() => handleSymptomClick(symptom)}
                className={cn(
                  "px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all tap-target",
                  input.includes(symptom)
                    ? "bg-primary text-primary-foreground"
                    : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                )}
              >
                {symptom}
              </button>
            ))}
          </div>
        </div>

        {/* Input */}
        <div className="px-4 py-3 border-t border-border/50 bg-background">
          <div className="flex gap-2">
            <button className="w-12 h-12 rounded-xl bg-secondary flex items-center justify-center tap-target">
              <Mic className="w-5 h-5 text-muted-foreground" />
            </button>
            <div className="flex-1 relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSend()}
                placeholder="Describe your symptoms..."
                className="w-full h-12 px-4 rounded-xl bg-secondary border-0 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className={cn(
                "w-12 h-12 rounded-xl flex items-center justify-center tap-target transition-all",
                input.trim()
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary text-muted-foreground"
              )}
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
