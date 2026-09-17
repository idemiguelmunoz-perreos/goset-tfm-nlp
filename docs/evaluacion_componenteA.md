# EVALUACION: COMPONENTE A (EXTRACCION NLP)

> Datos reales de 353 perros colaboradores: la informacion de cartilla que
> aportaron sus duenos (senalamiento, peso, microchip, vacunas, desparasitaciones).
> La evaluacion mide la extraccion estructurada de esa informacion a un esquema
> Pydantic y compara los cuatro metodos sobre entradas identicas.

## Nota metodologica (alcance de la prueba)

El objetivo del Componente A es convertir la informacion de cartilla aportada por
el dueno en un registro estructurado y validado, distinguiendo lo ausente de lo
inventado. La comparacion se realiza sobre el texto de esa informacion, identico
para los cuatro metodos, de modo que las diferencias miden capacidad de parseo
estructurado, no calidad de digitalizacion. No es una prueba de lectura de
documentos degradados (manuscritos, escaneos); esa extension queda como trabajo
futuro y no se reclama aqui.

## Resultados sobre 353 registros reales

| Metodo | macro F1 | exact match | hallucination | null handling | latencia (ms) | coste (USD/peticion) |
|---|---|---|---|---|---|---|
| regex (baseline) | 0,706 | 0,00 | 0,00 | 1,00 | 0,009 | 0,000000 |
| LLM zero-shot | 0,625 | 0,011 | 0,00 | 1,00 | 1744,7 | 0,000053 |
| LLM few-shot | 0,626 | 0,014 | 0,00 | 1,00 | 3437,0 | 0,000052 |
| structured outputs (propuesto) | 0,885 | 0,371 | 0,00 | 1,00 | 4011,5 | 0,000174 |

Coste estimado a precios de lista de gpt-4o-mini (entrada 0,15 y salida 0,60 USD
por millon de tokens), contando tokens de entrada y salida por peticion (estimador
aproximado de 4 caracteres por token). El baseline de regex no consume API.

## Lectura

El metodo propuesto lidera con claridad: **macro F1 0,885**, frente a 0,706 del
regex y ~0,63 de los LLM sin esquema. La **tasa de alucinacion es 0,00 en los
cuatro metodos** y el **null-handling es perfecto (1,00)**: ninguno inventa datos
ausentes, la propiedad critica en un documento clinico.

**Por que el exact-match es 0,371 pese al F1 0,885.** El exact-match exige que el
registro completo coincida campo a campo. La mayor parte de las discrepancias son
de formato y normalizacion (fechas equivalentes, mayusculas, sinonimos de raza,
unidades de peso), no errores de contenido: el F1 por campo, que tolera esas
equivalencias, es alto. El exact-match se reporta como cota inferior estricta.

**Trade-off coste/calidad/latencia.** El metodo propuesto cuesta ~3x el zero-shot
por peticion (envia el esquema en cada llamada) y es el mas lento (~4 s/documento),
a cambio de +0,26 de macro F1 y del exact-match mas alto. En terminos absolutos el
coste es marginal (~0,00017 USD/documento); la eleccion es de calidad, no de gasto.
