import { cn } from "@/lib/utils";
import { Bot, User } from "lucide-react";

interface ChatBubbleProps {
  message: string;
  isBot?: boolean;
  timestamp?: string;
  isTyping?: boolean;
}

export function ChatBubble({
  message,
  isBot = false,
  timestamp,
  isTyping = false,
}: ChatBubbleProps) {
  return (
    <div
      className={cn(
        "flex gap-3 animate-slide-up",
        isBot ? "justify-start" : "justify-end"
      )}
    >
      {isBot && (
        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
          <Bot className="w-4 h-4 text-primary-foreground" />
        </div>
      )}
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-3",
          isBot
            ? "bg-card border border-border/50 rounded-tl-md"
            : "bg-primary text-primary-foreground rounded-tr-md"
        )}
      >
        {isTyping ? (
          <div className="flex gap-1 items-center h-5">
            <span className="w-2 h-2 rounded-full bg-muted-foreground animate-pulse" />
            <span className="w-2 h-2 rounded-full bg-muted-foreground animate-pulse delay-100" />
            <span className="w-2 h-2 rounded-full bg-muted-foreground animate-pulse delay-200" />
          </div>
        ) : (
          <p className="text-sm leading-relaxed">{message}</p>
        )}
        {timestamp && (
          <span
            className={cn(
              "text-xs mt-1 block",
              isBot ? "text-muted-foreground" : "text-primary-foreground/70"
            )}
          >
            {timestamp}
          </span>
        )}
      </div>
      {!isBot && (
        <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0">
          <User className="w-4 h-4 text-foreground" />
        </div>
      )}
    </div>
  );
}
