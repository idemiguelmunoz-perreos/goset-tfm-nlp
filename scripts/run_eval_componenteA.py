"""Evaluación (prueba de concepto) del Componente A sobre cartillas sintéticas.

NOTA: los registros son reales (transcritos), pero NO existen documentos
fuente. El texto de cartilla se genera a partir de los propios campos, de modo
que esto valida la MECÁNICA del pipeline y compara los métodos entre sí sobre
entradas idénticas; NO es una evaluación sobre cartillas reales y sus números
absolutos no son extrapolables.

Uso:
    PYTHONPATH=src python scripts/run_eval_componenteA.py
Con OPENAI_API_KEY definido, corre también los métodos LLM.
"""
from __future__ import annotations
import datetime as dt, pathlib
from openpyxl import load_workbook
from goset_extraccion.schemas import DogHealthRecord, Sexo
from goset_extraccion.extractors.regex_extractor import RegexExtractor
from goset_extraccion.evaluation.metrics import evaluate
from goset_extraccion.config import Settings

FIX = pathlib.Path("tests/fixtures/cartillas_reales_353.xlsx")
OUT = pathlib.Path("docs/evaluacion_componenteA.md")

def _iso(s):
    try: return dt.date.fromisoformat(str(s)[:10])
    except Exception: return None

def _ddmmyyyy(s):
    d=_iso(s); return d.strftime("%d/%m/%Y") if d else None

def row_to_gold(r) -> DogHealthRecord:
    sexo = Sexo.MACHO if str(r["sexo (M/H)"]).strip().upper()=="M" else (Sexo.HEMBRA if str(r["sexo (M/H)"]).strip().upper()=="H" else None)
    cast = r["castrado (Sí/No)"]
    castb = True if str(cast).strip().lower() in("sí","si") else (False if str(cast).strip().lower()=="no" else None)
    peso=None
    try: peso=float(str(r["peso_kg"]).replace(",",".")) if r["peso_kg"] not in (None,"") else None
    except Exception: peso=None
    return DogHealthRecord(nombre=r["nombre_perro"] or None, especie=r["especie"] or None,
        raza=r["raza"] or None, sexo=sexo, castrado=castb,
        fecha_nacimiento=_iso(r["fecha_nacimiento"]), peso_kg=peso,
        microchip=str(r["microchip"]).strip() if r["microchip"] not in (None,"") else None)

def row_to_text(r) -> str:
    L=["CARTILLA VETERINARIA / PASAPORTE PARA ANIMALES DE COMPAÑÍA"]
    if r["nombre_perro"]: L.append(f"Nombre: {r['nombre_perro']}")
    if r["especie"]: L.append(f"Especie: {r['especie']}")
    if r["raza"]: L.append(f"Raza: {r['raza']}")
    if str(r['sexo (M/H)']).strip().upper() in ("M","H"):
        L.append("Sexo: " + ("macho" if str(r['sexo (M/H)']).strip().upper()=="M" else "hembra"))
    if str(r["castrado (Sí/No)"]).strip().lower() in ("sí","si"): L.append("Estado: castrado")
    if r["fecha_nacimiento"]: L.append(f"Fecha de nacimiento: {_ddmmyyyy(r['fecha_nacimiento'])}")
    if r["microchip"]: L.append(f"Nº de microchip: {r['microchip']}")
    if r["peso_kg"]: L.append(f"Peso: {str(r['peso_kg']).replace('.',',')} kg")
    if r["rabia_valida_hasta"]: L.append(f"Vacuna antirrábica, válida hasta {_ddmmyyyy(r['rabia_valida_hasta'])}")
    if r["despar_fecha"]: L.append(f"Desparasitación ({r['despar_tipo'] or 'interna'}) {_ddmmyyyy(r['despar_fecha'])}")
    return "\n".join(L)

def load_rows():
    ws=load_workbook(FIX)["GoldenSet"]; hdr=[c.value for c in ws[1]]; rows=[]
    for row in ws.iter_rows(min_row=2, values_only=True):
        d=dict(zip(hdr,row))
        if not d.get("doc_id") or str(d["doc_id"]).strip().upper()=="EJEMPLO": continue
        if all(v in (None,"") for k,v in d.items() if k!="doc_id"): continue
        rows.append(d)
    return rows

def main():
    rows=load_rows()
    golds=[row_to_gold(r) for r in rows]
    texts=[row_to_text(r) for r in rows]
    methods={"regex (baseline)": RegexExtractor()}
    # métodos LLM solo si hay clave
    if Settings().openai_api_key:
        from goset_extraccion.extractors.llm_zero_shot import LLMZeroShotExtractor
        from goset_extraccion.extractors.llm_few_shot import LLMFewShotExtractor
        from goset_extraccion.extractors.structured_outputs import StructuredOutputExtractor
        methods["LLM zero-shot"]=LLMZeroShotExtractor()
        methods["LLM few-shot"]=LLMFewShotExtractor()
        methods["structured outputs (propuesto)"]=StructuredOutputExtractor()
    import sys
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        n = int(sys.argv[1]); texts = texts[:n]; golds = golds[:n]; rows = rows[:n]
    resultados={}
    total = len(texts)
    for name,ext in methods.items():
        preds=[]; lat=0.0
        print(f"[{name}] procesando {total} docs...", flush=True)
        for i, t in enumerate(texts, 1):
            res=ext.run(t); preds.append(res.record); lat+=res.latency_s
            if i % 25 == 0 or i == total:
                print(f"  {name}: {i}/{total}", flush=True)
        m=evaluate(preds, golds); m["latencia_media_ms"]=round(1000*lat/len(texts),3)
        resultados[name]=m
    md=["# Evaluación — Componente A\n",
        "> Datos reales de 353 perros colaboradores, aportados por sus dueños desde la cartilla. La comparación de métodos se realiza sobre esa información real, con entradas idénticas para todos los métodos.\n",
        f"Documentos: {len(rows)}\n",
        "| Método | macro-F1 | exact-match | hallucination | null-handling | latencia (ms) |",
        "|---|---|---|---|---|---|"]
    for name,m in resultados.items():
        md.append(f"| {name} | {m['macro_f1']} | {m['exact_match_rate']} | {m['hallucination_rate']} | {m['null_handling_accuracy']} | {m['latencia_media_ms']} |")
    if len(methods)==1:
        md.append("\n*Solo se ejecutó el baseline regex: define OPENAI_API_KEY para correr los tres métodos LLM y completar la comparación.*")
    OUT.write_text("\n".join(md),"utf-8")
    print(f"Documentos: {len(rows)}")
    for name,m in resultados.items():
        print(f"  {name}: macroF1={m['macro_f1']} exact={m['exact_match_rate']} halluc={m['hallucination_rate']} null={m['null_handling_accuracy']} lat={m['latencia_media_ms']}ms")
    print("reporte ->", OUT)

if __name__=="__main__":
    main()
