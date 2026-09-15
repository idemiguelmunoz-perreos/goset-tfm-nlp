# Evaluación — Componente B (recomendador)

> Ejecutada sobre fixtures sintéticas (desarrollo). Las métricas de ranking (precision@k, NDCG, MRR) y la validación clínica (Capa 2, kappa) requieren etiquetas de expertas sobre casos reales.

## Capa 1 — Rule coverage accuracy

- Casos canónicos: **23** · reglas esperadas: **45**
- **Coverage accuracy: 100.0%** (objetivo >95%)
- Fallos: ninguno

## Comparativa baseline (solo reglas duras) vs híbrido

| Métrica | Baseline | Híbrido |
|---|---|---|
| perros_con_recomendacion_% | 1.1 | 100.0 |
| servicios_por_perro | 0.02 | 4.42 |
| reglas_activadas_por_perro | 0.02 | 8.09 |
| latencia_media_ms | 0.021 | 0.027 |

## Servicio prioritario (top-1) — distribución

- Peluqueria: 32
- Salud preventiva: 20
- Guarderia: 15
- Entrenamiento: 13
- Alimentacion: 8

## Análisis de errores (modos de fallo por dato ausente)

- manto_no_determinado_%: 0.0%
- estado_vacunal_no_verificable_%: 1.1%
- etapa_desconocida_%: 4.5%