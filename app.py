import os
import re
import unicodedata
from datetime import datetime

import pandas as pd
import streamlit as st

from analytics import (
    radar_chart,
    comparativa,
    generar_perfil
)

from pdf_report import generar_pdf

from examen2ESO import EXAMEN


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Evaluación Inicial - Lengua 2º ESO",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# FUNCIONES GENERALES
# ============================================================

def normalizar(texto):
    if texto is None:
        return ""

    texto = str(texto).lower().strip()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto


def normalizar_lista(texto):
    """
    Convierte respuestas del tipo:

    Lucía, Carlos
    Lucía
    Carlos

    en un texto normalizado fácil de comprobar.
    """

    texto = normalizar(texto)

    texto = texto.replace(
        "\n",
        " "
    )

    texto = re.sub(
        r"\b(?:y|e)\b",
        ",",
        texto
    )

    texto = texto.replace(
        ";",
        ","
    )

    texto = re.sub(
        r",+",
        ",",
        texto
    )

    return texto


def contiene_respuesta(respuesta, criterios):
    respuesta_norm = normalizar(respuesta)

    for criterio in criterios:
        if normalizar(criterio) in respuesta_norm:
            return True

    return False


def contiene_todas(respuesta, criterios):
    respuesta_norm = normalizar_lista(respuesta)

    return all(
        normalizar(criterio) in respuesta_norm
        for criterio in criterios
    )


def corregir_exacta(respuesta, correcta):
    return normalizar(respuesta) == normalizar(correcta)


def corregir_lista(respuesta, criterios):
    """
    Corrección para preguntas con varias respuestas.
    Devuelve proporcionalmente los puntos según los
    elementos encontrados.
    """

    if not respuesta:
        return 0

    respuesta_norm = normalizar_lista(respuesta)

    encontrados = 0

    for criterio in criterios:
        if normalizar(criterio) in respuesta_norm:
            encontrados += 1

    return encontrados / len(criterios)


def corregir_componentes(respuesta, esperadas):
    """
    Comprueba varios elementos dentro de una respuesta.

    Se utiliza, por ejemplo, para:
    - morfemas
    - categoría gramatical completa
    """

    respuesta_norm = normalizar(respuesta)

    if not respuesta_norm:
        return 0

    encontrados = 0

    for esperado in esperadas:
        if normalizar(esperado) in respuesta_norm:
            encontrados += 1

    return encontrados / len(esperadas)


def normalizar_metrica(texto):
    """
    Convierte:

    14A 14B 14B 14A
    14A, 14B, 14B, 14A
    14A/14B/14B/14A

    en:

    14a14b14b14a
    """

    texto = normalizar(texto)

    texto = re.sub(
        r"[\s,;/.-]+",
        "",
        texto
    )

    return texto


def corregir_metrica(respuesta, pregunta):
    respuesta_norm = normalizar_metrica(respuesta)

    if not respuesta_norm:
        return False

    alternativas = pregunta.get(
        "alternativas",
        [pregunta.get("respuesta", "")]
    )

    for alternativa in alternativas:
        if respuesta_norm == normalizar_metrica(alternativa):
            return True

    return False


# ============================================================
# ORTOGRAFÍA
# ============================================================

def detectar_ortografia(texto):
    """
    Intenta utilizar LanguageTool.

    Si no está disponible o produce un error,
    simplemente no aplica descuento.
    """

    if not texto or not texto.strip():
        return 0, 0.0

    try:
        import language_tool_python

        herramienta = language_tool_python.LanguageTool(
            "es"
        )

        errores = herramienta.check(texto)

        faltas = 0
        tildes = 0

        for error in errores:
            mensaje = normalizar(
                getattr(
                    error,
                    "message",
                    ""
                )
            )

            categoria = normalizar(
                getattr(
                    error,
                    "category",
                    ""
                )
            )

            if (
                "accent" in categoria
                or "tilde" in mensaje
                or "acento" in mensaje
            ):
                tildes += 1
            else:
                faltas += 1

        descuento = (
            faltas * 0.20
            + tildes * 0.10
        )

        descuento = min(
            descuento,
            2.0
        )

        return faltas, descuento

    except Exception:
        return 0, 0.0


