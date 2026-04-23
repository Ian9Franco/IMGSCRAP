"""
image_classifier.py — Módulo de clasificación por CLIP (Fase 2)

Responsabilidades:
- Cargar el modelo CLIP una sola vez al iniciar el backend (lazy load)
- Clasificación binaria: relevante vs basura
- Auto-tagging por nicho con etiquetas simples (5–10 por nicho)

El modelo se descarga automáticamente la primera vez (~350MB) y queda cacheado.
"""

from __future__ import annotations
from PIL import Image
from io import BytesIO
from typing import Optional
import threading

# ─────────────────────────────────────────────
# Modelo CLIP (cargado una sola vez, lazy)
# ─────────────────────────────────────────────
_model = None
_model_lock = threading.Lock()
_model_ready = False

# Cache de embeddings de texto: evita recalcular los labels del nicho en cada imagen
# Las etiquetas son fijas en runtime, así que calculamos una sola vez y guardamos.
_text_embeddings_cache: dict[str, object] = {}

def load_model():
    """Carga el modelo CLIP en background al arrancar el backend."""
    global _model, _model_ready
    try:
        from sentence_transformers import SentenceTransformer
        with _model_lock:
            if _model is None:
                print("[CLIP] Cargando modelo clip-ViT-B-32...")
                _model = SentenceTransformer("clip-ViT-B-32")
                _model_ready = True
                print("[CLIP] Modelo listo.")
    except Exception as e:
        print(f"[CLIP] Error al cargar modelo: {e}")

def is_model_ready() -> bool:
    return _model_ready

def _get_model():
    return _model

# ─────────────────────────────────────────────
# Categorías por nicho
# ─────────────────────────────────────────────

NICHO_TAGS: dict[str, list[str]] = {
    "inmobiliaria": [
        "fachada exterior del edificio",
        "cocina moderna",
        "baño con azulejos",
        "dormitorio con cama",
        "living comedor",
        "jardín o patio exterior",
        "terraza o balcón",
        "cochera o garaje",
        "pileta o piscina",
        "quincho o parrilla",
    ],
    "gastronomia": [
        "plato de comida principal",
        "detalle de ingrediente",
        "bebida o trago",
        "postre o dulce",
        "ambiente del local",
        "exterior del restaurante",
        "barra o mostrador",
        "menu o carta",
    ],
    "ecommerce": [
        "producto sobre fondo blanco",
        "detalle o textura del producto",
        "producto en uso o lifestyle",
        "empaque o packaging",
        "variante de color",
    ],
}

# Etiquetas de CONTENIDO NO DESEADO (Irrelevante)
# Se usan para descartar logos, capturas, banners, etc.
IRRELEVANT_LABELS = [
    "logo de empresa",
    "banner publicitario horizontal",
    "ícono pequeño de interfaz",
    "foto de stock genérica",
    "botón de sitio web",
    "imagen de fondo decorativa",
    "cartel o letrero de texto",
]

# Umbral de similitud: si la similitud con cualquier tag del nicho >= THRESHOLD, es relevante
RELEVANCE_THRESHOLD  = 0.22   # empírico, ajustar según resultados
IRRELEVANT_THRESHOLD = 0.28   # si supera esto en irrelevante, descartamos directo


# ─────────────────────────────────────────────
# Funciones principales
# ─────────────────────────────────────────────

def _embed_image(img: Image.Image):
    """Devuelve el embedding CLIP de una imagen PIL."""
    model = _get_model()
    if model is None:
        return None
    return model.encode(img, convert_to_tensor=True)

def _embed_texts(texts: list[str]):
    """Devuelve embeddings CLIP de una lista de textos."""
    model = _get_model()
    if model is None:
        return None
    return model.encode(texts, convert_to_tensor=True)


def _embed_texts_cached(texts: list[str]):
    """Igual que _embed_texts pero con cache en memoria por clave de texto.
    Como los labels del nicho y basura son constantes durante la sesión,
    se calculan una sola vez y se reutilizan para todas las imágenes."""
    key = "|".join(texts)
    if key not in _text_embeddings_cache:
        _text_embeddings_cache[key] = _embed_texts(texts)
    return _text_embeddings_cache[key]

def classify_image(img: Image.Image, nicho: str = "inmobiliaria") -> dict:
    """
    Clasifica una imagen PIL.

    Retorna:
    {
        "is_relevant": bool,
        "top_tag": str | None,       # categoría más probable del nicho
        "top_score": float,
        "is_irrelevant": bool,
        "irrelevant_score": float,
    }
    """
    if not _model_ready:
        return {"is_relevant": True, "top_tag": None, "top_score": 0.0,
                "is_irrelevant": False, "irrelevant_score": 0.0}

    try:
        from torch.nn.functional import cosine_similarity
        import torch

        nicho_labels = NICHO_TAGS.get(nicho, NICHO_TAGS["inmobiliaria"])

        img_emb = _embed_image(img)
        # Usamos cache para los embeddings de texto — se computan una sola vez por sesión
        text_embs_nicho      = _embed_texts_cached(nicho_labels)
        text_embs_irrelevant = _embed_texts_cached(IRRELEVANT_LABELS)

        # Similitud coseno imagen vs cada etiqueta
        scores_nicho      = cosine_similarity(img_emb.unsqueeze(0), text_embs_nicho).squeeze(0)
        scores_irrelevant = cosine_similarity(img_emb.unsqueeze(0), text_embs_irrelevant).squeeze(0)

        top_nicho_idx      = int(scores_nicho.argmax())
        top_nicho_score    = float(scores_nicho[top_nicho_idx])
        top_irrelevant_score = float(scores_irrelevant.max())

        is_irrelevant = top_irrelevant_score >= IRRELEVANT_THRESHOLD
        is_relevant   = (not is_irrelevant) and (top_nicho_score >= RELEVANCE_THRESHOLD)

        # Normalizar el label para usarlo como tag (solo la primera palabra descriptiva)
        raw_tag = nicho_labels[top_nicho_idx]
        short_tag = raw_tag.split()[0].capitalize()   # ej. "fachada"

        return {
            "is_relevant":      is_relevant,
            "top_tag":          short_tag if is_relevant else None,
            "top_score":        round(top_nicho_score, 4),
            "is_irrelevant":    is_irrelevant,
            "irrelevant_score": round(top_irrelevant_score, 4),
        }

    except Exception as e:
        print(f"[CLIP] Error clasificando imagen: {e}")
        return {"is_relevant": True, "top_tag": None, "top_score": 0.0,
                "is_irrelevant": False, "irrelevant_score": 0.0}
