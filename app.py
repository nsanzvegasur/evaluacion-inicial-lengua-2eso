import os
import re
import unicodedata
from datetime import datetime

import pandas as pd
import streamlit as st

from examen2ESO import EXAMEN
from pdf_report import generar_pdf


# ==============================================================
# CONFIGURACIÓN
# ==============================================================

st.set_page_config(
    page_title="Evaluación inicial - Lengua 2º ESO",
    page_icon="📚",
    layout="centered"
)


CSV_FILE = "results.csv"


# ==============================================================
# ESTILO
# ==============================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #666;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }

    .result-box {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #ddd;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==============================================================
# FUNCIONES DE NORMALIZACIÓN
# ==============================================================

def normalizar(valor):
    if valor is None:
        return ""

    texto = str(valor).strip().lower()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    texto = texto.replace(
        "º",
        ""
    )

    texto = texto.replace(
        "ª",
        ""
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def normalizar_lista(valor):
    """
    Convierte respuestas separadas por:
    - comas
    - saltos de línea
    - punto y coma
    en una lista normalizada.
    """

    if valor is None:
        return []

    texto = str(valor).strip()

    if not texto:
        return []

    partes = re.split(
        r"[,;\n]+",
        texto
    )

    resultado = []

    for parte in partes:
        parte = normalizar(parte)

        if parte:
            resultado.append(parte)

    return resultado


def contiene_respuesta(
    respuesta,
    criterios
):
    texto = normalizar(
        respuesta
    )

    if not texto:
        return False

    for criterio in criterios:
        if normalizar(criterio) in texto:
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


def corregir_lista(
    respuesta,
    criterios
):
    """
    Devuelve una puntuación proporcional.

    Ejemplo:
    2 personajes requeridos.
    1 correcto = 50%.
    2 correctos = 100%.
    """

    respuestas = normalizar_lista(
        respuesta
    )

    if not respuestas:
        return 0.0

    criterios_norm = [
        normalizar(c)
        for c in criterios
    ]

    encontrados = set()

    for respuesta_item in respuestas:
        for criterio in criterios_norm:

            if (
                respuesta_item == criterio
                or criterio in respuesta_item
                or respuesta_item in criterio
            ):
                encontrados.add(
                    criterio
                )

    if not criterios_norm:
        return 0.0

    return len(encontrados) / len(
        criterios_norm
    )


def corregir_componentes(
    respuesta,
    criterios
):
    """
    Utilizado para morfemas y categorías
    gramaticales.
    """

    respuestas = normalizar_lista(
        respuesta
    )

    criterios_norm = [
        normalizar(c)
        for c in criterios
    ]

    if not respuestas:
        return 0.0

    encontrados = set()

    for respuesta_item in respuestas:

        for criterio in criterios_norm:

            if (
                respuesta_item == criterio
                or criterio in respuesta_item
                or respuesta_item in criterio
            ):
                encontrados.add(
                    criterio
                )

    if not criterios_norm:
        return 0.0

    return len(encontrados) / len(
        criterios_norm
    )


# ==============================================================
# MÉTRICA
# ==============================================================

def normalizar_metrica(valor):
    if not valor:
        return ""

    texto = normalizar(valor)

    texto = texto.replace(
        ",",
        " "
    )

    texto = texto.replace(
        "/",
        " "
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def corregir_metrica(
    respuesta,
    pregunta
):
    respuesta_norm = normalizar_metrica(
        respuesta
    )

    for alternativa in pregunta.get(
        "alternativas",
        []
    ):
        if (
            respuesta_norm
            == normalizar_metrica(
                alternativa
            )
        ):
            return True

    return (
        respuesta_norm
        == normalizar_metrica(
            pregunta.get(
                "respuesta",
                ""
            )
        )
    )


# ==============================================================
# ORTOGRAFÍA
# ==============================================================

PALABRAS_CON_TILDE = {
    "tambien": "también",
    "despues": "después",
    "todavia": "todavía",
    "dias": "días",
    "accion": "acción",
    "acciones": "acciones",
    "numero": "número",
    "numero": "número",
    "oracion": "oración",
    "oraciones": "oraciones",
    "semantica": "semántica",
    "literatura": "literatura",
    "poema": "poema",
    "metric": "métrica",
    "metrica": "métrica",
    "sinalefa": "sinalefa",
    "personificacion": "personificación",
    "interlocutores": "interlocutores",
    "morfologia": "morfología",
    "gramatical": "gramatical",
    "clasificacion": "clasificación",
    "expositiva": "expositiva",
    "argumentativa": "argumentativa",
    "determinante": "determinante",
    "pronombre": "pronombre",
    "interrogativa": "interrogativa",
    "exclamativa": "exclamativa",
    "desiderativa": "desiderativa",
    "enunciativa": "enunciativa",
    "exhortativa": "exhortativa",
    "lucia": "Lucía",
    "carlos": "Carlos",
    "tambien": "también",
    "habia": "había",
    "si": "sí"
}


ERRORES_COMUNES = {
    "aver": "a ver",
    "haber si": "a ver si",
    "haver": "haber",
    "hechar": "echar",
    "echo": "hecho",
    "hecho": "hecho",
    "hay": "hay",
    "ai": "ahí",
    "ahi": "ahí",
    "porque": "porque"
}


def detectar_ortografia(textos):
    """
    Detector conservador.
    No penaliza automáticamente palabras que no
    conoce. Solo cuenta errores muy claros.
    """

    faltas = 0
    tildes = 0

    for texto in textos:

        if texto is None:
            continue

        texto = str(texto)

        texto_norm = normalizar(
            texto
        )

        # ------------------------------------------
        # Errores ortográficos evidentes
        # ------------------------------------------

        for incorrecta, correcta in ERRORES_COMUNES.items():

            if incorrecta == correcta:
                continue

            patron = r"\b" + re.escape(
                normalizar(incorrecta)
            ) + r"\b"

            if re.search(
                patron,
                texto_norm
            ):
                faltas += 1

        # ------------------------------------------
        # Tildes muy frecuentes
        # ------------------------------------------

        for sin_tilde, con_tilde in PALABRAS_CON_TILDE.items():

            if (
                sin_tilde == normalizar(
                    con_tilde
                )
            ):
                continue

            patron = r"\b" + re.escape(
                normalizar(sin_tilde)
            ) + r"\b"

            if re.search(
                patron,
                texto_norm
            ):
                tildes += 1

    descuento = (
        faltas * 0.20
        + tildes * 0.10
    )

    descuento = min(
        descuento,
        2.0
    )

    return {
        "faltas": faltas,
        "tildes": tildes,
        "descuento": descuento
    }


# ==============================================================
# CORRECCIÓN
# ==============================================================

def corregir_examen(
    respuestas
):
    examen = EXAMEN["2ESO"]

    puntos = {
        "comprension": 0.0,
        "morfologia": 0.0,
        "semantica": 0.0,
        "literatura": 0.0,
        "sintaxis": 0.0
    }

    respuestas_pdf = {}

    # ----------------------------------------------------------
    # COMPRENSIÓN
    # ----------------------------------------------------------

    acciones_usadas = set()

    for pregunta in examen["comprension"]["preguntas"]:

        pregunta_id = pregunta["id"]

        respuesta = respuestas.get(
            pregunta_id,
            ""
        )

        respuestas_pdf[
            pregunta["enunciado"]
        ] = respuesta

        tipo = pregunta.get(
            "tipo",
            "texto"
        )

        puntos_pregunta = float(
            pregunta.get(
                "puntos",
                0
            )
        )

        if tipo == "lista":

            proporcion = corregir_lista(
                respuesta,
                pregunta.get(
                    "criterios",
                    []
                )
            )

            puntos["comprension"] += (
                puntos_pregunta
                * proporcion
            )

        elif tipo == "accion":

            respuesta_norm = normalizar(
                respuesta
            )

            criterios = [
                normalizar(c)
                for c in pregunta.get(
                    "criterios",
                    []
                )
            ]

            if (
                respuesta_norm in criterios
                and respuesta_norm not in acciones_usadas
            ):
                puntos["comprension"] += (
                    puntos_pregunta
                )

                acciones_usadas.add(
                    respuesta_norm
                )

        else:

            if contiene_respuesta(
                respuesta,
                pregunta.get(
                    "criterios",
                    []
                )
            ):
                puntos["comprension"] += (
                    puntos_pregunta
                )

    # ----------------------------------------------------------
    # TIPOLOGÍA TEXTUAL
    # Se integra en comprensión para el dashboard.
    # ----------------------------------------------------------

    for pregunta in examen["textos"]:

        pregunta_id = pregunta["id"]

        respuesta = respuestas.get(
            pregunta_id,
            ""
        )

        texto = pregunta.get(
            "texto",
            ""
        )

        respuestas_pdf[
            pregunta["enunciado"]
        ] = respuesta

        if corregir_exacta(
            respuesta,
            pregunta.get(
                "respuesta",
                ""
            )
        ):
            puntos["comprension"] += float(
                pregunta.get(
                    "puntos",
                    0
                )
            )

    # ----------------------------------------------------------
    # MORFOLOGÍA
    # ----------------------------------------------------------

    for palabra in examen["morfologia"]:

        palabra_id = palabra["id"]

        for campo in palabra["campos"]:

            key = (
                f"{palabra_id}_"
                f"{campo}"
            )

            respuesta = respuestas.get(
                key,
                ""
            )

            respuestas_pdf[
                f"{palabra['palabra']} - {campo}"
            ] = respuesta

            puntos_campo = {
                "Lexema": 0.10,
                "Morfemas": 0.10,
                "Estructura de la palabra": 0.10,
                "Categoría gramatical completa": 0.15,
                "V / I": 0.05
            }.get(
                campo,
                0
            )

            correctas = palabra[
                "respuestas"
            ].get(
                campo,
                []
            )

            if campo in (
                "Morfemas",
                "Categoría gramatical completa"
            ):
                proporcion = corregir_componentes(
                    respuesta,
                    correctas
                )

                puntos["morfologia"] += (
                    puntos_campo
                    * proporcion
                )

            else:

                if correctas:
                    if corregir_exacta(
                        respuesta,
                        correctas[0]
                    ):
                        puntos["morfologia"] += (
                            puntos_campo
                        )

    # ----------------------------------------------------------
    # DETERMINANTES / PRONOMBRES
    # Se integran en morfología.
    # ----------------------------------------------------------

    for pregunta in examen[
        "determinantes_pronombres"
    ]:

        respuesta = respuestas.get(
            pregunta["id"],
            ""
        )

        respuestas_pdf[
            pregunta["enunciado"]
        ] = respuesta

        if corregir_exacta(
            respuesta,
            pregunta["respuesta"]
        ):
            puntos["morfologia"] += float(
                pregunta["puntos"]
            )

    # ----------------------------------------------------------
    # SEMÁNTICA
    # ----------------------------------------------------------

    for pregunta in examen[
        "semantica"
    ]:

        respuesta = respuestas.get(
            pregunta["id"],
            ""
        )

        respuestas_pdf[
            pregunta["enunciado"]
        ] = respuesta

        if corregir_exacta(
            respuesta,
            pregunta["respuesta"]
        ):
            puntos["semantica"] += float(
                pregunta["puntos"]
            )

    # ----------------------------------------------------------
    # LITERATURA
    # ----------------------------------------------------------

    for pregunta in examen[
        "literatura"
    ]:

        if pregunta.get(
            "tipo"
        ) == "poema":
            continue

        pregunta_id = pregunta[
            "id"
        ]

        respuesta = respuestas.get(
            pregunta_id,
            ""
        )

        respuestas_pdf[
            pregunta["enunciado"]
        ] = respuesta

        if pregunta.get(
            "tipo"
        ) == "sinalefa":

            validas = pregunta.get(
                "respuestas_validas",
                []
            )

            respuesta_norm = normalizar(
                respuesta
            )

            validas_norm = [
                normalizar(v)
                for v in validas
            ]

            if respuesta_norm in validas_norm:
                puntos["literatura"] += float(
                    pregunta["puntos"]
                )

        elif pregunta.get(
            "tipo"
        ) == "personificacion":

            validas = pregunta.get(
                "respuestas_validas",
                []
            )

            respuesta_norm = normalizar(
                respuesta
            )

            validas_norm = [
                normalizar(v)
                for v in validas
            ]

            if respuesta_norm in validas_norm:
                puntos["literatura"] += float(
                    pregunta["puntos"]
                )

        elif pregunta.get(
            "id"
        ) == "l3":

            if corregir_metrica(
                respuesta,
                pregunta
            ):
                puntos["literatura"] += float(
                    pregunta["puntos"]
                )

        else:

            if corregir_exacta(
                respuesta,
                pregunta.get(
                    "respuesta",
                    ""
                )
            ):
                puntos["literatura"] += float(
                    pregunta["puntos"]
                )

    # ----------------------------------------------------------
    # SINTAXIS
    # ----------------------------------------------------------

    for pregunta in examen[
        "sintaxis"
    ]:

        respuesta = respuestas.get(
            pregunta["id"],
            ""
        )

        respuestas_pdf[
            pregunta["enunciado"]
        ] = respuesta

        if corregir_exacta(
            respuesta,
            pregunta["respuesta"]
        ):
            puntos["sintaxis"] += float(
                pregunta["puntos"]
            )

    # ----------------------------------------------------------
    # DIÁLOGO
    # Se integra en sintaxis.
    # ----------------------------------------------------------

    dialogo = examen["dialogo"]

    for pregunta in dialogo[
        "preguntas"
    ]:

        respuesta = respuestas.get(
            pregunta["id"],
            ""
        )

        respuestas_pdf[
            pregunta["enunciado"]
        ] = respuesta

        tipo = pregunta.get(
            "tipo",
            ""
        )

        if tipo == "lista":

            proporcion = corregir_lista(
                respuesta,
                pregunta.get(
                    "criterios",
                    []
                )
            )

            puntos["sintaxis"] += (
                float(
                    pregunta["puntos"]
                )
                * proporcion
            )

        elif tipo == "estilo_indirecto":

            texto = normalizar(
                respuesta
            )

            verbos = [
                "dijo",
                "afirmo",
                "explico",
                "comento"
            ]

            tiene_verbo = any(
                verbo in texto
                for verbo in verbos
            )

            if (
                "carlos" in texto
                and tiene_verbo
                and (
                    "habia hecho" in texto
                    or "lo habia hecho" in texto
                )
            ):
                puntos["sintaxis"] += float(
                    pregunta["puntos"]
                )

        else:

            if corregir_exacta(
                respuesta,
                pregunta.get(
                    "respuesta",
                    ""
                )
            ):
                puntos["sintaxis"] += float(
                    pregunta["puntos"]
                )

    # ----------------------------------------------------------
    # RESULTADO
    # ----------------------------------------------------------

    nota_inicial = sum(
        puntos.values()
    )

    nota_inicial = round(
        min(
            nota_inicial,
            10.0
        ),
        2
    )

    return (
        puntos,
        nota_inicial,
        respuestas_pdf
    )


# ==============================================================
# GUARDAR RESULTADOS
# ==============================================================

def guardar_resultado(
    nombre,
    curso,
    puntos,
    nota_inicial,
    faltas,
    descuento,
    nota_final
):

    fila = {
        "fecha": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "nombre": nombre,
        "curso": curso,
        "comprension": round(
            puntos["comprension"],
            2
        ),
        "morfologia": round(
            puntos["morfologia"],
            2
        ),
        "semantica": round(
            puntos["semantica"],
            2
        ),
        "literatura": round(
            puntos["literatura"],
            2
        ),
        "sintaxis": round(
            puntos["sintaxis"],
            2
        ),
        "nota_inicial": round(
            nota_inicial,
            2
        ),
        "faltas_ortografia": faltas,
        "descuento_ortografia": round(
            descuento,
            2
        ),
        "nota_final": round(
            nota_final,
            2
        )
    }

    columnas = [
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

    df_nuevo = pd.DataFrame(
        [fila],
        columns=columnas
    )

    try:

        if os.path.exists(
            CSV_FILE
        ):

            df_existente = pd.read_csv(
                CSV_FILE
            )

            df_final = pd.concat(
                [
                    df_existente,
                    df_nuevo
                ],
                ignore_index=True
            )

        else:

            df_final = df_nuevo

        df_final.to_csv(
            CSV_FILE,
            index=False,
            encoding="utf-8-sig"
        )

        return True

    except Exception as error:

        st.error(
            "No se pudieron guardar los resultados."
        )

        st.exception(error)

        return False


# ==============================================================
# CABECERA
# ==============================================================

st.markdown(
    '<div class="main-title">📚 Evaluación inicial de Lengua</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">2.º ESO · Lengua Castellana y Literatura</div>',
    unsafe_allow_html=True
)


# ==============================================================
# ESTADO DESPUÉS DE ENVIAR
# ==============================================================

if st.session_state.get(
    "examen_enviado",
    False
):

    st.success(
        "El examen se ha enviado correctamente."
    )

    nombre = st.session_state.get(
        "nombre",
        ""
    )

    curso = st.session_state.get(
        "curso",
        ""
    )

    puntos = st.session_state.get(
        "puntos",
        {}
    )

    nota_inicial = st.session_state.get(
        "nota_inicial",
        0
    )

    nota_final = st.session_state.get(
        "nota_final",
        0
    )

    faltas = st.session_state.get(
        "faltas",
        0
    )

    descuento = st.session_state.get(
        "descuento",
        0
    )

    respuestas_pdf = st.session_state.get(
        "respuestas_pdf",
        {}
    )

    st.subheader(
        f"Resultado de {nombre}"
    )

    st.write(
        f"Curso: **{curso}**"
    )

    st.metric(
        "Nota final",
        f"{nota_final:.2f}/10"
    )

    st.write(
        "### Resultado por competencias"
    )

    columnas = st.columns(5)

    nombres = [
        ("comprension", "Comprensión"),
        ("morfologia", "Morfología"),
        ("semantica", "Semántica"),
        ("literatura", "Literatura"),
        ("sintaxis", "Sintaxis")
    ]

    for columna, (
        clave,
        titulo
    ) in zip(
        columnas,
        nombres
    ):

        columna.metric(
            titulo,
            f"{puntos.get(clave, 0):.2f}"
        )

    st.write(
        f"Faltas de ortografía detectadas: **{faltas}**"
    )

    st.write(
        f"Descuento ortográfico: **-{descuento:.2f}**"
    )

    # ----------------------------------------------------------
    # GENERAR PDF
    # ----------------------------------------------------------

    if st.button(
        "📄 Generar PDF",
        key="generar_pdf"
    ):

        try:

            ruta_pdf = generar_pdf(
                nombre=nombre,
                curso=curso,
                resultados=puntos,
                respuestas=respuestas_pdf,
                faltas_ortografia=faltas,
                descuento_ortografia=descuento,
                nota_inicial=nota_inicial,
                nota_final=nota_final
            )

            with open(
                ruta_pdf,
                "rb"
            ) as archivo:

                datos_pdf = archivo.read()

            st.download_button(
                label="⬇️ Descargar PDF",
                data=datos_pdf,
                file_name=os.path.basename(
                    ruta_pdf
                ),
                mime="application/pdf",
                key="download_pdf"
            )

        except Exception as error:

            st.error(
                "No se pudo generar el PDF."
            )

            st.exception(error)

    st.info(
        "El resultado de la clase y el historial de otros alumnos no se muestran en esta pantalla."
    )

    st.stop()


# ==============================================================
# DATOS DEL ALUMNO
# ==============================================================

st.markdown(
    '<div class="section-title">Datos del alumno</div>',
    unsafe_allow_html=True
)

nombre = st.text_input(
    "Nombre y apellidos",
    placeholder="Escribe tu nombre y apellidos"
)

curso = st.selectbox(
    "Curso",
    [
        "",
        "2º A",
        "2º B",
        "2º C",
        "2º D"
    ]
)


# ==============================================================
# VALIDACIÓN INICIAL
# ==============================================================

if not nombre.strip():
    st.info(
        "Escribe tu nombre y apellidos para comenzar."
    )
    st.stop()

if not curso:
    st.info(
        "Selecciona tu curso."
    )
    st.stop()


# ==============================================================
# FORMULARIO COMPLETO
# ==============================================================
#
# IMPORTANTE:
# Todo está dentro de un formulario.
# El examen NO se guarda hasta pulsar ENVIAR.
#
# ==============================================================

with st.form(
    "formulario_examen"
):

    respuestas = {}

    # ==========================================================
    # 1. COMPRENSIÓN
    # ==========================================================

    st.markdown(
        '<div class="section-title">1. Comprensión lectora</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        EXAMEN["2ESO"]["comprension"]["texto"]
    )

    for pregunta in EXAMEN[
        "2ESO"
    ]["comprension"]["preguntas"]:

        pregunta_id = pregunta[
            "id"
        ]

        tipo = pregunta.get(
            "tipo",
            "texto"
        )

        if tipo == "lista":

            respuesta = st.text_area(
                pregunta["enunciado"],
                help=pregunta.get(
                    "ayuda",
                    ""
                ),
                key=pregunta_id,
                height=80
            )

        else:

            respuesta = st.text_input(
                pregunta["enunciado"],
                help=pregunta.get(
                    "ayuda",
                    ""
                ),
                key=pregunta_id
            )

        respuestas[
            pregunta_id
        ] = respuesta

    # ==========================================================
    # 2. MORFOLOGÍA
    # ==========================================================

    st.markdown(
        '<div class="section-title">2. Morfología</div>',
        unsafe_allow_html=True
    )

    for palabra in EXAMEN[
        "2ESO"
    ]["morfologia"]:

        st.markdown(
            f"### {palabra['palabra']}"
        )

        # ------------------------------
        # Lexema
        # ------------------------------

        key_lexema = (
            f"{palabra['id']}_Lexema"
        )

        respuestas[
            key_lexema
        ] = st.text_input(
            "Lexema",
            key=key_lexema
        )

        # ------------------------------
        # Morfemas
        # ------------------------------

        key_morfemas = (
            f"{palabra['id']}_Morfemas"
        )

        respuestas[
            key_morfemas
        ] = st.text_input(
            "Morfemas",
            help=(
                "Si hay varios, sepáralos con "
                "comas, + o espacios. "
                "Ejemplo: a + mente"
            ),
            key=key_morfemas
        )

        # ------------------------------
        # Estructura
        # ------------------------------

        key_estructura = (
            f"{palabra['id']}_"
            "Estructura de la palabra"
        )

        respuestas[
            key_estructura
        ] = st.selectbox(
            "Estructura de la palabra",
            [
                "",
                "simple",
                "compuesta",
                "derivada",
                "parasintética"
            ],
            key=key_estructura
        )

        # ------------------------------
        # Categoría gramatical
        # ------------------------------

        key_categoria = (
            f"{palabra['id']}_"
            "Categoría gramatical completa"
        )

        respuestas[
            key_categoria
        ] = st.text_input(
            "Categoría gramatical completa",
            help=(
                "Escribe toda la información "
                "y sepárala por comas. "
                "Ejemplo: sustantivo, común, "
                "concreto, masculino, singular."
            ),
            key=key_categoria
        )

        # ------------------------------
        # Variable / Invariable
        # ------------------------------

        key_vi = (
            f"{palabra['id']}_V / I"
        )

        respuestas[
            key_vi
        ] = st.selectbox(
            "V / I",
            [
                "",
                "variable",
                "invariable"
            ],
            key=key_vi
        )

        st.divider()

    # ==========================================================
    # 3. DETERMINANTES / PRONOMBRES
    # ==========================================================

    st.markdown(
        '<div class="section-title">3. Determinantes y pronombres</div>',
        unsafe_allow_html=True
    )

    for pregunta in EXAMEN[
        "2ESO"
    ]["determinantes_pronombres"]:

        st.markdown(
            f"**{pregunta['frase']}**"
        )

        respuestas[
            pregunta["id"]
        ] = st.selectbox(
            pregunta["enunciado"],
            [
                "",
                "determinante",
                "pronombre"
            ],
            key=pregunta["id"]
        )

    # ==========================================================
    # 4. SEMÁNTICA
    # ==========================================================

    st.markdown(
        '<div class="section-title">4. Semántica y tipología textual</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "### 4. Semántica"
    )

    opciones_semantica = [
        "",
        "antonimia",
        "sinonimia",
        "campo semántico",
        "polisemia",
        "homonimia",
        "meronimia",
        "hipónimos",
        "hiperónimo"
    ]

    for pregunta in EXAMEN[
        "2ESO"
    ]["semantica"]:

        st.markdown(
            f"**{pregunta['elemento']}**"
        )

        respuestas[
            pregunta["id"]
        ] = st.selectbox(
            pregunta["enunciado"],
            opciones_semantica,
            key=pregunta["id"]
        )

    # ==========================================================
    # 4. TIPOLOGÍA TEXTUAL
    # ==========================================================

    st.markdown(
        "### 4.1. Tipología textual"
    )

    opciones_texto = [
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

        texto = pregunta.get(
            "texto",
            ""
        )

        if texto:
            st.markdown(
                f"**{texto}**"
            )

        st.markdown(
            f"**{pregunta['enunciado']}**"
        )

        respuestas[
            pregunta["id"]
        ] = st.selectbox(
            "Selecciona una opción",
            opciones_texto,
            key=pregunta["id"]
        )

    # ==========================================================
    # 5. LITERATURA
    # ==========================================================

    st.markdown(
        '<div class="section-title">5. Literatura</div>',
        unsafe_allow_html=True
    )

    literatura = EXAMEN[
        "2ESO"
    ]["literatura"]

    poema = literatura[0]

    if poema.get(
        "tipo"
    ) == "poema":

        st.markdown(
            f"**{poema['enunciado']}**"
        )

        for verso in poema[
            "versos"
        ]:
            st.markdown(
                verso
            )

    # 5.1
    l1 = next(
        p for p in literatura
        if p["id"] == "l1"
    )

    respuestas["l1"] = st.selectbox(
        l1["enunciado"],
        [
            "",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8"
        ],
        key="l1"
    )

    # 5.2
    l2 = next(
        p for p in literatura
        if p["id"] == "l2"
    )

    respuestas["l2"] = st.selectbox(
        l2["enunciado"],
        [
            "",
            "arte menor",
            "arte mayor"
        ],
        key="l2"
    )

    # 5.3 MÉTRICA - TEXT INPUT
    l3 = next(
        p for p in literatura
        if p["id"] == "l3"
    )

    respuestas["l3"] = st.text_input(
        l3["enunciado"],
        help=(
            "Ejemplo: 14A 14B 14B 14A. "
            "También se admiten comas o barras."
        ),
        key="l3"
    )

    # 5.4 RIMA
    l4 = next(
        p for p in literatura
        if p["id"] == "l4"
    )

    respuestas["l4"] = st.selectbox(
        l4["enunciado"],
        [
            "",
            "asonante",
            "consonante"
        ],
        key="l4"
    )

    # 5.5 SINALEFA
    l5 = next(
        p for p in literatura
        if p["id"] == "l5"
    )

    respuestas["l5"] = st.text_input(
        l5["enunciado"],
        help=l5.get(
            "ayuda",
            ""
        ),
        key="l5"
    )

    # 5.6 PERSONIFICACIÓN
    l6 = next(
        p for p in literatura
        if p["id"] == "l6"
    )

    respuestas["l6"] = st.text_input(
        l6["enunciado"],
        help=l6.get(
            "ayuda",
            ""
        ),
        key="l6"
    )

    # ==========================================================
    # 6. SINTAXIS
    # ==========================================================

    st.markdown(
        '<div class="section-title">6. Sintaxis</div>',
        unsafe_allow_html=True
    )

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

            opciones = [
                "",
                "frase",
                "oración"
            ]

        else:

            opciones = [
                "",
                "enunciativa",
                "interrogativa",
                "exclamativa",
                "desiderativa",
                "exhortativa"
            ]

        respuestas[
            pregunta["id"]
        ] = st.selectbox(
            pregunta["enunciado"],
            opciones,
            key=pregunta["id"]
        )

    # ==========================================================
    # 7. DIÁLOGO
    # ==========================================================

    st.markdown(
        '<div class="section-title">7. Diálogo</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "### Texto dialogado"
    )

    st.markdown(
        EXAMEN[
            "2ESO"
        ]["dialogo"]["texto"]
    )

    for pregunta in EXAMEN[
        "2ESO"
    ]["dialogo"]["preguntas"]:

        tipo = pregunta.get(
            "tipo",
            ""
        )

        if tipo == "lista":

            respuestas[
                pregunta["id"]
            ] = st.text_area(
                pregunta["enunciado"],
                help=pregunta.get(
                    "ayuda",
                    ""
                ),
                key=pregunta["id"],
                height=70
            )

        elif tipo == "estilo_indirecto":

            respuestas[
                pregunta["id"]
            ] = st.text_area(
                pregunta["enunciado"],
                help=(
                    "Escribe la respuesta completa "
                    "en estilo indirecto."
                ),
                key=pregunta["id"],
                height=100
            )

        else:

            respuestas[
                pregunta["id"]
            ] = st.text_input(
                pregunta["enunciado"],
                key=pregunta["id"]
            )

    # ==========================================================
    # ENVÍO
    # ==========================================================

    st.divider()

    enviar = st.form_submit_button(
        "✅ ENVIAR EXAMEN",
        use_container_width=True
    )


# ==============================================================
# PROCESAR ENVÍO
# ==============================================================

if enviar:

    # ----------------------------------------------------------
    # Comprobar nombre y curso
    # ----------------------------------------------------------

    if not nombre.strip():

        st.error(
            "Debes escribir tu nombre y apellidos."
        )

        st.stop()

    if not curso:

        st.error(
            "Debes seleccionar tu curso."
        )

        st.stop()

    # ----------------------------------------------------------
    # CORREGIR
    # ----------------------------------------------------------

    puntos, nota_inicial, respuestas_pdf = (
        corregir_examen(
            respuestas
        )
    )

    # ----------------------------------------------------------
    # ORTOGRAFÍA
    # ----------------------------------------------------------

    textos_para_ortografia = list(
        respuestas.values()
    )

    resultado_ortografia = detectar_ortografia(
        textos_para_ortografia
    )

    faltas = resultado_ortografia[
        "faltas"
    ]

    descuento = resultado_ortografia[
        "descuento"
    ]

    nota_final = max(
        0.0,
        nota_inicial - descuento
    )

    nota_final = round(
        nota_final,
        2
    )

    # ----------------------------------------------------------
    # GUARDAR CSV
    # ----------------------------------------------------------

    guardado = guardar_resultado(
        nombre=nombre.strip(),
        curso=curso,
        puntos=puntos,
        nota_inicial=nota_inicial,
        faltas=faltas,
        descuento=descuento,
        nota_final=nota_final
    )

    if not guardado:
        st.stop()

    # ----------------------------------------------------------
    # GUARDAR EN SESSION STATE
    # ----------------------------------------------------------

    st.session_state[
        "examen_enviado"
    ] = True

    st.session_state[
        "nombre"
    ] = nombre.strip()

    st.session_state[
        "curso"
    ] = curso

    st.session_state[
        "puntos"
    ] = puntos

    st.session_state[
        "nota_inicial"
    ] = nota_inicial

    st.session_state[
        "nota_final"
    ] = nota_final

    st.session_state[
        "faltas"
    ] = faltas

    st.session_state[
        "descuento"
    ] = descuento

    st.session_state[
        "respuestas_pdf"
    ] = respuestas_pdf

    # ----------------------------------------------------------
    # RECARGAR PARA MOSTRAR RESULTADO
    # ----------------------------------------------------------

    st.rerun()