# ============================================================
# PUNTUACIONES MÁXIMAS
# ============================================================

def calcular_maximos():
    examen = EXAMEN["2ESO"]

    max_comprension = sum(
        pregunta["puntos"]
        for pregunta in examen["comprension"]["preguntas"]
    )

    max_morfologia = sum(
        palabra["puntos"]
        for palabra in examen["morfologia"]
    )

    max_dp = sum(
        pregunta["puntos"]
        for pregunta in examen["determinantes_pronombres"]
    )

    max_semantica = sum(
        pregunta["puntos"]
        for pregunta in examen["semantica"]
    )

    max_textos = sum(
        pregunta["puntos"]
        for pregunta in examen["textos"]
    )

    max_literatura = sum(
        pregunta["puntos"]
        for pregunta in examen["literatura"]
        if pregunta.get("id") != "l0"
    )

    max_sintaxis = sum(
        pregunta["puntos"]
        for pregunta in examen["sintaxis"]
    )

    max_dialogo = sum(
        pregunta["puntos"]
        for pregunta in examen["dialogo"]["preguntas"]
    )

    return {
        "comprension": max_comprension,
        "morfologia": max_morfologia + max_dp,
        "semantica": max_semantica,
        "textos": max_textos,
        "literatura": max_literatura,
        "sintaxis": max_sintaxis + max_dialogo
    }


# ============================================================
# CORRECCIÓN DEL EXAMEN
# ============================================================

