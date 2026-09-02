import streamlit as st
import pandas as pd
from datetime import datetime
import unicodedata
import re
import os

from analytics import (
    radar_chart,
    comparativa,
    generar_perfil
)

from pdf_report import generar_pdf

from examen2ESO import EXAMEN


# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Evaluación Inicial Lengua 2º ESO",
    page_icon="📘",
    layout="wide"
)

st.title(
    "📘 Evaluación Inicial - Lengua Castellana y Literatura"
)

st.caption(
    "2.º ESO"
)


# =========================================================
# CARGA DE RESULTADOS
# =========================================================

COLUMNAS = [
    "name",
    "group",
    "date",
    "comprension",
    "morfologia",
    "semantica",
    "literatura",
    "sintaxis",
    "nota_inicial",
    "faltas_ortografia",
    "faltas_tildes",
    "descuento_ortografia",
    "nota_final"
]


try:

    df = pd.read_csv(
        "results.csv"
    )

    for columna in COLUMNAS:

        if columna not in df.columns:

            df[columna] = 0

except Exception:

    df = pd.DataFrame(
        columns=COLUMNAS
    )


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def normalizar(texto):

    texto = str(
        texto
    ).lower().strip()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        c
        for c in texto
        if unicodedata.category(c) != "Mn"
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def contiene_respuesta(
    respuesta,
    criterios
):

    texto = normalizar(
        respuesta
    )

    for criterio in criterios:

        if normalizar(
            criterio
        ) in texto:

            return True

    return False


def corregir_exacta(
    respuesta,
    correcta
):

    return (
        normalizar(respuesta)
        == normalizar(correcta)
    )


def palabras_respuesta(
    respuesta
):

    texto = normalizar(
        respuesta
    )

    texto = texto.replace(
        ",",
        " "
    )

    return [
        palabra
        for palabra in texto.split()
        if palabra
    ]


# =========================================================
# CORRECCIÓN ORTOGRÁFICA
# =========================================================

def detectar_ortografia(
    respuestas
):

    textos = []

    for respuesta in respuestas:

        if (
            respuesta
            and str(respuesta).strip()
        ):

            textos.append(
                str(respuesta)
            )

    texto_completo = "\n".join(
        textos
    )

    if not texto_completo.strip():

        return 0, 0

    try:

        import language_tool_python

        tool = language_tool_python.LanguageTool(
            "es"
        )

        matches = tool.check(
            texto_completo
        )

        faltas = set()
        tildes = set()

        for match in matches:

            regla = str(
                getattr(
                    match,
                    "rule_id",
                    ""
                )
            ).upper()

            mensaje = str(
                getattr(
                    match,
                    "message",
                    ""
                )
            ).lower()

            palabra = texto_completo[
                match.offset:
                match.offset
                + match.errorLength
            ]

            clave = (
                palabra.lower(),
                match.offset
            )

            if (
                "ACCENT" in regla
                or "TILDE" in regla
                or "DIACRIT" in regla
                or "ACENTO" in mensaje
                or "TILDE" in mensaje
            ):

                tildes.add(
                    clave
                )

            elif (
                "TYPO" in regla
                or "SPELL" in regla
                or "MORFO" in regla
                or "HUNSPELL" in regla
            ):

                faltas.add(
                    clave
                )

        try:

            tool.close()

        except Exception:

            pass

        return (
            len(faltas),
            len(tildes)
        )

    except Exception:

        return 0, 0


# =========================================================
# CORRECCIÓN DEL EXAMEN
# =========================================================

