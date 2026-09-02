import io
import os
import re
import unicodedata
from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from examen2ESO import EXAMEN

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    REPORTLAB_OK = True
except Exception:
    REPORTLAB_OK = False

st.set_page_config(page_title="Evaluación inicial - Lengua 2º ESO", page_icon="📚", layout="centered")

# ============================================================
# DATOS FIJOS DEL EXAMEN
# ============================================================
TEXTOS = {
    "A": "Apaga el horno y deja reposar la masa durante diez minutos antes de usarla.",
    "B": "Los mamíferos son animales vertebrados que alimentan a sus crías con leche.",
    "C": "Reciclar ayuda a reducir la contaminación y cuidar el medio ambiente.",
}

DIALOGO = """Lucía: ¿Has terminado el resumen de Lengua?
Carlos: Sí, lo hice ayer por la tarde.
Lucía: Yo todavía estoy con la conclusión.
Carlos: Si quieres, lo revisamos juntos después de clase.
Lucía: Vale, quedamos en la biblioteca.
Carlos: Perfecto, allí estaremos más tranquilos."""

# Puntuación exacta del documento original
PESOS = {
    "comprension": 2.0,
    "morfologia": 2.5,
    "semantica": 1.5,
    "textos": 1.0,
    "literatura": 2.0,
    "sintaxis": 1.0,
    "dialogo": 0.5,
}

# ============================================================
# NORMALIZACIÓN
# ============================================================
def normalizar(valor):
    if valor is None:
        return ""
    texto = str(valor).strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = texto.replace("º", "").replace("ª", "")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def lista_normalizada(valor):
    if not valor:
        return []
    return [normalizar(x) for x in re.split(r"[,;\n]+", str(valor)) if normalizar(x)]


def contiene(valor, *terminos):
    t = normalizar(valor)
    return bool(t) and any(normalizar(x) in t for x in terminos)


def exacta(valor, *alternativas):
    t = normalizar(valor)
    return bool(t) and any(t == normalizar(x) for x in alternativas)


def puntos_si(condicion, puntos):
    return float(puntos) if condicion else 0.0

