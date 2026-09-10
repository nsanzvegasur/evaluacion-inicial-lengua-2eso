import csv
import io
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path

import streamlit.components.v1 as components

import pandas as pd
import streamlit as st
from openpyxl import Workbook

from examen2ESO import EXAMEN
from analytics import radar_chart, comparativa, generar_perfil

TAB_MONITOR = components.declare_component("tab_monitor", path=str(Path(__file__).parent / "tab_monitor"))

st.set_page_config(
    page_title="Evaluación Inicial Lengua 2.º ESO",
    page_icon="📚",
    layout="centered",
)

CSV_FILE = "results.csv"

if "examen_enviado" not in st.session_state:
    st.session_state.examen_enviado = False

if "resultado_fila" not in st.session_state:
    st.session_state.resultado_fila = None

if "resultado_respuestas" not in st.session_state:
    st.session_state.resultado_respuestas = None

if "resultado_perfil" not in st.session_state:
    st.session_state.resultado_perfil = None

if "resultado_excel" not in st.session_state:
    st.session_state.resultado_excel = None

if "resultado_csv" not in st.session_state:
    st.session_state.resultado_csv = None

if "cambios_pestana" not in st.session_state:
    st.session_state.cambios_pestana = 0

EXAM = EXAMEN["2ESO"]

PESOS = {
    "comprension": 2.0,
    "morfologia": 2.5,
    "semantica": 1.0,
    "textos": 1.5,
    "literatura": 2.0,
    "sintaxis": 1.0,
}

NOMBRES = {
    "comprension": "Comprensión",
    "morfologia": "Morfología",
    "semantica": "Semántica",
    "textos": "Textos",
    "literatura": "Literatura",
    "sintaxis": "Sintaxis",
}


def normalizar(valor):
    if valor is None:
        return ""
    texto = str(valor).strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def lista_normalizada(valor):
    if valor is None:
        return []
    texto = str(valor).strip()
    if not texto:
        return []
    return [normalizar(x) for x in re.split(r"[,;\n]+", texto) if normalizar(x)]


def exacta(valor, *alternativas):
    v = normalizar(valor)
    return bool(v) and any(v == normalizar(x) for x in alternativas)


def contiene(valor, *alternativas):
    v = normalizar(valor)
    return bool(v) and any(normalizar(x) in v for x in alternativas)


def repartir_por_criterios(respuesta, criterios):
    texto = normalizar(respuesta)
    if not texto or not criterios:
        return 0.0
    aciertos = sum(1 for grupo in criterios if any(normalizar(x) in texto for x in grupo))
    return aciertos / len(criterios)