def corregir_examen(
    respuestas,
    respuestas_morf,
    respuestas_dp
):

    puntos = {
        "comprension": 0,
        "morfologia": 0,
        "semantica": 0,
        "literatura": 0,
        "sintaxis": 0
    }

    detalles = []

    # =====================================================
    # 1. COMPRENSIÓN
    # =====================================================

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "comprension"
    ][
        "preguntas"
    ]:

        pid = pregunta["id"]

        respuesta = respuestas.get(
            pid,
            ""
        )

        maximo = pregunta[
            "puntos"
        ]

        obtenido = 0

        tipo = pregunta.get(
            "tipo",
            "texto"
        )

        # -----------------------------------------------
        # PERSONAJES
        # -----------------------------------------------

        if tipo == "personajes":

            texto = normalizar(
                respuesta
            )

            criterios = [
                normalizar(c)
                for c in pregunta.get(
                    "criterios",
                    []
                )
            ]

            encontrados = 0

            for criterio in criterios:

                if criterio in texto:

                    encontrados += 1

            # Se consideran correctos los dos personajes
            # principales: hombre joven/viajero y anciana.
            #
            # "hombre joven" y "viajero" hacen referencia
            # al mismo personaje.

            tiene_viajero = (
                "hombre joven" in texto
                or "viajero" in texto
                or "hombre" in texto
            )

            tiene_anciana = (
                "anciana" in texto
            )

            if (
                tiene_viajero
                and tiene_anciana
            ):

                obtenido = maximo

        # -----------------------------------------------
        # ACCIONES
        # -----------------------------------------------

        elif tipo == "accion":

            if contiene_respuesta(
                respuesta,
                pregunta.get(
                    "criterios",
                    []
                )
            ):

                obtenido = maximo

        # -----------------------------------------------
        # TEXTO GENERAL
        # -----------------------------------------------

        else:

            if contiene_respuesta(
                respuesta,
                pregunta.get(
                    "criterios",
                    []
                )
            ):

                obtenido = maximo

        puntos[
            "comprension"
        ] += obtenido

        detalles.append(
            (
                pid,
                pregunta["enunciado"],
                obtenido,
                maximo
            )
        )

    # =====================================================
    # 2. MORFOLOGÍA
    # =====================================================

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "morfologia"
    ]:

        pid = pregunta["id"]

        respuestas_palabra = respuestas_morf.get(
            pid,
            {}
        )

        numero_campos = len(
            pregunta["campos"]
        )

        puntos_por_campo = (
            pregunta["puntos"]
            / numero_campos
        )

        for campo in pregunta[
            "campos"
        ]:

            respuesta = respuestas_palabra.get(
                campo,
                ""
            )

            correctas = pregunta[
                "respuestas"
            ].get(
                campo,
                []
            )

            correcto = contiene_respuesta(
                respuesta,
                correctas
            )

            obtenido = (
                puntos_por_campo
                if correcto
                else 0
            )

            puntos[
                "morfologia"
            ] += obtenido

            detalles.append(
                (
                    f"{pid}_{campo}",
                    f"{pregunta['palabra']} - {campo}",
                    obtenido,
                    puntos_por_campo
                )
            )

    # =====================================================
    # 2.2. DETERMINANTES Y PRONOMBRES
    # =====================================================

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "determinantes_pronombres"
    ]:

        respuesta = respuestas_dp.get(
            pregunta["id"],
            ""
        )

        correcto = corregir_exacta(
            respuesta,
            pregunta["respuesta"]
        )

        obtenido = (
            pregunta["puntos"]
            if correcto
            else 0
        )

        puntos[
            "morfologia"
        ] += obtenido

        detalles.append(
            (
                pregunta["id"],
                pregunta["enunciado"],
                obtenido,
                pregunta["puntos"]
            )
        )

    # =====================================================
    # 3. SEMÁNTICA
    # =====================================================

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "semantica"
    ]:

        respuesta = respuestas.get(
            pregunta["id"],
            ""
        )

        correcto = corregir_exacta(
            respuesta,
            pregunta["respuesta"]
        )

        obtenido = (
            pregunta["puntos"]
            if correcto
            else 0
        )

        puntos[
            "semantica"
        ] += obtenido

        detalles.append(
            (
                pregunta["id"],
                pregunta["elemento"],
                obtenido,
                pregunta["puntos"]
            )
        )

    # =====================================================
    # 4. TEXTOS
    # =====================================================

    textos_puntos = 0

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "textos"
    ]:

        respuesta = respuestas.get(
            pregunta["id"],
            ""
        )

        maximo = pregunta[
            "puntos"
        ]

        correcto = corregir_exacta(
            respuesta,
            pregunta["respuesta"]
        )

        obtenido = (
            maximo
            if correcto
            else 0
        )

        textos_puntos += obtenido

        detalles.append(
            (
                pregunta["id"],
                pregunta["enunciado"],
                obtenido,
                maximo
            )
        )

    # =====================================================
    # 5. LITERATURA
    # =====================================================

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "literatura"
    ]:

        if pregunta["id"] == "l0":
            continue

        respuesta = respuestas.get(
            pregunta["id"],
            ""
        )

        maximo = pregunta[
            "puntos"
        ]

        tipo = pregunta.get(
            "tipo",
            "exacta"
        )

        obtenido = 0

        # -----------------------------------------------
        # EXACTA
        # -----------------------------------------------

        if tipo == "exacta":

            correcto = corregir_exacta(
                respuesta,
                pregunta.get(
                    "respuesta",
                    ""
                )
            )

            if not correcto:

                alternativas = pregunta.get(
                    "alternativas",
                    []
                )

                correcto = any(
                    corregir_exacta(
                        respuesta,
                        alt
                    )
                    for alt in alternativas
                )

            if correcto:
                obtenido = maximo

        # -----------------------------------------------
        # ESQUEMA MÉTRICO
        # -----------------------------------------------

        elif pregunta["id"] == "l3":

            texto = normalizar(
                respuesta
            )

            texto = texto.replace(
                ",",
                " "
            )

            texto = re.sub(
                r"\s+",
                " ",
                texto
            ).strip()

            correcto = (
                texto
                == "14a 14b 14b 14a"
            )

            if correcto:
                obtenido = maximo

        # -----------------------------------------------
        # SINALEFA
        # -----------------------------------------------

        elif tipo == "sinalefa":

            respuesta_normalizada = normalizar(
                respuesta
            )

            validas = [
                normalizar(x)
                for x in pregunta.get(
                    "respuestas_validas",
                    []
                )
            ]

            if respuesta_normalizada in validas:

                obtenido = maximo

        # -----------------------------------------------
        # PERSONIFICACIÓN
        # -----------------------------------------------

        elif tipo == "personificacion":

            respuesta_normalizada = normalizar(
                respuesta
            )

            validas = [
                normalizar(x)
                for x in pregunta.get(
                    "respuestas_validas",
                    []
                )
            ]

            if respuesta_normalizada in validas:

                obtenido = maximo

        puntos[
            "literatura"
        ] += obtenido

        detalles.append(
            (
                pregunta["id"],
                pregunta["enunciado"],
                obtenido,
                maximo
            )
        )

    # =====================================================
    # 6. SINTAXIS
    # =====================================================

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "sintaxis"
    ]:

        respuesta = respuestas.get(
            pregunta["id"],
            ""
        )

        correcto = corregir_exacta(
            respuesta,
            pregunta["respuesta"]
        )

        obtenido = (
            pregunta["puntos"]
            if correcto
            else 0
        )

        puntos[
            "sintaxis"
        ] += obtenido

        detalles.append(
            (
                pregunta["id"],
                pregunta["frase"],
                obtenido,
                pregunta["puntos"]
            )
        )

    # =====================================================
    # 7. DIÁLOGO
    # =====================================================

    dialogo_puntos = 0

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "dialogo"
    ][
        "preguntas"
    ]:

        respuesta = respuestas.get(
            pregunta["id"],
            ""
        )

        maximo = pregunta[
            "puntos"
        ]

        tipo = pregunta.get(
            "tipo",
            "exacta"
        )

        obtenido = 0

        # -----------------------------------------------
        # INTERLOCUTORES
        # -----------------------------------------------

        if tipo == "interlocutores":

            texto = normalizar(
                respuesta
            )

            validos = [
                normalizar(x)
                for x in pregunta.get(
                    "respuestas_validas",
                    []
                )
            ]

            encontrados = [
                nombre
                for nombre in validos
                if nombre in texto
            ]

            if len(
                set(encontrados)
            ) == len(validos):

                obtenido = maximo

        # -----------------------------------------------
        # ESTILO INDIRECTO
        # -----------------------------------------------

        elif tipo == "estilo_indirecto":

            texto = normalizar(
                respuesta
            )

            condiciones = [

                "carlos" in texto,

                "dijo" in texto,

                (
                    "habia hecho"
                    in texto
                ),

                (
                    "lo habia hecho"
                    in texto
                )
            ]

            if all(
                condiciones
            ):

                obtenido = maximo

        # -----------------------------------------------
        # EXACTA
        # -----------------------------------------------

        else:

            correcto = corregir_exacta(
                respuesta,
                pregunta.get(
                    "respuesta",
                    ""
                )
            )

            if correcto:

                obtenido = maximo

        dialogo_puntos += obtenido

        detalles.append(
            (
                pregunta["id"],
                pregunta["enunciado"],
                obtenido,
                maximo
            )
        )

    # =====================================================
    # DEVOLVER
    # =====================================================

    return (
        puntos,
        detalles,
        textos_puntos,
        dialogo_puntos
    )


