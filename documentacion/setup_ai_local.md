# Guía de Configuración: IA Local (Ollama + Phi-3)

Esta guía explica cómo configurar el motor de IA local para que la aplicación pueda generar contenidos sin depender de internet o de claves de API externas.

## 1. Requisitos Previos
- Windows 10 o superior.
- Al menos 8GB de RAM (recomendado 16GB).

## 2. Instalación de Ollama
1. Descarga el instalador de [Ollama para Windows](https://ollama.com/download/windows).
2. Ejecuta el archivo y sigue los pasos de instalación.
3. Una vez instalado, verás el ícono de Ollama en la bandeja de sistema (barra de tareas).

## 3. Instalación del Modelo
Abre una terminal (PowerShell o CMD) y ejecuta:
```bash
# Para el modelo liviano y rápido
ollama run phi3

# Para el modelo más inteligente y potente
ollama run gemma3
```
Estos comandos descargarán los modelos. Una vez que veas el prompt `>>>`, el modelo está listo. Puedes salir escribiendo `/bye`.

## 4. Motores Disponibles en la App
Ahora puedes elegir entre 3 niveles de potencia:

- **Local Phi-3 (`local_phi3`):** El más rápido. Ideal para equipos con poca RAM o tareas simples.
- **Local Gemma 3 (`local_gemma3`):** Mucho más inteligente y creativo. Recomendado si tienes una buena placa de video (GPU).
- **Cloud Gemini (`cloud_gemini`):** El tope de gama. Requiere internet y API Key, pero es el más preciso.

## 5. Troubleshooting
- **Error "Connection Refused":** Asegúrate de que Ollama esté abierto (mira el ícono en la barra de tareas).
- **Lentitud:** La IA local depende de tu procesador (CPU) y tarjeta gráfica (GPU). La primera vez que genera puede tardar unos segundos extra en cargar el modelo en memoria.
