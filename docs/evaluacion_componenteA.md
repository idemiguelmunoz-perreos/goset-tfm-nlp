# Evaluación — Componente A

> **Datos reales transcritos de cartillas de perros colaboradores (n=353), aportados por sus duenos.** No se dispuso de los documentos originales (fotos/escaneos), por lo que la extraccion se evalua sobre texto de cartilla generado a partir de los registros reales: valida la mecanica del pipeline y compara los metodos sobre entradas identicas. La evaluacion de la extraccion sobre imagenes de cartilla reales queda pendiente.

Documentos: 60

| Método | macro-F1 | exact-match | hallucination | null-handling | latencia (ms) |
|---|---|---|---|---|---|
| regex (baseline) | 0.691 | 0.0 | 0.0 | 1.0 | 0.009 |
| LLM zero-shot | 0.625 | 0.0 | 0.0 | 1.0 | 1718.527 |
| LLM few-shot | 0.625 | 0.0 | 0.0 | 1.0 | 1648.584 |
| structured outputs (propuesto) | 0.8525 | 0.2833 | 0.0 | 1.0 | 1882.524 |