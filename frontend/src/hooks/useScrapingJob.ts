"use client";

import { useState, useEffect, useCallback } from "react";
import { toast } from "sonner";
import type { Config, ConfigActions } from "./useConfig";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export interface ImageData {
  path: string;
  width: number;
  height: number;
  ai_tag?: string | null;
}

export interface ScrapeStatus {
  is_running: boolean;
  current: number;
  total: number;
  message: string;
  images: ImageData[];
}

const INITIAL_STATUS: ScrapeStatus = {
  is_running: false,
  current: 0,
  total: 0,
  message: "Listo para iniciar",
  images: [],
};

export interface ScrapingJobActions {
  status: ScrapeStatus;
  jobId: string | null;
  isExporting: boolean;
  useAI: boolean;
  nicho: string;
  aiModelReady: boolean;
  onlyLarge: boolean;
  targetFolder: string;
  foldersWithCopy: Set<string>;
  setUseAI: (v: boolean) => void;
  setNicho: (v: string) => void;
  setOnlyLarge: (v: boolean) => void;
  setTargetFolder: (v: string) => void;
  startScrape: (url: string, propertyName: string) => Promise<void>;
  stopScrape: () => Promise<void>;
  loadSession: (selectedHistory: string) => Promise<void>;
  handleRename: (oldPath: string, newTag: string) => Promise<string | null>;
  handleExport: (propertyName: string) => Promise<void>;
  clearImages: () => void;
  clearAll: () => void;
}