def corregir_examen(respuestas):
    examen = EXAMEN["2ESO"]

    obtenidos = {
        "comprension": 0.0,
        "morfologia": 0.0,
        "semantica": 0.0,
        "textos": 0.0,
        "literatura": 0.0,
        "sintaxis": 0.0
    }

    # --------------------------------------------------------
    # COMPRENSIÓN
    # --------------------------------------------------------

    acciones_usadas = set()

    for pregunta in examen["comprension"]["preguntas"]:

        pid = pregunta["id"]

        respuesta = respuestas.get(
            pid,
            ""
        )

        puntos = pregunta["puntos"]

        if pregunta["tipo"] == "lista":

            proporcion = corregir_lista(
                respuesta,
                pregunta["criterios"]
            )

            obtenidos["comprension"] += (
                puntos * proporcion
            )

        elif pregunta["tipo"] == "accion":

            respuesta_norm = normalizar(
                respuesta
            )

            if respuesta_norm in [
                normalizar(c)
                for c in pregunta["criterios"]
            ]:

                # Evita que se repita exactamente
                # la misma acción en los tres huecos.
                if respuesta_norm not in acciones_usadas:
                    obtenidos["comprension"] += puntos
                    acciones_usadas.add(
                        respuesta_norm
                    )

        else:

            if contiene_respuesta(
                respuesta,
                pregunta["criterios"]
            ):
                obtenidos["comprension"] += puntos

    # --------------------------------------------------------
    # MORFOLOGÍA
    # --------------------------------------------------------

    for palabra in examen["morfologia"]:

        respuestas_palabra = respuestas.get(
            palabra["id"],
            {}
        )

        # Cada palabra vale 0.50 puntos.
        # Reparto:
        # Lexema = 0.10
        # Morfemas = 0.10
        # Estructura = 0.10
        # Categoría = 0.15
        # V/I = 0.05

        reparto = {
            "Lexema": 0.10,
            "Morfemas": 0.10,
            "Estructura de la palabra": 0.10,
            "Categoría gramatical completa": 0.15,
            "V / I": 0.05
        }

        for campo, puntos in reparto.items():

            respuesta = respuestas_palabra.get(
                campo,
                ""
            )

            esperadas = palabra["respuestas"].get(
                campo,
                []
            )

            if campo == "Estructura de la palabra":
                if corregir_exacta(
                    respuesta,
                    esperadas[0]
                ):
                    obtenidos["morfologia"] += puntos

            elif campo == "V / I":
                if corregir_exacta(
                    respuesta,
                    esperadas[0]
                ):
                    obtenidos["morfologia"] += puntos

            else:
                proporcion = corregir_componentes(
                    respuesta,
                    esperadas
                )

                obtenidos["morfologia"] += (
                    puntos * proporcion
                )

    # --------------------------------------------------------
    # DETERMINANTES / PRONOMBRES
    # --------------------------------------------------------

    for pregunta in examen["determinantes_pronombres"]:

        respuesta = respuestas.get(
            pregunta["id"],
            ""
        )

        if corregir_exacta(
            respuesta,
            pregunta["respuesta"]
        ):
            obtenidos["morfologia"] += pregunta["puntos"]

    # --------------------------------------------------------
    # SEMÁNTICA
    # --------------------------------------------------------

    for pregunta in examen["semantica"]:

        respuesta = respuestas.get(
            pregunta["id"],
            ""
        )

        if corregir_exacta(
            respuesta,
            pregunta["respuesta"]
        ):
            obtenidos["semantica"] += pregunta["puntos"]

    # --------------------------------------------------------
    # TEXTOS
    # --------------------------------------------------------

    for pregunta in examen["textos"]:

        respuesta = respuestas.get(
            pregunta["id"],
            ""
        )

        if corregir_exacta(
            respuesta,
            pregunta["respuesta"]
        ):
            obtenidos["textos"] += pregunta["puntos"]

    # --------------------------------------------------------
    # LITERATURA
    # --------------------------------------------------------

    for pregunta in examen["literatura"]:

        pid = pregunta.get("id")

        if pid == "l0":
            continue

        respuesta = respuestas.get(
            pid,
            ""
        )

        puntos = pregunta["puntos"]

        if pregunta.get("tipo") == "sinalefa":

            respuestas_validas = [
                normalizar(r)
                for r in pregunta[
                    "respuestas_validas"
                ]
            ]

            if normalizar(respuesta) in respuestas_validas:
                obtenidos["literatura"] += puntos

        elif pregunta.get("tipo") == "personificacion":

            respuestas_validas = [
                normalizar(r)
                for r in pregunta[
                    "respuestas_validas"
                ]
            ]

            if normalizar(respuesta) in respuestas_validas:
                obtenidos["literatura"] += puntos

        elif pid == "l3":

            if corregir_metrica(
                respuesta,
                pregunta
            ):
                obtenidos["literatura"] += puntos

        else:

            if corregir_exacta(
                respuesta,
                pregunta["respuesta"]
            ):
                obtenidos["literatura"] += puntos

    # --------------------------------------------------------
    # SINTAXIS
    # --------------------------------------------------------

    for pregunta in examen["sintaxis"]:

        respuesta = respuestas.get(
            pregunta["id"],
            ""
        )

        if corregir_exacta(
            respuesta,
            pregunta["respuesta"]
        ):
            obtenidos["sintaxis"] += pregunta["puntos"]

    # --------------------------------------------------------
    # DIÁLOGO
    # --------------------------------------------------------

    for pregunta in examen["dialogo"]["preguntas"]:

        pid = pregunta["id"]

        respuesta = respuestas.get(
            pid,
            ""
        )

        puntos = pregunta["puntos"]

        if pregunta.get("tipo") == "lista":

            proporcion = corregir_lista(
                respuesta,
                pregunta["criterios"]
            )

            obtenidos["sintaxis"] += (
                puntos * proporcion
            )

        elif pregunta.get("tipo") == "estilo_indirecto":

            texto = normalizar(
                respuesta
            )

            requisitos = [
                "carlos",
                "dijo",
                "habia hecho"
            ]

            if all(
                requisito in texto
                for requisito in requisitos
            ):
                obtenidos["sintaxis"] += puntos

        else:

            if corregir_exacta(
                respuesta,
                pregunta["respuesta"]
            ):
                obtenidos["sintaxis"] += puntos

    # --------------------------------------------------------
    # NORMALIZACIÓN A 10
    # --------------------------------------------------------

    maximos = calcular_maximos()

    max_total = sum(
        maximos.values()
    )

    total_obtenido = sum(
        obtenidos.values()
    )

    nota_inicial = (
        total_obtenido / max_total * 10
        if max_total > 0
        else 0
    )

    # --------------------------------------------------------
    # NOTAS POR COMPETENCIA
    # --------------------------------------------------------

    max_comprension_total = (
        maximos["comprension"]
        + maximos["textos"]
    )

    comprension_total = (
        obtenidos["comprension"]
        + obtenidos["textos"]
    )

    comprension = (
        comprension_total
        / max_comprension_total
        * 10
        if max_comprension_total > 0
        else 0
    )

    morfologia = (
        obtenidos["morfologia"]
        / maximos["morfologia"]
        * 10
        if maximos["morfologia"] > 0
        else 0
    )

    semantica = (
        obtenidos["semantica"]
        / maximos["semantica"]
        * 10
        if maximos["semantica"] > 0
        else 0
    )

    literatura = (
        obtenidos["literatura"]
        / maximos["literatura"]
        * 10
        if maximos["literatura"] > 0
        else 0
    )

    sintaxis = (
        obtenidos["sintaxis"]
        / maximos["sintaxis"]
        * 10
        if maximos["sintaxis"] > 0
        else 0
    )

    scores = {
        "comprension": round(
            min(comprension, 10),
            2
        ),
        "morfologia": round(
            min(morfologia, 10),
            2
        ),
        "semantica": round(
            min(semantica, 10),
            2
        ),
        "literatura": round(
            min(literatura, 10),
            2
        ),
        "sintaxis": round(
            min(sintaxis, 10),
            2
        )
    }

    return (
        scores,
        round(nota_inicial, 2),
        obtenidos
    )


