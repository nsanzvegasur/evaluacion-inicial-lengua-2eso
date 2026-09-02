import streamlit as st
import pandas as pd
from datetime import datetime
import re
import unicodedata

from analytics import (
    radar_chart,
    comparativa,
    generar_perfil
)

from pdf_report import generar_pdf

from examen2ESO import EXAMEN


# =========================================================
# CONFIGURACION
# =========================================================

st.set_page_config(
    page_title="Evaluación Inicial Lengua 2º ESO",
    page_icon="📘",
    layout="wide"
)

st.title("📘 Evaluación Inicial - Lengua Castellana y Literatura")
st.caption("2.º ESO")


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

    df = pd.read_csv("results.csv")

    for columna in COLUMNAS:

        if columna not in df.columns:
            df[columna] = 0

except Exception:

    df = pd.DataFrame(columns=COLUMNAS)


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def normalizar(texto):

    texto = str(texto).lower().strip()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )

    return texto


def contiene_respuesta(respuesta, criterios):

    texto = normalizar(respuesta)

    for criterio in criterios:

        if normalizar(criterio) in texto:
            return True

    return False


def corregir_exacta(respuesta, correcta):

    return normalizar(respuesta) == normalizar(correcta)


# =========================================================
# CORRECCION AUTOMATICA DE ORTOGRAFIA
# =========================================================

def detectar_ortografia(respuestas):

    """
    Intenta utilizar LanguageTool para detectar faltas.

    Si LanguageTool no está disponible, la aplicación
    continúa funcionando y devuelve 0 errores.
    """

    textos = []

    for respuesta in respuestas:

        if respuesta and str(respuesta).strip():
            textos.append(str(respuesta))

    texto_completo = "\n".join(textos)

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
                match.offset + match.errorLength
            ]

            clave = (
                palabra.lower(),
                match.offset
            )

            # Reglas relacionadas con tildes
            if (
                "ACCENT" in regla
                or "TILDE" in regla
                or "DIACRIT" in regla
                or "ACENTO" in mensaje
                or "TILDE" in mensaje
            ):

                tildes.add(clave)

            # Reglas de posible error ortográfico
            elif (
                "TYPO" in regla
                or "SPELL" in regla
                or "MORFO" in regla
                or "HUNSPELL" in regla
            ):

                faltas.add(clave)

        try:
            tool.close()
        except Exception:
            pass

        return len(faltas), len(tildes)

    except Exception:

        return 0, 0


