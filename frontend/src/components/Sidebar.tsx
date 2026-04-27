"use client";

import {  } from "react";
import {
  FolderOpen, Search, Image as ImageIcon, Loader2,
  CheckCircle2, Play, Square, Send, RotateCcw, FolderSync, Settings, Brain, Copy
} from "lucide-react";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import type { Config, ConfigActions } from "@/hooks/useConfig";
import type { ScrapingJobActions } from "@/hooks/useScrapingJob";
import type { CopyGeneratorState } from "@/hooks/useCopyGenerator";

interface SidebarProps {
  url: string;
  setUrl: (v: string) => void;
  propertyName: string;
  setPropertyName: (v: string) => void;
  config: Config & ConfigActions;
  job: ScrapingJobActions;
  copy: CopyGeneratorState;
  activeTab: "manual" | "brain";
  setActiveTab: (tab: "manual" | "brain") => void;
}

interface ToggleProps {
  enabled: boolean;
  onChange: (v: boolean) => void;
  disabled?: boolean;
  label?: string;
  className?: string;
}

function Toggle({ enabled, onChange, disabled, label, className }: ToggleProps) {
  return (
    <div className={`flex items-center justify-between group cursor-pointer ${className}`} onClick={() => !disabled && onChange(!enabled)}>
      {label && <span className={`text-xs font-medium select-none transition-colors ${disabled ? 'text-muted-foreground/40' : 'text-muted-foreground group-hover:text-primary'}`}>{label}</span>}
      <button 
        disabled={disabled}
        className={`w-9 h-5 rounded-full transition-all duration-300 relative shadow-inner ${disabled ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'} ${enabled ? 'bg-primary shadow-primary/20' : 'bg-muted'}`}
      >
        <motion.div 
          className="absolute top-1 w-3 h-3 bg-white rounded-full shadow-sm"
          animate={{ x: enabled ? 20 : 4 }}
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
        />
      </button>
    </div>
  );
}