# ============================================================
# CORRECCIÓN
# ============================================================
def corregir(res):
    p = {k: 0.0 for k in PESOS}
    detalle = {}

    # ---------- 1. Comprensión (2,0) ----------
    # 1.1 lugar, tiempo, ambiente = 0,5
    c1 = res.get("c1", "")
    c2 = res.get("c2", "")
    c3 = res.get("c3", "")
    pc1 = 0.5 / 3 * sum([
        contiene(c1, "tren", "vagon", "vagón", "estacion", "estación", "ciudad"),
        contiene(c2, "madrugada", "amanecer", "noche", "temprano"),
        contiene(c3, "silencio", "silencioso", "extrano", "extraño", "tenso", "misterioso")
    ])
    p["comprension"] += pc1
    detalle["c1"] = pc1

    # 1.2 tres acciones distintas = 0,5
    acciones = [
        "recorria", "recorría", "cubria", "cubría", "se detenia", "se detenía",
        "avanzaba", "miraba", "sujetaba", "dormia", "dormía", "llego", "llegó",
        "bajo", "bajó", "respiro", "respiró", "camino", "caminó"
    ]
    t_acc = normalizar(res.get("c4", ""))
    halladas = set()
    for a in acciones:
        if normalizar(a) in t_acc:
            halladas.add(normalizar(a))
    # agrupar variantes equivalentes
    grupos = [
        {normalizar("recorría")},
        {normalizar("cubría")},
        {normalizar("se detenía")},
        {normalizar("avanzaba")},
        {normalizar("miraba")},
        {normalizar("sujetaba")},
        {normalizar("dormía")},
        {normalizar("llegó")},
        {normalizar("bajó")},
        {normalizar("respiró")},
        {normalizar("caminó")},
    ]
    n_acc = sum(any(x in t_acc for x in g) for g in grupos)
    pc2 = min(n_acc, 3) / 3 * 0.5
    p["comprension"] += pc2
    detalle["c2"] = pc2

    # 1.3 resumen = 1,0. Se corrige por contenido, no por nº de palabras.
    resumen = res.get("c5", "")
    criterios_resumen = [
        ("tren", "viaje", "vagon", "vagón"),
        ("hombre", "viajero", "joven"),
        ("niebla", "silencio", "paisaje"),
        ("estacion final", "estación final", "salida", "baja", "bajó"),
    ]
    nr = sum(contiene(resumen, *x) for x in criterios_resumen)
    pc3 = min(nr / 4, 1.0)
    p["comprension"] += pc3
    detalle["c3"] = pc3

    # ---------- 2. Morfología (2,5) ----------
    # 2.1 = 2,0: cada palabra 0,5; campos ponderados.
    claves_morf = {
        "m1": {
            "Lexema": ("silenci", "silenc-"),
            "Morfemas": ("o", "-o"),
            "Estructura": ("simple",),
            "Categoría gramatical": ("sustantivo", "comun", "común", "abstracto", "masculino", "singular"),
            "V/I": ("variable", "v"),
        },
        "m2": {
            "Lexema": ("lent", "lent-"),
            "Morfemas": ("a", "mente", "-mente"),
            "Estructura": ("derivada", "derivacion"),
            "Categoría gramatical": ("adverbio", "modo"),
            "V/I": ("invariable", "i"),
        },
        "m3": {
            "Lexema": ("conoc", "conoc-"),
            "Morfemas": ("des", "ido", "-ido", "-o"),
            "Estructura": ("derivada", "derivacion"),
            "Categoría gramatical": ("adjetivo", "calificativo", "masculino", "singular"),
            "V/I": ("variable", "v"),
        },
        "m4": {
            "Lexema": ("mochil", "mochil-"),
            "Morfemas": ("a", "s", "-a", "-s"),
            "Estructura": ("simple",),
            "Categoría gramatical": ("sustantivo", "comun", "común", "concreto", "femenino", "plural"),
            "V/I": ("variable", "v"),
        },
    }
    campos_peso = {
        "Lexema": 0.10,
        "Morfemas": 0.10,
        "Estructura": 0.10,
        "Categoría gramatical": 0.15,
        "V/I": 0.05,
    }
    for mid, campos in claves_morf.items():
        for campo, correctas in campos.items():
            valor = res.get(f"{mid}_{campo}", "")
            if campo == "Categoría gramatical":
                # Cada término relevante suma proporcionalmente; evita exigir una redacción exacta.
                cat = normalizar(valor)
                req = [x for x in correctas if len(normalizar(x)) > 2]
                # Para categoría completa, exigimos categoría + rasgos principales.
                if mid == "m1": ok = "sustantivo" in cat and "masculino" in cat and "singular" in cat
                elif mid == "m2": ok = "adverbio" in cat
                elif mid == "m3": ok = "adjetivo" in cat and "masculino" in cat and "singular" in cat
                else: ok = "sustantivo" in cat and "femenino" in cat and "plural" in cat
            elif campo == "Morfemas":
                partes = lista_normalizada(valor)
                if mid == "m1": ok = "o" in partes or "-o" in partes or "flexivo" in normalizar(valor)
                elif mid == "m2": ok = "mente" in normalizar(valor) and ("a" in partes or "-a" in partes)
                elif mid == "m3": ok = "des" in normalizar(valor) and ("ido" in normalizar(valor) or "id" in normalizar(valor))
                else: ok = "a" in partes and "s" in partes
            else:
                ok = exacta(valor, *correctas)
            p["morfologia"] += puntos_si(ok, campos_peso[campo])

    # 2.2 determinantes/pronombres = 0,5
    dp = {
        "dp1": ("determinante", 1/3),
        "dp2": ("determinante", 1/3),
        "dp3": ("pronombre", 1/3),
    }
    for k, (correcta, frac) in dp.items():
        ok = exacta(res.get(k, ""), correcta)
        p["morfologia"] += puntos_si(ok, 0.5 * frac)

    # ---------- 3. Semántica (1,5) ----------
    sem_correctas = {"s1": "antonimia", "s2": "campo semantico", "s3": "polisemia", "s4": "meronimia", "s5": "hiponimos"}
    for k, correcta in sem_correctas.items():
        p["semantica"] += puntos_si(exacta(res.get(k, ""), correcta), 0.10)

    defs = {
        "sd1": (("polisemia",), ("varios significados", "varios sentidos", "mismo palabra", "misma palabra"), 0.25),
        "sd2": (("homonimia",), ("misma forma", "suenan igual", "suenan igual", "distinto significado"), 0.25),
        "sd3": (("hiperonimo",), ("termino general", "término general", "engloba", "incluye otros"), 0.25),
        "sd4": (("campo semantico",), ("campo semantico", "campo semántico", "mismo tema", "relacionadas por significado"), 0.25),
    }
    for k, (conceptos, pistas, peso) in defs.items():
        txt = res.get(k, "")
        ok_concepto = any(normalizar(c) in normalizar(txt) for c in conceptos)
        ok_pista = any(normalizar(x) in normalizar(txt) for x in pistas)
        p["semantica"] += puntos_si(ok_concepto and ok_pista, peso)

    # ---------- 4. Textos (1,0) ----------
    # 4.1 tres tipos = 0,75; 4.2 finalidad = 0,25
    tipos = {"t1": ("instructivo", "instruccional"), "t2": ("expositivo",), "t3": ("argumentativo", "persuasivo", "expositivo argumentativo")}
    for k, alternativas in tipos.items():
        p["textos"] += puntos_si(exacta(res.get(k, ""), *alternativas), 0.25)
    finalidad = res.get("t4", "")
    ok_finalidad = (
        contiene(finalidad, "dar instrucciones", "indicar pasos", "explicar como", "explicar cómo", "informar", "convencer", "persuadir", "concienciar")
        and contiene(finalidad, "texto a", "texto b", "texto c", "receta", "mamiferos", "mamíferos", "reciclar", "contaminacion", "contaminación", "medio ambiente")
    )
    p["textos"] += puntos_si(ok_finalidad, 0.25)

    # ---------- 5. Literatura (2,0) ----------
    p["literatura"] += puntos_si(exacta(res.get("l1", ""), "4"), 0.30)
    p["literatura"] += puntos_si(exacta(res.get("l2", ""), "arte mayor"), 0.30)
    met = normalizar(res.get("l3", "")).replace(",", " ").replace("/", " ")
    met = re.sub(r"\s+", " ", met)
    metricas_validas = ["10a 11b 11b 11a", "10a 11b 11b 11a", "10 11 11 11", "10-11-11-11", "10 11 11 11a"]
    p["literatura"] += puntos_si(any(met == x for x in metricas_validas), 0.35)
    p["literatura"] += puntos_si(exacta(res.get("l4", ""), "asonante", "rima asonante", "rima asonante en los versos 1 y 4"), 0.35)
    sinal = normalizar(res.get("l5", ""))
    ok_sinal = ("suave en" in sinal or "suave_en" in sinal or "solo en" in sinal or "solo_en" in sinal or "y el" in sinal or "y_el" in sinal) and ("un" in sinal or "sinalefa" in sinal or "unen" in sinal or "union" in sinal or "unión" in sinal)
    p["literatura"] += puntos_si(ok_sinal, 0.35)
    pers = normalizar(res.get("l6", ""))
    ok_pers = ("viento juega" in pers) and ("persona" in pers or "humana" in pers or "humano" in pers or "accion" in pers or "acción" in pers or "personificacion" in pers or "personificación" in pers)
    p["literatura"] += puntos_si(ok_pers, 0.35)

    # ---------- 6. Sintaxis (1,0) ----------
    syn = {
        "x1": ("frase",), "x2": ("oracion", "oración"), "x3": ("frase",), "x4": ("frase",), "x5": ("oracion", "oración"),
        "x6": ("interrogativa",), "x7": ("desiderativa",), "x8": ("exclamativa",), "x9": ("enunciativa",), "x10": ("exhortativa", "imperativa")
    }
    for k, alternativas in syn.items():
        p["sintaxis"] += puntos_si(exacta(res.get(k, ""), *alternativas), 0.10)

    # ---------- 7. Diálogo (0,5) ----------
    interlocutores = lista_normalizada(res.get("d1", ""))
    tiene_lucia = any("lucia" == x or "lucia" in x for x in interlocutores)
    tiene_carlos = any("carlos" == x or "carlos" in x for x in interlocutores)
    p["dialogo"] += puntos_si(tiene_lucia and tiene_carlos, 0.10)
    p["dialogo"] += puntos_si(exacta(res.get("d2", ""), "6", "seis", "6 intervenciones", "seis intervenciones"), 0.10)
    indirecto = normalizar(res.get("d3", ""))
    ok_ind = (
        ("carlos" in indirecto or "respondio" in indirecto or "respondió" in indirecto)
        and "que" in indirecto
        and ("habia hecho" in indirecto or "lo habia hecho" in indirecto)
        and ("dia anterior" in indirecto or "el dia anterior" in indirecto or "dia antes" in indirecto)
    )
    p["dialogo"] += puntos_si(ok_ind, 0.30)

    # Redondeo y tope de cada apartado
    for k in p:
        p[k] = round(min(p[k], PESOS[k]), 2)
    total = round(sum(p.values()), 2)
    return p, total, detalle

