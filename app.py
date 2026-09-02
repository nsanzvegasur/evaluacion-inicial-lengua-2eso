import csv
import io
import os
import re
import unicodedata
from datetime import datetime

import pandas as pd
import streamlit as st
import language_tool_python

from examen2ESO import EXAMEN

st.set_page_config(
    page_title="Evaluación Inicial Lengua 2.º ESO",
    page_icon="📚",
    layout="centered"
)

CSV_FILE = "results.csv"


def normalizar(valor):
    if valor is None:
        return ""
    texto = str(valor).strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def lista_respuestas(valor):
    if valor is None:
        return []
    partes = re.split(r"[,;\n]+", str(valor))
    return [normalizar(x) for x in partes if normalizar(x)]


def exacta(respuesta, correcta):
    return normalizar(respuesta) == normalizar(correcta)


def contiene(respuesta, criterios):
    texto = normalizar(respuesta)
    return any(normalizar(c) in texto for c in criterios) if texto else False


def corregir_lista(respuesta, criterios):
    respuestas = lista_respuestas(respuesta)
    criterios = [normalizar(c) for c in criterios]
    encontrados = set()
    for item in respuestas:
        for criterio in criterios:
            if item == criterio or item in criterio or criterio in item:
                encontrados.add(criterio)
    return len(encontrados) / len(criterios) if criterios else 0.0


def corregir_estilo_indirecto(respuesta):
    texto = normalizar(respuesta)
    if not texto:
        return 0.0
    criterios = [
        "carlos" in texto,
        any(v in texto for v in ["dijo", "afirmo", "comento", "respondio", "explico"]),
        "que" in texto,
        "habia hecho" in texto or "lo habia hecho" in texto,
        "dia anterior" in texto or "ese dia" in texto or "por la tarde" in texto,
    ]
    return sum(criterios) / len(criterios)


def corregir_examen(respuestas):
    examen = EXAMEN["2ESO"]
    puntos = {k: 0.0 for k in [
        "comprension", "morfologia", "determinantes", "semantica",
        "textos", "literatura", "sintaxis", "dialogo"
    ]}

    # 1. Comprensión = 2 puntos
    acciones_usadas = set()
    for p in examen["comprension"]["preguntas"]:
        respuesta = respuestas.get(p["id"], "")
        pts = float(p["puntos"])
        if p.get("tipo") == "lista":
            puntos["comprension"] += pts * corregir_lista(respuesta, p.get("criterios", []))
        elif p.get("tipo") == "accion":
            r = normalizar(respuesta)
            criterios = [normalizar(c) for c in p.get("criterios", [])]
            if r in criterios and r not in acciones_usadas:
                puntos["comprension"] += pts
                acciones_usadas.add(r)
        elif contiene(respuesta, p.get("criterios", [])):
            puntos["comprension"] += pts

    # 2. Morfología = 2 puntos
    valores_campo = {
        "Lexema": 0.10,
        "Morfemas": 0.10,
        "Estructura de la palabra": 0.10,
        "Categoría gramatical completa": 0.15,
        "V / I": 0.05,
    }
    for palabra in examen["morfologia"]:
        for campo in palabra["campos"]:
            clave = f"{palabra['id']}_{campo}"
            respuesta = respuestas.get(clave, "")
            correctas = palabra["respuestas"].get(campo, [])
            valor = valores_campo[campo]
            if campo in ["Morfemas", "Categoría gramatical completa"]:
                if correctas:
                    texto = normalizar(respuesta)
                    encontrados = sum(1 for c in correctas if normalizar(c) in texto)
                    puntos["morfologia"] += valor * min(1.0, encontrados / len(correctas))
            elif correctas and any(exacta(respuesta, c) for c in correctas):
                puntos["morfologia"] += valor

    # 3. Determinantes/pronombres = 0.5
    for p in examen["determinantes_pronombres"]:
        respuesta = respuestas.get(p["id"], "")
        if exacta(respuesta, p["respuesta"]):
            puntos["determinantes"] += float(p["puntos"])

    # 4. Semántica = 1
    for p in examen["semantica"]:
        if exacta(respuestas.get(p["id"], ""), p["respuesta"]):
            puntos["semantica"] += float(p["puntos"])

    # 5. Textos = 1
    for p in examen["textos"]:
        if exacta(respuestas.get(p["id"], ""), p["respuesta"]):
            puntos["textos"] += float(p["puntos"])

    # 6. Literatura = 2
    for p in examen["literatura"]:
        if p.get("tipo") == "poema":
            continue
        respuesta = respuestas.get(p["id"], "")
        pts = float(p["puntos"])
        tipo = p.get("tipo", "")
        if p["id"] == "l3":
            r = normalizar(respuesta).replace(" ", "").replace(",", "").replace("/", "")
            validas = [p.get("respuesta", "")] + p.get("alternativas", [])
            if any(r == normalizar(v).replace(" ", "").replace(",", "").replace("/", "") for v in validas):
                puntos["literatura"] += pts
        elif tipo in ["sinalefa", "personificacion"]:
            r = normalizar(respuesta)
            validas = [normalizar(x) for x in p.get("respuestas_validas", [])]
            if r in validas:
                puntos["literatura"] += pts
        elif exacta(respuesta, p.get("respuesta", "")):
            puntos["literatura"] += pts

    # 7. Sintaxis = 1
    for p in examen["sintaxis"]:
        if exacta(respuestas.get(p["id"], ""), p["respuesta"]):
            puntos["sintaxis"] += float(p["puntos"])

    # 8. Diálogo = 0.5
    for p in examen["dialogo"]["preguntas"]:
        respuesta = respuestas.get(p["id"], "")
        pts = float(p["puntos"])
        if p.get("tipo") == "lista":
            puntos["dialogo"] += pts * corregir_lista(respuesta, p.get("criterios", []))
        elif p.get("tipo") == "estilo_indirecto":
            puntos["dialogo"] += pts * corregir_estilo_indirecto(respuesta)
        elif exacta(respuesta, p.get("respuesta", "")):
            puntos["dialogo"] += pts

    # Corrección de redondeo para que un máximo perfecto sea 10,00.
    for k in puntos:
        puntos[k] = round(puntos[k], 2)

    nota = round(sum(puntos.values()), 2)
    return puntos, nota