# =========================================================
# CÁLCULO DE PUNTUACIONES MÁXIMAS
# =========================================================

def calcular_maximos():

    maximos = {
        "comprension": 0,
        "morfologia": 0,
        "semantica": 0,
        "literatura": 0,
        "sintaxis": 0,
        "textos": 0,
        "dialogo": 0
    }

    # Comprensión

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "comprension"
    ][
        "preguntas"
    ]:

        maximos[
            "comprension"
        ] += pregunta["puntos"]

    # Morfología

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "morfologia"
    ]:

        maximos[
            "morfologia"
        ] += pregunta["puntos"]

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "determinantes_pronombres"
    ]:

        maximos[
            "morfologia"
        ] += pregunta["puntos"]

    # Semántica

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "semantica"
    ]:

        maximos[
            "semantica"
        ] += pregunta["puntos"]

    # Textos

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "textos"
    ]:

        maximos[
            "textos"
        ] += pregunta["puntos"]

    # Literatura

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "literatura"
    ]:

        if pregunta["id"] != "l0":

            maximos[
                "literatura"
            ] += pregunta["puntos"]

    # Sintaxis

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "sintaxis"
    ]:

        maximos[
            "sintaxis"
        ] += pregunta["puntos"]

    # Diálogo

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "dialogo"
    ][
        "preguntas"
    ]:

        maximos[
            "dialogo"
        ] += pregunta["puntos"]

    return maximos


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3 = st.tabs(
    [
        "🧑‍🎓 Examen",
        "📊 Dashboard",
        "👤 Alumno"
    ]
)