# ============================================================
# CARGAR RESULTADOS
# ============================================================

ARCHIVO_RESULTADOS = "results.csv"

columnas_base = [
    "fecha",
    "nombre",
    "curso",
    "comprension",
    "morfologia",
    "semantica",
    "literatura",
    "sintaxis",
    "nota_inicial",
    "faltas_ortografia",
    "descuento_ortografia",
    "nota_final"
]

if os.path.exists(ARCHIVO_RESULTADOS):

    try:
        df_resultados = pd.read_csv(
            ARCHIVO_RESULTADOS
        )
    except Exception:
        df_resultados = pd.DataFrame(
            columns=columnas_base
        )

else:
    df_resultados = pd.DataFrame(
        columns=columnas_base
    )


for columna in columnas_base:

    if columna not in df_resultados.columns:
        df_resultados[columna] = 0


# ============================================================
# CABECERA
# ============================================================

st.title(
    "📚 Evaluación Inicial de Lengua Castellana y Literatura"
)

st.caption(
    "Prueba diagnóstica automática · 2.º ESO"
)


# ============================================================
# MENÚ
# ============================================================

opcion = st.sidebar.radio(
    "Menú",
    [
        "📝 Realizar evaluación",
        "📊 Resultados de la clase",
        "👤 Historial del alumno"
    ]
)


# ============================================================
# REALIZAR EVALUACIÓN
# ============================================================

