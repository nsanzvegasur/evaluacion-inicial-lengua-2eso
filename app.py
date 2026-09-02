import os
import re
import unicodedata
from datetime import datetime

import pandas as pd
import streamlit as st

from analytics import radar_chart, comparativa_clase, comparativa, generar_perfil
from examen2ESO import EXAMEN
from pdf_report import generar_pdf


# ==============================================================
# CONFIGURACIÓN
# ==============================================================

st.set_page_config(
    page_title="Evaluación inicial de Lengua - 2.º ESO",
    page_icon="📚",
    layout="centered",
)

CSV_FILE = "results.csv"
EXAM = EXAMEN["2ESO"]

PESOS = {
    "comprension": 2.0,
    "morfologia": 2.5,
    "semantica": 1.5,
    "textos": 1.0,
    "literatura": 2.0,
    "sintaxis": 1.0,
    "dialogo": 0.5,
}

PUNTUACION_BRUTA_MAXIMA = sum(PESOS.values())  # El examen original suma 10,5 puntos.

NOMBRES = {
    "comprension": "Comprensión lectora",
    "morfologia": "Morfología",
    "semantica": "Semántica",
    "textos": "Textos",
    "literatura": "Literatura",
    "sintaxis": "Sintaxis",
    "dialogo": "Diálogo",
}

# ==============================================================
# ESTILO
# ==============================================================

