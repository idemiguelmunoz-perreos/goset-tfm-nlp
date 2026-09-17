# CAPA 3: ANALISIS CUALITATIVO DE ERRORES Y REFINAMIENTO (COMPONENTE B)

El ciclo de evaluacion tuvo dos rondas. En la primera, las expertas puntuaron una
muestra inicial y sus comentarios sobre los items peor valorados revelaron tres
patrones de fallo concretos. Esos patrones motivaron los refinamientos del motor.
En la segunda ronda, el sistema refinado se valido sobre los 96 perros reales
(ver Capa 2): media agregada 3,16/4, 79,9% de recomendaciones apropiadas y acuerdo
entre las dos expertas de dominio AC2 0,80.

## 1. Patrones de fallo detectados

**F1: Guarderia sobre-recomendada a perros ansiosos o reactivos.** Fue el servicio
peor valorado en la primera ronda. Ejemplos y verbatim experto:

- *Teckel reactivo con ansiedad, top Guarderia*: "puede provocar conflictos o traumas; requiere etologo antes".
- *Podenco senior con ansiedad, top Guarderia*: "un hotel o guarderia la descolocara por completo; faltan pautas etologicas".

Causa: la regla GU-05 (ansiedad como apoyo a guarderia) no capturaba que, en
reactividad o ansiedad marcada, el grupo esta **contraindicado** hasta modificar conducta.

**F2: Peluqueria sobre-recomendada en manto corto.** Teckel, Boxer y Bodeguero
(pelo corto) salian con Peluqueria arriba. Verbatim: "el pelo corto apenas
necesita peluqueria profesional". Causa: PE-05, PE-08 y PE-09 (oidos, agua, piel)
se activaban con independencia del manto y se acumulaban hasta encabezar el ranking.

**F3: En cachorro, peluqueria por delante de la salud preventiva.** Cachorro de
bodeguero, top Peluqueria. Verbatim: "poner peluqueria primero en un cachorro
no tiene sentido; urgian las vacunas". Causa: la prioridad no reflejaba la
urgencia clinica de la vacunacion en cachorros.

## 2. Por que discrepan las evaluadoras

El acuerdo inter-evaluador se mide entre las dos expertas de dominio (veterinaria y
peluquera), que apenas difieren entre si (AC2 0,80) y ambas consideran apropiada mas
del 90% de las recomendaciones. Donde si discrepan es en los perros ansiosos con
guarderia arriba: la peluquera los leyo desde el aseo (aceptables) y la veterinaria
detecto la contraindicacion conductual. La evaluacion **necesita las dos lentes**,
clinica y de aseo, lo que respalda el diseno multi-evaluador. La autora aporta una
revision de sentido comun, con umbral mas estricto, fuera del calculo de acuerdo.

## 3. Refinamientos implementados

| ID | Ajuste | Fundamento |
|---|---|---|
| a | Ansiedad o reactividad penaliza guarderia y anade nota "etologia antes de grupo" | AVSAB (S7); verbatim vet |
| b | Peluqueria incidental (oidos, agua, piel) pesa 0,4x si el manto no es intensivo | verbatim peluquera |
| c | En cachorro, salud preventiva x1,5 (domina sobre peluqueria) | AAHA/WSAVA; verbatim vet |

## 4. Before / after sobre los casos problematicos

| Caso | Antes | Despues | Alineado con experta |
|---|---|---|---|
| Teckel reactivo con ansiedad | Guarderia | Entrenamiento | Si |
| Cachorro bodeguero | Peluqueria | Salud preventiva | Si |
| Teckel pelo corto | Peluqueria | Salud preventiva | Si |
| Podenco senior con ansiedad | Guarderia | Hotel | Parcial (sigue siendo alojamiento) |
| Boxer pelo corto | Guarderia | Guarderia | No (pendiente) |

**4 de 6 casos** se mueven hacia la recomendacion que pedian las expertas, sin
romper Capa 1 (coverage 100%) ni los tests.

## 5. Cierre del bucle y limitaciones residuales

El bucle evaluar, analizar, corregir, re-evaluar queda **cerrado**: el sistema
refinado se re-evaluo sobre los 96 perros reales y las dos expertas independientes
lo validan (AC2 0,80; 90% de recomendaciones apropiadas). Limitaciones residuales:

- El ajuste (a) penaliza guarderia pero **no hotel**: el Podenco ansioso migro a
  Hotel, que tambien es alojamiento. Siguiente iteracion: extender la penalizacion
  conductual a hotel y enrutar a Entrenamiento o etologia.
- El Boxer (braquicefalo, alta energia) sigue en Guarderia; requiere afinar el
  peso de la energia frente al foco en salud que pedia la experta.
- La revision de sentido comun de la autora mantiene un umbral mas estricto; se
  reporta por separado y no entra en el acuerdo experto de referencia.