if opcion == "📝 Realizar evaluación":

    st.header(
        "Datos del alumno"
    )

    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input(
            "Nombre y apellidos",
            key="nombre_alumno"
        )

    with col2:
        curso = st.text_input(
            "Curso",
            value="2º ESO",
            key="curso_alumno"
        )

    st.divider()

    respuestas = {}

    # ========================================================
    # 1. COMPRENSIÓN
    # ========================================================

    st.header("1. Comprensión lectora")

    st.markdown(
        f"### Texto\n\n{EXAMEN['2ESO']['comprension']['texto']}"
    )

    st.subheader("1.1. Lugar, personajes y tiempo")

    for pregunta in EXAMEN["2ESO"]["comprension"]["preguntas"]:

        pid = pregunta["id"]

        if pid.startswith("c1_"):

            st.markdown(
                f"**{pregunta['enunciado']}**"
            )

            if pregunta.get("tipo") == "lista":

                respuestas[pid] = st.text_input(
                    pregunta["ayuda"],
                    key=pid
                )

            else:

                respuestas[pid] = st.text_input(
                    pregunta["ayuda"],
                    key=pid
                )

    st.subheader("1.2. Acciones")

    st.info(
        "Escribe una acción que aparezca en el texto y "
        "ponla en infinitivo. Debes escribir una acción "
        "diferente en cada hueco."
    )

    acciones = [
        pregunta
        for pregunta
        in EXAMEN["2ESO"]["comprension"]["preguntas"]
        if pregunta["tipo"] == "accion"
    ]

    for numero, pregunta in enumerate(
        acciones,
        start=1
    ):

        st.markdown(
            f"**{pregunta['enunciado']}**"
        )

        respuestas[pregunta["id"]] = st.text_input(
            pregunta["ayuda"],
            key=pregunta["id"]
        )

    # ========================================================
    # 2. MORFOLOGÍA
    # ========================================================

    st.divider()

    st.header("2. Morfología")

    st.info(
        "Escribe las respuestas en los campos de texto. "
        "En «Estructura de la palabra» y «V / I» "
        "elige la opción correcta."
    )

    for palabra in EXAMEN["2ESO"]["morfologia"]:

        st.subheader(
            f"Palabra: «{palabra['palabra']}»"
        )

        respuestas_palabra = {}

        col1, col2 = st.columns(2)

        with col1:

            respuestas_palabra["Lexema"] = st.text_input(
                "Lexema",
                key=f"{palabra['id']}_lexema"
            )

            respuestas_palabra["Morfemas"] = st.text_input(
                "Morfemas",
                help="Puedes separarlos con +, espacios o comas.",
                key=f"{palabra['id']}_morfemas"
            )

            respuestas_palabra[
                "Estructura de la palabra"
            ] = st.selectbox(
                "Estructura de la palabra",
                [
                    "",
                    "simple",
                    "compuesta",
                    "derivada",
                    "parasintética"
                ],
                key=f"{palabra['id']}_estructura"
            )

        with col2:

            respuestas_palabra[
                "Categoría gramatical completa"
            ] = st.text_input(
                "Categoría gramatical completa",
                help=(
                    "Escribe toda la información gramatical "
                    "que conozcas, por ejemplo: sustantivo, "
                    "común, concreto, masculino, singular."
                ),
                key=f"{palabra['id']}_categoria"
            )

            respuestas_palabra["V / I"] = st.selectbox(
                "V / I",
                [
                    "",
                    "variable",
                    "invariable"
                ],
                key=f"{palabra['id']}_vi"
            )

        respuestas[palabra["id"]] = respuestas_palabra

    # ========================================================
    # 2.1 DETERMINANTES Y PRONOMBRES
    # ========================================================

    st.subheader(
        "2.1. Determinantes y pronombres"
    )

    opciones_dp = [
        "",
        "determinante",
        "pronombre"
    ]

    for pregunta in EXAMEN[
        "2ESO"
    ]["determinantes_pronombres"]:

        st.markdown(
            f"**{pregunta['frase']}**"
        )

        respuestas[pregunta["id"]] = st.selectbox(
            pregunta["enunciado"],
            opciones_dp,
            key=pregunta["id"]
        )

    # ========================================================
    # 3. SEMÁNTICA
    # ========================================================

    st.divider()

    st.header("3. Semántica")

    opciones_semantica = [
        "",
        "antonimia",
        "campo semántico",
        "polisemia",
        "meronimia",
        "hipónimos",
        "sinonimia",
        "homonimia",
        "hiperonimia"
    ]

    for pregunta in EXAMEN[
        "2ESO"
    ]["semantica"]:

        st.markdown(
            f"**{pregunta['elemento']}**"
        )

        respuestas[pregunta["id"]] = st.selectbox(
            pregunta["enunciado"],
            opciones_semantica,
            key=pregunta["id"]
        )

    # ========================================================
    # 4. TEXTOS
    # ========================================================

    st.divider()

    st.header(
        "4. Tipología textual"
    )

    opciones_textos = [
        "",
        "narrativo",
        "descriptivo",
        "expositivo",
        "argumentativo",
        "instructivo",
        "dialogado"
    ]

    for pregunta in EXAMEN[
        "2ESO"
    ]["textos"]:

        st.markdown(
            f"**{pregunta['texto']}**"
        )

        respuestas[pregunta["id"]] = st.selectbox(
            pregunta["enunciado"],
            opciones_textos,
            key=pregunta["id"]
        )

    # ========================================================
    # 5. LITERATURA
    # ========================================================

    st.divider()

    st.header(
        "5. Literatura y métrica"
    )

    poema = EXAMEN[
        "2ESO"
    ]["literatura"][0]

    st.markdown(
        "### Poema"
    )

    for verso in poema["versos"]:
        st.markdown(
            f"> {verso}"
        )

    preguntas_literatura = EXAMEN[
        "2ESO"
    ]["literatura"][1:]

    for pregunta in preguntas_literatura:

        pid = pregunta["id"]

        st.markdown(
            f"**{pregunta['enunciado']}**"
        )

        if pid == "l1":

            respuestas[pid] = st.selectbox(
                "Selecciona el número de versos",
                [
                    "",
                    "3",
                    "4",
                    "5",
                    "6"
                ],
                key=pid
            )

        elif pid == "l2":

            respuestas[pid] = st.selectbox(
                "Selecciona la opción",
                [
                    "",
                    "arte menor",
                    "arte mayor"
                ],
                key=pid
            )

        elif pid == "l3":

            respuestas[pid] = st.text_input(
                "Esquema métrico",
                help=(
                    "Escribe, por ejemplo: "
                    "14A 14B 14B 14A. "
                    "También se admiten comas o barras."
                ),
                key=pid
            )

        elif pid == "l4":

            respuestas[pid] = st.selectbox(
                "Selecciona el tipo de rima",
                [
                    "",
                    "asonante",
                    "consonante",
                    "sin rima"
                ],
                key=pid
            )

        elif pid == "l5":

            respuestas[pid] = st.text_input(
                "Escribe las dos palabras exactas",
                help=(
                    "Escribe únicamente las dos palabras "
                    "que forman la sinalefa."
                ),
                key=pid
            )

        elif pid == "l6":

            respuestas[pid] = st.text_input(
                "Escribe las palabras exactas",
                help=(
                    "Escribe únicamente las palabras "
                    "que forman la personificación."
                ),
                key=pid
            )

    # ========================================================
    # 6. SINTAXIS
    # ========================================================

    st.divider()

    st.header(
        "6. Sintaxis"
    )

    opciones_frase_oracion = [
        "",
        "frase",
        "oración"
    ]

    opciones_modalidad = [
        "",
        "enunciativa",
        "interrogativa",
        "exclamativa",
        "desiderativa",
        "exhortativa",
        "dubitativa"
    ]

    for pregunta in EXAMEN[
        "2ESO"
    ]["sintaxis"]:

        st.markdown(
            f"**{pregunta['frase']}**"
        )

        if pregunta["id"] in [
            "x1",
            "x2",
            "x3",
            "x4",
            "x5"
        ]:

            respuestas[pregunta["id"]] = st.selectbox(
                pregunta["enunciado"],
                opciones_frase_oracion,
                key=pregunta["id"]
            )

        else:

            respuestas[pregunta["id"]] = st.selectbox(
                pregunta["enunciado"],
                opciones_modalidad,
                key=pregunta["id"]
            )

    # ========================================================
    # 7. DIÁLOGO
    # ========================================================

    st.divider()

    st.header(
        "7. Texto dialogado"
    )

    st.markdown(
        EXAMEN[
            "2ESO"
        ]["dialogo"]["texto"]
    )

    for pregunta in EXAMEN[
        "2ESO"
    ]["dialogo"]["preguntas"]:

        pid = pregunta["id"]

        st.markdown(
            f"**{pregunta['enunciado']}**"
        )

        if pid == "d1":

            respuestas[pid] = st.text_input(
                pregunta["ayuda"],
                help=(
                    "Ejemplo: Lucía, Carlos. "
                    "También puedes escribirlos en líneas diferentes."
                ),
                key=pid
            )

        elif pid == "d2":

            respuestas[pid] = st.selectbox(
                "Número de intervenciones",
                [
                    "",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8"
                ],
                key=pid
            )

        elif pid == "d3":

            respuestas[pid] = st.text_area(
                "Respuesta",
                key=pid,
                height=100
            )

    # ========================================================
    # BOTÓN CORREGIR
    # ========================================================

    st.divider()

    corregir = st.button(
        "✅ Corregir evaluación",
        type="primary",
        use_container_width=True
    )

    if corregir:

        if not nombre.strip():

            st.error(
                "Introduce el nombre y apellidos del alumno."
            )

        else:

            # ------------------------------------------------
            # Corrección
            # ------------------------------------------------

            scores, nota_inicial, obtenidos = corregir_examen(
                respuestas
            )

            # ------------------------------------------------
            # Texto para ortografía
            # ------------------------------------------------

            texto_para_ortografia = []

            for clave, valor in respuestas.items():

                if isinstance(valor, dict):

                    for subvalor in valor.values():
                        texto_para_ortografia.append(
                            str(subvalor)
                        )

                else:
                    texto_para_ortografia.append(
                        str(valor)
                    )

            texto_completo = " ".join(
                texto_para_ortografia
            )

            faltas, descuento = detectar_ortografia(
                texto_completo
            )

            nota_final = max(
                0,
                nota_inicial - descuento
            )

            # ------------------------------------------------
            # Perfil
            # ------------------------------------------------

            perfil = generar_perfil(
                scores
            )

            # ------------------------------------------------
            # Guardar resultado
            # ------------------------------------------------

            nuevo_resultado = {
                "fecha": datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                ),
                "nombre": nombre,
                "curso": curso,
                "comprension": scores["comprension"],
                "morfologia": scores["morfologia"],
                "semantica": scores["semantica"],
                "literatura": scores["literatura"],
                "sintaxis": scores["sintaxis"],
                "nota_inicial": nota_inicial,
                "faltas_ortografia": faltas,
                "descuento_ortografia": descuento,
                "nota_final": nota_final
            }

            df_nuevo = pd.DataFrame(
                [nuevo_resultado]
            )

            df_resultados = pd.concat(
                [
                    df_resultados,
                    df_nuevo
                ],
                ignore_index=True
            )

            df_resultados.to_csv(
                ARCHIVO_RESULTADOS,
                index=False
            )

            # ------------------------------------------------
            # Resultados
            # ------------------------------------------------

            st.success(
                "Evaluación corregida correctamente."
            )

            st.header(
                f"Resultados de {nombre}"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Nota inicial",
                    f"{nota_inicial:.2f} / 10"
                )

            with col2:
                st.metric(
                    "Descuento ortografía",
                    f"-{descuento:.2f}"
                )

            with col3:
                st.metric(
                    "Nota final",
                    f"{nota_final:.2f} / 10"
                )

            # ------------------------------------------------
            # Competencias
            # ------------------------------------------------

            st.subheader(
                "Perfil competencial"
            )

            col1, col2, col3, col4, col5 = st.columns(5)

            columnas = [
                ("Comprensión", "comprension"),
                ("Morfología", "morfologia"),
                ("Semántica", "semantica"),
                ("Literatura", "literatura"),
                ("Sintaxis", "sintaxis")
            ]

            columnas_st = [
                col1,
                col2,
                col3,
                col4,
                col5
            ]

            for columna_st, (etiqueta, clave) in zip(
                columnas_st,
                columnas
            ):

                with columna_st:
                    st.metric(
                        etiqueta,
                        f"{scores[clave]:.2f}"
                    )

            # ------------------------------------------------
            # Radar
            # ------------------------------------------------

            st.plotly_chart(
                radar_chart(
                    scores,
                    nombre
                ),
                use_container_width=True,
                key="radar_resultado"
            )

            # ------------------------------------------------
            # Perfil escrito
            # ------------------------------------------------

            st.subheader(
                "Observaciones"
            )

            for observacion in perfil:
                st.write(
                    f"• {observacion}"
                )

            # ------------------------------------------------
            # PDF
            # ------------------------------------------------

            st.subheader(
                "Informe individual"
            )

            try:

                pdf_file = generar_pdf(
                    nombre=nombre,
                    curso=curso,
                    scores=scores,
                    nota_inicial=nota_inicial,
                    descuento_ortografia=descuento,
                    nota_final=nota_final,
                    perfil=perfil
                )

                if os.path.exists(pdf_file):

                    with open(
                        pdf_file,
                        "rb"
                    ) as archivo:

                        pdf_bytes = archivo.read()

                    st.download_button(
                        label="📥 Descargar informe PDF",
                        data=pdf_bytes,
                        file_name=os.path.basename(
                            pdf_file
                        ),
                        mime="application/pdf",
                        use_container_width=True,
                        key="download_pdf"
                    )

                else:

                    st.error(
                        "No se ha podido localizar el PDF generado."
                    )

            except Exception as error:

                st.error(
                    f"No se pudo generar el PDF: {error}"
                )