# =========================================================
# TAB 1 - EXAMEN
# =========================================================

with tab1:

    st.subheader(
        "Evaluación inicial de Lengua Castellana y Literatura"
    )

    nombre = st.text_input(
        "Nombre y apellidos"
    )

    grupo = st.text_input(
        "Grupo"
    )

    respuestas = {}
    respuestas_morf = {}
    respuestas_dp = {}

    # =====================================================
    # 1. COMPRENSIÓN
    # =====================================================

    st.divider()

    st.header(
        "1. Comprensión lectora"
    )

    st.write(
        EXAMEN[
            "2ESO"
        ][
            "comprension"
        ][
            "texto"
        ]
    )

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "comprension"
    ][
        "preguntas"
    ]:

        pid = pregunta["id"]

        # PERSONAJES

        if pregunta.get(
            "tipo"
        ) == "personajes":

            st.markdown(
                f"**{pregunta['enunciado']}**"
            )

            st.caption(
                pregunta.get(
                    "ayuda",
                    ""
                )
            )

            respuestas[
                pid
            ] = st.text_input(
                "Respuesta",
                key=f"comp_{pid}"
            )

        # ACCIONES

        elif pregunta.get(
            "tipo"
        ) == "accion":

            st.markdown(
                f"**{pregunta['enunciado']}**"
            )

            st.caption(
                pregunta.get(
                    "ayuda",
                    ""
                )
            )

            respuestas[
                pid
            ] = st.text_input(
                "Escribe la acción en infinitivo",
                key=f"comp_{pid}"
            )

        # RESTO

        else:

            respuestas[
                pid
            ] = st.text_area(
                pregunta["enunciado"],
                help=pregunta.get(
                    "ayuda",
                    ""
                ),
                key=f"comp_{pid}"
            )

    # =====================================================
    # 2. MORFOLOGÍA
    # =====================================================

    st.divider()

    st.header(
        "2. Morfología y categorías gramaticales"
    )

    st.subheader(
        "2.1. Análisis morfológico"
    )

    st.info(
        "Escribe las respuestas directamente en cada apartado. "
        "No es necesario escribir frases completas."
    )

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "morfologia"
    ]:

        st.markdown(
            f"### {pregunta['palabra']}"
        )

        respuestas_morf[
            pregunta["id"]
        ] = {}

        columnas = st.columns(
            len(
                pregunta["campos"]
            )
        )

        for columna, campo in zip(
            columnas,
            pregunta["campos"]
        ):

            with columna:

                respuestas_morf[
                    pregunta["id"]
                ][campo] = st.text_input(
                    campo,
                    key=(
                        f"morf_"
                        f"{pregunta['id']}_"
                        f"{campo}"
                    )
                )

    # =====================================================
    # 2.2. DETERMINANTES
    # =====================================================

    st.subheader(
        "2.2. Determinantes y pronombres"
    )

    st.write(
        "Indica si la palabra destacada es determinante o pronombre."
    )

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "determinantes_pronombres"
    ]:

        st.markdown(
            f"**{pregunta['frase']}**"
        )

        respuestas_dp[
            pregunta["id"]
        ] = st.selectbox(
            pregunta["enunciado"],
            [
                "",
                "Determinante",
                "Pronombre"
            ],
            key=f"dp_{pregunta['id']}"
        )

    # =====================================================
    # 3. SEMÁNTICA
    # =====================================================

    st.divider()

    st.header(
        "3. Semántica"
    )

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "semantica"
    ]:

        st.write(
            f"**{pregunta['elemento']}**"
        )

        respuestas[
            pregunta["id"]
        ] = st.selectbox(
            pregunta["enunciado"],
            [
                "",
                "Antonimia",
                "Campo semántico",
                "Polisemia",
                "Meronimia",
                "Hipónimos"
            ],
            key=f"sem_{pregunta['id']}"
        )

    # =====================================================
    # 4. TEXTOS
    # =====================================================

    st.divider()

    st.header(
        "4. Textos"
    )

    opciones_texto = [
        "",
        "Narrativo",
        "Descriptivo",
        "Expositivo",
        "Argumentativo",
        "Instructivo",
        "Dialogado"
    ]

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "textos"
    ]:

        st.info(
            pregunta["texto"]
        )

        respuestas[
            pregunta["id"]
        ] = st.selectbox(
            pregunta["enunciado"],
            opciones_texto,
            key=f"texto_{pregunta['id']}"
        )

    # =====================================================
    # 5. LITERATURA
    # =====================================================

    st.divider()

    st.header(
        "5. Literatura"
    )

    poema = next(
        p
        for p in EXAMEN[
            "2ESO"
        ][
            "literatura"
        ]
        if p["id"] == "l0"
    )

    st.write(
        poema["enunciado"]
    )

    st.table(
        pd.DataFrame(
            {
                "Verso": poema["versos"]
            }
        )
    )

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "literatura"
    ]:

        if pregunta["id"] == "l0":
            continue

        # ESQUEMA MÉTRICO
        if pregunta["id"] == "l3":

            respuestas[
                pregunta["id"]
            ] = st.text_input(
                pregunta["enunciado"],
                help=pregunta.get(
                    "ayuda",
                    ""
                ),
                key="lit_l3"
            )

        # SINALEFA
        elif pregunta.get(
            "tipo"
        ) == "sinalefa":

            respuestas[
                pregunta["id"]
            ] = st.text_input(
                pregunta["enunciado"],
                help=pregunta.get(
                    "ayuda",
                    ""
                ),
                key=f"lit_{pregunta['id']}"
            )

        # PERSONIFICACIÓN
        elif pregunta.get(
            "tipo"
        ) == "personificacion":

            respuestas[
                pregunta["id"]
            ] = st.text_input(
                pregunta["enunciado"],
                help=pregunta.get(
                    "ayuda",
                    ""
                ),
                key=f"lit_{pregunta['id']}"
            )

        # RESTO
        else:

            respuestas[
                pregunta["id"]
            ] = st.selectbox(
                pregunta["enunciado"],
                [
                    "",
                    "4",
                    "Arte mayor",
                    "Arte menor",
                    "Consonante",
                    "Asonante"
                ],
                key=f"lit_{pregunta['id']}"
            )

    # =====================================================
    # 6. SINTAXIS
    # =====================================================

    st.divider()

    st.header(
        "6. Sintaxis"
    )

    st.subheader(
        "6.1. Frase u oración"
    )

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "sintaxis"
    ][:5]:

        st.markdown(
            f"**{pregunta['frase']}**"
        )

        respuestas[
            pregunta["id"]
        ] = st.selectbox(
            pregunta["enunciado"],
            [
                "",
                "Frase",
                "Oración"
            ],
            key=f"syn_{pregunta['id']}"
        )

    st.subheader(
        "6.2. Modalidad oracional"
    )

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "sintaxis"
    ][5:]:

        st.markdown(
            f"**{pregunta['frase']}**"
        )

        respuestas[
            pregunta["id"]
        ] = st.selectbox(
            pregunta["enunciado"],
            [
                "",
                "Enunciativa",
                "Interrogativa",
                "Exclamativa",
                "Desiderativa",
                "Exhortativa",
                "Dubitativa"
            ],
            key=f"syn_{pregunta['id']}"
        )

    # =====================================================
    # 7. DIÁLOGO
    # =====================================================

    st.divider()

    st.header(
        "7. Diálogo"
    )

    st.write(
        EXAMEN[
            "2ESO"
        ][
            "dialogo"
        ][
            "texto"
        ]
    )

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "dialogo"
    ][
        "preguntas"
    ]:

        respuestas[
            pregunta["id"]
        ] = st.text_input(
            pregunta["enunciado"],
            help=pregunta.get(
                "ayuda",
                ""
            ),
            key=f"dialogo_{pregunta['id']}"
        )

    # =====================================================
    # ORTOGRAFÍA
    # =====================================================

    st.divider()

    st.info(
        "La ortografía se corregirá automáticamente a partir "
        "de las respuestas. El alumno no introduce ni modifica "
        "el número de faltas."
    )

    # =====================================================
    # ENVIAR
    # =====================================================

    if st.button(
        "📤 Corregir y guardar examen",
        type="primary",
        key="corregir_examen"
    ):

        if not nombre.strip():

            st.error(
                "Introduce el nombre y apellidos."
            )

        elif not grupo.strip():

            st.error(
                "Introduce el grupo."
            )

        else:

            # =============================================
            # CORREGIR
            # =============================================

            (
                puntos,
                detalles,
                textos_puntos,
                dialogo_puntos
            ) = corregir_examen(
                respuestas,
                respuestas_morf,
                respuestas_dp
            )

            # =============================================
            # MÁXIMOS
            # =============================================

            maximos = calcular_maximos()

            # =============================================
            # NOTA POR COMPETENCIAS
            # =============================================

            max_comprension = maximos[
                "comprension"
            ]

            max_morfologia = maximos[
                "morfologia"
            ]

            max_semantica = maximos[
                "semantica"
            ]

            max_literatura = maximos[
                "literatura"
            ]

            max_sintaxis = maximos[
                "sintaxis"
            ]

            # Textos se integran en comprensión.
            comprension_total = (
                puntos["comprension"]
                + textos_puntos
            )

            max_comprension_total = (
                max_comprension
                + maximos["textos"]
            )

            # Diálogo se integra en sintaxis.
            sintaxis_total = (
                puntos["sintaxis"]
                + dialogo_puntos
            )

            max_sintaxis_total = (
                max_sintaxis
                + maximos["dialogo"]
            )

            scores = {

                "comprension": (
                    comprension_total
                    / max_comprension_total
                    * 10
                    if max_comprension_total > 0
                    else 0
                ),

                "morfologia": (
                    puntos["morfologia"]
                    / max_morfologia
                    * 10
                    if max_morfologia > 0
                    else 0
                ),

                "semantica": (
                    puntos["semantica"]
                    / max_semantica
                    * 10
                    if max_semantica > 0
                    else 0
                ),

                "literatura": (
                    puntos["literatura"]
                    / max_literatura
                    * 10
                    if max_literatura > 0
                    else 0
                ),

                "sintaxis": (
                    sintaxis_total
                    / max_sintaxis_total
                    * 10
                    if max_sintaxis_total > 0
                    else 0
                )
            }

            # =============================================
            # NOTA GLOBAL
            # =============================================

            puntos_obtenidos = (
                puntos["comprension"]
                + puntos["morfologia"]
                + puntos["semantica"]
                + textos_puntos
                + puntos["literatura"]
                + puntos["sintaxis"]
                + dialogo_puntos
            )

            puntos_maximos = (
                maximos["comprension"]
                + maximos["morfologia"]
                + maximos["semantica"]
                + maximos["textos"]
                + maximos["literatura"]
                + maximos["sintaxis"]
                + maximos["dialogo"]
            )

            nota_inicial = (
                puntos_obtenidos
                / puntos_maximos
                * 10
                if puntos_maximos > 0
                else 0
            )

            nota_inicial = max(
                0,
                min(
                    10,
                    nota_inicial
                )
            )

            # =============================================
            # ORTOGRAFÍA
            # =============================================

            todas_respuestas = list(
                respuestas.values()
            )

            for palabra in respuestas_morf.values():

                for respuesta in palabra.values():

                    todas_respuestas.append(
                        respuesta
                    )

            for respuesta in respuestas_dp.values():

                todas_respuestas.append(
                    respuesta
                )

            (
                faltas_ortografia,
                faltas_tildes
            ) = detectar_ortografia(
                todas_respuestas
            )

            descuento_ortografia = (
                faltas_ortografia * 0.20
                + faltas_tildes * 0.10
            )

            descuento_ortografia = min(
                2.0,
                descuento_ortografia
            )

            nota_final = max(
                0,
                nota_inicial
                - descuento_ortografia
            )

            # =============================================
            # PERFIL
            # =============================================

            perfil = generar_perfil(
                scores
            )

            # =============================================
            # GUARDAR RESULTADO
            # =============================================

            nueva_fila = {

                "name": nombre,

                "group": grupo,

                "date": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

                "comprension": round(
                    scores["comprension"],
                    2
                ),

                "morfologia": round(
                    scores["morfologia"],
                    2
                ),

                "semantica": round(
                    scores["semantica"],
                    2
                ),

                "literatura": round(
                    scores["literatura"],
                    2
                ),

                "sintaxis": round(
                    scores["sintaxis"],
                    2
                ),

                "nota_inicial": round(
                    nota_inicial,
                    2
                ),

                "faltas_ortografia": (
                    faltas_ortografia
                ),

                "faltas_tildes": (
                    faltas_tildes
                ),

                "descuento_ortografia": round(
                    descuento_ortografia,
                    2
                ),

                "nota_final": round(
                    nota_final,
                    2
                )
            }

            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        [nueva_fila]
                    )
                ],
                ignore_index=True
            )

            df.to_csv(
                "results.csv",
                index=False
            )

            # =============================================
            # RESULTADO
            # =============================================

            st.success(
                "Examen corregido y guardado correctamente."
            )

            col1, col2, col3 = st.columns(
                3
            )

            with col1:

                st.metric(
                    "Nota inicial",
                    f"{nota_inicial:.2f}/10"
                )

            with col2:

                st.metric(
                    "Descuento ortográfico",
                    f"-{descuento_ortografia:.2f}"
                )

            with col3:

                st.metric(
                    "Nota final",
                    f"{nota_final:.2f}/10"
                )

            # =============================================
            # ORTOGRAFÍA
            # =============================================

            st.write(
                "### Corrección ortográfica"
            )

            st.write(
                "Faltas de ortografía detectadas: "
                f"**{faltas_ortografia}**"
            )

            st.write(
                "Faltas de tilde detectadas: "
                f"**{faltas_tildes}**"
            )

            st.write(
                "Descuento aplicado: "
                f"**-{descuento_ortografia:.2f} puntos**"
            )

            # =============================================
            # RADAR
            # =============================================

            st.plotly_chart(
                radar_chart(
                    scores,
                    nombre
                ),
                use_container_width=True,
                key="radar_resultado"
            )

            # =============================================
            # PERFIL
            # =============================================

            st.write(
                "### Perfil del alumno"
            )

            for item in perfil:

                st.write(
                    f"- {item}"
                )

            # =============================================
            # DETALLE
            # =============================================

            st.write(
                "### Detalle de corrección"
            )

            tabla_detalles = []

            for (
                pid,
                pregunta,
                obtenido,
                maximo
            ) in detalles:

                tabla_detalles.append(
                    {
                        "Pregunta": pid,
                        "Contenido": pregunta,
                        "Puntos": round(
                            obtenido,
                            3
                        ),
                        "Máximo": round(
                            maximo,
                            3
                        ),
                        "Resultado": (
                            "✓"
                            if obtenido >= maximo
                            else "✗"
                        )
                    }
                )

            st.dataframe(
                pd.DataFrame(
                    tabla_detalles
                ),
                use_container_width=True
            )

            # =============================================
            # PDF
            # =============================================

            st.write(
                "### Informe PDF"
            )

            try:

                pdf_file = generar_pdf(
                    nombre,
                    grupo,
                    scores,
                    perfil,
                    nota_inicial,
                    descuento_ortografia,
                    faltas_ortografia,
                    faltas_tildes,
                    nota_final
                )

                if (
                    pdf_file
                    and os.path.exists(pdf_file)
                ):

                    with open(
                        pdf_file,
                        "rb"
                    ) as archivo:

                        datos_pdf = archivo.read()

                    st.download_button(
                        label="📄 Descargar informe PDF",
                        data=datos_pdf,
                        file_name=os.path.basename(
                            pdf_file
                        ),
                        mime="application/pdf",
                        key="descargar_pdf"
                    )

                    st.success(
                        "Informe PDF generado correctamente."
                    )

            except Exception as error:

                st.error(
                    "No se pudo generar el PDF: "
                    f"{error}"
                )


