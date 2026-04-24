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
  isExtracting: boolean;
  extractedOk: boolean;
  isEditingCopy: boolean;
  geminiVersion: string;
  setCopyData: (data: CopyData) => void;
  setGeneratedCopy: (text: string) => void;
  generateCopy: (nicho: string, propertyName: string) => Promise<void>;
  editCopy: (prompt: string) => Promise<void>;
  saveDocx: (propertyName: string) => Promise<void>;
  copyCopyToClipboard: () => void;
}

export function useCopyGenerator(
  url: string,
  nicho: string,
  isAiEnabled: boolean = true
): CopyGeneratorState {
  const [copyData, setCopyData] = useState<CopyData>(EMPTY_COPY_DATA);
  const [generatedCopy, setGeneratedCopy] = useState("");
  const [isGeneratingCopy, setIsGeneratingCopy] = useState(false);
  const [isEditingCopy, setIsEditingCopy] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractedOk, setExtractedOk] = useState(false);
  const [geminiVersion, setGeminiVersion] = useState("LITE");

  // Escucha el evento emitido por loadSession cuando hay copy guardado en la carpeta
  useEffect(() => {
    const handler = (e: Event) => {
      const ev = e as CustomEvent<{
        copy?: string;
        raw_data?: {
          title?: string;
          address?: string;
          price?: string;
          location?: string;
          features?: string | string[];
          description?: string;
          operation_type?: string;
        };
      } | string>;
      const payload = ev.detail;
      
      // Si el evento viene con el nuevo formato (objeto)
      if (payload && typeof payload === 'object') {
        if (payload.copy) {
          setGeneratedCopy(payload.copy);
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
      } else if (typeof payload === 'string') {
        // Fallback por si acaso
        setGeneratedCopy(payload);
      }
    };
    window.addEventListener("imgscrap:copy-loaded", handler);
    return () => window.removeEventListener("imgscrap:copy-loaded", handler);
  }, []);

  // Auto-extrae datos de la propiedad al pegar una URL (debounce 800ms)
  useEffect(() => {
    if (!url || !url.startsWith("http") || nicho !== "inmobiliaria") return;
    const timer = setTimeout(async () => {
      setExtractedOk(false);
      setIsExtracting(true);
      try {
        const res = await fetch(`${API_BASE}/api/property/extract`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url, nicho }),
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
    }, 800);
    return () => clearTimeout(timer);
  }, [url, nicho]); // eslint-disable-line react-hooks/exhaustive-deps

  const generateCopy = useCallback(async (nicho: string, propertyName: string) => {
    if (!propertyName) {
      toast.error("Seleccioná una carpeta o sesión primero");
      return;
    }
    setIsGeneratingCopy(true);
    setGeminiVersion("2.5");
    try {
      const res = await fetch(`${API_BASE}/api/copy/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nicho,
          use_ai: isAiEnabled,
          data: {
            ...copyData,
            features: copyData.features.split(",").map(f => f.trim()),
          },
          property_folder: propertyName,
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
  }, [copyData, isAiEnabled]);

  const editCopy = useCallback(async (prompt: string) => {
    if (!generatedCopy || !prompt) return;
    setIsEditingCopy(true);
    setGeminiVersion("2.5");
    try {
      const res = await fetch(`${API_BASE}/api/copy/edit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ current_copy: generatedCopy, prompt }),
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
  }, [generatedCopy]);

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
        toast.success("Documento Word (.docx) actualizado");
      } else {
        toast.error("Error al actualizar el docx");
      }
    } catch {
      toast.error("Error al guardar el docx");
    }
  }, [generatedCopy, copyData]);

  const copyCopyToClipboard = useCallback(() => {
    if (!generatedCopy) return;
    navigator.clipboard.writeText(generatedCopy);
    toast.success("Texto copiado al portapapeles 📋");
  }, [generatedCopy]);

  return {
    copyData, generatedCopy, isGeneratingCopy, isExtracting, extractedOk, isEditingCopy, geminiVersion,
    setCopyData, setGeneratedCopy, generateCopy, editCopy, saveDocx, copyCopyToClipboard,
  };
}
