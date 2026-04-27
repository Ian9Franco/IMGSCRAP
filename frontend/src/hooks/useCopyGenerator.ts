"use client";

import { useState, useEffect, useCallback } from "react";
import { toast } from "sonner";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export interface CopyData {
  title: string;
  address: string;
  price: string;
  location: string;
  features: string;
  description: string;
  operation_type: string;
}

const EMPTY_COPY_DATA: CopyData = {
  title: "", address: "", price: "", location: "", features: "", description: "", operation_type: "venta",
};

export interface CopyGeneratorState {
  copyData: CopyData;
  generatedCopy: string;
  isGeneratingCopy: boolean;
  isAiEnabled: boolean;
  isExtractionAiEnabled: boolean;
  setIsAiEnabled: (v: boolean) => void;
  setIsExtractionAiEnabled: (v: boolean) => void;
  isEditingCopy: boolean;
  isExtracting: boolean;
  extractedOk: boolean;
  geminiVersion: string;
  generationEngine: string;
  editEngine: string;
  setGenerationEngine: (v: string) => void;
  setEditEngine: (v: string) => void;
  setCopyData: (data: CopyData) => void;
  setGeneratedCopy: (text: string) => void;
  versions: string[];
  currentFilename: string;
  extractionEngine: string;
  setExtractionEngine: (v: string) => void;
  loadSpecificVersion: (propertyName: string, filename: string) => Promise<void>;
  generateCopy: (nicho: string, propertyName: string) => Promise<void>;
  editCopy: (prompt: string) => Promise<void>;
  saveDocx: (propertyName: string) => Promise<void>;
  copyCopyToClipboard: () => void;
}