export function useScrapingJob(config: Pick<Config, "localBase"> & Pick<ConfigActions, "fetchHistory">): ScrapingJobActions {
  const [status, setStatus] = useState<ScrapeStatus>(INITIAL_STATUS);
  const [jobId, setJobId] = useState<string | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [useAI, setUseAI] = useState(false);
  const [nicho, setNicho] = useState("inmobiliaria");
  const [aiModelReady, setAiModelReady] = useState(false);
  const [onlyLarge, setOnlyLarge] = useState(false);
  const [targetFolder, setTargetFolder] = useState("");
  const [foldersWithCopy, setFoldersWithCopy] = useState<Set<string>>(new Set());
  const [isClassifying, setIsClassifying] = useState(false);

  // Poll del estado del modelo IA cada 2s hasta que esté listo
  useEffect(() => {
    const poll = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/ai/status`);
        if (res.ok) {
          const data = await res.json();
          setAiModelReady(data.ready);
          if (data.ready) clearInterval(poll);
        }
      } catch { /* backend no listo todavía */ }
    }, 2000);
    return () => clearInterval(poll);
  }, []);

  // Polling de progreso cada 1s mientras el job corre
  useEffect(() => {
    if (!jobId || !status.is_running) return;
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/scrape/status/${jobId}`);
        if (res.ok) setStatus(await res.json());
      } catch { /* ignoro errores menores de red */ }
    }, 1000);
    return () => clearInterval(interval);
  }, [jobId, status.is_running]);

  // Al terminar de descargar, refresco el historial
  useEffect(() => {
    if (!status.is_running && status.images.length > 0) config.fetchHistory();
  }, [status.is_running]); // eslint-disable-line react-hooks/exhaustive-deps

  const startScrape = useCallback(async (url: string, propertyName: string) => {
    if (!url || !propertyName) {
      toast.error("Completá la URL y el nombre de carpeta primero");
      return;
    }
    const localDestFolder = `${config.localBase}\\${propertyName}`;
    setStatus({ is_running: true, current: 0, total: 0, message: "Iniciando...", images: [] });
    try {
      const res = await fetch(`${API_BASE}/api/scrape/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, dest_folder: localDestFolder, only_large: onlyLarge, use_ai: useAI, nicho }),
      });
      const data = await res.json();
      setJobId(data.job_id);
    } catch {
      toast.error("Error conectando con el backend. ¿Está corriendo?");
      setStatus(prev => ({ ...prev, is_running: false, message: "Error de conexión" }));
    }
  }, [config.localBase, onlyLarge, useAI, nicho]);

  const stopScrape = useCallback(async () => {
    if (!jobId) return;
    try {
      await fetch(`${API_BASE}/api/scrape/stop/${jobId}`, { method: "POST" });
      setStatus(prev => ({ ...prev, is_running: false, message: "Cancelado" }));
      toast.info("Extracción cancelada");
    } catch { /* ignoro */ }
  }, [jobId]);

  const loadSession = useCallback(async (selectedHistory: string) => {
    if (!selectedHistory) return;
    try {
      const res = await fetch(
        `${API_BASE}/api/images/history/folder?name=${encodeURIComponent(selectedHistory)}`
      );
      if (res.ok) {
        const data = await res.json();
        if (!data.images || data.images.length === 0) {
          toast.info("Esta carpeta está vacía");
          return;
        }
        const formattedImages = data.images.map((img: ImageData | string) =>
          typeof img === "string" ? { path: img, width: 0, height: 0 } : img
        );
        setStatus({
          is_running: false,
          current: data.images.length,
          total: data.images.length,
          message: `Sesión cargada: ${selectedHistory}`,
          images: formattedImages,
        });

        // Actualizo el set de carpetas con copy
        if (data.has_copy) {
          setFoldersWithCopy(prev => new Set([...prev, selectedHistory]));
        }

        toast.success(`Sesión "${selectedHistory}" cargada${data.has_copy ? " · copy disponible 📄" : ""}`);

        // Intentamos cargar el copy y los datos crudos (property_data.json)
        try {
          const copyRes = await fetch(
            `${API_BASE}/api/copy/load?folder_name=${encodeURIComponent(selectedHistory)}`
          );
          if (copyRes.ok) {
            const copyData = await copyRes.json();
            // Emitimos todo el objeto, así el generador toma el copy (si hay) y los datos
            window.dispatchEvent(
              new CustomEvent("imgscrap:copy-loaded", { detail: copyData })
            );
          }
        } catch { /* falla silenciosa */ }
      } else {
        const err = await res.json();
        toast.error(`Error: ${err.detail}`);
      }
    } catch {
      toast.error("Error de conexión al cargar la sesión");
    }
  }, []);

  const handleRename = useCallback(async (oldPath: string, newTag: string): Promise<string | null> => {
    try {
      const res = await fetch(`${API_BASE}/api/images/rename`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ old_path: oldPath, new_tag: newTag }),
      });
      if (res.ok) {
        const data = await res.json();
        setStatus(prev => ({
          ...prev,
          images: prev.images.map(img =>
            img.path === oldPath ? { ...img, path: data.new_path } : img
          ),
        }));
        return data.new_path;
      }
    } catch { /* ignoro */ }
    return null;
  }, []);

  const handleExport = useCallback(async (propertyName: string) => {
    if (!targetFolder) {
      toast.error("Elegí la carpeta de destino primero");
      return;
    }
    if (status.images.length === 0) {
      toast.error("No hay imágenes para exportar");
      return;
    }
    if (!propertyName) {
      toast.error("Cargá una sesión primero");
      return;
    }
    setIsExporting(true);
    try {
      const res = await fetch(`${API_BASE}/api/images/export`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ property_name: propertyName, target_folder: targetFolder }),
      });
      if (res.ok) {
        const data = await res.json();
        toast.success(`¡Listo! ${data.moved} archivos movidos a ${targetFolder}`);
        setStatus(prev => ({ ...prev, images: [], message: "Exportación completada" }));
        config.fetchHistory();
      } else {
        const err = await res.json();
        toast.error(`Error al exportar: ${err.detail}`);
      }
    } catch {
      toast.error("Error de conexión al exportar");
    } finally {
      setIsExporting(false);
    }
  }, [targetFolder, status.images.length, config]);

  const clearImages = useCallback(() => {
    setStatus(INITIAL_STATUS);
    setJobId(null);
  }, []);

  const clearAll = useCallback(() => {
    setStatus(INITIAL_STATUS);
    setJobId(null);
    setTargetFolder("");
    // Emitimos un evento para que el componente padre (Home) limpie propertyName y url si lo desea
    window.dispatchEvent(new CustomEvent("imgscrap:clear-all"));
  }, []);

  const classifyExisting = useCallback(async (currentImages: ImageData[], currentNicho: string) => {
    const imagesToClassify = currentImages.filter(img => !img.ai_tag);
    if (imagesToClassify.length === 0) return;

    setIsClassifying(true);
    toast.info(`Clasificando ${imagesToClassify.length} imágenes existentes...`);

    try {
      const res = await fetch(`${API_BASE}/api/images/classify-existing`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image_paths: imagesToClassify.map(img => img.path),
          nicho: currentNicho
        }),
      });

      if (res.ok) {
        const data = await res.json();
        // data.results viene con { path, new_path, ai_tag }
        const resultsMap = new Map<string, { new_path: string; tag: string }>(
          data.results.map((r: { path: string; new_path: string; ai_tag: string }) => [r.path, { new_path: r.new_path, tag: r.ai_tag }])
        );

        // Actualizamos el estado de una sola vez con los nuevos nombres del backend
        setStatus(prev => ({
          ...prev,
          images: prev.images.map(img => {
            const result = resultsMap.get(img.path);
            if (result && result.tag) {
              return { ...img, path: result.new_path, ai_tag: result.tag };
            }
            return img;
          }),
        }));
        toast.success("Clasificación retroactiva completada");
      }
    } catch (error) {
      console.error("Error en clasificación retroactiva:", error);
      toast.error("Error al clasificar imágenes existentes");
    } finally {
      setIsClassifying(false);
    }
  }, [status.images, handleRename]);

  // Efecto para disparar clasificación si se activa useAI con imágenes ya presentes
  useEffect(() => {
    if (useAI && aiModelReady && status.images.length > 0 && !status.is_running && !isClassifying) {
      const hasUntagged = status.images.some(img => !img.ai_tag);
      if (hasUntagged) {
        setTimeout(() => {
          classifyExisting(status.images, nicho);
        }, 0);
      }
    }
  }, [useAI, status.images.length, aiModelReady, status.is_running]); // Ahora reacciona a más cambios críticos

  return {
    status, jobId, isExporting,
    useAI, nicho, aiModelReady, onlyLarge, targetFolder, foldersWithCopy,
    setUseAI, setNicho, setOnlyLarge, setTargetFolder,
    startScrape, stopScrape, loadSession, handleRename, handleExport, clearImages, clearAll,
  };
}