# =========================================================
# TAB 2 - DASHBOARD
# =========================================================

with tab2:

    st.header(
        "📊 Dashboard de la clase"
    )

    if df.empty:

        st.info(
            "Todavía no hay exámenes corregidos."
        )

    else:

        # =============================================
        # MEDIA
        # =============================================

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

        st.bar_chart(
            df[
                competencias
            ].mean()
        )

        # =============================================
        # GENERALES
        # =============================================

        col1, col2, col3 = st.columns(
            3
        )

        with col1:

            st.metric(
                "Alumnos",
                len(df)
            )

        with col2:

            st.metric(
                "Media inicial",
                f"{df['nota_inicial'].mean():.2f}"
            )

        with col3:

            st.metric(
                "Media final",
                f"{df['nota_final'].mean():.2f}"
            )

        # =============================================
        # TABLA
        # =============================================

        st.subheader(
            "Resultados"
        )

        columnas_mostrar = [
            "name",
            "group",
            "comprension",
            "morfologia",
            "semantica",
            "literatura",
            "sintaxis",
            "nota_inicial",
            "faltas_ortografia",
            "faltas_tildes",
            "descuento_ortografia",
            "nota_final"
        ]

        columnas_validas = [
            c
            for c in columnas_mostrar
            if c in df.columns
        ]

        st.dataframe(
            df[
                columnas_validas
            ],
            use_container_width=True
        )

        # =============================================
        # COMPARATIVA
        # =============================================

        st.subheader(
            "Comparativa individual"
        )

        nombres_alumnos = sorted(
            df["name"]
            .dropna()
            .astype(str)
            .unique()
        )

        if nombres_alumnos:

            alumno_seleccionado = st.selectbox(
                "Selecciona alumno",
                nombres_alumnos,
                key="dashboard_alumno"
            )

            alumno = df[
                df["name"]
                == alumno_seleccionado
            ].iloc[-1]

            st.plotly_chart(
                comparativa(
                    alumno,
                    df
                ),
                use_container_width=True,
                key="radar_dashboard_comparativa"
            )