export function useCopyGenerator(
  url: string,
  nicho: string,
  isAiEnabledDefault: boolean = true
): CopyGeneratorState {
  const [copyData, setCopyData] = useState<CopyData>(EMPTY_COPY_DATA);
  const [generatedCopy, setGeneratedCopy] = useState("");
  const [isGeneratingCopy, setIsGeneratingCopy] = useState(false);
  const [isEditingCopy, setIsEditingCopy] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractedOk, setExtractedOk] = useState(false);
  const [isAiEnabled, setIsAiEnabled] = useState(isAiEnabledDefault);
  const [isExtractionAiEnabled, setIsExtractionAiEnabled] = useState(false);
  const [geminiVersion, setGeminiVersion] = useState("LITE");
  const [generationEngine, setGenerationEngine] = useState("local_phi3");
  const [extractionEngine, setExtractionEngine] = useState("local_phi3");
  const [editEngine, setEditEngine] = useState("cloud_gemini");
  const [versions, setVersions] = useState<string[]>([]);
  const [currentFilename, setCurrentFilename] = useState("");

  // Escucha el evento emitido por loadSession cuando hay copy guardado en la carpeta
  useEffect(() => {
    setIsAiEnabled(isAiEnabledDefault);
  }, [isAiEnabledDefault]);

  useEffect(() => {
    const handler = (e: Event) => {
      const ev = e as CustomEvent<{
        copy?: string;
        url?: string;
        versions?: string[];
        filename?: string;
        raw_data?: {
          title?: string;
          address?: string;
          price?: string;
          location?: string;
          features?: string | string[];
          description?: string;
          operation_type?: string;
          url?: string;
        };
      } | string>;
      const payload = ev.detail;
      
      // Si el evento viene con el nuevo formato (objeto)
      if (payload && typeof payload === 'object') {
        if (payload.copy) {
          setGeneratedCopy(payload.copy);
        }
        if (payload.versions) {
          setVersions(payload.versions);
        }
        if (payload.filename) {
          setCurrentFilename(payload.filename);
        }
        if (payload.raw_data) {
          setCopyData({
            title: payload.raw_data.title || "",
            address: payload.raw_data.address || "",
            price: payload.raw_data.price || "",
            location: payload.raw_data.location || "",
            features: Array.isArray(payload.raw_data.features) 
              ? payload.raw_data.features.join(", ") 
              : (payload.raw_data.features || ""),
            description: payload.raw_data.description || "",
            operation_type: payload.raw_data.operation_type || "venta",
          });
        }
        // Si viene una URL, avisamos para que se pueble el campo de link
        const finalUrl = payload.url || (payload.raw_data?.url);
        if (finalUrl) {
          window.dispatchEvent(new CustomEvent("imgscrap:url-loaded", { detail: finalUrl }));
        }
      } else if (typeof payload === 'string') {
        // Fallback por si acaso
        setGeneratedCopy(payload);
      }
    };
    window.addEventListener("imgscrap:copy-loaded", handler);
    return () => window.removeEventListener("imgscrap:copy-loaded", handler);
  }, []);

  // Auto-extrae datos de la propiedad al pegar una URL (debounce 1500ms)
  useEffect(() => {
    if (!url || !url.startsWith("http") || nicho !== "inmobiliaria") return;
    
    const extract = async () => {
      setExtractedOk(false);
      setIsExtracting(true);
      try {
        const engine = isExtractionAiEnabled ? extractionEngine : null;
        const res = await fetch(`${API_BASE}/api/property/extract`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ 
            url, 
            nicho, 
            engine 
          }),
        });
        if (res.ok) {
          const data = await res.json();
          if (data.extracted) {
            const addr = data.address || "";
            const newCopyData: CopyData = {
              title:       data.title || "",
              address:     addr,
              price:       data.price || "",
              location:    data.location || "",
              features:    Array.isArray(data.features)
                ? data.features.join(", ")
                : (data.features || ""),
              description: data.description || "",
              operation_type: data.operation_type || "venta",
            };
            setCopyData(newCopyData);

            // Auto-sugerir nombre de carpeta y devolver la dirección para el padre
            if (addr) {
              try {
                const sugRes = await fetch(`${API_BASE}/api/folder/suggest?address=${encodeURIComponent(addr)}`);
                if (sugRes.ok) {
                  const sugData = await sugRes.json();
                  // Emitimos el nombre sugerido vía el event para que lo maneje el padre
                  window.dispatchEvent(new CustomEvent("imgscrap:folder-suggest", { detail: sugData.folder }));
                }
              } catch { /* falla silenciosa */ }
            }
            setExtractedOk(true);
          }
        }
      } catch { /* falla silenciosa */ }
      finally { setIsExtracting(false); }
    };
    
    const timer = setTimeout(extract, 1500);
    return () => clearTimeout(timer);
  }, [url, nicho, generationEngine, extractionEngine, isExtractionAiEnabled]); // eslint-disable-line react-hooks/exhaustive-deps

  const generateCopy = useCallback(async (nicho: string, propertyName: string) => {
    if (!propertyName) {
      toast.error("Primero definí una carpeta de destino");
      return;
    }
    
    setIsGeneratingCopy(true);
    // Solo activamos modo '2.5' (efecto visual de IA) si hay IA habilitada
    if (isAiEnabled) setGeminiVersion("2.5");

    try {
      const res = await fetch(`${API_BASE}/api/copy/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nicho,
          data: {
            ...copyData,
            features: copyData.features.split(",").map(f => f.trim()),
          },
          property_folder: propertyName,
          use_ai: isAiEnabled,
          engine: isAiEnabled ? generationEngine : null
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setGeneratedCopy(data.copy);
        toast.success("Publicación generada y guardada en .docx");
      } else {
        const err = await res.json();
        toast.error(`Error: ${err.detail}`);
      }
    } catch {
      toast.error("Error al conectar con el generador de copy");
    } finally {
      setIsGeneratingCopy(false);
      setGeminiVersion("LITE");
    }
  }, [copyData, isAiEnabled, generationEngine]);

  const editCopy = useCallback(async (prompt: string) => {
    if (!generatedCopy || !prompt) return;
    setIsEditingCopy(true);
    setGeminiVersion("2.5");
    try {
      const res = await fetch(`${API_BASE}/api/copy/edit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          current_copy: generatedCopy, 
          prompt,
          engine: editEngine
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setGeneratedCopy(data.copy);
        toast.success("Copy editado exitosamente con Gemini");
      } else {
        const err = await res.json();
        toast.error(`Error: ${err.detail}`);
      }
    } catch {
      toast.error("Error al conectar con Gemini para edición");
    } finally {
      setIsEditingCopy(false);
      setGeminiVersion("LITE");
    }
  }, [generatedCopy, editEngine]);
  
  const loadSpecificVersion = useCallback(async (propertyName: string, filename: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/copy/load?folder_name=${propertyName}&filename=${filename}`);
      if (res.ok) {
        const data = await res.json();
        setGeneratedCopy(data.copy);
        setCurrentFilename(data.filename);
        toast.success(`Cargada versión: ${filename}`);
      }
    } catch {
      toast.error("Error al cargar la versión específica");
    }
  }, []);

  const saveDocx = useCallback(async (propertyName: string) => {
    if (!propertyName || !generatedCopy) return;
    try {
      const res = await fetch(`${API_BASE}/api/copy/save-docx`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          copy: generatedCopy,
          property_folder: propertyName,
          title: copyData.title || "Propiedad",
          features: copyData.features.split(",").map(f => f.trim()),
        }),
      });
      if (res.ok) {
        toast.success("Documento word guardado");
        
        // Recargar la lista de versiones para que el dropdown se actualice si creamos un V2/V3
        loadSpecificVersion(propertyName, ""); 
      } else {
        const err = await res.json();
        toast.error(`Error: ${err.detail || "No se pudo guardar el documento"}`);
      }
    } catch {
      toast.error("Error al conectar con el servidor para guardar el docx");
    }
  }, [generatedCopy, copyData]);

  const copyCopyToClipboard = useCallback(() => {
    if (!generatedCopy) return;
    navigator.clipboard.writeText(generatedCopy);
    toast.success("Texto copiado al portapapeles 📋");
  }, [generatedCopy]);

  return {
    copyData, generatedCopy, isGeneratingCopy, isExtracting, extractedOk, isEditingCopy, geminiVersion,
    isAiEnabled, setIsAiEnabled,
    generationEngine, editEngine, setGenerationEngine, setEditEngine,
    setCopyData, setGeneratedCopy, generateCopy, editCopy,
    saveDocx,
    copyCopyToClipboard,
    versions,
    currentFilename,
    loadSpecificVersion,
    isExtractionAiEnabled,
    setIsExtractionAiEnabled,
    extractionEngine,
    setExtractionEngine
  };
}