# =========================================================
# CORRECCION DE PREGUNTAS
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
    # COMPRENSION
    # =====================================================

    for pregunta in EXAMEN["2ESO"]["comprension"]["preguntas"]:

        pid = pregunta["id"]

        respuesta = respuestas.get(
            pid,
            ""
        )

        maximo = pregunta["puntos"]

        obtenido = 0

        tipo = pregunta.get(
            "tipo",
            "texto"
        )

        if tipo in ["texto", "accion"]:

            if contiene_respuesta(
                respuesta,
                pregunta.get(
                    "criterios",
                    []
                )
            ):

                obtenido = maximo

        elif tipo == "resumen":

            texto = normalizar(
                respuesta
            )

            criterios = pregunta.get(
                "criterios",
                []
            )

            encontrados = sum(
                1
                for c in criterios
                if normalizar(c) in texto
            )

            if len(texto.split()) >= 15:

                porcentaje = encontrados / max(
                    len(criterios),
                    1
                )

                obtenido = maximo * min(
                    porcentaje,
                    1
                )

        puntos["comprension"] += obtenido

        detalles.append(
            (
                pid,
                pregunta["enunciado"],
                obtenido,
                maximo
            )
        )

    # =====================================================
    # MORFOLOGIA
    # =====================================================

    for pregunta in EXAMEN["2ESO"]["morfologia"]:

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

        for campo in pregunta["campos"]:

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

            puntos["morfologia"] += obtenido

            detalles.append(
                (
                    f"{pid}_{campo}",
                    f"{pregunta['palabra']} - {campo}",
                    obtenido,
                    puntos_por_campo
                )
            )

    # =====================================================
    # DETERMINANTES / PRONOMBRES
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

        puntos["morfologia"] += obtenido

        detalles.append(
            (
                pregunta["id"],
                pregunta["enunciado"],
                obtenido,
                pregunta["puntos"]
            )
        )

    # =====================================================
    # SEMANTICA
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

        puntos["semantica"] += obtenido

        detalles.append(
            (
                pregunta["id"],
                pregunta["elemento"],
                obtenido,
                pregunta["puntos"]
            )
        )

    # =====================================================
    # TEXTOS
    # =====================================================

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "textos"
    ]:

        respuesta = respuestas.get(
            pregunta["id"],
            ""
        )

        maximo = pregunta["puntos"]

        if pregunta.get("tipo") == "finalidad":

            texto = normalizar(
                respuesta
            )

            palabras_clave = [
                "informar",
                "explicar",
                "enseñar",
                "indicar",
                "ordenar",
                "dar instrucciones",
                "convencer",
                "persuadir",
                "concienciar",
                "conciencia"
            ]

            encontrados = sum(
                1
                for palabra in palabras_clave
                if normalizar(palabra) in texto
            )

            if encontrados >= 1:
                obtenido = maximo
            else:
                obtenido = 0

        else:

            obtenido = (
                maximo
                if corregir_exacta(
                    respuesta,
                    pregunta["respuesta"]
                )
                else 0
            )

        puntos["literatura"] += 0

        # Los textos tienen competencia propia,
        # pero no existe columna "textos":
        # se incorpora a semántica/competencia de textos
        # mediante literatura no.
        #
        # Se guarda temporalmente en detalles.

        detalles.append(
            (
                pregunta["id"],
                pregunta["enunciado"],
                obtenido,
                maximo
            )
        )

    # =====================================================
    # LITERATURA
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

        maximo = pregunta["puntos"]

        tipo = pregunta.get(
            "tipo",
            "exacta"
        )

        obtenido = 0

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

        elif tipo == "sinalefa":

            texto = normalizar(
                respuesta
            )

            if (
                "sinalefa" in texto
                and len(texto.split()) >= 2
            ):
                obtenido = maximo

            elif any(
                x in texto
                for x in [
                    "lluvia cae",
                    "suave en",
                    "y el",
                    "juega solo",
                    "si todo",
                    "todo fuera"
                ]
            ):
                obtenido = maximo

        elif tipo == "personificacion":

            texto = normalizar(
                respuesta
            )

            if (
                "viento juega" in texto
                or "el viento juega" in texto
                or (
                    "personificacion" in texto
                    and "viento" in texto
                )
            ):
                obtenido = maximo

        puntos["literatura"] += obtenido

        detalles.append(
            (
                pregunta["id"],
                pregunta["enunciado"],
                obtenido,
                maximo
            )
        )

    # =====================================================
    # SINTAXIS
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

        puntos["sintaxis"] += obtenido

        detalles.append(
            (
                pregunta["id"],
                pregunta["frase"],
                obtenido,
                pregunta["puntos"]
            )
        )

    # =====================================================
    # DIÁLOGO
    # =====================================================

    dialogo = EXAMEN[
        "2ESO"
    ][
        "dialogo"
    ]

    for pregunta in dialogo["preguntas"]:

        respuesta = respuestas.get(
            pregunta["id"],
            ""
        )

        maximo = pregunta["puntos"]

        tipo = pregunta.get(
            "tipo",
            "exacta"
        )

        obtenido = 0

        if tipo == "exacta":

            correcto = corregir_exacta(
                respuesta,
                pregunta["respuesta"]
            )

            if correcto:
                obtenido = maximo

        elif tipo == "estilo_indirecto":

            texto = normalizar(
                respuesta
            )

            # Respuestas válidas del tipo:
            # Carlos dijo que lo había hecho
            # Carlos dijo que sí, que lo había hecho
            if (
                "carlos" in texto
                and "dijo" in texto
                and (
                    "habia hecho" in texto
                    or "lo habia hecho" in texto
                )
            ):
                obtenido = maximo

        detalles.append(
            (
                pregunta["id"],
                pregunta["enunciado"],
                obtenido,
                maximo
            )
        )

    return puntos, detalles


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
    # 1. COMPRENSION
    # =====================================================

    st.divider()
    st.header("1. Comprensión lectora")

    st.write(
        EXAMEN["2ESO"]["comprension"]["texto"]
    )

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "comprension"
    ][
        "preguntas"
    ]:

        respuestas[
            pregunta["id"]
        ] = st.text_area(
            pregunta["enunciado"],
            help=pregunta.get(
                "ayuda",
                ""
            ),
            key=f"comp_{pregunta['id']}"
        )

    # =====================================================
    # 2. MORFOLOGIA
    # =====================================================

    st.divider()
    st.header(
        "2. Morfología y categorías gramaticales"
    )

    st.subheader(
        "2.1. Análisis morfológico"
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
            len(pregunta["campos"])
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
                    key=f"morf_{pregunta['id']}_{campo}"
                )

    # =====================================================
    # 2.2 DETERMINANTES
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
    # 3. SEMANTICA
    # =====================================================

    st.divider()
    st.header("3. Semántica")

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
    st.header("4. Textos")

    for pregunta in EXAMEN[
        "2ESO"
    ][
        "textos"
    ]:

        if "texto" in pregunta:

            st.info(
                pregunta["texto"]
            )

            respuestas[
                pregunta["id"]
            ] = st.selectbox(
                pregunta["enunciado"],
                [
                    "",
                    "Narrativo",
                    "Descriptivo",
                    "Expositivo",
                    "Argumentativo",
                    "Instructivo",
                    "Dialogado"
                ],
                key=f"texto_{pregunta['id']}"
            )

        else:

            respuestas[
                pregunta["id"]
            ] = st.text_area(
                pregunta["enunciado"],
                key=f"texto_{pregunta['id']}"
            )

    # =====================================================
    # 5. LITERATURA
    # =====================================================

    st.divider()
    st.header("5. Literatura")

    poema = next(
        p for p in EXAMEN[
            "2ESO"
        ][
            "literatura"
        ]
        if p["id"] == "l0"
    )

    st.write(
        poema["enunciado"]
    )

    # =====================================================
    # POEMA EN TABLA
    # =====================================================

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

        respuestas[
            pregunta["id"]
        ] = st.text_area(
            pregunta["enunciado"],
            key=f"lit_{pregunta['id']}"
        )

    # =====================================================
    # 6. SINTAXIS
    # =====================================================

    st.divider()
    st.header("6. Sintaxis")

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
    # 7. DIALOGO
    # =====================================================

    st.divider()
    st.header("7. Diálogo")

    st.write(
        EXAMEN["2ESO"]["dialogo"]["texto"]
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
        ] = st.text_area(
            pregunta["enunciado"],
            key=f"dialogo_{pregunta['id']}"
        )

    # =====================================================
    # AVISO ORTOGRAFIA
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
        type="primary"
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

            puntos, detalles = corregir_examen(
                respuestas,
                respuestas_morf,
                respuestas_dp
            )

            # =============================================
            # CONVERTIR A NOTAS SOBRE 10
            # =============================================

            # Comprensión = 2 puntos
            # Morfología = 2.5 puntos
            # Semántica = 1.5 puntos
            # Literatura = 2 puntos
            # Sintaxis = 1 punto
            #
            # Textos = 1 punto
            # Diálogo = 0.5 puntos
            #
            # Como el dashboard tiene 5 competencias,
            # Textos se integra en comprensión y diálogo
            # en sintaxis.

            # Puntuación real de cada bloque

            comprension_puntos = puntos[
                "comprension"
            ]

            morfologia_puntos = puntos[
                "morfologia"
            ]

            semantica_puntos = puntos[
                "semantica"
            ]

            literatura_puntos = puntos[
                "literatura"
            ]

            sintaxis_puntos = puntos[
                "sintaxis"
            ]

            # Recuperamos textos y diálogo
            textos_puntos = 0
            dialogo_puntos = 0

            for detalle in detalles:

                pid = detalle[0]
                obtenido = detalle[2]

                if pid.startswith("t"):
                    textos_puntos += obtenido

                if pid.startswith("d"):
                    dialogo_puntos += obtenido

            # =============================================
            # NOTAS SOBRE 10
            # =============================================

            scores = {

                "comprension": min(
                    10,
                    (
                        comprension_puntos
                        + textos_puntos
                    ) / 3 * 10
                ),

                "morfologia": min(
                    10,
                    morfologia_puntos
                    / 3 * 10
                ),

                "semantica": min(
                    10,
                    semantica_puntos
                    / 0.5 * 10
                ),

                "literatura": min(
                    10,
                    literatura_puntos
                    / 2 * 10
                ),

                "sintaxis": min(
                    10,
                    (
                        sintaxis_puntos
                        + dialogo_puntos
                    ) / 1.5 * 10
                )
            }

            # =============================================
            # NOTA INICIAL
            # =============================================

            nota_inicial = (
                (
                    comprension_puntos
                    + morfologia_puntos
                    + semantica_puntos
                    + textos_puntos
                    + literatura_puntos
                    + sintaxis_puntos
                    + dialogo_puntos
                )
                / 10
            ) * 10

            nota_inicial = max(
                0,
                min(
                    10,
                    nota_inicial
                )
            )

            # =============================================
            # ORTOGRAFIA AUTOMATICA
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

            faltas_ortografia, faltas_tildes = detectar_ortografia(
                todas_respuestas
            )

            # =============================================
            # DESCUENTO
            # =============================================

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

                **scores,

                "nota_inicial": round(
                    nota_inicial,
                    2
                ),

                "faltas_ortografia": faltas_ortografia,

                "faltas_tildes": faltas_tildes,

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
            # RESULTADO EN PANTALLA
            # =============================================

            st.success(
                "Examen corregido y guardado correctamente."
            )

            col1, col2, col3 = st.columns(3)

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
            # ORTOGRAFIA
            # =============================================

            st.write(
                "### Corrección ortográfica"
            )

            st.write(
                f"Faltas de ortografía detectadas: "
                f"**{faltas_ortografia}**"
            )

            st.write(
                f"Faltas de tilde detectadas: "
                f"**{faltas_tildes}**"
            )

            st.write(
                f"Descuento aplicado: "
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
                use_container_width=True
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
            # DETALLE DE CORRECCION
            # =============================================

            st.write(
                "### Detalle de corrección"
            )

            tabla_detalles = []

            for pid, pregunta, obtenido, maximo in detalles:

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

                with open(
                    pdf_file,
                    "rb"
                ) as archivo:

                    st.download_button(
                        label="📄 Descargar informe PDF",
                        data=archivo,
                        file_name=pdf_file,
                        mime="application/pdf"
                    )

            except Exception as error:

                st.error(
                    f"No se pudo generar el PDF: {error}"
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
        # MEDIA CLASE
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
            df[competencias].mean()
        )

        # =============================================
        # NOTAS GENERALES
        # =============================================

        col1, col2, col3 = st.columns(3)

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

        st.dataframe(
            df[columnas_mostrar],
            use_container_width=True
        )

        # =============================================
        # ALUMNO
        # =============================================

        st.subheader(
            "Comparativa individual"
        )

        alumno_seleccionado = st.selectbox(
            "Selecciona alumno",
            sorted(
                df["name"]
                .dropna()
                .unique()
            ),
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
            use_container_width=True
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

        alumno_seleccionado = st.selectbox(
            "Selecciona alumno",
            sorted(
                df["name"]
                .dropna()
                .unique()
            ),
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

        col1, col2, col3 = st.columns(3)

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
            use_container_width=True
        )