def corregir(res):
    p = {k: 0.0 for k in PESOS}

    p["comprension"] += 0.30 * (1 if contiene(res.get("c1", ""), "tren", "vagon", "vagón", "estacion", "estación", "ciudad") else 0)

    personajes = lista_normalizada(res.get("c2", ""))
    tiene_viajero = any(x in {"hombre", "hombre joven", "joven", "viajero", "viajero joven"} or "hombre" in x or "viajero" in x for x in personajes)
    tiene_anciana = any("anciana" in x for x in personajes)
    p["comprension"] += 0.35 * ((int(tiene_viajero) + int(tiene_anciana)) / 2)
    p["comprension"] += 0.35 * (1 if contiene(res.get("c3", ""), "madrugada", "amanecer", "temprano", "noche") else 0)

    acciones_respuesta = lista_normalizada(res.get("c4", ""))
    acciones_validas = {
        "mirar": {"mirar", "miraba"},
        "sujetar": {"sujetar", "sujetaba"},
        "dormir": {"dormir", "dormia"},
        "llegar": {"llegar", "llego"},
        "bajar": {"bajar", "bajo"},
        "respirar": {"respirar", "respiro"},
        "caminar": {"caminar", "camino"},
        "detenerse": {"detenerse", "se detenia"},
        "avanzar": {"avanzar", "avanzaba"},
        "recorrer": {"recorrer", "recorria"},
        "cubrir": {"cubrir", "cubria"},
        "ver": {"ver", "veia"},
        "salir": {"salir", "salio"},
        "sentir": {"sentir", "sintio"},
    }
    acciones_encontradas = set()
    for respuesta in acciones_respuesta:
        for infinitivo, formas in acciones_validas.items():
            if respuesta in {normalizar(forma) for forma in formas}:
                acciones_encontradas.add(infinitivo)
                break
    p["comprension"] += min(len(acciones_encontradas), 3) * (0.35 / 3)
    p["comprension"] = min(p["comprension"], 2.0)

    claves = {
        "m1": {"lexema": ("silenci", "silenc"), "morfemas": ("o",), "estructura": ("simple",), "categoria": ("sustantivo", "comun", "común", "abstracto", "masculino", "singular"), "vi": ("variable", "v")},
        "m2": {"lexema": ("lent",), "morfemas": ("a", "mente", "-mente"), "estructura": ("derivada", "derivacion", "derivación"), "categoria": ("adverbio", "modo"), "vi": ("invariable", "i")},
        "m3": {"lexema": ("conoc",), "morfemas": ("des", "ido", "-ido"), "estructura": ("derivada", "derivacion", "derivación"), "categoria": ("adjetivo", "calificativo", "masculino", "singular"), "vi": ("variable", "v")},
        "m4": {"lexema": ("mochil",), "morfemas": ("a", "s", "-a", "-s"), "estructura": ("simple",), "categoria": ("sustantivo", "comun", "común", "concreto", "femenino", "plural"), "vi": ("variable", "v")},
    }
    campos_peso = {"lexema": 0.10, "morfemas": 0.10, "estructura": 0.10, "categoria": 0.15, "vi": 0.05}
    for mid, campo in claves.items():
        for nombre, alternativas in campo.items():
            valor = res.get(f"{mid}_{nombre}", "")
            v = normalizar(valor)
            if nombre == "lexema":
                ok = any(normalizar(a) in v for a in alternativas) and len(v) >= 3
            elif nombre == "morfemas":
                partes = lista_normalizada(valor)
                if mid == "m1": ok = "o" in partes or "o" in v
                elif mid == "m2": ok = "mente" in v
                elif mid == "m3": ok = "des" in v and ("ido" in v or "id" in v)
                else: ok = "s" in partes and ("a" in partes or "a" in v)
            elif nombre == "categoria":
                if mid == "m1": ok = all(x in v for x in ["sustantivo", "masculino", "singular"])
                elif mid == "m2": ok = "adverbio" in v
                elif mid == "m3": ok = all(x in v for x in ["adjetivo", "masculino", "singular"])
                else: ok = all(x in v for x in ["sustantivo", "femenino", "plural"])
            else:
                ok = any(v == normalizar(a) for a in alternativas)
            if ok: p["morfologia"] += campos_peso[nombre]
    for k, correcta in {"dp1": "determinante", "dp2": "determinante", "dp3": "pronombre"}.items():
        if exacta(res.get(k, ""), correcta): p["morfologia"] += 0.1667
    p["morfologia"] = min(round(p["morfologia"], 4), 2.5)

    sem_correctas = {"s1": ("antonimia",), "s2": ("campo semantico", "campo semántico"), "s3": ("polisemia",), "s4": ("meronimia",), "s5": ("hiponimos", "hipónimos", "hiponimia")}
    for k, alternativas in sem_correctas.items():
        if exacta(res.get(k, ""), *alternativas): p["semantica"] += 0.20

    tipos = {"t1": ("instructivo", "instruccional"), "t2": ("expositivo",), "t3": ("argumentativo", "persuasivo")}
    for k, alternativas in tipos.items():
        if exacta(res.get(k, ""), *alternativas): p["textos"] += 0.3333
    interlocutores = lista_normalizada(res.get("d1", ""))
    if any("lucia" in x for x in interlocutores) and any("carlos" in x for x in interlocutores): p["textos"] += 0.10
    if exacta(res.get("d2", ""), "6", "seis", "6 intervenciones", "seis intervenciones"): p["textos"] += 0.10
    ind = normalizar(res.get("d3", ""))
    if any(v in ind for v in ["dijo", "respondio", "contesto", "afirmo", "explico"]): p["textos"] += 0.10
    if "que" in ind: p["textos"] += 0.10
    if any(v in ind for v in ["dia anterior", "dia antes"]): p["textos"] += 0.05
    if any(v in ind for v in ["habia hecho", "habia realizado"]): p["textos"] += 0.05

    if exacta(res.get("l1", ""), "4"): p["literatura"] += 0.30
    if exacta(res.get("l2", ""), "arte mayor"): p["literatura"] += 0.30
    met = re.sub(r"[,;]+", " ", str(res.get("l3", "")).strip())
    met = re.sub(r"\s+", " ", met).strip()
    if met == "10A 10B 10A 10B": p["literatura"] += 0.35
    if exacta(res.get("l4", ""), "consonante"): p["literatura"] += 0.35
    sinal = normalizar(res.get("l5", ""))
    if any(x in sinal for x in ["sobre el", "junto al"]) and any(x in sinal for x in ["sinalefa", "se unen", "se unen las vocales", "union", "unen"]): p["literatura"] += 0.35
    pers = normalizar(res.get("l6", ""))
    if "viento susurra" in pers and any(x in pers for x in ["persona", "humana", "humano", "accion humana", "personificacion"]): p["literatura"] += 0.35

    # MODALIDADES ORACIONALES: «exhortativa» se elimina porque en este examen
    # se trabaja como equivalente de la modalidad imperativa.
    syn = {
        "x1": ("frase",),
        "x2": ("oracion", "oración"),
        "x3": ("frase",),
        "x4": ("frase",),
        "x5": ("oracion", "oración"),
        "x6": ("interrogativa",),
        "x7": ("desiderativa",),
        "x8": ("exclamativa",),
        "x9": ("enunciativa",),
        "x10": ("imperativa",)
    }
    for k, alternativas in syn.items():
        if exacta(res.get(k, ""), *alternativas): p["sintaxis"] += 0.10
    p["sintaxis"] = min(round(p["sintaxis"], 4), 1.0)

    total = round(sum(p.values()) * 0.9, 2)
    return p, total