def detectar_ortografia(textos):
    """
    Detecta faltas ortográficas y tildes con LanguageTool en español.
    Solo contamos errores ortográficos (TYPOS) y de tildes/diacríticos
    (DIACRITICS), no errores gramaticales ni de estilo.
    La misma falta repetida se cuenta una sola vez.
    """
    try:
        herramienta = language_tool_python.LanguageToolPublicAPI("es")
    except Exception:
        return 0, 0, 0.0

    errores_vistos = set()
    tildes_vistas = set()

    try:
        for texto in textos:
            if not isinstance(texto, str) or not texto.strip():
                continue

            try:
                coincidencias = herramienta.check(texto)
            except Exception:
                continue

            for match in coincidencias:
                categoria = str(getattr(match, "category", ""))
                rule_id = str(getattr(match, "rule_id", ""))
                mensaje = str(getattr(match, "message", ""))

                # TYPOS = faltas de ortografía como "sustantibo".
                # DIACRITICS = errores de tildes/diacríticos.
                es_tilde = (
                    categoria == "DIACRITICS"
                    or "TILDE" in rule_id.upper()
                    or "ACCENT" in rule_id.upper()
                    or "tilde" in mensaje.lower()
                )

                es_ortografia = (
                    categoria == "TYPOS"
                    or "MORFOLOGIK" in rule_id.upper()
                    or "SPELL" in rule_id.upper()
                    or "SPELLING" in rule_id.upper()
                )

                contexto = str(getattr(match, "sentence", ""))
                offset = int(getattr(match, "offset_in_context", 0))
                longitud = int(getattr(match, "error_length", 0))
                palabra = contexto[offset:offset + longitud].strip().lower()

                clave = (palabra, rule_id, categoria)

                if es_tilde:
                    tildes_vistas.add(clave)
                elif es_ortografia:
                    errores_vistos.add(clave)

    finally:
        try:
            herramienta.close()
        except Exception:
            pass

    faltas = len(errores_vistos)
    faltas_tilde = len(tildes_vistas)

    descuento = min(
        2.0,
        faltas * 0.20 + faltas_tilde * 0.10
    )

    return faltas, faltas_tilde, round(descuento, 2)