# ============================================================
# RESULTADOS DE LA CLASE
# ============================================================

elif opcion == "📊 Resultados de la clase":

    st.header(
        "📊 Resultados de la clase"
    )

    if df_resultados.empty:

        st.info(
            "Todavía no hay resultados registrados."
        )

    else:

        columnas_mostrar = [
            "nombre",
            "curso",
            "comprension",
            "morfologia",
            "semantica",
            "literatura",
            "sintaxis",
            "nota_inicial",
            "nota_final"
        ]

        columnas_existentes = [
            columna
            for columna in columnas_mostrar
            if columna in df_resultados.columns
        ]

        st.dataframe(
            df_resultados[
                columnas_existentes
            ],
            use_container_width=True,
            hide_index=True
        )

        st.subheader(
            "Media de la clase"
        )

        competencias = [
            "comprension",
            "morfologia",
            "semantica",
            "literatura",
            "sintaxis"
        ]

        medias = {}

        for competencia in competencias:

            medias[competencia] = pd.to_numeric(
                df_resultados[competencia],
                errors="coerce"
            ).fillna(0).mean()

        col1, col2, col3, col4, col5 = st.columns(5)

        for columna, competencia in zip(
            [col1, col2, col3, col4, col5],
            competencias
        ):

            with columna:

                st.metric(
                    competencia.capitalize(),
                    f"{medias[competencia]:.2f}"
                )

        # ----------------------------------------------------
        # Comparativa
        # ----------------------------------------------------

        st.subheader(
            "Comparativa"
        )

        if not df_resultados.empty:

            ultimo = df_resultados.iloc[-1]

            st.plotly_chart(
                comparativa(
                    ultimo,
                    df_resultados
                ),
                use_container_width=True,
                key="comparativa_dashboard"
            )