# ============================================================
# PDF PLANO PARA CLASSROOM
# ============================================================
def crear_pdf(nombre, curso, respuestas, puntos, total):
    if not REPORTLAB_OK:
        return None
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Title"], alignment=TA_CENTER, fontSize=17, leading=21)
    small = ParagraphStyle("small", parent=styles["BodyText"], fontSize=8.5, leading=11)
    story = [
        Paragraph("ENTREGA — EVALUACIÓN INICIAL DE LENGUA 2.º ESO", title),
        Spacer(1, 12),
        Paragraph(f"<b>Nombre y apellidos:</b> {nombre}", styles["BodyText"]),
        Paragraph(f"<b>Grupo:</b> {curso}", styles["BodyText"]),
        Paragraph(f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["BodyText"]),
        Spacer(1, 12),
        Paragraph("<b>NOTA AUTOMÁTICA</b>", styles["Heading2"]),
        Paragraph(f"<font size='18'><b>{total:.2f} / 10</b></font>", styles["BodyText"]),
        Spacer(1, 10),
    ]
    data = [["Apartado", "Puntuación"]] + [[k.capitalize(), f"{puntos[k]:.2f} / {PESOS[k]:.1f}"] for k in PESOS]
    table = Table(data, colWidths=[280, 130])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (1,1), (1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story += [table, PageBreak(), Paragraph("RESPUESTAS ENTREGADAS", styles["Heading1"]), Spacer(1, 8)]
    for pregunta, respuesta in respuestas:
        texto = str(respuesta).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
        story.append(Paragraph(f"<b>{pregunta}</b>", styles["BodyText"]))
        story.append(Paragraph(texto if texto.strip() else "<i>Sin respuesta</i>", small))
        story.append(Spacer(1, 7))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ============================================================
# CSV DE LA SESIÓN / DESCARGA INDIVIDUAL
# ============================================================
def fila_csv(nombre, curso, puntos, total):
    fila = {"fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "nombre": nombre, "curso": curso}
    fila.update({k: puntos[k] for k in PESOS})
    fila["nota_final"] = total
    return pd.DataFrame([fila])

# ============================================================
# INTERFAZ
# ============================================================
st.title("📚 Evaluación inicial de Lengua — 2.º ESO")
st.caption("Lengua Castellana y Literatura · Curso 2026-2027")

if st.session_state.get("enviado"):
    st.success("✅ Examen enviado y corregido.")
    nombre = st.session_state["nombre"]
    curso = st.session_state["curso"]
    puntos = st.session_state["puntos"]
    total = st.session_state["total"]
    respuestas_pdf = st.session_state["respuestas_pdf"]

    st.metric("NOTA FINAL", f"{total:.2f} / 10")
    st.subheader("Resultado por apartados")
    cols = st.columns(4)
    for i, k in enumerate(PESOS):
        cols[i % 4].metric(k.capitalize(), f"{puntos[k]:.2f} / {PESOS[k]:.1f}")

    if REPORTLAB_OK:
        pdf = crear_pdf(nombre, curso, respuestas_pdf, puntos, total)
        st.download_button(
            "📄 DESCARGAR ENTREGA PARA CLASSROOM",
            data=pdf,
            file_name=f"Entrega_2ESO_{re.sub(r'[^A-Za-z0-9_-]+', '_', nombre.strip())}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.info("Descarga este PDF y súbelo como entrega en Classroom. El archivo no contiene campos editables.")
    else:
        st.error("Falta reportlab. Añade reportlab==4.2.2 a requirements.txt y vuelve a desplegar.")

    csv = fila_csv(nombre, curso, puntos, total).to_csv(index=False, encoding="utf-8-sig")
    st.download_button("📊 Descargar resultado CSV", data=csv, file_name=f"Resultado_2ESO_{nombre.replace(' ', '_')}.csv", mime="text/csv")

    if st.button("🔄 Volver al inicio"):
        st.session_state.clear()
        st.rerun()
    st.stop()

nombre = st.text_input("Nombre y apellidos")
curso = st.selectbox("Grupo", ["", "2º A", "2º B", "2º C", "2º D"])

with st.form("examen"):
    respuestas = {}
    respuestas_pdf = []

    # 1 Comprensión
    st.header("1. Comprensión lectora — 2 puntos")
    st.write(EXAMEN["2ESO"]["comprension"]["texto"])
    preguntas_comp = [
        ("c1", "1.1. Indica el lugar del texto."),
        ("c2", "1.1. Indica el tiempo del texto."),
        ("c3", "1.1. Describe el ambiente del texto."),
        ("c4", "1.2. Escribe tres acciones que ocurren en el texto, separadas por comas."),
        ("c5", "1.3. Resume el texto con tus palabras (3-4 líneas)."),
    ]
    for k, label in preguntas_comp:
        val = st.text_area(label, key=k, height=80 if k == "c5" else 55)
        respuestas[k] = val
        respuestas_pdf.append((label, val))

    # 2 Morfología
    st.header("2. Morfología y categorías gramaticales — 2,5 puntos")
    for palabra in EXAMEN["2ESO"]["morfologia"]:
        st.subheader(palabra["palabra"])
        for campo in ["Lexema", "Morfemas", "Estructura", "Categoría gramatical", "V/I"]:
            key = f"{palabra['id']}_{campo}"
            if campo == "Estructura":
                val = st.selectbox(f"{palabra['palabra']} → {campo}", ["", "simple", "compuesta", "derivada", "parasintética"], key=key)
            elif campo == "V/I":
                val = st.selectbox(f"{palabra['palabra']} → {campo}", ["", "variable", "invariable"], key=key)
            else:
                val = st.text_input(f"{palabra['palabra']} → {campo}", key=key)
            respuestas[key] = val
            respuestas_pdf.append((f"{palabra['palabra']} → {campo}", val))

    st.subheader("2.2. Determinantes y pronombres — 0,5 puntos")
    dp = [
        ("dp1", "a) Aquellos estudiantes llegaron tarde."),
        ("dp2", "b) Mi cuaderno está en la mesa."),
        ("dp3", "c) Nadie respondió a la pregunta."),
    ]
    for k, frase in dp:
        val = st.selectbox(frase, ["", "determinante", "pronombre"], key=k)
        respuestas[k] = val
        respuestas_pdf.append((frase, val))

    # 3 Semántica
    st.header("3. Semántica — 1,5 puntos")
    opciones_sem = ["", "antonimia", "sinonimia", "campo semántico", "polisemia", "homonimia", "meronimia", "hipónimos", "hiperónimo"]
    sem_items = [
        ("s1", "Frío / calor → relación semántica"),
        ("s2", "Perro, gato, caballo → relación semántica"),
        ("s3", "Hoja (árbol / papel) → relación semántica"),
        ("s4", "Rueda y volante respecto a coche → relación semántica"),
        ("s5", "León, tigre, pantera → relación semántica"),
    ]
    for k, label in sem_items:
        val = st.selectbox(label, opciones_sem, key=k)
        respuestas[k] = val
        respuestas_pdf.append((label, val))

    st.subheader("3.2. Explica con definición y ejemplo — 1 punto")
    defs_labels = [
        ("sd1", "Polisemia"), ("sd2", "Homonimia"), ("sd3", "Hiperónimo"), ("sd4", "Campo semántico")
    ]
    for k, label in defs_labels:
        val = st.text_area(label, key=k, height=70)
        respuestas[k] = val
        respuestas_pdf.append((label, val))

    # 4 Textos INDEPENDIENTE
    st.header("4. Textos — 1 punto")
    st.write("Lee los siguientes textos:")
    for letra, texto in TEXTOS.items():
        st.markdown(f"**Texto {letra}:** {texto}")
    opciones_texto = ["", "instructivo", "narrativo", "descriptivo", "expositivo", "argumentativo", "dialogado"]
    for k, label in [("t1", "Texto A → tipo de texto"), ("t2", "Texto B → tipo de texto"), ("t3", "Texto C → tipo de texto")]:
        val = st.selectbox(label, opciones_texto, key=k)
        respuestas[k] = val
        respuestas_pdf.append((label, val))
    val = st.text_area("4.2. Explica la finalidad de UNO de los textos.", key="t4", height=80)
    respuestas["t4"] = val
    respuestas_pdf.append(("4.2. Finalidad de uno de los textos", val))

    # 5 Literatura
    st.header("5. Literatura — 2 puntos")
    poema = EXAMEN["2ESO"]["literatura"][0]["texto"]
    st.markdown(poema.replace("\n", "  \n"))
    respuestas["l1"] = st.selectbox("5.1. Número de versos", ["", "2", "3", "4", "5", "6", "7", "8"], key="l1")
    respuestas_pdf.append(("5.1. Número de versos", respuestas["l1"]))
    respuestas["l2"] = st.selectbox("5.2. ¿Arte mayor o menor?", ["", "arte menor", "arte mayor"], key="l2")
    respuestas_pdf.append(("5.2. Arte mayor o menor", respuestas["l2"]))
    respuestas["l3"] = st.text_input("5.3. Esquema métrico", key="l3", help="Ejemplo: 10A 11B 11B 11A")
    respuestas_pdf.append(("5.3. Esquema métrico", respuestas["l3"]))
    respuestas["l4"] = st.selectbox("5.4. Tipo de rima", ["", "asonante", "consonante"], key="l4")
    respuestas_pdf.append(("5.4. Tipo de rima", respuestas["l4"]))
    respuestas["l5"] = st.text_input("5.5. Escribe una sinalefa y explícala.", key="l5")
    respuestas_pdf.append(("5.5. Una sinalefa (explicada)", respuestas["l5"]))
    respuestas["l6"] = st.text_area("5.6. Escribe una personificación y explica por qué lo es.", key="l6", height=70)
    respuestas_pdf.append(("5.6. Una personificación (explicada)", respuestas["l6"]))

    # 6 Sintaxis
    st.header("6. Sintaxis — 1 punto")
    opciones_frase = ["", "frase", "oración"]
    opciones_modalidad = ["", "enunciativa", "interrogativa", "exclamativa", "desiderativa", "exhortativa"]
    for k, frase, tipo in [
        ("x1", "Buenas tardes", "frase"), ("x2", "Llueve mucho hoy", "frase"), ("x3", "¡Qué alegría!", "frase"), ("x4", "No hablar en clase", "frase"), ("x5", "El perro ladra", "frase"),
        ("x6", "¿Vienes conmigo?", "modal"), ("x7", "Ojalá apruebe el examen", "modal"), ("x8", "¡Qué frío hace!", "modal"), ("x9", "Mañana iremos al cine", "modal"), ("x10", "Cierra la puerta", "modal")]:
        opciones = opciones_frase if tipo == "frase" else opciones_modalidad
        val = st.selectbox(f"**{frase}** → {('Frase u oración' if tipo == 'frase' else 'Modalidad oracional')}", opciones, key=k)
        respuestas[k] = val
        respuestas_pdf.append((frase + " → " + ("Frase u oración" if tipo == "frase" else "Modalidad oracional"), val))

    # 7 Diálogo
    st.header("7. Diálogo — 0,5 puntos")
    st.markdown(DIALOGO.replace("\n", "  \n"))
    val = st.text_input("7.1. Interlocutores (personajes que participan), separados por comas.", key="d1")
    respuestas["d1"] = val
    respuestas_pdf.append(("7.1. Interlocutores", val))
    val = st.number_input("7.2. Número de intervenciones", min_value=0, max_value=20, step=1, key="d2")
    respuestas["d2"] = str(int(val))
    respuestas_pdf.append(("7.2. Número de intervenciones", str(int(val))))
    val = st.text_area("7.3. Pasa al estilo indirecto: Carlos: «Sí, lo hice ayer por la tarde».", key="d3", height=90)
    respuestas["d3"] = val
    respuestas_pdf.append(("7.3. Estilo indirecto", val))

    st.divider()
    enviar = st.form_submit_button("📤 ENVIAR EXAMEN", use_container_width=True)

if enviar:
    if not nombre.strip():
        st.error("Escribe tu nombre y apellidos.")
        st.stop()
    if not curso:
        st.error("Selecciona tu grupo.")
        st.stop()

    puntos, total, _ = corregir(respuestas)
    st.session_state.update({
        "enviado": True,
        "nombre": nombre.strip(),
        "curso": curso,
        "puntos": puntos,
        "total": total,
        "respuestas_pdf": respuestas_pdf,
    })
    st.rerun()