def guardar_csv(fila):
    columnas = list(fila.keys())
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
        except Exception:
            df = pd.DataFrame(columns=columnas)
        for c in columnas:
            if c not in df.columns:
                df[c] = ""
        df = pd.concat([df[columnas], pd.DataFrame([fila])], ignore_index=True)
    else:
        df = pd.DataFrame([fila], columns=columnas)
    df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")


def csv_individual(fila):
    salida = io.StringIO()
    writer = csv.DictWriter(salida, fieldnames=list(fila.keys()))
    writer.writeheader()
    writer.writerow(fila)
    return salida.getvalue().encode("utf-8-sig")


st.title("📚 Evaluación Inicial de Lengua")
st.caption("2.º ESO · Lengua Castellana y Literatura · Curso 2026-2027")

if st.session_state.get("enviado", False):
    nombre = st.session_state["nombre"]
    curso = st.session_state["curso"]
    puntos = st.session_state["puntos"]
    nota_inicial = st.session_state["nota_inicial"]
    descuento = st.session_state["descuento"]
    nota_final = st.session_state["nota_final"]
    faltas = st.session_state["faltas"]
    faltas_tilde = st.session_state["faltas_tilde"]
    fila = st.session_state["fila"]

    st.success("✅ Examen enviado correctamente.")
    st.subheader(f"Resultado de {nombre}")

    st.metric("Nota final", f"{nota_final:.2f}/10")

    cols = st.columns(4)
    nombres = [
        ("comprension", "Comprensión"),
        ("morfologia", "Morfología"),
        ("determinantes", "Determinantes y pronombres"),
        ("semantica", "Semántica"),
        ("textos", "Textos y diálogo"),
        ("literatura", "Literatura"),
        ("sintaxis", "Sintaxis"),
    ]
    for i, (clave, titulo) in enumerate(nombres):
        cols[i % 4].metric(titulo, f"{puntos[clave]:.2f}")

    st.write(f"**Nota sin faltas de ortografía:** {nota_inicial:.2f}/10")
    st.write(f"**Descuento por faltas de ortografía:** -{descuento:.2f}")
    st.write(f"**Faltas detectadas:** {faltas} · **Tildes:** {faltas_tilde}")
    st.write(f"**Nota final:** {nota_final:.2f}/10")

    st.info("Textos y diálogo se valoran conjuntamente sobre 10 para identificar el nivel de refuerzo.")

    st.subheader("📥 Descargar resultado")
    st.download_button(
        "⬇️ Descargar mi resultado CSV",
        data=csv_individual(fila),
        file_name=f"resultado_{re.sub(r'[^A-Za-z0-9_-]+', '_', nombre)}.csv",
        mime="text/csv",
        use_container_width=True
    )
    st.stop()

nombre = st.text_input("Nombre y apellidos")
curso = st.selectbox("Grupo", ["", "2º A", "2º B", "2º C", "2º D"])

respuestas = {}

st.header("1. Comprensión lectora")
st.write(EXAMEN["2ESO"]["comprension"]["texto"])
for p in EXAMEN["2ESO"]["comprension"]["preguntas"]:
    if p.get("tipo") == "lista":
        respuestas[p["id"]] = st.text_input(p["enunciado"], help=p.get("ayuda", ""))
    else:
        respuestas[p["id"]] = st.text_input(p["enunciado"], help=p.get("ayuda", ""))

st.header("2. Morfología")
for palabra in EXAMEN["2ESO"]["morfologia"]:
    st.subheader(palabra["palabra"])
    for campo in palabra["campos"]:
        clave = f"{palabra['id']}_{campo}"
        if campo == "Estructura de la palabra":
            respuestas[clave] = st.selectbox(campo, ["", "simple", "derivada", "compuesta", "parasintética"], key=clave)
        elif campo == "V / I":
            respuestas[clave] = st.selectbox(campo, ["", "variable", "invariable"], key=clave)
        else:
            respuestas[clave] = st.text_input(campo, key=clave)

st.header("3. Determinantes y pronombres")
for p in EXAMEN["2ESO"]["determinantes_pronombres"]:
    st.write(f"**{p['frase']}**")
    respuestas[p["id"]] = st.selectbox(p["enunciado"], ["", "determinante", "pronombre"], key=p["id"])

st.header("4. Semántica")
opciones_sem = ["", "antonimia", "sinonimia", "campo semántico", "polisemia", "homonimia", "meronimia", "hipónimos", "hiperónimo"]
for p in EXAMEN["2ESO"]["semantica"]:
    st.write(f"**{p['elemento']}**")
    respuestas[p["id"]] = st.selectbox(p["enunciado"], opciones_sem, key=p["id"])

