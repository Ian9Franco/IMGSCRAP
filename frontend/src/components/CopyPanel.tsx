"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, RotateCcw, Save, Sparkles, Loader2 } from "lucide-react";
import type { CopyGeneratorState } from "@/hooks/useCopyGenerator";

interface CopyPanelProps {
  propertyName: string;
  copy: Pick<CopyGeneratorState, 
    "generatedCopy" | "setGeneratedCopy" | "copyCopyToClipboard" | 
    "isEditingCopy" | "isGeneratingCopy" | "editCopy" | "saveDocx"
  >;
}

export default function CopyPanel({ copy, propertyName }: CopyPanelProps) {
  const [prompt, setPrompt] = useState("");

  const handleEdit = async () => {
    if (!prompt.trim()) return;
    await copy.editCopy(prompt);
    setPrompt("");
  };

  return (
    <AnimatePresence mode="wait">
      {copy.isGeneratingCopy && !copy.generatedCopy ? (
        <motion.div
          key="skeleton"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="p-6 rounded-2xl bg-card border border-primary/20 shadow-xl relative overflow-hidden flex flex-col h-[60vh]"
        >
          {/* Shimmer Effect overlay */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-primary/5 to-transparent -translate-x-full animate-[shimmer_1.5s_infinite]" />
          
          <div className="absolute top-0 left-0 w-1.5 h-full bg-primary/30" />

          {/* Header Mockup */}
          <div className="flex items-center justify-between mb-8">
             <div className="h-4 bg-muted rounded-full w-32" />
             <div className="flex gap-2">
                <div className="w-16 h-6 bg-muted rounded-lg" />
             </div>
          </div>

          {/* Animación de "Escritura" */}
          <motion.div 
            className="space-y-6"
            variants={{
              animate: { transition: { staggerChildren: 0.15 } }
            }}
            initial="initial"
            animate="animate"
          >
            {/* Title Block */}
            <div className="space-y-3">
               <motion.div 
                 variants={{ initial: { scaleX: 0, opacity: 0 }, animate: { scaleX: 1, opacity: 1 } }}
                 transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 2, repeatType: "reverse" }}
                 className="h-6 bg-primary/20 rounded-lg w-3/4 origin-left" 
               />
               <motion.div 
                 variants={{ initial: { opacity: 0 }, animate: { opacity: 1 } }}
                 transition={{ duration: 0.3, repeat: Infinity, repeatDelay: 2.2, repeatType: "reverse" }}
                 className="flex items-center gap-2"
               >
                  <div className="w-3 h-3 rounded-full bg-primary/30" />
                  <div className="h-2 bg-muted rounded-full w-1/2" />
               </motion.div>
            </div>

            {/* Paragraph 1 */}
            <div className="space-y-2">
               {[1, 0.9, 0.8].map((w, i) => (
                 <motion.div 
                   key={i}
                   variants={{ initial: { scaleX: 0, opacity: 0 }, animate: { scaleX: 1, opacity: 1 } }}
                   transition={{ 
                     duration: 0.6, 
                     delay: i * 0.1, 
                     repeat: Infinity, 
                     repeatDelay: 2.5,
                     repeatType: "reverse"
                   }}
                   className="h-2.5 bg-muted rounded-full origin-left" 
                   style={{ width: `${w * 100}%` }}
                 />
               ))}
            </div>

            {/* Paragraph 2 */}
            <div className="space-y-2">
               {[0.95, 0.7].map((w, i) => (
                 <motion.div 
                   key={i}
                   variants={{ initial: { scaleX: 0, opacity: 0 }, animate: { scaleX: 1, opacity: 1 } }}
                   transition={{ 
                     duration: 0.6, 
                     delay: 0.5 + i * 0.1, 
                     repeat: Infinity, 
                     repeatDelay: 2.5,
                     repeatType: "reverse" 
                   }}
                   className="h-2.5 bg-muted rounded-full origin-left" 
                   style={{ width: `${w * 100}%` }}
                 />
               ))}
            </div>

            {/* List items */}
            <div className="space-y-3 pt-4 border-t border-border/20">
               {[0.6, 0.5, 0.4].map((w, i) => (
                 <div key={i} className="flex items-center gap-3">
                    <motion.div 
                      initial={{ scale: 0 }} 
                      animate={{ scale: 1 }} 
                      transition={{ delay: 1 + i * 0.1, repeat: Infinity, repeatDelay: 3 }}
                      className="w-1.5 h-1.5 rounded-full bg-primary/40" 
                    />
                    <motion.div 
                      variants={{ initial: { scaleX: 0 }, animate: { scaleX: 1 } }}
                      transition={{ 
                        duration: 0.4, 
                        delay: 1.1 + i * 0.1, 
                        repeat: Infinity, 
                        repeatDelay: 3,
                        repeatType: "reverse"
                      }}
                      className="h-2 bg-muted rounded-full origin-left" 
                      style={{ width: `${w * 100}%` }}
                    />
                 </div>
               ))}
            </div>
          </motion.div>

          {/* Floating Indicator */}
          <div className="absolute bottom-8 left-1/2 -translate-x-1/2">
             <motion.div 
               animate={{ y: [0, -5, 0] }}
               transition={{ duration: 2, repeat: Infinity }}
               className="bg-card/90 backdrop-blur-sm p-3 rounded-2xl border border-primary/20 shadow-2xl flex items-center gap-3 whitespace-nowrap"
             >
                <Loader2 className="w-4 h-4 text-primary animate-spin" />
                <span className="text-[10px] font-black uppercase tracking-widest text-foreground">Escritura en curso...</span>
             </motion.div>
          </div>
        </motion.div>
      ) : copy.generatedCopy ? (
        <motion.div
          key="content"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 20 }}
          className="p-5 rounded-2xl bg-card border border-primary/20 shadow-xl relative overflow-hidden group"
        >
          {/* Barra de acento izquierda */}
          <div className="absolute top-0 left-0 w-1.5 h-full bg-primary" />

          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Send className="w-4 h-4 text-primary" />
              <h3 className="text-sm font-bold text-foreground uppercase tracking-widest">
                Publicación Generada
              </h3>
            </div>
            <div className="flex gap-2">
              <button
                onClick={copy.copyCopyToClipboard}
                className="px-3 py-1.5 rounded-lg bg-secondary text-secondary-foreground text-[10px] font-bold hover:bg-secondary/80 transition-all border border-border"
              >
                COPIAR TEXTO
              </button>
              <button
                onClick={() => copy.setGeneratedCopy("")}
                className="p-1.5 rounded-lg text-muted-foreground hover:text-destructive transition-all"
                title="Cerrar"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Contenido del copy editable */}
          <div className="relative">
            <textarea
              value={copy.generatedCopy}
              onChange={(e) => copy.setGeneratedCopy(e.target.value)}
              className="w-full h-[45vh] text-xs text-foreground/90 font-sans leading-relaxed bg-input/30 p-4 rounded-xl border border-border/50 focus:ring-1 focus:ring-primary focus:outline-none resize-y minimal-scrollbar transition-all"
              spellCheck={false}
            />
            {copy.isGeneratingCopy && (
               <div className="absolute inset-0 bg-background/40 backdrop-blur-[1px] flex items-center justify-center rounded-xl">
                  <Loader2 className="w-8 h-8 text-primary animate-spin" />
               </div>
            )}
          </div>

          <div className="mt-2 flex items-center justify-between">
            <p className="text-[9px] text-muted-foreground italic">
              Podés editar el texto manualmente.
            </p>
            <button 
              onClick={() => copy.saveDocx(propertyName)} 
              className="text-[9px] font-bold text-primary hover:text-foreground transition-colors flex items-center gap-1 bg-primary/10 px-2 py-1 rounded-md"
            >
              <Save className="w-3 h-3" /> GUARDAR DOCX
            </button>
          </div>

          {/* Interacción IA */}
          <div className="mt-6 pt-4 border-t border-border/50">
             <label className="text-[10px] font-bold uppercase tracking-widest text-primary flex items-center gap-1.5 mb-2">
                <Sparkles className="w-3.5 h-3.5" /> Edición con IA
             </label>
             <div className="flex gap-2">
                <input 
                  type="text" 
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Ej: Agregá más emojis y achicalo..."
                  className="flex-1 bg-input border border-border rounded-lg text-xs py-2 px-3 focus:ring-1 focus:ring-primary focus:outline-none text-foreground shadow-sm"
                  onKeyDown={(e) => e.key === "Enter" && handleEdit()}
                />
                <button 
                  onClick={handleEdit}
                  disabled={copy.isEditingCopy || !prompt.trim()}
                  className="bg-primary text-primary-foreground p-2 rounded-lg hover:opacity-90 active:scale-95 transition-all disabled:opacity-50 flex items-center justify-center neo-shadow-sm"
                >
                  {copy.isEditingCopy ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4 -ml-0.5" />}
                </button>
             </div>
          </div>

        </motion.div>
      ) : (
        <div className="flex flex-col items-center justify-center h-[200px] text-center px-4 opacity-50 border-2 border-dashed border-border rounded-2xl">
           <Sparkles className="w-8 h-8 text-muted-foreground mb-3" />
           <p className="text-xs font-medium text-muted-foreground">Completá los datos y presioná &quot;Generar Publicación&quot; para ver el borrador aquí.</p>
        </div>
      )}
    </AnimatePresence>
  );
}
