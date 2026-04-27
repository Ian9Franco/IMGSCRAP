"use client";

import { useState, useEffect } from "react";
import { FolderOpen, FileText } from "lucide-react";

import { useConfig } from "@/hooks/useConfig";
import { useScrapingJob } from "@/hooks/useScrapingJob";
import { useCopyGenerator } from "@/hooks/useCopyGenerator";

import Sidebar from "@/components/Sidebar";
import ImageGrid from "@/components/ImageGrid";
import CopyPanel from "@/components/CopyPanel";
import { ConsoleTerminal } from "@/components/ConsoleTerminal";

export default function Home() {
  const [url, setUrl] = useState("");
  const [propertyName, setPropertyName] = useState("");
  const [activeTab, setActiveTab] = useState<"manual" | "brain">("manual");

  const config = useConfig();
  const job = useScrapingJob(config);
  const copy = useCopyGenerator(url, job.nicho, config.isAiEnabled);

  // Escucha eventos de limpieza y sugerencia
  useEffect(() => {
    const handleSuggest = (e: Event) => {
      const customEvent = e as CustomEvent<string>;
      if (customEvent.detail) setPropertyName(customEvent.detail);
    };
    const handleClear = () => {
      setUrl("");
      setPropertyName("");
    };
    const handleUrlLoaded = (e: Event) => {
      const customEvent = e as CustomEvent<string>;
      if (customEvent.detail) setUrl(customEvent.detail);
    };
    window.addEventListener("imgscrap:folder-suggest", handleSuggest);
    window.addEventListener("imgscrap:clear-all", handleClear);
    window.addEventListener("imgscrap:url-loaded", handleUrlLoaded);
    return () => {
      window.removeEventListener("imgscrap:folder-suggest", handleSuggest);
      window.removeEventListener("imgscrap:clear-all", handleClear);
      window.removeEventListener("imgscrap:url-loaded", handleUrlLoaded);
    };
  }, []);

  return (
    <div className={`flex flex-col h-screen overflow-hidden bg-background text-foreground selection:bg-primary/20 transition-colors duration-500 
      ${(config.isAiEnabled || copy.isExtractionAiEnabled) ? 'brain-enabled' : ''} 
      ${(activeTab === 'brain' && config.isAiEnabled) ? 'brain-mode' : ''}`}>
      
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          url={url}
          setUrl={setUrl}
          propertyName={propertyName}
          setPropertyName={setPropertyName}
          config={config}
          job={job}
          copy={copy}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />

        <div className="flex-1 flex flex-col overflow-hidden relative">
          <div className="flex flex-1 overflow-hidden">
            {/* 2. ÁREA CENTRAL (Grilla de Imágenes) */}
            <main className="flex-1 h-screen overflow-hidden flex flex-col relative bg-background border-r border-border/50">
              {/* Degradado de fondo */}
              <div className="absolute inset-0 pointer-events-none opacity-20 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-primary/20 via-background to-background" />

              {/* Header Superior (IA & Status) */}
              <header className="h-16 flex-shrink-0 flex items-center justify-between px-6 border-b border-border bg-card/50 backdrop-blur-md z-20 overflow-hidden">
                <div className="flex items-center gap-3 min-w-0 flex-1 mr-4">
                  <h2 className="text-base font-bold tracking-tight text-foreground flex items-center gap-2 min-w-0">
                    {propertyName
                      ? (
                        <>
                          <FolderOpen className="w-4 h-4 text-primary shrink-0" /> 
                          <span className="truncate" title={propertyName}>{propertyName}</span>
                        </>
                      )
                      : "Explorador de Archivos"
                    }
                  </h2>
                  <div className="h-4 w-[1px] bg-border shrink-0" />
                  <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider whitespace-nowrap shrink-0">
                    {job.status.images.length} Archivos
                  </p>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                    {/* Indicador de IA Dinámico */}
                    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-[10px] font-bold transition-all whitespace-nowrap relative ${config.isAiEnabled ? (copy.geminiVersion === '2.5' ? 'bg-primary/20 border-primary/40 text-primary brain-border-beam' : 'bg-primary/10 border-primary/30 text-primary') : 'bg-muted border-border text-muted-foreground'}`}>
                       <div className={`w-1.5 h-1.5 rounded-full ${config.isAiEnabled ? 'bg-primary animate-pulse' : 'bg-muted-foreground'}`} />
                      {config.isAiEnabled ? (
                        <span className="flex items-center gap-1.5 uppercase">
                          BRAIN: 
                          <span className="opacity-70">
                            {copy.generationEngine === 'local_phi3' ? 'PHI-3 LOCAL' : 
                             copy.generationEngine === 'local_gemma3' ? 'GEMMA 3 LOCAL' : 
                             'GEMINI CLOUD'}
                          </span>
                          {job.useAI && (
                            <>
                              <span className="w-1 h-1 rounded-full bg-primary/40" /> 
                              <span className="opacity-70">CLIP</span>
                            </>
                          )}
                        </span>
                      ) : (
                        "IA DESACTIVADA"
                      )}
                   </div>
                </div>
              </header>

              {/* Contenedor de la Grilla con Scroll Independiente */}
              <div className="flex-1 overflow-y-auto p-8 minimal-scrollbar relative z-10">
                <ImageGrid
                  images={job.status.images}
                  isRunning={job.status.is_running}
                  onRename={job.handleRename}
                />
              </div>
            </main>

            {/* 3. PANEL DERECHO (Copy & Drafts) */}
            <aside className="w-[400px] flex-shrink-0 h-screen bg-card border-l border-border flex flex-col overflow-hidden relative z-30 shadow-2xl">
              <div className="h-16 flex-shrink-0 flex items-center px-6 border-b border-border bg-background/50">
                <h3 className="text-sm font-black uppercase tracking-[0.2em] text-foreground/70 flex items-center gap-2">
                  <FileText className="w-4 h-4" /> Vista Previa del Copy
                </h3>
              </div>
              
              <div className="flex-1 overflow-y-auto p-6 minimal-scrollbar">
                <CopyPanel copy={copy} propertyName={propertyName} />
                
                {/* Espacio extra para info técnica o tips */}
                <div className="mt-8 p-4 rounded-xl bg-muted/30 border border-border/50 border-dashed">
                   <p className="text-[10px] text-muted-foreground leading-relaxed">
                     <strong>Tip:</strong> El copy se genera automáticamente usando el motor <b>{copy.generationEngine.includes('local') ? 'Local' : 'Cloud'}</b>. Podés editar los campos en la sidebar izquierda y presionar "Generar Publicación" para crear una versión nueva instantáneamente.
                   </p>
                </div>
              </div>
            </aside>
          </div>

          <ConsoleTerminal />
        </div>
      </div>

    </div>
  );
}
