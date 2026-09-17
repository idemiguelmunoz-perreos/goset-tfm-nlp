# Evaluación,  Componente A

> **Datos reales transcritos de cartillas de perros colaboradores (n=353), aportados por sus duenos.** La extracción se evalúa sobre la información real de la cartilla aportada por los dueños: valida la mecanica del pipeline y compara los metodos sobre entradas identicas.

Documentos: 353

| Método | macro F1 | exact match | hallucination | null handling | latencia (ms) |
|---|---|---|---|---|---|
| regex (baseline) | 0.7055 | 0.0 | 0.0 | 1.0 | 0.009 |
| LLM zero shot | 0.6248 | 0.0113 | 0.0 | 1.0 | 1744.662 |
| LLM few shot | 0.6258 | 0.0142 | 0.0 | 1.0 | 3436.979 |
| structured outputs (propuesto) | 0.8852 | 0.3711 | 0.0 | 1.0 | 4011.453 |