"use client";

import { useState, useEffect, useCallback } from "react";
import { toast } from "sonner";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export interface Config {
  localBase: string;
  openaiApiKey: string;
  historyFolders: string[];
  selectedHistory: string;
  isEditingConfig: boolean;
  configInput: string;
  apiInput: string;
  showConsole: boolean;
  isAiEnabled: boolean;
}

export interface ConfigActions {
  fetchHistory: () => Promise<void>;
  saveConfig: () => Promise<void>;
  setSelectedHistory: (f: string) => void;
  setIsEditingConfig: (v: boolean) => void;
  setConfigInput: (v: string) => void;
  setApiInput: (v: string) => void;
  setShowConsole: (v: boolean) => void;
  setIsAiEnabled: (v: boolean) => void;
  browseBaseFolder: () => Promise<void>;
  browseTargetFolder: () => Promise<string | null>;
}

export function useConfig(): Config & ConfigActions {
  const [localBase, setLocalBase] = useState("D:\\Dev\\imgscrap");
  const [openaiApiKey, setOpenaiApiKey] = useState("");
  const [historyFolders, setHistoryFolders] = useState<string[]>([]);
  const [selectedHistory, setSelectedHistory] = useState("");
  const [isEditingConfig, setIsEditingConfig] = useState(false);
  const [configInput, setConfigInput] = useState("");
  const [apiInput, setApiInput] = useState("");
  const [showConsole, setShowConsole] = useState(false);
  const [isAiEnabled, setIsAiEnabled] = useState(false);

  // Cargar preferencias al montar
  useEffect(() => {
    const savedConsole = localStorage.getItem("imgscrap:show-console");
    if (savedConsole !== null) setShowConsole(savedConsole === "true");

    const savedAi = localStorage.getItem("imgscrap:is-ai-enabled");
    if (savedAi !== null) setIsAiEnabled(savedAi === "true");
  }, []);

  // Persistir preferencias
  useEffect(() => {
    localStorage.setItem("imgscrap:show-console", String(showConsole));
  }, [showConsole]);

  useEffect(() => {
    localStorage.setItem("imgscrap:is-ai-enabled", String(isAiEnabled));
  }, [isAiEnabled]);

  const fetchHistory = useCallback(async () => {
    try {
      const confRes = await fetch(`${API_BASE}/api/config`);
      if (confRes.ok) {
        const confData = await confRes.json();
        setLocalBase(confData.base_dir);
        setOpenaiApiKey(confData.openai_api_key);
        setConfigInput(confData.base_dir);
        setApiInput(confData.openai_api_key);
      }
    } catch { /* backend todavía no arrancó */ }

    try {
      const res = await fetch(`${API_BASE}/api/images/history`);
      if (res.ok) {
        const data = await res.json();
        const folders: string[] = data.folders ?? [];
        setHistoryFolders(folders);
        if (folders.length > 0) setSelectedHistory(f => f || folders[0]);
      }
    } catch { /* ignoro si falla */ }
  }, []);

  const saveConfig = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/config`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ base_dir: configInput, openai_api_key: apiInput }),
      });
      if (res.ok) {
        setLocalBase(configInput);
        setOpenaiApiKey(apiInput);
        setIsEditingConfig(false);
        fetchHistory();
        toast.success("Configuración guardada");
      }
    } catch {
      toast.error("Error al guardar la configuración");
    }
  }, [configInput, apiInput, fetchHistory]);

  const browseBaseFolder = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/browse/folder`);
      if (res.ok) {
        const data = await res.json();
        if (data.path) setConfigInput(data.path);
      }
    } catch {
      toast.error("No pude abrir el explorador de archivos");
    }
  }, []);

  const browseTargetFolder = useCallback(async (): Promise<string | null> => {
    try {
      const res = await fetch(`${API_BASE}/api/browse/folder`);
      if (res.ok) {
        const data = await res.json();
        return data.path || null;
      }
    } catch {
      toast.error("No pude abrir el explorador de archivos");
    }
    return null;
  }, []);

  // Al montar, cargo el historial
  useEffect(() => { 
    const timer = setTimeout(() => {
      fetchHistory(); 
    }, 0);
    return () => clearTimeout(timer);
  }, [fetchHistory]);

  return {
    localBase,
    openaiApiKey,
    historyFolders,
    selectedHistory,
    isEditingConfig,
    configInput,
    apiInput,
    fetchHistory,
    saveConfig,
    setSelectedHistory,
    setIsEditingConfig,
    setConfigInput,
    setApiInput,
    browseBaseFolder,
    browseTargetFolder,
    showConsole,
    setShowConsole,
    isAiEnabled,
    setIsAiEnabled,
  };
}
