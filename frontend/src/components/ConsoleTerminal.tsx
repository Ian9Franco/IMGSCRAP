"use client";

import React, { useEffect, useState, useRef } from "react";
import { Terminal, ChevronUp, X, Copy, Check } from "lucide-react";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";

interface LogEntry {
  time: string;
  source: string;
  level: string;
  message: string;
}

export function ConsoleTerminal() {
  const [isEnabled, setIsEnabled] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [isTabHovered, setIsTabHovered] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isCopiedAll, setIsCopiedAll] = useState(false);
  const [shouldBlink, setShouldBlink] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const isAtBottom = useRef(true);

  // Detectar si el usuario está al final del scroll
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const target = e.currentTarget;
    const diff = Math.abs(target.scrollHeight - target.scrollTop - target.clientHeight);
    isAtBottom.current = diff < 10;
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;
    interval = setInterval(async () => {
        try {
          const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
          const res = await fetch(`${API_BASE}/api/logs`);
          if (res.ok) {
            const data = await res.json();
            
            // Solo scrolleamos si hay logs nuevos Y el usuario estaba al final
            setLogs(prev => {
              const hasNew = data.logs.length > prev.length;
              if (hasNew && !isOpen) {
                setShouldBlink(true);
              }
              if (hasNew && isAtBottom.current && isOpen) {
                setTimeout(() => {
                  scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
                }, 100);
              }
              return data.logs;
            });
          }
        } catch {
          // ignore
        }
      }, 1500);
    return () => clearInterval(interval);
  }, [isEnabled, isOpen]);

  // Resetear parpadeo al abrir
  useEffect(() => {
    if (isOpen) {
      setShouldBlink(false);
    }
  }, [isOpen]);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copiado al portapapeles");
  };

  const copyAll = () => {
    const text = logs.map(l => `[${l.time}] [${l.source}] ${l.message}`).join("\n");
    navigator.clipboard.writeText(text);
    setIsCopiedAll(true);
    setTimeout(() => setIsCopiedAll(false), 2000);
    toast.success("Historial completo copiado");
  };

  const getColorClass = (source: string, level: string) => {
    if (level === "ERROR") return "text-red-500";
    if (source === "GEMINI-PROMPT") return "text-blue-400";
    if (source === "GEMINI-RESPONSE") return "text-green-400";
    if (source === "SigLIP" || source === "SigLIP") return "text-emerald-400";
    if (source === "CLIP") return "text-purple-400";
    return "text-gray-300";
  };

  // Botón de solapa (central)
  const renderTab = (mode: "enable" | "disable") => (
    <motion.button
      onMouseEnter={() => setIsTabHovered(true)}
      onMouseLeave={() => setIsTabHovered(false)}
      onClick={(e) => {
        e.stopPropagation();
        if (mode === "enable") {
          setIsEnabled(true);
        } else {
          setIsEnabled(false);
          setIsOpen(false);
        }
      }}
      className={`absolute left-1/2 -translate-x-1/2 w-12 h-6 bg-[#1e293b] border border-primary/30 rounded-t-xl flex items-center justify-center transition-all duration-300 shadow-[0_-4px_12px_rgba(0,0,0,0.5)] group z-50 overflow-hidden ${mode === "enable" ? "bottom-0" : "-top-6"}`}
      initial={false}
      animate={{
        backgroundColor: isTabHovered && mode === "disable" ? "#ef4444" : "#1e293b",
        borderColor: shouldBlink ? "#22c55e" : "rgba(91, 140, 255, 0.3)",
        boxShadow: shouldBlink ? "0 0 15px rgba(34, 197, 94, 0.5)" : "0 -4px 12px rgba(0,0,0,0.5)",
      }}
      transition={{
        borderColor: { duration: 0.5, repeat: shouldBlink ? Infinity : 0, repeatType: "reverse" },
        boxShadow: { duration: 0.5, repeat: shouldBlink ? Infinity : 0, repeatType: "reverse" }
      }}
    >
      <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity" />
      {shouldBlink && (
        <motion.div 
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-500 rounded-full shadow-[0_0_8px_#10b981] z-[60]"
        />
      )}
      {mode === "disable" ? (
        <X className={`w-3.5 h-3.5 transition-colors ${isTabHovered ? 'text-red-500 scale-110' : 'text-muted-foreground'}`} />
      ) : (
        <motion.div
          animate={{
            color: shouldBlink ? "#22c55e" : "rgba(16, 185, 129, 0.6)",
            scale: shouldBlink ? 1.2 : 1
          }}
          transition={{ duration: 0.5, repeat: shouldBlink ? Infinity : 0, repeatType: "reverse" }}
        >
          <ChevronUp className="w-4 h-4" />
        </motion.div>
      )}
    </motion.button>
  );

  if (!isEnabled) {
    return (
      <div className="relative w-full h-0 shrink-0">
        {renderTab("enable")}
      </div>
    );
  }

  return (
    <div className="relative w-full shrink-0 z-40">
      {renderTab("disable")}

      <div className={`relative w-full bg-background/95 border-t border-border/50 backdrop-blur-md transition-all duration-300 flex flex-col font-mono text-xs ${isOpen ? 'h-80' : 'h-10'}`}>
        
        {/* Header / Barra no interactiva (solo el chevron expande) */}
        <div 
          className="h-10 flex items-center justify-between px-4 border-b border-border/30 shrink-0"
        >
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-muted-foreground font-sans text-sm tracking-wide">
              <Terminal className="w-4 h-4 text-blue-400" />
              <span>AGENT.IO // BRAIN CONSOLE</span>
            </div>
            {isOpen && (
              <button 
                onClick={(e) => { e.stopPropagation(); copyAll(); }}
                className="flex items-center gap-1.5 px-2 py-1 rounded bg-primary/10 hover:bg-primary/20 text-primary text-[10px] font-bold transition-all border border-primary/20"
              >
                {isCopiedAll ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                COPIAR TODO
              </button>
            )}
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            <span className="text-[10px] opacity-50 mr-2">{logs.length} EVENTOS</span>
            <button 
              onClick={(e) => { e.stopPropagation(); setIsOpen(!isOpen); }}
              className="p-1 hover:bg-white/10 rounded-md transition-colors"
            >
              {isOpen ? <ChevronUp className="w-4 h-4 rotate-180 transition-transform" /> : <ChevronUp className="w-4 h-4 transition-transform" />}
            </button>
          </div>
        </div>

        {/* Contenido (Logs) */}
        {isOpen && (
          <div 
            ref={scrollRef}
            onScroll={handleScroll}
            className="flex-1 overflow-y-auto p-4 space-y-1 select-text scrollbar-thin scrollbar-thumb-primary/20"
          >
            {logs.length === 0 ? (
              <div className="text-gray-500 italic">Esperando actividad de la IA...</div>
            ) : (
              logs.map((log, idx) => (
                <div key={idx} className="group flex gap-3 items-start border-b border-border/10 pb-1.5 mb-1.5 hover:bg-white/[0.02] transition-colors relative">
                  <span className="text-gray-500 min-w-[65px] flex-shrink-0 select-none">[{log.time}]</span>
                  <span className={`font-semibold min-w-[120px] flex-shrink-0 select-none ${getColorClass(log.source, log.level)}`}>
                    [{log.source}]
                  </span>
                  <span className={`flex-1 whitespace-pre-wrap ${getColorClass(log.source, log.level)} opacity-90`}>
                    {log.message}
                  </span>
                  
                  {/* Botón copiar fila */}
                  <button 
                    onClick={() => copyToClipboard(log.message)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-primary/20 rounded transition-all text-muted-foreground hover:text-primary shrink-0"
                    title="Copiar mensaje"
                  >
                    <Copy className="w-3 h-3" />
                  </button>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