st.markdown(
    """
    <style>
    .titulo-principal {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.15rem;
    }
    .subtitulo {
        color: #666;
        margin-bottom: 1.4rem;
    }
    .bloque {
        padding: 0.4rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================
# NORMALIZACIÓN
# ==============================================================

def normalizar(valor):
    if valor is None:
        return ""

    texto = str(valor).strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )
    texto = texto.replace("º", "").replace("ª", "")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def dividir_lista(valor):
    """
    Conserva correctamente las comas introducidas por el alumno.
    Acepta comas, punto y coma y saltos de línea.
    """
    if valor is None:
        return []

    texto = str(valor).strip()
    if not texto:
        return []

    return [
        normalizar(parte)
        for parte in re.split(r"[,;\n]+", texto)
        if normalizar(parte)
    ]


def contiene(valor, *criterios):
    texto = normalizar(valor)
    if not texto:
        return False

    return any(
        normalizar(criterio) in texto
        for criterio in criterios
    )


def exacta(valor, *alternativas):
    texto = normalizar(valor)
    if not texto:
        return False

    return any(
        texto == normalizar(alternativa)
        for alternativa in alternativas
    )


def parcial_lista(valor, criterios):
    """
    Devuelve proporción de criterios encontrados.
    Evita exigir una redacción idéntica.
    """
    respuestas = dividir_lista(valor)
    criterios_n = [normalizar(x) for x in criterios]

    if not respuestas or not criterios_n:
        return 0.0

    encontrados = set()

    for respuesta in respuestas:
        for criterio in criterios_n:
            if respuesta == criterio or criterio in respuesta or respuesta in criterio:
                encontrados.add(criterio)

    return len(encontrados) / len(criterios_n)


def suma_correcta(condicion, puntos):
    return float(puntos) if condicion else 0.0


# ==============================================================
# CORRECCIÓN
# ==============================================================

def corregir_examen(respuestas):
    puntos = {clave: 0.0 for clave in PESOS}
    detalle = {}

    # ----------------------------------------------------------
    # 1. COMPRENSIÓN — 2 puntos
    # ----------------------------------------------------------
    comprension = EXAM["comprension"]
    acciones_utilizadas = set()

    for pregunta in comprension["preguntas"]:
        pid = pregunta["id"]
        respuesta = respuestas.get(pid, "")
        tipo = pregunta.get("tipo", "texto")
        valor = float(pregunta.get("puntos", 0))

        if tipo == "lista":
            obtenido = valor * parcial_lista(
                respuesta,
                pregunta.get("criterios", [])
            )

        elif tipo == "accion":
            texto = normalizar(respuesta)
            validas = [normalizar(x) for x in pregunta.get("criterios", [])]

            # Cada una de las tres respuestas debe ser una acción distinta.
            ok = False
            for candidata in validas:
                if texto == candidata and candidata not in acciones_utilizadas:
                    acciones_utilizadas.add(candidata)
                    ok = True
                    break

            # También aceptamos el verbo dentro de una respuesta algo más larga.
            if not ok and texto:
                for candidata in validas:
                    if candidata in texto and candidata not in acciones_utilizadas:
                        acciones_utilizadas.add(candidata)
                        ok = True
                        break

            obtenido = valor if ok else 0.0

        else:
            obtenido = valor if contiene(
                respuesta,
                *pregunta.get("criterios", [])
            ) else 0.0

        puntos["comprension"] += obtenido
        detalle[pid] = round(obtenido, 2)

    # ----------------------------------------------------------
    # 2. MORFOLOGÍA — 2,5 puntos
    # ----------------------------------------------------------
    pesos_campo = {
        "Lexema": 0.10,
        "Morfemas": 0.10,
        "Estructura de la palabra": 0.10,
        "Categoría gramatical completa": 0.15,
        "V / I": 0.05,
        "Estructura": 0.10,
        "Categoría gramatical": 0.15,
    }

    for palabra in EXAM["morfologia"]:
        mid = palabra["id"]
        correctas = palabra.get("respuestas", {})

        for campo in palabra.get("campos", []):
            key = f"{mid}_{campo}"
            respuesta = respuestas.get(key, "")
            posibles = correctas.get(campo, [])
            posibles_n = [normalizar(x) for x in posibles]

            peso = pesos_campo.get(campo, 0.0)
            correcto = False

            if campo == "Lexema":
                correcto = any(
                    normalizar(respuesta).replace("-", "") == x.replace("-", "")
                    for x in posibles_n
                )

            elif campo == "Morfemas":
                partes = dividir_lista(respuesta)
                texto = normalizar(respuesta).replace(" ", "")

                if mid == "m1":
                    correcto = "o" in partes or "-o" in partes or texto.endswith("o")

                elif mid == "m2":
                    correcto = "mente" in texto and ("a" in partes or "-a" in texto)

                elif mid == "m3":
                    correcto = (
                        "des" in texto
                        and ("id" in texto or "ido" in texto)
                        and ("o" in texto or "-o" in texto)
                    )

                elif mid == "m4":
                    correcto = "a" in partes and "s" in partes

                else:
                    correcto = all(x in texto for x in posibles_n if len(x) > 1)

            elif campo in (
                "Estructura de la palabra",
                "Estructura",
                "V / I",
                "Categoría gramatical completa",
                "Categoría gramatical",
            ):
                texto = normalizar(respuesta)

                if campo in ("Estructura de la palabra", "Estructura"):
                    correcto = any(texto == x for x in posibles_n)

                elif campo == "V / I":
                    correcto = any(texto == x for x in posibles_n)

                else:
                    if mid == "m1":
                        correcto = (
                            "sustantivo" in texto
                            and "masculino" in texto
                            and "singular" in texto
                        )
                    elif mid == "m2":
                        correcto = "adverbio" in texto
                    elif mid == "m3":
                        correcto = (
                            "adjetivo" in texto
                            and "masculino" in texto
                            and "singular" in texto
                        )
                    elif mid == "m4":
                        correcto = (
                            "sustantivo" in texto
                            and "femenino" in texto
                            and "plural" in texto
                        )
                    else:
                        correcto = any(x in texto for x in posibles_n)

            puntos["morfologia"] += suma_correcta(correcto, peso)
            detalle[key] = round(suma_correcta(correcto, peso), 2)

    # 2.2 Determinantes y pronombres — 0,5
    for pregunta in EXAM.get("determinantes_pronombres", []):
        pid = pregunta["id"]
        correcto = exacta(
            respuestas.get(pid, ""),
            pregunta.get("respuesta", "")
        )
        obtenido = suma_correcta(
            correcto,
            pregunta.get("puntos", 0)
        )
        puntos["morfologia"] += obtenido
        detalle[pid] = round(obtenido, 2)

    # ----------------------------------------------------------
    # 3. SEMÁNTICA — 1,5 puntos
    # ----------------------------------------------------------
    for pregunta in EXAM.get("semantica", []):
        pid = pregunta["id"]
        correcto = exacta(
            respuestas.get(pid, ""),
            pregunta.get("respuesta", "")
        )
        obtenido = suma_correcta(
            correcto,
            pregunta.get("puntos", 0)
        )
        puntos["semantica"] += obtenido
        detalle[pid] = round(obtenido, 2)

    # Definiciones de 3.2: están en el examen oficial aunque
    # la lista semantica de examen2ESO.py contiene las relaciones.
    definiciones = {
        "sd1": {
            "concepto": "polisemia",
            "pistas": ["varios significados", "varios sentidos", "misma palabra"],
            "puntos": 0.25,
        },
        "sd2": {
            "concepto": "homonimia",
            "pistas": ["misma forma", "igual forma", "suenan igual", "distinto significado"],
            "puntos": 0.25,
        },
        "sd3": {
            "concepto": "hiperonimo",
            "pistas": ["termino general", "término general", "engloba", "incluye otros", "nombre general"],
            "puntos": 0.25,
        },
        "sd4": {
            "concepto": "campo semantico",
            "pistas": ["campo semantico", "campo semántico", "mismo tema", "relacionadas por significado"],
            "puntos": 0.25,
        },
    }

    for pid, info in definiciones.items():
        texto = respuestas.get(pid, "")
        t = normalizar(texto)
        concepto = normalizar(info["concepto"])
        tiene_concepto = concepto in t
        tiene_pista = any(normalizar(p) in t for p in info["pistas"])
        obtenido = info["puntos"] if tiene_concepto and tiene_pista else 0.0
        puntos["semantica"] += obtenido
        detalle[pid] = round(obtenido, 2)

    # ----------------------------------------------------------
    # 4. TEXTOS — 1 punto
    # ----------------------------------------------------------
    for pregunta in EXAM["textos"]:
        pid = pregunta["id"]
        correcto = exacta(
            respuestas.get(pid, ""),
            pregunta.get("respuesta", "")
        )
        obtenido = suma_correcta(correcto, pregunta.get("puntos", 0))
        puntos["textos"] += obtenido
        detalle[pid] = round(obtenido, 2)

    # 4.2 finalidad: 0,25. Aceptamos explicar la finalidad aunque
    # no use exactamente las mismas palabras del modelo.
    finalidad = normalizar(respuestas.get("t4", ""))
    finalidad_ok = (
        contiene(finalidad, "dar instrucciones", "indicar pasos", "explicar como", "explicar cómo", "informar", "transmitir informacion", "transmitir información", "convencer", "persuadir", "concienciar")
        and contiene(finalidad, "texto a", "texto b", "texto c", "horno", "mamiferos", "mamíferos", "reciclar", "contaminacion", "contaminación", "medio ambiente")
    )
    puntos["textos"] += 0.25 if finalidad_ok else 0.0
    detalle["t4"] = 0.25 if finalidad_ok else 0.0

    # ----------------------------------------------------------
    # 5. LITERATURA — 2 puntos
    # ----------------------------------------------------------
    lit = {p["id"]: p for p in EXAM["literatura"]}

    # l1: 4 versos
    ok = exacta(respuestas.get("l1", ""), "4")
    puntos["literatura"] += 0.25 if ok else 0.0
    detalle["l1"] = 0.25 if ok else 0.0

    # l2: usamos literalmente la respuesta que aparece en examen2ESO.py
    ok = exacta(respuestas.get("l2", ""), lit["l2"].get("respuesta", "arte mayor"))
    puntos["literatura"] += 0.25 if ok else 0.0
    detalle["l2"] = 0.25 if ok else 0.0

    # l3: acepta las alternativas del examen oficial
    l3 = lit["l3"]
    ok = exacta(
        respuestas.get("l3", ""),
        l3.get("respuesta", ""),
        *l3.get("alternativas", [])
    )
    puntos["literatura"] += float(l3.get("puntos", 0)) if ok else 0.0
    detalle["l3"] = float(l3.get("puntos", 0)) if ok else 0.0

    # l4: respuesta del examen oficial
    l4 = lit["l4"]
    ok = exacta(respuestas.get("l4", ""), l4.get("respuesta", ""))
    puntos["literatura"] += float(l4.get("puntos", 0)) if ok else 0.0
    detalle["l4"] = float(l4.get("puntos", 0)) if ok else 0.0

    # l5: sinalefa
    l5 = lit["l5"]
    l5_resp = normalizar(respuestas.get("l5", ""))
    l5_validas = [normalizar(x) for x in l5.get("respuestas_validas", [])]
    ok = l5_resp in l5_validas
    puntos["literatura"] += float(l5.get("puntos", 0)) if ok else 0.0
    detalle["l5"] = float(l5.get("puntos", 0)) if ok else 0.0

    # l6: personificación
    l6 = lit["l6"]
    l6_resp = normalizar(respuestas.get("l6", ""))
    l6_validas = [normalizar(x) for x in l6.get("respuestas_validas", [])]
    ok = l6_resp in l6_validas or (
        "viento" in l6_resp and "juega" in l6_resp
    )
    puntos["literatura"] += float(l6.get("puntos", 0)) if ok else 0.0
    detalle["l6"] = float(l6.get("puntos", 0)) if ok else 0.0

    # ----------------------------------------------------------
    # 6. SINTAXIS — 1 punto
    # ----------------------------------------------------------
    for pregunta in EXAM["sintaxis"]:
        pid = pregunta["id"]
        correcta = pregunta.get("respuesta", "")
        respuesta = respuestas.get(pid, "")
        ok = exacta(respuesta, correcta)
        obtenido = float(pregunta.get("puntos", 0)) if ok else 0.0
        puntos["sintaxis"] += obtenido
        detalle[pid] = round(obtenido, 2)

    # ----------------------------------------------------------
    # 7. DIÁLOGO — 0,5 puntos
    # ----------------------------------------------------------
    dialogo = EXAM["dialogo"]

    for pregunta in dialogo["preguntas"]:
        pid = pregunta["id"]
        respuesta = respuestas.get(pid, "")
        tipo = pregunta.get("tipo", "")
        valor = float(pregunta.get("puntos", 0))

        if tipo == "lista":
            proporcion = parcial_lista(
                respuesta,
                pregunta.get("criterios", [])
            )
            obtenido = valor * proporcion

        elif tipo == "estilo_indirecto":
            t = normalizar(respuesta)
            ok = (
                "carlos" in t
                and any(v in t for v in ["dijo", "afirmo", "afirmó", "explico", "explicó", "comento", "comentó"])
                and "habia hecho" in t
                and (
                    "dia anterior" in t
                    or "día anterior" in t
                    or "aquel dia" in t
                    or "aquel día" in t
                )
            )
            obtenido = valor if ok else 0.0

        else:
            obtenido = valor if exacta(
                respuesta,
                pregunta.get("respuesta", "")
            ) else 0.0

        puntos["dialogo"] += obtenido
        detalle[pid] = round(obtenido, 2)

    # ----------------------------------------------------------
    # AJUSTE FINAL PARA EVITAR REDONDEOS > PUNTUACIÓN MÁXIMA
    # ----------------------------------------------------------
    for clave, maximo in PESOS.items():
        puntos[clave] = round(
            min(puntos[clave], maximo),
            2
        )

    nota_bruta = round(
        min(sum(puntos.values()), PUNTUACION_BRUTA_MAXIMA),
        2
    )

    # El examen original suma 10,5 puntos. Para que la calificación
    # final sea sobre 10, se convierte proporcionalmente.
    nota_inicial = round(
        (nota_bruta / PUNTUACION_BRUTA_MAXIMA) * 10,
        2
    )

    return puntos, nota_inicial, detalle


# ==============================================================
# ORTOGRAFÍA
# ==============================================================

# Para no dar falsos positivos, solo se detectan algunos errores
# muy claros. El descuento máximo sigue siendo 2 puntos.
ERRORES_COMUNES = {
    "aver": "a ver",
    "haver": "haber",
    "hechar": "echar",
    "ahi": "ahí",
    "ai": "ahí",
}


def detectar_ortografia(textos):
    faltas = 0

    for texto in textos:
        t = normalizar(texto)
        if not t:
            continue

        for incorrecta in ERRORES_COMUNES:
            if re.search(
                rf"\b{re.escape(incorrecta)}\b",
                t
            ):
                faltas += 1

    descuento = min(
        faltas * 0.20,
        2.0
    )

    return faltas, round(descuento, 2)


# ==============================================================
# CSV
# ==============================================================

def guardar_resultado(nombre, curso, puntos, nota_inicial, faltas, descuento, nota_final):
    fila = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nombre": nombre,
        "curso": curso,
        **{clave: round(puntos.get(clave, 0), 2) for clave in PESOS},
        "puntuacion_bruta": round(sum(puntos.values()), 2),
        "nota_inicial": round(nota_inicial, 2),
        "faltas_ortografia": int(faltas),
        "descuento_ortografia": round(descuento, 2),
        "nota_final": round(nota_final, 2),
    }

    columnas = [
        "fecha",
        "nombre",
        "curso",
        "comprension",
        "morfologia",
        "semantica",
        "textos",
        "literatura",
        "sintaxis",
        "dialogo",
        "puntuacion_bruta",
        "nota_inicial",
        "faltas_ortografia",
        "descuento_ortografia",
        "nota_final",
    ]

    nuevo = pd.DataFrame([fila], columns=columnas)

    try:
        if os.path.exists(CSV_FILE):
            antiguo = pd.read_csv(CSV_FILE)

            for columna in columnas:
                if columna not in antiguo.columns:
                    antiguo[columna] = 0

            antiguo = antiguo[columnas]
            final = pd.concat([antiguo, nuevo], ignore_index=True)
        else:
            final = nuevo

        final.to_csv(
            CSV_FILE,
            index=False,
            encoding="utf-8-sig"
        )

        return True

    except Exception as error:
        st.error("No se pudo guardar el resultado en results.csv.")
        st.exception(error)
        return False


# ==============================================================
# RESPUESTAS PARA PDF
# ==============================================================

def preparar_respuestas_pdf(respuestas):
    salida = []

    orden = [
        "c1_lugar",
        "c1_personajes",
        "c1_tiempo",
        "c2_accion1",
        "c2_accion2",
        "c2_accion3",
        "c5",
        "dp1",
        "dp2",
        "dp3",
        "s1",
        "s2",
        "s3",
        "s4",
        "s5",
        "sd1",
        "sd2",
        "sd3",
        "sd4",
        "t1",
        "t2",
        "t3",
        "t4",
        "l1",
        "l2",
        "l3",
        "l4",
        "l5",
        "l6",
        "x1",
        "x2",
        "x3",
        "x4",
        "x5",
        "x6",
        "x7",
        "x8",
        "x9",
        "x10",
        "d1",
        "d2",
        "d3",
    ]

    etiquetas = {
        "c1_lugar": "1.1. Lugar",
        "c1_personajes": "1.1. Personajes (separados por comas)",
        "c1_tiempo": "1.1. Tiempo",
        "c2_accion1": "1.2. Acción 1",
        "c2_accion2": "1.2. Acción 2",
        "c2_accion3": "1.2. Acción 3",
        "c5": "1.3. Resumen",
        "dp1": "2.2. Aquellos",
        "dp2": "2.2. Mi",
        "dp3": "2.2. Nadie",
        "s1": "3.1. Frío / calor",
        "s2": "3.1. Perro, gato, caballo",
        "s3": "3.1. Hoja (árbol / papel)",
        "s4": "3.1. Rueda y volante respecto a coche",
        "s5": "3.1. León, tigre, pantera",
        "sd1": "3.2. Polisemia",
        "sd2": "3.2. Homonimia",
        "sd3": "3.2. Hiperónimo",
        "sd4": "3.2. Campo semántico",
        "t1": "4.1. Texto A - Tipo de texto",
        "t2": "4.1. Texto B - Tipo de texto",
        "t3": "4.1. Texto C - Tipo de texto",
        "t4": "4.2. Finalidad de uno de los textos",
        "l1": "5.1. Número de versos",
        "l2": "5.2. Arte mayor o menor",
        "l3": "5.3. Esquema métrico",
        "l4": "5.4. Tipo de rima",
        "l5": "5.5. Sinalefa",
        "l6": "5.6. Personificación",
        "x1": "6.1. Buenas tardes",
        "x2": "6.1. Llueve mucho hoy",
        "x3": "6.1. ¡Qué alegría!",
        "x4": "6.1. No hablar en clase",
        "x5": "6.1. El perro ladra",
        "x6": "6.2. ¿Vienes conmigo?",
        "x7": "6.2. Ojalá apruebe el examen",
        "x8": "6.2. ¡Qué frío hace!",
        "x9": "6.2. Mañana iremos al cine",
        "x10": "6.2. Cierra la puerta",
        "d1": "7.1. Interlocutores (separados por comas)",
        "d2": "7.2. Número de intervenciones",
        "d3": "7.3. Estilo indirecto",
    }

    for clave in orden:
        if clave in respuestas:
            salida.append(
                (
                    etiquetas.get(clave, clave),
                    respuestas.get(clave, "")
                )
            )

    # Añadir cualquier respuesta que no estuviera en la lista de orden.
    for clave, valor in respuestas.items():
        if clave not in orden:
            salida.append((clave, valor))

    return salida


# ==============================================================
# CARGA CSV PARA DASHBOARD
# ==============================================================

def cargar_resultados():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(
            columns=[
                "fecha", "nombre", "curso",
                *PESOS.keys(),
                "nota_inicial",
                "faltas_ortografia",
                "descuento_ortografia",
                "nota_final",
            ]
        )

    try:
        return pd.read_csv(CSV_FILE)
    except Exception:
        return pd.DataFrame()


# ==============================================================
# CABECERA
# ==============================================================

st.markdown(
    '<div class="titulo-principal">📚 Evaluación inicial de Lengua</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitulo">2.º ESO · Lengua Castellana y Literatura · Curso 2026-2027</div>',
    unsafe_allow_html=True,
)


# ==============================================================
# RESULTADO DESPUÉS DE ENVIAR
# ============================================================== 

if st.session_state.get("examen_enviado", False):
    nombre = st.session_state["nombre"]
    curso = st.session_state["curso"]
    puntos = st.session_state["puntos"]
    nota_inicial = st.session_state["nota_inicial"]
    faltas = st.session_state["faltas"]
    descuento = st.session_state["descuento"]
    nota_final = st.session_state["nota_final"]
    respuestas = st.session_state["respuestas"]

    st.success("✅ Examen enviado correctamente.")

    st.metric("NOTA FINAL", f"{nota_final:.2f} / 10")
    st.caption("La puntuación de los apartados suma 10,5 puntos en el examen original y se convierte proporcionalmente a una nota sobre 10.")

    st.subheader("Resultado por apartados")

    claves = list(PESOS.keys())
    for inicio in range(0, len(claves), 4):
        cols = st.columns(4)
        for col, clave in zip(cols, claves[inicio:inicio + 4]):
            col.metric(
                NOMBRES[clave],
                f"{puntos[clave]:.2f}/{PESOS[clave]:.1f}"
            )

    st.divider()

    st.subheader("📄 Entrega para Classroom")
    st.write(
        "Descarga el PDF y súbelo directamente a la tarea de Classroom. "
        "El PDF se genera sin campos de formulario editables."
    )

    perfil = generar_perfil(puntos)
    respuestas_pdf = preparar_respuestas_pdf(respuestas)

    try:
        pdf_file = generar_pdf(
            nombre=nombre,
            curso=curso,
            resultados=puntos,
            respuestas=respuestas_pdf,
            faltas_ortografia=faltas,
            descuento_ortografia=descuento,
            nota_inicial=nota_inicial,
            nota_final=nota_final,
        )

        with open(pdf_file, "rb") as archivo:
            pdf_bytes = archivo.read()

        nombre_pdf = os.path.basename(pdf_file)

        st.download_button(
            "⬇️ DESCARGAR PDF PARA CLASSROOM",
            data=pdf_bytes,
            file_name=nombre_pdf,
            mime="application/pdf",
            use_container_width=True,
        )

    except Exception as error:
        st.error("No se pudo generar el PDF.")
        st.exception(error)

    st.divider()

    st.caption(
        f"Ortografía detectada automáticamente: {faltas} falta(s). "
        f"Descuento aplicado: -{descuento:.2f}."
    )

    with st.expander("Ver perfil competencial"):
        for clave, info in perfil.items():
            st.write(
                f"**{info['nombre']}**: {info['nota']:.2f}/10 — {info['nivel']}"
            )

    st.divider()

    # CSV individual, solo como apoyo.
    fila = pd.DataFrame([{
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nombre": nombre,
        "curso": curso,
        **puntos,
        "puntuacion_bruta": round(sum(puntos.values()), 2),
        "nota_inicial": nota_inicial,
        "faltas_ortografia": faltas,
        "descuento_ortografia": descuento,
        "nota_final": nota_final,
    }])

    st.download_button(
        "📊 Descargar resultado individual en CSV",
        data=fila.to_csv(index=False, encoding="utf-8-sig"),
        file_name="resultado_2ESO.csv",
        mime="text/csv",
        use_container_width=True,
    )

    if st.button("🔄 Volver al inicio", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.stop()


# ==============================================================
# DATOS DEL ALUMNO
# ============================================================== 

st.subheader("Datos del alumno")

nombre = st.text_input(
    "Nombre y apellidos",
    placeholder="Escribe tu nombre y apellidos"
)

curso = st.selectbox(
    "Grupo",
    ["", "2º A", "2º B", "2º C", "2º D"]
)

if not nombre.strip():
    st.info("Escribe tu nombre y apellidos para comenzar.")
    st.stop()

if not curso:
    st.info("Selecciona tu grupo.")
    st.stop()


# ==============================================================
# FORMULARIO DEL EXAMEN
# ============================================================== 

with st.form("examen_2eso"):
    respuestas = {}

    # ----------------------------------------------------------
    # 1. COMPRENSIÓN
    # ----------------------------------------------------------
    st.header("1. Comprensión lectora — 2 puntos")
    st.write(EXAM["comprension"]["texto"])

    for pregunta in EXAM["comprension"]["preguntas"]:
        pid = pregunta["id"]
        tipo = pregunta.get("tipo", "texto")

        if tipo == "lista" or pid == "c5":
            valor = st.text_area(
                pregunta["enunciado"],
                help=pregunta.get("ayuda", ""),
                key=pid,
                height=80 if pid == "c5" else 65,
            )
        else:
            valor = st.text_input(
                pregunta["enunciado"],
                help=pregunta.get("ayuda", ""),
                key=pid,
            )

        respuestas[pid] = valor

    # ----------------------------------------------------------
    # 2. MORFOLOGÍA
    # ----------------------------------------------------------
    st.header("2. Morfología y categorías gramaticales — 2,5 puntos")

    for palabra in EXAM["morfologia"]:
        st.subheader(palabra["palabra"])

        for campo in palabra["campos"]:
            pid = palabra["id"]
            key = f"{pid}_{campo}"

            if campo == "Estructura de la palabra":
                valor = st.selectbox(
                    campo,
                    ["", "simple", "compuesta", "derivada", "parasintética"],
                    key=key,
                )
            elif campo == "V / I":
                valor = st.selectbox(
                    campo,
                    ["", "variable", "invariable"],
                    key=key,
                )
            else:
                valor = st.text_input(
                    campo,
                    help=(
                        "En 'Morfemas' puedes separarlos con comas. "
                        "En 'Categoría gramatical completa' escribe los rasgos separados por comas."
                    ),
                    key=key,
                )

            respuestas[key] = valor

        st.divider()

    st.subheader("2.2. Determinantes y pronombres — 0,5 puntos")

    for pregunta in EXAM["determinantes_pronombres"]:
        pid = pregunta["id"]
        st.write(f"**{pregunta['frase']}**")
        respuestas[pid] = st.selectbox(
            pregunta["enunciado"],
            ["", "determinante", "pronombre"],
            key=pid,
        )

    # ----------------------------------------------------------
    # 3. SEMÁNTICA
    # ----------------------------------------------------------
    st.header("3. Semántica — 1,5 puntos")

    opciones_semantica = [
        "",
        "antonimia",
        "sinonimia",
        "campo semántico",
        "polisemia",
        "homonimia",
        "meronimia",
        "hipónimos",
        "hiperónimo",
    ]

    for pregunta in EXAM["semantica"]:
        pid = pregunta["id"]
        st.write(f"**{pregunta['elemento']}**")
        respuestas[pid] = st.selectbox(
            pregunta["enunciado"],
            opciones_semantica,
            key=pid,
        )

    st.subheader("3.2. Explica con definición y ejemplo — 1 punto")

    for pid, concepto in [
        ("sd1", "Polisemia"),
        ("sd2", "Homonimia"),
        ("sd3", "Hiperónimo"),
        ("sd4", "Campo semántico"),
    ]:
        respuestas[pid] = st.text_area(
            concepto,
            key=pid,
            height=75,
        )

    # ----------------------------------------------------------
    # 4. TEXTOS
    # ----------------------------------------------------------
    st.header("4. Textos — 1 punto")

    st.write("Lee los siguientes textos:")
    for letra, texto in [
        ("A", "Apaga el horno y deja reposar la masa durante diez minutos antes de usarla."),
        ("B", "Los mamíferos son animales vertebrados que alimentan a sus crías con leche."),
        ("C", "Reciclar ayuda a reducir la contaminación y cuidar el medio ambiente."),
    ]:
        st.markdown(f"**Texto {letra}:** {texto}")

    opciones_textos = [
        "",
        "narrativo",
        "descriptivo",
        "expositivo",
        "argumentativo",
        "instructivo",
        "dialogado",
    ]

    for pid, texto_nombre in [
        ("t1", "Texto A → Tipo de texto"),
        ("t2", "Texto B → Tipo de texto"),
        ("t3", "Texto C → Tipo de texto"),
    ]:
        respuestas[pid] = st.selectbox(
            texto_nombre,
            opciones_textos,
            key=pid,
        )

    respuestas["t4"] = st.text_area(
        "4.2. Explica la finalidad de UNO de los textos.",
        key="t4",
        height=80,
    )

    # ----------------------------------------------------------
    # 5. LITERATURA
    # ----------------------------------------------------------
    st.header("5. Literatura — 2 puntos")

    poema = next(
        item for item in EXAM["literatura"]
        if item.get("tipo") == "poema"
    )

    st.markdown(f"**{poema['enunciado']}**")
    for verso in poema["versos"]:
        st.markdown(verso + "  ")

    respuestas["l1"] = st.selectbox(
        "5.1. Número de versos",
        ["", "2", "3", "4", "5", "6", "7", "8"],
        key="l1",
    )

    respuestas["l2"] = st.selectbox(
        "5.2. ¿Es de arte mayor o de arte menor?",
        ["", "arte menor", "arte mayor"],
        key="l2",
    )

    respuestas["l3"] = st.text_input(
        "5.3. Esquema métrico",
        key="l3",
        help="Escribe el esquema métrico. Se aceptan las alternativas previstas en el examen.",
    )

    respuestas["l4"] = st.selectbox(
        "5.4. Tipo de rima",
        ["", "asonante", "consonante"],
        key="l4",
    )

    respuestas["l5"] = st.text_input(
        "5.5. Localiza una sinalefa del poema y escribe las dos palabras exactas que la forman.",
        help="Ejemplos del poema: suave en, y el, solo en, la escuela.",
        key="l5",
    )

    respuestas["l6"] = st.text_input(
        "5.6. Localiza una personificación del poema y escribe las palabras exactas que la forman.",
        help="Ejemplo: el viento juega.",
        key="l6",
    )

    # ----------------------------------------------------------
    # 6. SINTAXIS
    # ----------------------------------------------------------
    st.header("6. Sintaxis — 1 punto")

    opciones_frase = ["", "frase", "oración"]
    opciones_modalidad = [
        "",
        "enunciativa",
        "interrogativa",
        "exclamativa",
        "desiderativa",
        "exhortativa",
    ]

    for pregunta in EXAM["sintaxis"]:
        pid = pregunta["id"]
        st.write(f"**{pregunta['frase']}**")

        if pid in {"x1", "x2", "x3", "x4", "x5"}:
            opciones = opciones_frase
        else:
            opciones = opciones_modalidad

        respuestas[pid] = st.selectbox(
            pregunta["enunciado"],
            opciones,
            key=pid,
        )

    # ----------------------------------------------------------
    # 7. DIÁLOGO
    # ----------------------------------------------------------
    st.header("7. Diálogo — 0,5 puntos")

    st.markdown(
        EXAM["dialogo"]["texto"].replace("\n", "  \n")
    )

    for pregunta in EXAM["dialogo"]["preguntas"]:
        pid = pregunta["id"]
        tipo = pregunta.get("tipo", "")

        if tipo == "lista":
            respuestas[pid] = st.text_area(
                pregunta["enunciado"],
                help=pregunta.get("ayuda", ""),
                key=pid,
                height=60,
            )
        elif tipo == "estilo_indirecto":
            respuestas[pid] = st.text_area(
                pregunta["enunciado"],
                help="Escribe una oración completa en estilo indirecto.",
                key=pid,
                height=90,
            )
        else:
            respuestas[pid] = st.text_input(
                pregunta["enunciado"],
                key=pid,
            )

    st.divider()

    enviar = st.form_submit_button(
        "📤 ENVIAR EXAMEN",
        use_container_width=True,
    )


# ==============================================================
# PROCESAR ENVÍO
# ============================================================== 

if enviar:
    puntos, nota_inicial, detalle = corregir_examen(respuestas)

    todos_los_textos = list(respuestas.values())
    faltas, descuento = detectar_ortografia(todos_los_textos)

    nota_final = round(
        max(0.0, nota_inicial - descuento),
        2,
    )

    guardado = guardar_resultado(
        nombre=nombre.strip(),
        curso=curso,
        puntos=puntos,
        nota_inicial=nota_inicial,
        faltas=faltas,
        descuento=descuento,
        nota_final=nota_final,
    )

    if not guardado:
        st.stop()

    st.session_state["examen_enviado"] = True
    st.session_state["nombre"] = nombre.strip()
    st.session_state["curso"] = curso
    st.session_state["puntos"] = puntos
    st.session_state["nota_inicial"] = nota_inicial
    st.session_state["faltas"] = faltas
    st.session_state["descuento"] = descuento
    st.session_state["nota_final"] = nota_final
    st.session_state["respuestas"] = respuestas
    st.session_state["detalle"] = detalle

    st.rerun()


# ==============================================================
# DASHBOARD OCULTO/INDEPENDIENTE PARA EL PROFESOR
# ============================================================== 
# Se deja accesible al final para no interferir en el examen.

with st.expander("📊 Consulta docente"):
    df = cargar_resultados()

    if df.empty:
        st.info("Todavía no hay resultados disponibles en results.csv en esta sesión del servidor.")
    else:
        st.write(f"Resultados disponibles: **{len(df)}**")

        if "nota_final" in df.columns:
            notas = pd.to_numeric(df["nota_final"], errors="coerce")
            st.write(f"Media: **{notas.mean():.2f}**")
            st.write(f"Aprobados: **{int((notas >= 5).sum())}**")
            st.write(f"Suspensos: **{int((notas < 5).sum())}**")

        grafica = comparativa_clase(df)
        if grafica is not None:
            st.plotly_chart(grafica, use_container_width=True)

        if "nombre" in df.columns:
            alumno = st.selectbox(
                "Selecciona alumno",
                sorted(df["nombre"].dropna().unique().tolist()),
                key="docente_alumno",
            )

            fila = df[df["nombre"] == alumno].iloc[-1]
            st.dataframe(fila.to_frame("Resultado"), use_container_width=True)

            grafica_individual = comparativa(fila, df)
            if grafica_individual is not None:
                st.plotly_chart(grafica_individual, use_container_width=True)