st.header("5. Textos")
opciones_texto = ["", "narrativo", "descriptivo", "expositivo", "argumentativo", "instructivo", "dialogado"]
for p in EXAMEN["2ESO"]["textos"]:
    st.write(p["texto"])
    respuestas[p["id"]] = st.selectbox(p["enunciado"], opciones_texto, key=p["id"])

st.header("6. Literatura")
lit = EXAMEN["2ESO"]["literatura"]
poema = lit[0]
for verso in poema["versos"]:
    st.write(verso)
respuestas["l1"] = st.selectbox("6.1. Número de versos", ["", "1", "2", "3", "4", "5", "6"], key="l1")
respuestas["l2"] = st.selectbox("6.2. ¿Es de arte mayor o de arte menor?", ["", "arte menor", "arte mayor"], key="l2")
respuestas["l3"] = st.text_input("6.3. Esquema métrico", help="Ejemplo: 14A 14B 14B 14A", key="l3")
respuestas["l4"] = st.selectbox("6.4. Tipo de rima", ["", "asonante", "consonante"], key="l4")
respuestas["l5"] = st.text_input("6.5. Localiza una sinalefa", help="Escribe las dos palabras exactas.", key="l5")
respuestas["l6"] = st.text_input("6.6. Localiza una personificación", help="Escribe las palabras exactas.", key="l6")

st.header("7. Sintaxis")
for p in EXAMEN["2ESO"]["sintaxis"]:
    st.write(f"**{p['frase']}**")
    opciones = ["", "frase", "oración"] if p["id"] in ["x1", "x2", "x3", "x4", "x5"] else ["", "enunciativa", "interrogativa", "exclamativa", "desiderativa", "exhortativa"]
    respuestas[p["id"]] = st.selectbox(p["enunciado"], opciones, key=p["id"])

st.header("8. Diálogo")
st.write(EXAMEN["2ESO"]["dialogo"]["texto"])
for p in EXAMEN["2ESO"]["dialogo"]["preguntas"]:
    if p.get("tipo") == "lista":
        respuestas[p["id"]] = st.text_input(p["enunciado"], help=p.get("ayuda", ""), key=p["id"])
    else:
        respuestas[p["id"]] = st.text_area(p["enunciado"], help=p.get("ayuda", ""), key=p["id"], height=90)

st.divider()

if st.button("✅ ENVIAR EXAMEN", use_container_width=True):
    if not nombre.strip():
        st.error("Escribe tu nombre y apellidos.")
        st.stop()
    if not curso:
        st.error("Selecciona tu grupo.")
        st.stop()

    puntos, nota_inicial = corregir_examen(respuestas)
    textos_para_ortografia = [v for v in respuestas.values() if isinstance(v, str)]
    faltas, faltas_tilde, descuento = detectar_ortografia(textos_para_ortografia)
    nota_final = round(max(0.0, nota_inicial - descuento), 2)

    fila = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nombre": nombre.strip(),
        "curso": curso,
        "comprension": puntos["comprension"],
        "morfologia": puntos["morfologia"],
        "determinantes": puntos["determinantes"],
        "semantica": puntos["semantica"],
        "textos": round((puntos["textos"] + puntos["dialogo"]) / 1.5 * 10, 2),
        "literatura": puntos["literatura"],
        "sintaxis": puntos["sintaxis"],
        "nota_sin_faltas": nota_inicial,
        "faltas_ortografia": faltas,
        "faltas_tilde": faltas_tilde,
        "descuento_ortografia": descuento,
        "nota_final": nota_final,
    }

    try:
        guardar_csv(fila)
    except Exception as e:
        st.error("No se pudo guardar el resultado en el CSV del servidor.")
        st.exception(e)
        st.stop()

    st.session_state["enviado"] = True
    st.session_state["nombre"] = nombre.strip()
    st.session_state["curso"] = curso
    st.session_state["puntos"] = puntos
    st.session_state["nota_inicial"] = nota_inicial
    st.session_state["descuento"] = descuento
    st.session_state["nota_final"] = nota_final
    st.session_state["faltas"] = faltas
    st.session_state["faltas_tilde"] = faltas_tilde
    st.session_state["fila"] = fila
    st.rerun()