# ============================================================
# HISTORIAL DEL ALUMNO
# ============================================================

elif opcion == "👤 Historial del alumno":

    st.header(
        "👤 Historial del alumno"
    )

    if df_resultados.empty:

        st.info(
            "Todavía no hay alumnos registrados."
        )

    else:

        nombres = sorted(
            df_resultados["nombre"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        alumno_seleccionado = st.selectbox(
            "Selecciona un alumno",
            nombres,
            key="historial_alumno"
        )

        historial = df_resultados[
            df_resultados["nombre"].astype(str)
            == alumno_seleccionado
        ].copy()

        historial = historial.sort_values(
            "fecha"
        )

        st.subheader(
            f"Historial de {alumno_seleccionado}"
        )

        st.dataframe(
            historial,
            use_container_width=True,
            hide_index=True
        )

        ultimo = historial.iloc[-1]

        scores_historial = {
            "comprension": float(
                ultimo.get("comprension", 0)
            ),
            "morfologia": float(
                ultimo.get("morfologia", 0)
            ),
            "semantica": float(
                ultimo.get("semantica", 0)
            ),
            "literatura": float(
                ultimo.get("literatura", 0)
            ),
            "sintaxis": float(
                ultimo.get("sintaxis", 0)
            )
        }

        st.subheader(
            "Perfil competencial"
        )

        st.plotly_chart(
            radar_chart(
                scores_historial,
                alumno_seleccionado
            ),
            use_container_width=True,
            key="radar_historial"
        )

        st.subheader(
            "Últimas notas"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Nota inicial",
                f"{float(ultimo.get('nota_inicial', 0)):.2f}"
            )

        with col2:
            st.metric(
                "Ortografía",
                f"-{float(ultimo.get('descuento_ortografia', 0)):.2f}"
            )

        with col3:
            st.metric(
                "Nota final",
                f"{float(ultimo.get('nota_final', 0)):.2f}"
            )