export default function Sidebar({
  url, setUrl,
  propertyName, setPropertyName,
  config, job, copy,
  activeTab, setActiveTab
}: SidebarProps) {

  const progressPct = job.status.total > 0
    ? Math.round((job.status.current / job.status.total) * 100)
    : 0;

  return (
    <aside className="w-[340px] flex-shrink-0 flex flex-col h-screen bg-sidebar border-r border-sidebar-border z-20 neo-shadow transition-all duration-300">

      {/* Título */}
      <div className="px-6 pt-8 pb-6 border-b border-sidebar-border relative overflow-hidden group">
        <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        <h1 className="text-xl font-black tracking-tighter text-sidebar-foreground flex items-center gap-3 relative z-10">
          <div className="p-2 rounded-xl bg-primary text-primary-foreground shadow-lg shadow-primary/20 transition-all duration-500">
            {activeTab === "brain" ? (
              <Brain className="w-5 h-5 flex-shrink-0 animate-pulse" />
            ) : (
              <ImageIcon className="w-5 h-5 flex-shrink-0" />
            )}
          </div>
          <div className="flex flex-col">
            <span>SCRAP.IO</span>
            <div className="flex gap-1.5 mt-1">
              <div title="Phi-3 (Local)" className={`w-1.5 h-1.5 rounded-full ${config.phi3Status === 'online' ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-red-500/30'}`} />
              <div title="Gemma-3 (Local)" className={`w-1.5 h-1.5 rounded-full ${config.gemma3Status === 'online' ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-red-500/30'}`} />
              <div title="Gemini (Cloud)" className={`w-1.5 h-1.5 rounded-full ${config.openaiApiKey ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-red-500/30'}`} />
            </div>
          </div>
        </h1>
      </div>

      {/* TABS Selector */}
      <div className="flex px-6 pt-4 border-b border-sidebar-border bg-sidebar/50 backdrop-blur-md">
        <button
          onClick={() => setActiveTab("manual")}
          className={`flex-1 pb-3 text-xs font-black uppercase tracking-widest border-b-2 transition-all ${activeTab === "manual" ? "border-foreground text-foreground" : "border-transparent text-muted-foreground hover:text-foreground/70"}`}
        >
          Manual
        </button>
        <button
          onClick={() => setActiveTab("brain")}
          className={`flex-1 pb-3 text-xs font-black uppercase tracking-widest border-b-2 transition-all flex items-center justify-center gap-1.5 ${activeTab === "brain" ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-primary/70"}`}
        >
          <Brain className="w-3.5 h-3.5" /> Brain
        </button>
      </div>

      {/* Contenido scrolleable */}
      <div className="flex-1 overflow-y-auto px-6 py-6 minimal-scrollbar">
        <AnimatePresence mode="wait">
          {activeTab === "manual" ? (
            <motion.div
              key="manual"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              transition={{ duration: 0.2 }}
              className="space-y-8"
            >
              {/* ── NUEVA EXTRACCIÓN ── */}
              <section>
                <div className="flex items-center justify-between mb-4">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-2">
                    <Search className="w-3.5 h-3.5" /> Nueva Extracción
                  </p>
                  <button 
                    onClick={job.clearAll}
                    className="text-[9px] font-bold text-muted-foreground hover:text-destructive flex items-center gap-1 transition-colors hover:bg-destructive/10 px-2 py-1 rounded-md active:scale-95"
                  >
                    <RotateCcw className="w-2.5 h-2.5" /> LIMPIAR
                  </button>
                </div>
                <div className="space-y-3">
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <label className="text-xs font-medium text-muted-foreground ml-1">URL</label>
                      {copy.isExtracting && (
                        <span className="text-[9px] font-bold text-primary flex items-center gap-1 animate-pulse">
                          <Loader2 className="w-2.5 h-2.5 animate-spin" /> Extrayendo...
                        </span>
                      )}
                    </div>
                    <div className="relative group">
                      <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <input
                        type="text"
                        value={url}
                        onChange={e => setUrl(e.target.value)}
                        placeholder="https://..."
                        className="w-full bg-input border border-border rounded-lg py-2.5 pl-10 pr-20 text-sm text-foreground focus:ring-1 focus:ring-ring transition-all"
                      />
                      <button
                        onClick={async () => {
                          try {
                            const text = await navigator.clipboard.readText();
                            setUrl(text);
                          } catch {
                            toast.error("No se pudo acceder al portapapeles");
                          }
                        }}
                        className="absolute right-2 top-1/2 -translate-y-1/2 px-2 py-1 rounded bg-secondary/50 text-[10px] font-bold text-muted-foreground hover:bg-secondary hover:text-foreground transition-all flex items-center gap-1 border border-border/50"
                      >
                        <Copy className="w-3 h-3" /> PEGAR
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-medium text-muted-foreground ml-1 mb-1.5 block">Carpeta Destino</label>
                    <div className="relative">
                      <FolderOpen className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <input
                        type="text"
                        value={propertyName}
                        onChange={e => setPropertyName(e.target.value)}
                        placeholder="Ej: Malabia 648"
                        className="w-full bg-input border border-border rounded-lg py-2.5 pl-10 pr-4 text-sm text-foreground focus:ring-1 focus:ring-ring transition-all"
                      />
                    </div>
                  </div>

                  <Toggle 
                    label="Solo imágenes grandes (+600px)"
                    enabled={job.onlyLarge}
                    onChange={job.setOnlyLarge}
                    className="px-1 py-1"
                  />

                  <Toggle 
                    label="Mejorar datos con IA (Brain)"
                    enabled={copy.isExtractionAiEnabled}
                    onChange={copy.setIsExtractionAiEnabled}
                    className="px-1 py-1"
                  />

                  {copy.isExtractionAiEnabled && (
                    <div className="pt-1 pb-2">
                      <select
                        value={copy.extractionEngine}
                        onChange={e => copy.setExtractionEngine(e.target.value)}
                        className="w-full bg-input border border-border rounded-lg text-[10px] font-bold text-foreground py-2 px-3 appearance-none focus:outline-none focus:ring-1 focus:ring-ring cursor-pointer transition-all shadow-sm"
                      >
                        <option value="local_phi3">Phi-3 (Local)</option>
                        <option value="local_gemma3">Gemma 3 (Local)</option>
                        <option value="cloud_gemini">Gemini 1.5 (Cloud)</option>
                      </select>
                    </div>
                  )}

                  <button
                    onClick={job.status.is_running ? job.stopScrape : () => job.startScrape(url, propertyName)}
                    className={`w-full py-2.5 rounded-lg font-bold text-sm flex items-center justify-center gap-2 transition-all neo-shadow-sm active:scale-95 ${job.status.is_running ? 'bg-secondary text-secondary-foreground hover:bg-secondary/80' : 'bg-primary text-primary-foreground hover:opacity-90'}`}
                  >
                    {job.status.is_running ? <><Square className="w-4 h-4" /> Detener</> : <><Play className="w-4 h-4" /> Extraer Fotos</>}
                  </button>
                </div>
              </section>

              <div className="border-t border-sidebar-border" />

              {/* ── MIS SESIONES ── */}
              <section>
                <div className="flex items-center justify-between mb-3">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground !mb-0">Mis Sesiones</p>
                  <button onClick={config.fetchHistory} title="Actualizar" className="p-1 rounded-lg hover:bg-accent hover:text-accent-foreground transition-all">
                    <RotateCcw className="w-3.5 h-3.5" />
                  </button>
                </div>
                {config.historyFolders.length === 0 ? (
                  <p className="text-xs italic text-center py-2 text-muted-foreground rounded-xl">Todavía no bajé nada</p>
                ) : (
                  <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1 minimal-scrollbar">
                    {config.historyFolders.map(f => (
                      <button
                        key={f}
                        onClick={() => config.setSelectedHistory(f)}
                        className={config.selectedHistory === f
                          ? "w-full text-left px-3 py-2.5 rounded-lg text-xs font-bold bg-accent text-accent-foreground border border-border neo-shadow-sm transition-all flex items-center gap-1.5"
                          : "w-full text-left px-3 py-2.5 rounded-lg text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-accent/50 border border-transparent transition-all flex items-center gap-1.5"
                        }
                      >
                        <span className="truncate flex-1">📁 {f}</span>
                        {job.foldersWithCopy.has(f) && (
                          <span className="flex-shrink-0 text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-primary/20 text-primary">
                            📄
                          </span>
                        )}
                      </button>
                    ))}
                  </div>
                )}
                {config.selectedHistory && (
                  <button
                    onClick={() => {
                      job.loadSession(config.selectedHistory);
                      setPropertyName(config.selectedHistory);
                    }}
                    disabled={job.status.is_running}
                    className="w-full mt-3 py-2.5 rounded-lg text-xs font-bold bg-secondary text-secondary-foreground hover:bg-secondary/80 border border-border transition-all neo-shadow-sm disabled:opacity-50 active:scale-[0.98]"
                  >
                    Cargar &quot;{config.selectedHistory}&quot;
                  </button>
                )}
              </section>
            </motion.div>
          ) : (
            <motion.div
              key="brain"
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.2 }}
              className="space-y-8"
            >
              {/* ── MASTER AI SWITCH ── */}
              <section className={`p-4 rounded-xl border border-primary/20 shadow-inner transition-all duration-700 ${config.isAiEnabled ? 'brain-container-glow' : 'bg-muted/30'}`}>
                <Toggle 
                  label="BRAIN MODE (GLOBAL IA)"
                  enabled={config.isAiEnabled}
                  onChange={(v) => {
                    config.setIsAiEnabled(v);
                    fetch(`${process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000'}/api/ai/status`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ enabled: v })
                    }).catch(() => {});
                  }}
                  className="font-black tracking-tighter"
                />
                <p className="text-[9px] text-muted-foreground/60 mt-2 leading-tight">
                  {config.isAiEnabled 
                    ? "Motor inteligente encendido. Redacción y clasificación activa."
                    : "Motor inteligente apagado. Usando plantillas locales de emergencia."
                  }
                </p>
              </section>

              {config.isAiEnabled && (
                <AnimatePresence>
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="space-y-8 overflow-hidden"
                  >
                    {/* ── FILTRO IA ── */}
                    <section className={`rounded-xl bg-card border border-border p-4 neo-shadow-sm space-y-4 brain-mode-bg transition-all duration-500 ${job.useAI ? 'brain-container-glow' : ''}`}>
                      <div className="flex items-center justify-between">
                        <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Filtro de Relevancia IA</p>
                        <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full ${
                          job.aiModelReady ? "bg-primary/20 text-primary" : "bg-muted text-muted-foreground animate-pulse"
                        }`}>
                          {job.aiModelReady ? "LISTO" : "CARGANDO..."}
                        </span>
                      </div>

                      <Toggle 
                        label="Clasificar fotos con IA (Local CLIP)"
                        enabled={job.useAI}
                        onChange={job.setUseAI}
                        disabled={!job.aiModelReady}
                        className="px-1"
                      />
                      
                      {job.useAI && job.aiModelReady && (
                        <div className="pt-2">
                          <select
                            value={job.nicho}
                            onChange={e => job.setNicho(e.target.value)}
                            className="w-full bg-input border border-border rounded-lg text-xs font-bold text-foreground py-2 px-3 appearance-none focus:outline-none focus:ring-1 focus:ring-ring cursor-pointer transition-all shadow-sm mb-3"
                          >
                            <option value="inmobiliaria">Inmobiliaria</option>
                            <option value="gastronomia">Gastronomía</option>
                            <option value="ecommerce">Ecommerce</option>
                          </select>
                        </div>
                      )}
                    </section>
                  </motion.div>
                </AnimatePresence>
              )}

              <div className="border-t border-sidebar-border" />

              {/* ── GENERADOR DE COPY ── */}
              <section className="space-y-4">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Generador de Copy</p>
                </div>
                <div className="space-y-3">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <label className="text-xs font-medium text-muted-foreground ml-1 block">Link de la Propiedad</label>
                      {copy.isExtracting && (
                        <span className="text-[9px] font-bold text-primary flex items-center gap-1 animate-pulse">
                          <Loader2 className="w-2.5 h-2.5 animate-spin" /> Auto-completando...
                        </span>
                      )}
                    </div>
                    <input
                      type="text"
                      value={url}
                      onChange={e => setUrl(e.target.value)}
                      placeholder="Pegá el link acá para rellenar datos..."
                      className="w-full bg-input border border-primary/30 rounded-lg py-2.5 px-3 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary transition-all shadow-sm"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-muted-foreground ml-1 mb-1 block">Dirección</label>
                    <input
                      type="text"
                      value={copy.copyData.address}
                      onChange={e => copy.setCopyData({ ...copy.copyData, address: e.target.value })}
                      placeholder="Ej: Marmol 1426"
                      className="w-full bg-input border border-border rounded-lg py-2.5 px-3 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring transition-all shadow-sm"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-muted-foreground ml-1 mb-1 block">Tipo de Op.</label>
                    <select
                      value={copy.copyData.operation_type}
                      onChange={e => copy.setCopyData({ ...copy.copyData, operation_type: e.target.value })}
                      className="w-full bg-input border border-border rounded-lg py-2.5 px-3 text-xs font-bold text-foreground appearance-none focus:outline-none focus:ring-1 focus:ring-ring cursor-pointer transition-all shadow-sm"
                    >
                      <option value="venta">Venta</option>
                      <option value="alquiler">Alquiler</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-xs font-medium text-muted-foreground ml-1 mb-1 block">Zona / Barrio</label>
                      <input
                        type="text"
                        value={copy.copyData.location}
                        onChange={e => copy.setCopyData({ ...copy.copyData, location: e.target.value })}
                        placeholder="Ramos Mejia Sur"
                        className="w-full bg-input border border-border rounded-lg py-2 px-3 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-medium text-muted-foreground ml-1 mb-1 block">Precio</label>
                      <input
                        type="text"
                        value={copy.copyData.price}
                        onChange={e => copy.setCopyData({ ...copy.copyData, price: e.target.value })}
                        placeholder="U$D 150.000"
                        className="w-full bg-input border border-border rounded-lg py-2 px-3 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-muted-foreground ml-1 mb-1 block">Destacados</label>
                    <textarea
                      value={copy.copyData.features}
                      onChange={e => copy.setCopyData({ ...copy.copyData, features: e.target.value })}
                      placeholder="Auto-extraído de la URL..."
                      rows={3}
                      className="w-full bg-input border border-border rounded-lg py-2 px-3 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring resize-none"
                    />
                  </div>

                  {config.isAiEnabled && (
                    <div className="pt-2 pb-2">
                      <label className="text-xs font-medium text-muted-foreground ml-1 mb-1.5 block">Motor Inteligente</label>
                      <select
                        value={copy.generationEngine}
                        onChange={e => copy.setGenerationEngine(e.target.value)}
                        className="w-full bg-input border border-border rounded-lg text-xs font-bold text-foreground py-2 px-3 appearance-none focus:outline-none focus:ring-1 focus:ring-ring cursor-pointer transition-all shadow-sm"
                      >
                        <option value="local_phi3">Phi-3 (Local - Rápido)</option>
                        <option value="local_gemma3">Gemma 3 (Local - Potente)</option>
                        <option value="cloud_gemini">Gemini 1.5 (Cloud - Full)</option>
                      </select>
                    </div>
                  )}

                  <button
                    onClick={() => copy.generateCopy(job.nicho, propertyName)}
                    disabled={copy.isGeneratingCopy}
                    className={`w-full py-2.5 rounded-lg font-bold text-xs flex items-center justify-center gap-2 active:scale-95 transition-all disabled:opacity-50 neo-shadow-sm shadow-md ${config.isAiEnabled ? 'bg-primary text-primary-foreground hover:bg-primary/90 brain-border-beam' : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'}`}
                  >
                    {copy.isGeneratingCopy
                      ? <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Generando...</>
                      : <><Send className="w-4 h-4" /> {config.isAiEnabled ? 'Generar Publicación con Brain' : 'Generar Publicación'}</>
                    }
                  </button>
                  <p className="text-[9px] text-center text-muted-foreground/60 uppercase font-bold tracking-widest mt-1">
                    {copy.generationEngine === 'cloud_gemini' ? '🛰️ Cloud Engine' : '🏠 Local Engine'}
                  </p>
                </div>
              </section>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── PROGRESO (AMBOS MODOS) ── */}
        <div className="pt-8">
          <div className="border-t border-sidebar-border mb-8" />
          <section className="rounded-xl bg-card border border-border p-5 neo-shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground !mb-0">Progreso</p>
              {job.status.is_running ? <Loader2 className="w-3.5 h-3.5 text-primary animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5 text-primary" />}
            </div>
            <div className="w-full bg-muted rounded-full h-1.5 overflow-hidden">
              <motion.div className="h-full bg-primary rounded-full" animate={{ width: `${progressPct}%` }} transition={{ duration: 0.4 }} />
            </div>
          </section>
        </div>
      </div>

      {/* ── FOOTER PERSISTENTE ── */}
      <div className="px-6 py-4 border-t border-sidebar-border bg-sidebar space-y-4">
        
        {!config.isEditingConfig && (
          <button
            onClick={() => job.handleExport(propertyName)}
            disabled={job.isExporting || job.status.images.length === 0 || job.status.is_running || !propertyName}
            className="w-full py-2.5 rounded-lg font-bold text-xs flex items-center justify-center gap-2 bg-primary text-primary-foreground hover:opacity-90 active:scale-95 transition-all disabled:opacity-30 disabled:grayscale neo-shadow-sm"
          >
            {job.isExporting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <FolderSync className="w-3.5 h-3.5" />}
            {job.isExporting ? "Exportando..." : "EXPORTAR SESIÓN"}
          </button>
        )}

        {config.isEditingConfig ? (
          <div className="flex flex-col gap-3">
            <div>
              <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest mb-1.5 block">Carpeta Base</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={config.configInput}
                  onChange={e => config.setConfigInput(e.target.value)}
                  className="flex-1 min-w-0 bg-input border border-border rounded-lg py-2 px-3 text-xs font-medium text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                />
                <button onClick={config.browseBaseFolder} className="p-2 rounded-lg bg-input border border-border text-muted-foreground">
                  <FolderOpen className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
            <div>
              <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest mb-1.5 block">Gemini API KEY</label>
              <input
                type="password"
                value={config.apiInput}
                onChange={e => config.setApiInput(e.target.value)}
                placeholder="AIza..."
                className="w-full bg-input border border-border rounded-lg py-2 px-3 text-xs font-medium text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
              />
            </div>

            <div className="flex gap-2 mt-1">
              <button onClick={config.saveConfig} className="flex-1 py-1.5 rounded-md font-bold text-xs bg-primary text-primary-foreground">Guardar</button>
              <button onClick={() => config.setIsEditingConfig(false)} className="flex-1 py-1.5 rounded-md font-bold text-xs bg-secondary text-secondary-foreground">Cancelar</button>
            </div>
          </div>
        ) : (
          <div className="flex justify-between items-center">
            <div className="flex flex-col">
              <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest mb-0.5">Directorio Base</p>
              <p className="text-xs font-medium text-foreground truncate max-w-[200px]" title={config.localBase}>
                {config.localBase}
              </p>
            </div>
            <button
              onClick={() => config.setIsEditingConfig(true)}
              className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition-all"
              title="Configurar Carpeta Base"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}
