# Capa 3 — Análisis cualitativo de errores y refinamiento (Componente B)

Evaluación experta (Capa 2) sobre 20 perfiles. Media Likert ~2,9/4 y acuerdo
desigual (kappa_w: vet–Isabela 0,79; vet–peluquera 0,32; peluquera–Isabela 0,13).
El análisis de los ítems peor valorados revela tres patrones de fallo concretos.

## 1. Patrones de fallo detectados

**F1 · Guardería sobre-recomendada a perros ansiosos/reactivos.** Es el servicio
peor valorado (media 2,08). Ejemplos y verbatim experto:
- *Teckel reactivo + ansiedad → top Guardería*: "puede provocar conflictos o traumas; requiere etólogo antes".
- *Podenco senior con ansiedad → top Guardería*: "un hotel o guardería la descolocará por completo; faltan pautas etológicas".
Causa: la regla GU-05 (ansiedad → guardería como apoyo) no captura que, en
reactividad/ansiedad marcada, el grupo está **contraindicado** hasta modificar conducta.

**F2 · Peluquería sobre-recomendada en manto corto.** Teckel, Boxer, Bodeguero
(pelo corto) salían con Peluquería arriba. Verbatim: "el pelo corto apenas
necesita peluquería profesional". Causa: PE-05/PE-08/PE-09 (oídos, agua, piel)
se activan con independencia del manto y se acumulan hasta encabezar el ranking.

**F3 · En cachorro, peluquería por delante de la salud preventiva.** Cachorro de
bodeguero → top Peluquería. Verbatim: "poner peluquería primero en un cachorro
no tiene sentido; urgían las vacunas". Causa: la prioridad no reflejaba la
urgencia clínica de la vacunación en cachorros.

## 2. Por qué discrepan las evaluadoras (lectura del kappa bajo)

La divergencia de la peluquera (kappa 0,13–0,32) se concentra en los perros
ansiosos con guardería top: la peluquera los puntuó como aceptables (lente de
aseo) mientras vet e Isabela detectaron la **contraindicación conductual** y los
suspendieron. No es ruido: es que la evaluación **necesita las dos lentes**
(clínica y de aseo). Refuerza el diseño multi-evaluador del scope.

## 3. Refinamientos implementados

| ID | Ajuste | Fundamento |
|---|---|---|
| a | Ansiedad/reactividad → penaliza guardería y añade nota "etología antes de grupo" | AVSAB (S7); verbatim vet |
| b | Peluquería incidental (oídos/agua/piel) pesa 0,4× si el manto no es intensivo | verbatim peluquera |
| c | En cachorro, salud preventiva ×1,5 (domina sobre peluquería) | AAHA/WSAVA; verbatim vet |

## 4. Before / after sobre los casos problemáticos

| Caso | Antes | Después | ¿Alineado con experta? |
|---|---|---|---|
| Teckel reactivo+ansiedad | Guardería | Entrenamiento | Sí |
| Cachorro bodeguero | Peluquería | Salud preventiva | Sí |
| Teckel pelo corto | Peluquería | Salud preventiva | Sí |
| Podenco senior+ansiedad | Guardería | Hotel | Parcial (sigue siendo alojamiento) |
| Boxer pelo corto | Guardería | Guardería | No (pendiente) |

**4 de 6 casos** se mueven hacia la recomendación que pedían las expertas, sin
romper Capa 1 (coverage 100%) ni los tests.

## 5. Limitaciones y siguiente iteración

- El ajuste (a) penaliza guardería pero **no hotel**: el Podenco ansioso migró a
  Hotel, que también es alojamiento. Siguiente iteración: extender la penalización
  conductual a hotel y enrutar a Entrenamiento/etología.
- El Boxer (braquicéfalo, alta energía) sigue en Guardería; requiere afinar el
  peso de la energía frente al foco en salud que pedía la experta.
- **Re-evaluación pendiente:** este before/after es coherencia interna; la mejora
  debe confirmarse con una **segunda ronda de Capa 2** de las expertas, idealmente
  sobre **perros reales**. El bucle evaluar→analizar→corregir→re-evaluar queda abierto.
