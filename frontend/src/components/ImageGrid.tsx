"use client";

import { useState, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Tag, CheckCircle2, X, Maximize2, FilterX } from "lucide-react";
import type { ImageData } from "@/hooks/useScrapingJob";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

const ROOM_TAGS = [
  "(Renombrar)", "Frente", "Fondo", "Cocina", "Comedor", "Living",
  "Dormitorio", "Dormitorio 2", "Dormitorio 3", "Baño", "Baño 2",
  "Patio", "Terraza", "Lavadero", "Cochera", "Jardín", "Balcón",
  "Estudio", "Quincho", "Pileta", "Vista"
];

interface ImageGridProps {
  images: ImageData[];
  isRunning: boolean;
  onRename: (oldPath: string, newTag: string) => Promise<string | null>;
}

function ImageCard({ 
  img, 
  onRename, 
  onPreview 
}: { 
  img: ImageData; 
  onRename: (old: string, tag: string) => Promise<string | null>;
  onPreview: (path: string) => void;
}) {
  const [renamed, setRenamed] = useState(false);
  const [currentPath, setCurrentPath] = useState(img.path);

  const filename = currentPath.split("\\").pop()?.split("/").pop() ?? "image.jpg";
  
  const getAspectRatio = (w: number, h: number) => {
    if (w === 0 || h === 0) return "";
    const gcd = (a: number, b: number): number => (b === 0 ? a : gcd(b, a % b));
    const common = gcd(w, h);
    return `${w / common}:${h / common}`;
  };

  const ratio = getAspectRatio(img.width, img.height);
  const resolutionText = img.width > 0 ? `${img.width}×${img.height} (${ratio})` : "";

  const handleChange = useCallback(async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const tag = e.target.value;
    if (tag === ROOM_TAGS[0]) return;
    const newPath = await onRename(currentPath, tag);
    if (newPath) {
      setCurrentPath(newPath);
      setRenamed(true);
    }
  }, [currentPath, onRename]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9, y: 10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
      className="rounded-xl bg-card border border-border overflow-hidden hover:border-primary neo-shadow hover-lift transition-all duration-300 transform-gpu group relative"
    >
      {/* Badge resolución */}
      {resolutionText && (
        <div className="absolute top-2 right-2 z-20 px-1.5 py-0.5 rounded bg-black/60 backdrop-blur-md border border-white/10 text-[9px] font-bold text-white opacity-0 group-hover:opacity-100 transition-opacity">
          {resolutionText}
        </div>
      )}

      {/* Badge AI tag */}
      {img.ai_tag && (
        <div className="absolute top-2 left-2 z-20 px-1.5 py-0.5 rounded-full bg-primary/80 backdrop-blur-md text-[9px] font-bold text-primary-foreground">
          {img.ai_tag}
        </div>
      )}

      {/* Badge renombrado ✅ */}
      <AnimatePresence>
        {renamed && (
          <motion.div
            initial={{ opacity: 0, scale: 0.7 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="absolute top-2 right-2 z-30 flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-emerald-500/90 backdrop-blur-md text-[9px] font-bold text-white"
          >
            <CheckCircle2 className="w-2.5 h-2.5" />
            OK
          </motion.div>
        )}
      </AnimatePresence>

      {/* Imagen */}
      <div className="aspect-square relative overflow-hidden bg-black/20 cursor-zoom-in" onClick={() => onPreview(currentPath)}>
        {/* Overlay Hover */}
        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity z-10 flex items-center justify-center">
            <Maximize2 className="w-6 h-6 text-white drop-shadow-lg" />
        </div>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={`${API_BASE}/api/images/serve?path=${encodeURIComponent(currentPath)}`}
          alt="Scraped"
          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
          loading="lazy"
        />
      </div>

      {/* Footer de la tarjeta */}
      <div className="p-3">
        <p className="text-[11px] font-bold text-foreground opacity-90 truncate mb-2" title={filename}>
          {filename}
        </p>
        <div className="relative">
          <Tag className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
          <select
            defaultValue={ROOM_TAGS[0]}
            onChange={handleChange}
            className="w-full bg-input border border-border hover:border-muted-foreground rounded-lg text-xs font-bold text-foreground py-2 pl-8 pr-3 appearance-none focus:outline-none focus:ring-1 focus:ring-ring cursor-pointer transition-all shadow-sm"
          >
            {ROOM_TAGS.map(tag => <option key={tag} value={tag}>{tag}</option>)}
          </select>
        </div>
      </div>
    </motion.div>
  );
}

export default function ImageGrid({ images, isRunning, onRename }: ImageGridProps) {
  const [previewPath, setPreviewPath] = useState<string | null>(null);
  const [filterTag, setFilterTag] = useState<string | null>(null);

  // Extraemos todos los tags únicos presentes para el filtro
  const availableTags = useMemo(() => {
      const tags = new Set<string>();
      images.forEach(img => { if (img.ai_tag) tags.add(img.ai_tag); });
      return Array.from(tags);
  }, [images]);

  const filteredImages = useMemo(() => {
      if (!filterTag) return images;
      return images.filter(img => img.ai_tag === filterTag);
  }, [images, filterTag]);

  const sorted = useMemo(() => {
      return [...filteredImages].sort((a, b) => (b.width * b.height) - (a.width * a.height));
  }, [filteredImages]);

  // Estado vacío
  if (images.length === 0 && !isRunning) {
    return (
      <div className="h-[60vh] flex flex-col items-center justify-center opacity-50 gap-4 relative z-10">
        <div className="p-8 rounded-2xl bg-card border border-border text-muted-foreground neo-shadow-sm">
          <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" strokeWidth={1.5} />
            <circle cx="8.5" cy="8.5" r="1.5" strokeWidth={1.5} />
            <polyline points="21 15 16 10 5 21" strokeWidth={1.5} />
          </svg>
        </div>
        <p className="text-sm font-bold text-muted-foreground text-center">
          Pegá una URL en la barra lateral o cargá alguna sesión vieja
        </p>
      </div>
    );
  }

  // Skeletons mientras carga
  if (isRunning && images.length === 0) {
    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-6 relative z-10">
        {[...Array(10)].map((_, i) => (
          <div key={i} className="rounded-xl aspect-square bg-card border border-border animate-pulse neo-shadow-sm" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6 relative z-10">
      
      {/* Barra de Filtros */}
      {availableTags.length > 0 && (
          <div className="flex flex-wrap items-center gap-2 mb-2 p-1 bg-muted/30 rounded-2xl border border-border/50 w-fit">
              <button
                onClick={() => setFilterTag(null)}
                className={`px-3 py-1.5 rounded-xl text-[10px] font-bold transition-all flex items-center gap-1.5 ${
                    !filterTag ? "bg-primary text-primary-foreground shadow-lg" : "text-muted-foreground hover:bg-muted"
                }`}
              >
                  TODAS ({images.length})
              </button>
              {availableTags.map(tag => (
                  <button
                    key={tag}
                    onClick={() => setFilterTag(tag)}
                    className={`px-3 py-1.5 rounded-xl text-[10px] font-bold uppercase tracking-tight transition-all ${
                        filterTag === tag ? "bg-primary text-primary-foreground shadow-lg" : "bg-card border border-border text-muted-foreground hover:border-muted-foreground"
                    }`}
                  >
                      {tag} ({images.filter(i => i.ai_tag === tag).length})
                  </button>
              ))}
              {filterTag && (
                  <button 
                    onClick={() => setFilterTag(null)}
                    className="p-1.5 rounded-full hover:bg-destructive/10 hover:text-destructive text-muted-foreground transition-all"
                    title="Limpiar filtro"
                  >
                    <FilterX className="w-3.5 h-3.5" />
                  </button>
              )}
          </div>
      )}

      {/* Grilla */}
      {sorted.length === 0 ? (
          <div className="py-20 text-center text-muted-foreground italic text-xs">
              No hay imágenes con el tag &quot;{filterTag}&quot;
          </div>
      ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-6">
            <AnimatePresence mode="popLayout">
              {sorted.map(img => (
                <ImageCard 
                    key={img.path} 
                    img={img} 
                    onRename={onRename} 
                    onPreview={(path) => setPreviewPath(path)}
                />
              ))}
            </AnimatePresence>
          </div>
      )}

      {/* Modal de Vista Previa (Lightbox) */}
      <AnimatePresence>
        {previewPath && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md"
            onClick={() => setPreviewPath(null)}
          >
            <button 
                className="absolute top-6 right-6 p-3 rounded-full bg-black/50 text-white hover:bg-white hover:text-black transition-all duration-300 z-[110]"
                onClick={() => setPreviewPath(null)}
            >
                <X className="w-6 h-6" />
            </button>

            <motion.div
              key={previewPath}
              initial={{ scale: 0.95, opacity: 0, filter: "blur(10px)" }}
              animate={{ scale: 1, opacity: 1, filter: "blur(0px)" }}
              exit={{ scale: 0.95, opacity: 0, filter: "blur(10px)" }}
              transition={{ duration: 0.2 }}
              className="relative max-w-[90vw] max-h-[85vh] flex flex-col items-center justify-center"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Imagen Principal */}
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={`${API_BASE}/api/images/serve?path=${encodeURIComponent(previewPath)}`}
                alt="Full size preview"
                className="max-w-full max-h-[75vh] object-contain rounded-xl shadow-[0_0_50px_rgba(0,0,0,0.5)] border border-white/10"
              />

              {/* Controles Inferiores (Título y Flechas) */}
              <div className="w-full flex items-center justify-between mt-6 px-4">
                
                {/* Navegación Anterior */}
                <button 
                    className="p-3 rounded-full bg-black/40 text-white hover:bg-primary hover:scale-110 transition-all duration-300 z-[110]"
                    onClick={(e) => {
                      e.stopPropagation();
                      const idx = sorted.findIndex(img => img.path === previewPath);
                      const prevIdx = idx > 0 ? idx - 1 : sorted.length - 1;
                      setPreviewPath(sorted[prevIdx].path);
                    }}
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 19l-7-7 7-7" /></svg>
                </button>

                {/* Datos de la Imagen */}
                <div className="flex flex-col items-center gap-1">
                  <div className="text-white text-base font-bold tracking-tight">
                    {previewPath.split("\\").pop()?.split("/").pop()}
                  </div>
                  {sorted.find(i => i.path === previewPath) && (
                    <div className="px-2 py-0.5 rounded bg-primary/20 border border-primary/30 text-primary text-[10px] font-bold">
                      {(() => {
                        const i = sorted.find(img => img.path === previewPath)!;
                        const gcd = (a: number, b: number): number => (b === 0 ? a : gcd(b, a % b));
                        const common = gcd(i.width, i.height);
                        return `${i.width} × ${i.height} PX — ${i.width / common}:${i.height / common} RATIO`;
                      })()}
                    </div>
                  )}
                </div>

                {/* Navegación Siguiente */}
                <button 
                    className="p-3 rounded-full bg-black/40 text-white hover:bg-primary hover:scale-110 transition-all duration-300 z-[110]"
                    onClick={(e) => {
                      e.stopPropagation();
                      const idx = sorted.findIndex(img => img.path === previewPath);
                      const nextIdx = idx < sorted.length - 1 ? idx + 1 : 0;
                      setPreviewPath(sorted[nextIdx].path);
                    }}
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" /></svg>
                </button>
              </div>

            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}