def detectar_ortografia(respuestas):
    errores = {"sustantibo", "haver", "hechar", "aver", "aora", "havia", "bamos", "llendo", "dijistes", "hicistes", "estava", "tubieron", "tubo"}
    encontrados = set()
    for respuesta in respuestas:
        if not respuesta: continue
        palabras = re.findall(r"\b[\wáéíóúüñ]+\b", str(respuesta).lower(), flags=re.UNICODE)
        for palabra in palabras:
            if palabra in errores: encontrados.add(palabra)
    return len(encontrados), 0


def guardar_csv(fila):
    campos = ["name", "group", "date", "comprension", "morfologia", "semantica", "textos", "literatura", "sintaxis", "nota_sin_faltas", "faltas_ortografia", "faltas_tildes", "descuento_ortografia", "nota_examen_9", "produccion_escrita", "nota_produccion_escrita", "nota_final_10", "cambios_pestana"]
    if os.path.exists(CSV_FILE):
        try: df = pd.read_csv(CSV_FILE)
        except Exception: df = pd.DataFrame(columns=campos)
    else: df = pd.DataFrame(columns=campos)
    for c in campos:
        if c not in df.columns: df[c] = ""
    df = pd.concat([df[campos], pd.DataFrame([{c: fila.get(c, "") for c in campos}])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")


def csv_individual(fila):
    salida = io.StringIO()
    campos = list(fila.keys())
    writer = csv.DictWriter(salida, fieldnames=campos)
    writer.writeheader(); writer.writerow(fila)
    return salida.getvalue().encode("utf-8-sig")


def excel_individual(fila, respuestas, perfil, cambios_pestana=0):
    from openpyxl.styles import Font, Alignment
    wb = Workbook()
    ws = wb.active; ws.title = "Resultado"
    ws["A1"] = "📚 Evaluación inicial de Lengua — 2.º ESO"; ws["A1"].font = Font(bold=True, size=16)
    ws["A3"] = "Alumno"; ws["B3"] = fila["name"]
    ws["A4"] = "Grupo"; ws["B4"] = fila["group"]
    ws["A5"] = "Fecha y hora"; ws["B5"] = fila["date"]
    ws["A6"] = "Cambios de pestaña detectados"; ws["B6"] = cambios_pestana
    ws["A7"] = "NOTA DE ESTA PARTE (SOBRE 9)"; ws["B7"] = fila["nota_examen_9"]
    ws["A8"] = "Nota antes del descuento por ortografía (sobre 9)"; ws["B8"] = fila["nota_sin_faltas"]
    ws["A9"] = "Descuento por ortografía"; ws["B9"] = fila["descuento_ortografia"]
    ws["A10"] = "Producción escrita"; ws["B10"] = fila["produccion_escrita"]
    ws["A11"] = "Nota producción escrita (hasta 1 punto)"; ws["B11"] = fila["nota_produccion_escrita"]
    ws["A12"] = "NOTA FINAL (SOBRE 10)"; ws["B12"] = fila["nota_final_10"]
    ws["A14"] = "RESULTADOS POR ÁREAS"; ws["A14"].font = Font(bold=True)
    fila_excel = 15
    for clave, nombre_area in NOMBRES.items():
        ws.cell(fila_excel, 1).value = nombre_area; ws.cell(fila_excel, 2).value = fila[clave]; fila_excel += 1
    ws[f"A{fila_excel + 1}"] = "PERFIL COMPETENCIAL"; ws[f"A{fila_excel + 1}"].font = Font(bold=True)
    fila_perfil = fila_excel + 2
    for item in perfil:
        ws.cell(fila_perfil, 1).value = item["texto"]; ws.cell(fila_perfil, 1).alignment = Alignment(wrap_text=True, vertical="top"); fila_perfil += 1
    ws.column_dimensions["A"].width = 48; ws.column_dimensions["B"].width = 30
    ws2 = wb.create_sheet("Respuestas")
    ws2["A1"] = "Pregunta"; ws2["B1"] = "Respuesta"; ws2["A1"].font = Font(bold=True); ws2["B1"].font = Font(bold=True)
    fila_respuesta = 2
    for pregunta, respuesta in respuestas.items():
        ws2.cell(fila_respuesta, 1).value = pregunta; ws2.cell(fila_respuesta, 2).value = str(respuesta); ws2.cell(fila_respuesta, 2).alignment = Alignment(wrap_text=True, vertical="top"); fila_respuesta += 1
    ws2.column_dimensions["A"].width = 25; ws2.column_dimensions["B"].width = 80
    salida = io.BytesIO(); wb.save(salida); salida.seek(0)
    return salida.getvalue()


def safe_read_results():
    if not os.path.exists(CSV_FILE): return pd.DataFrame(columns=["name", "group", "date", "comprension", "morfologia", "semantica", "textos", "literatura", "sintaxis", "nota_sin_faltas", "faltas_ortografia", "faltas_tildes", "descuento_ortografia", "nota_final"])
    try: return pd.read_csv(CSV_FILE)
    except Exception: return pd.DataFrame()


def alumno_ya_realizo_examen(nombre, grupo):
    df = safe_read_results()
    if df.empty or "name" not in df.columns or "group" not in df.columns: return False
    return (df["name"].astype(str).map(normalizar).eq(normalizar(nombre)) & df["group"].astype(str).eq(grupo)).any()


if st.session_state.examen_enviado:
    fila = st.session_state.resultado_fila; respuestas = st.session_state.resultado_respuestas; perfil = st.session_state.resultado_perfil
    st.title("📊 Resultados de tu evaluación")
    st.success("✅ Esta parte de la evaluación se ha enviado correctamente.")
    st.info("✍️ **IMPORTANTE:** Has terminado esta parte de la evaluación. Esta prueba automática vale **9 puntos**. Ahora debes continuar con la **producción escrita**, que se corregirá aparte y supondrá hasta **1 punto adicional**.")
    st.write(f"**Fecha y hora:** {fila['date']}"); st.metric("Nota de esta parte", f"{fila['nota_examen_9']:.2f} / 9")
    st.write(f"**Nota antes del descuento por ortografía:** {fila['nota_sin_faltas']:.2f} / 9")
    if int(fila.get("cambios_pestana", 0) or 0) > 0:
        cambios = int(fila.get("cambios_pestana", 0) or 0)
        st.warning(f"⚠️ Durante el examen se detectaron {cambios} cambios de pestaña o salida de la ventana.")
    st.divider(); st.subheader("📚 Resultados por áreas")
    columnas = st.columns(2)
    for i, (clave, nombre_area) in enumerate(NOMBRES.items()):
        with columnas[i % 2]: st.metric(nombre_area, f"{fila[clave]:.2f} / 10")
    st.divider(); st.subheader("📝 Perfil de aprendizaje")
    for item in perfil: st.write(f"• {item['texto']}")
    st.divider(); st.subheader("📥 Descargar resultados")
    st.download_button("📊 Descargar Excel", data=st.session_state.resultado_excel, file_name=f"resultado_{fila['name']}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    st.divider(); st.subheader("📊 Comparación con la clase")
    df = safe_read_results()
    if not df.empty and "group" in df.columns:
        df_clase = df[df["group"].astype(str) == str(fila["group"])].copy()
        if not df_clase.empty:
            df_anon = df_clase.copy()
            df_anon["name"] = [f"Alumno {i + 1}" for i in range(len(df_anon))]
            try:
                figura = comparativa(df_anon)
                if figura is not None:
                    st.caption("Se muestra la nota de la prueba automática, sobre 9 puntos.")
                    st.plotly_chart(figura, use_container_width=True)
                    valores_clase = pd.to_numeric(df_clase["nota_examen_9"], errors="coerce").dropna()
                    if not valores_clase.empty:
                        media_clase = float(valores_clase.mean())
                        diferencia = float(fila["nota_examen_9"]) - media_clase
                        c1, c2 = st.columns(2)
                        c1.metric("Media de la clase", f"{media_clase:.2f} / 9")
                        c2.metric("Tu diferencia respecto a la media", f"{diferencia:+.2f}")
                else:
                    st.info("Todavía no hay notas suficientes para mostrar la comparativa.")
            except Exception:
                st.info("La comparativa no está disponible en este momento.")
        else:
            st.info("Todavía no hay resultados de tu grupo para realizar la comparativa.")
    else:
        st.info("Todavía no hay resultados de tu grupo para realizar la comparativa.")
    st.success("Tu evaluación está lista para descargar y entregar en Classroom."); st.stop()

st.title("📚 Evaluación inicial de Lengua — 2.º ESO"); st.caption("Lengua Castellana y Literatura · Curso 2026-2027")

# Monitor de cambios de pestaña/ventana durante el examen.
evento_pestana = TAB_MONITOR(key="monitor_pestana")
if isinstance(evento_pestana, dict):
    try:
        nuevo = int(evento_pestana.get("count", 0))
        if nuevo > st.session_state.cambios_pestana:
            st.session_state.cambios_pestana = nuevo
    except (TypeError, ValueError):
        pass

if st.session_state.cambios_pestana:
    if st.session_state.cambios_pestana >= 3:
        st.error("🚨 Se han detectado 3 cambios de pestaña o salida de la ventana. El examen se enviará automáticamente.")
    else:
        restante = 3 - st.session_state.cambios_pestana
        st.warning(f"⚠️ Cambio de pestaña detectado ({st.session_state.cambios_pestana}). Evita salir del examen. Tras {restante} cambio(s) más, se enviará automáticamente.")
nombre = st.text_input("Nombre y apellidos")
grupo = st.selectbox("Grupo", ["", "2º A", "2º B", "2º C", "2º D"])
examen_bloqueado = False
if nombre.strip() and grupo: examen_bloqueado = alumno_ya_realizo_examen(nombre, grupo)
if examen_bloqueado:
    st.warning("⚠️ Este examen ya ha sido realizado con este nombre y grupo. No puedes volver a enviarlo."); st.stop()

with st.form("examen"):
    respuestas = {}
    st.header("1. Comprensión lectora — 2 puntos")
    st.write(EXAM["comprension"]["texto"])
    respuestas["c1"] = st.text_input("1.1. Lugar")
    respuestas["c2"] = st.text_input("1.1. Personajes, separados por comas", help="Ejemplo: hombre joven, anciana")
    respuestas["c3"] = st.text_input("1.1. Momento del día")
    respuestas["c4"] = st.text_input("1.2. Tres acciones, separadas por comas", help="Ejemplo: miraba, bajó, caminó")
    st.divider(); st.header("2. Morfología y categorías gramaticales — 2,5 puntos")
    for palabra in EXAM["morfologia"]:
        st.subheader(palabra["palabra"])
        for campo in palabra["campos"]:
            clave = campo.lower().replace(" ", "_").replace("/", "_"); key = f"{palabra['id']}_{clave}"
            if campo == "Estructura": valor = st.selectbox(f"{palabra['palabra']} → {campo}", ["", "simple", "compuesta", "derivada", "parasintética"], key=key)
            elif campo == "V/I": valor = st.selectbox(f"{palabra['palabra']} → {campo}", ["", "variable", "invariable"], key=key)
            elif campo == "Categoría gramatical": valor = st.text_input(f"{palabra['palabra']} → {campo}", key=key, help="Indica categoría y rasgos principales.")
            else: valor = st.text_input(f"{palabra['palabra']} → {campo}", key=key, help="Si hay varios morfemas, sepáralos con comas. Ejemplo: in, s" if campo == "Morfemas" else None)
            respuestas[f"{palabra['id']}_{clave}"] = valor
    st.subheader("2.2. Determinantes y pronombres — incluido en Morfología")
    for q in EXAM["determinantes_pronombres"]:
        respuestas[q["id"]] = st.selectbox(q["frase"] + " — " + q["enunciado"], ["", "determinante", "pronombre"], key=q["id"])
    st.divider(); st.header("3. Semántica — 1 punto")
    opciones_sem = ["", "antonimia", "sinonimia", "campo semántico", "polisemia", "homonimia", "meronimia", "hipónimos", "hiperónimo"]
    for q in EXAM["semantica"]: respuestas[q["id"]] = st.selectbox(q["enunciado"], opciones_sem, key=q["id"])
    st.divider(); st.header("4. Textos y diálogo — 1,5 puntos")
    st.write(EXAM["textos"]["enunciado"])
    for letra, texto in EXAM["textos"]["textos"].items(): st.markdown(f"**Texto {letra}:** {texto}")
    opciones_texto = ["", "instructivo", "narrativo", "descriptivo", "expositivo", "argumentativo", "dialogado"]
    for q in EXAM["textos"]["preguntas"]: respuestas[q["id"]] = st.selectbox(q["enunciado"], opciones_texto, key=q["id"])
    st.subheader("Diálogo")
    for linea in EXAM["dialogo"]["texto"].splitlines(): st.markdown(f"**{linea}**")
    respuestas["d1"] = st.text_input(EXAM["dialogo"]["preguntas"][0]["enunciado"], help="Escribe los dos personajes separados por comas.")
    respuestas["d2"] = st.number_input(EXAM["dialogo"]["preguntas"][1]["enunciado"], min_value=0, max_value=20, value=0, step=1)
    respuestas["d2"] = str(int(respuestas["d2"]))
    respuestas["d3"] = st.text_area(EXAM["dialogo"]["preguntas"][2]["enunciado"])
    st.divider(); st.header("5. Literatura — 2 puntos")
    st.markdown(EXAM["literatura"]["poema"].replace("\n", "  \n"))
    respuestas["l1"] = st.selectbox(EXAM["literatura"]["preguntas"][0]["enunciado"], ["", "2", "3", "4", "5", "6", "7", "8"], key="l1")
    respuestas["l2"] = st.selectbox(EXAM["literatura"]["preguntas"][1]["enunciado"], ["", "arte menor", "arte mayor"], key="l2")
    respuestas["l3"] = st.text_input(EXAM["literatura"]["preguntas"][2]["enunciado"], help="Ejemplo: 14A 11B 14B 10A. Puedes separar los grupos con espacios o comas")
    respuestas["l4"] = st.selectbox(EXAM["literatura"]["preguntas"][3]["enunciado"], ["", "asonante", "consonante"], key="l4")
    respuestas["l5"] = st.text_input(EXAM["literatura"]["preguntas"][4]["enunciado"])
    respuestas["l6"] = st.text_area(EXAM["literatura"]["preguntas"][5]["enunciado"])
    st.divider(); st.header("6. Sintaxis — 1 punto")
    st.subheader("6.1. Frase u oración")
    for q in EXAM["sintaxis"][:5]: respuestas[q["id"]] = st.selectbox(f"**{q['frase']}** → {q['enunciado']}", ["", "frase", "oración"], key=q["id"])
    st.subheader("6.2. Modalidad oracional")
    for q in EXAM["sintaxis"][5:]: respuestas[q["id"]] = st.selectbox(f"**{q['frase']}** → {q['enunciado']}", ["", "enunciativa", "interrogativa", "exclamativa", "desiderativa", "imperativa"], key=q["id"])
    enviar = st.form_submit_button("📤 ENVIAR EXAMEN", use_container_width=True)

if enviar or st.session_state.cambios_pestana >= 3:
    if not nombre.strip(): st.error("Escribe tu nombre y apellidos."); st.stop()
    if not grupo: st.error("Selecciona tu grupo."); st.stop()
    puntos, nota_sin_faltas = corregir(respuestas)
    todas_respuestas = [v for v in respuestas.values() if isinstance(v, str)]
    faltas_ortografia, faltas_tildes = detectar_ortografia(todas_respuestas)
    descuento = round(min(2.0, faltas_ortografia * 0.20 + faltas_tildes * 0.10), 2)
    nota_final = round(max(0.0, nota_sin_faltas - descuento), 2)
    scores = {clave: round(puntos[clave] / PESOS[clave] * 10, 2) for clave in PESOS}
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fila = {"name": nombre.strip(), "group": grupo, "date": fecha_hora, **scores, "nota_sin_faltas": round(nota_sin_faltas, 2), "faltas_ortografia": faltas_ortografia, "faltas_tildes": faltas_tildes, "descuento_ortografia": descuento, "nota_examen_9": nota_final, "produccion_escrita": "Pendiente", "nota_produccion_escrita": "", "nota_final_10": "", "cambios_pestana": st.session_state.cambios_pestana}
    guardar_csv(fila)
    perfil = generar_perfil(scores)
    st.session_state.examen_enviado = True
    st.session_state.resultado_fila = fila
    st.session_state.resultado_respuestas = respuestas
    st.session_state.resultado_perfil = perfil
    st.session_state.resultado_csv = csv_individual(fila)
    st.session_state.resultado_excel = excel_individual(fila, respuestas, perfil, st.session_state.cambios_pestana)
    st.rerun()