# =========================================================
# TAB 3 - ALUMNO
# =========================================================

with tab3:

    st.header(
        "👤 Historial del alumno"
    )

    if df.empty:

        st.info(
            "Todavía no hay alumnos registrados."
        )

    else:

        nombres_alumnos = sorted(
            df["name"]
            .dropna()
            .astype(str)
            .unique()
        )

        if nombres_alumnos:

            alumno_seleccionado = st.selectbox(
                "Selecciona alumno",
                nombres_alumnos,
                key="historial_alumno"
            )

            historial = df[
                df["name"]
                == alumno_seleccionado
            ]

            st.dataframe(
                historial,
                use_container_width=True
            )

            alumno_actual = historial.iloc[-1]

            st.subheader(
                "Último resultado"
            )

            col1, col2, col3 = st.columns(
                3
            )

            with col1:

                st.metric(
                    "Nota inicial",
                    f"{float(alumno_actual['nota_inicial']):.2f}"
                )

            with col2:

                st.metric(
                    "Descuento",
                    f"-{float(alumno_actual['descuento_ortografia']):.2f}"
                )

            with col3:

                st.metric(
                    "Nota final",
                    f"{float(alumno_actual['nota_final']):.2f}"
                )

            scores_alumno = {
                competencia: float(
                    alumno_actual[competencia]
                )
                for competencia in [
                    "comprension",
                    "morfologia",
                    "semantica",
                    "literatura",
                    "sintaxis"
                ]
            }

            st.plotly_chart(
                radar_chart(
                    scores_alumno,
                    alumno_seleccionado
                ),
                use_container_width=True,
                key="radar_historial_alumno"
            )
