# EVALUACION: COMPONENTE B (RECOMENDADOR)

> Ejecutada sobre 96 perros reales (formulario de contexto + cartilla, identidad del dueno eliminada). Capa 1 sobre casos canonicos; Capas 2 y 3 sobre la muestra real completa.

## Capa 1: Rule coverage accuracy

- Casos canonicos: **23**, reglas esperadas: **45**
- **Coverage accuracy: 100.0%** (objetivo >95%)
- Fallos: ninguno

## Comparativa: baseline (solo reglas duras) vs hibrido

| Metrica | Baseline | Hibrido |
|---|---|---|
| perros_con_recomendacion_% | 34.4 | 99.0 |
| servicios_por_perro | 0.59 | 4.2 |
| reglas_activadas_por_perro | 0.59 | 7.44 |
| latencia_media_ms | 0.027 | 0.03 |

## Servicio prioritario (top-1) sobre 96 perros reales

- Peluqueria: 32
- Salud preventiva: 32
- Alimentacion: 13
- Guarderia: 9
- Entrenamiento: 5
- Hotel: 4
- sin recomendacion: 1

- Perros marcados para revision humana: 18 de 96
- Perros no elegibles a servicio de grupo (bloqueo por regla dura): 33 de 96

## Capa 2: validacion experta (n=96)

Dos expertas de dominio independientes (veterinaria y peluquera canina) puntuaron de forma independiente la idoneidad de cada recomendacion en Likert 1-4 (1 inapropiada, 4 totalmente apropiada). El acuerdo inter-evaluador se calcula entre ellas dos. La autora realizo ademas una revision de sentido comun sobre las mismas 96 salidas, reportada por separado y fuera del calculo de acuerdo (evita usar a la autora como anotadora de referencia).

### Idoneidad percibida (validacion experta)

| Evaluadora experta | Media Likert | % apropiado (>=3) |
|---|---|---|
| Veterinaria | 3.48 | 90.6% |
| Peluquera canina | 3.34 | 91.7% |
| **Conjunto experto** | **3.41** | **91.1%** |

### Acuerdo inter-evaluador (veterinaria vs peluquera)

| Coeficiente | Valor |
|---|---|
| Kappa ponderado (Cohen) | 0.054 |
| AC2 ponderado (Gwet) | **0.801** |
| Acuerdo observado ponderado (Pa) | 0.911 |
| Acuerdo dentro de +-1 punto | 93.8% |

**Lectura.** El acuerdo observado ponderado es alto (0,91) y el 94% de los pares difiere como mucho en un punto, pero el kappa ponderado se desploma (0,05). Es la paradoja del kappa (Feinstein y Cicchetti, 1990): con las puntuaciones concentradas en 3-4 (mas del 90% de ambas expertas), el termino de acuerdo esperado se infla y kappa tiende a cero pese al acuerdo real. Por eso la metrica de referencia es el AC2 de Gwet (2008), robusto a esa concentracion: **0,80**, acuerdo bueno entre las dos expertas de dominio.

**Revision de sentido comun (autora).** Sobre las mismas 96 salidas, la autora aplico un umbral mas estricto (media 2.67, 57% apropiadas). No entra en el acuerdo inter-evaluador; sirve de contraste conservador y coincide con las expertas en el signo del juicio (la mayoria de recomendaciones son defendibles), con un listón mas alto.

## Analisis de errores (modos de fallo por dato ausente)

- manto_no_determinado_%: 1.0%
- estado_vacunal_no_verificable_%: 5.2%
- etapa_desconocida_%: 0.0%