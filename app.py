import streamlit as st
import pandas as pd
from datetime import datetime
import re

from analytics import radar_chart, comparativa, generar_perfil
from pdf_report import generar_pdf
from examen2ESO import EXAMEN


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Evaluación Inicial Lengua ESO",
    page_icon="📘",
    layout="wide"
)

st.title("📘 Evaluación Inicial - Lengua Castellana y Literatura")
st.caption("2.º ESO · Prueba inicial diagnóstica")


# ============================================================
# CARGA DE RESULTADOS
# ============================================================

COLUMNAS = [
    "name",
    "group",
    "date",
    "comprension",
    "morfologia",
    "semantica",
    "textos",
    "literatura",
    "sintaxis",
    "dialogo",
    "total"
]

try:
    df = pd.read_csv("results.csv")

    for columna in COLUMNAS:
        if columna not in df.columns:
            df[columna] = 0

except Exception:
    df = pd.DataFrame(columns=COLUMNAS)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def normalizar(texto):
    """Normaliza respuestas para comparaciones automáticas."""
    texto = str(texto).strip().lower()

    reemplazos = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ü": "u"
    }

    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo)

    texto = re.sub(r"[¿?¡!.,;:\"'«»]", "", texto)

    return texto.strip()


def contiene_alguna(texto, opciones):
    texto = normalizar(texto)

    return any(
        normalizar(opcion) in texto
        for opcion in opciones
    )


def corregir_exacta(respuesta, correcta):
    return normalizar(respuesta) == normalizar(correcta)


def puntuar_texto_por_claves(respuesta, claves, puntos):
    """
    Corrección básica de respuestas abiertas.
    No pretende sustituir una corrección docente.
    """
    texto = normalizar(respuesta)

    if not texto:
        return 0

    encontradas = sum(
        1 for clave in claves
        if normalizar(clave) in texto
    )

    if encontradas == 0:
        return 0

    proporcion = encontradas / len(claves)

    return round(puntos * proporcion, 2)


# ============================================================
# PESTAÑAS
# ============================================================

tab_examen, tab_dashboard, tab_alumno = st.tabs(
    [
        "🧑‍🎓 Examen",
        "📊 Dashboard",
        "👤 Alumno"
    ]
)


# ============================================================
# EXAMEN
# ============================================================

with tab_examen:

    st.header("Evaluación inicial")

    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input(
            "Nombre y apellidos",
            key="nombre"
        )

    with col2:
        grupo = st.text_input(
            "Grupo",
            key="grupo"
        )

    fecha = st.date_input(
        "Fecha",
        value=datetime.now().date()
    )


    # ========================================================
    # ORTOGRAFÍA Y PRESENTACIÓN
    # ========================================================

    with st.expander("📝 Ortografía y presentación", expanded=False):

        st.write(
            "Estas penalizaciones reproducen las indicaciones del examen."
        )

        col1, col2 = st.columns(2)

        with col1:
            faltas_ortografia = st.number_input(
                "Faltas de ortografía",
                min_value=0,
                max_value=20,
                value=0,
                step=1
            )

        with col2:
            faltas_tildes = st.number_input(
                "Faltas de tilde",
                min_value=0,
                max_value=20,
                value=0,
                step=1
            )

        nee = st.checkbox(
            "Alumno con adaptación por Dificultades de Lectoescritura / NEE"
        )

        presentacion = st.number_input(
            "Descuento por presentación (0 a 1,5 puntos)",
            min_value=0.0,
            max_value=1.5,
            value=0.0,
            step=0.1
        )


    # ========================================================
    # 1. COMPRENSIÓN
    # ========================================================

    st.divider()
    st.header("1. COMPRENSIÓN LECTORA · 2 puntos")

    st.write(
        "### Lee el siguiente texto"
    )

    st.info(
        EXAMEN["2ESO"]["comprension"]["texto"]
    )

    q_comp = {}

    st.subheader("1.1. Lugar, tiempo y ambiente")

    c1, c2, c3 = st.columns(3)

    with c1:
        q_comp["c1"] = st.text_input(
            "Lugar",
            key="c_c1"
        )

    with c2:
        q_comp["c2"] = st.text_input(
            "Tiempo",
            key="c_c2"
        )

    with c3:
        q_comp["c3"] = st.text_input(
            "Ambiente",
            key="c_c3"
        )

    q_comp["c4"] = st.text_area(
        "1.2. Escribe tres acciones que ocurren en el texto.",
        key="c_c4"
    )

    q_comp["c5"] = st.text_area(
        "1.3. Resume el texto con tus palabras.",
        height=130,
        key="c_c5"
    )


    # ========================================================
    # 2. MORFOLOGÍA
    # ========================================================

    st.divider()
    st.header("2. MORFOLOGÍA Y CATEGORÍAS GRAMATICALES · 2,5 puntos")

    st.subheader("2.1. Análisis morfológico · 2 puntos")

    q_morf = {}

    for palabra in EXAMEN["2ESO"]["morfologia"]:

        st.markdown(
            f"### Palabra: **{palabra['palabra']}**"
        )

        respuestas = {}

        columnas = st.columns(5)

        for i, campo in enumerate(palabra["campos"]):

            with columnas[i]:

                if campo == "V/I":

                    respuestas[campo] = st.selectbox(
                        "V/I",
                        [
                            "",
                            "Variable",
                            "Invariable"
                        ],
                        key=f"{palabra['id']}_{campo}"
                    )

                else:

                    respuestas[campo] = st.text_input(
                        campo,
                        key=f"{palabra['id']}_{campo}"
                    )

        q_morf[palabra["id"]] = respuestas

    st.subheader("2.2. Determinantes y pronombres · 0,5 puntos")

    q_det = {}

    for pregunta in EXAMEN["2ESO"]["determinantes_pronombres"]:

        q_det[pregunta["id"]] = st.selectbox(
            pregunta["texto"],
            [
                "",
                "Determinante",
                "Pronombre"
            ],
            key=pregunta["id"]
        )


    # ========================================================
    # 3. SEMÁNTICA
    # ========================================================

    st.divider()
    st.header("3. SEMÁNTICA · 1,5 puntos")

    st.write(
        "Relaciona cada caso con la relación semántica correspondiente."
    )

    opciones_semantica = [
        "",
        "Antonimia",
        "Campo semántico",
        "Polisemia",
        "Meronimia",
        "Hipónimos"
    ]

    q_sem = {}

    for pregunta in EXAMEN["2ESO"]["semantica"]:

        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(
                f"**{pregunta['texto']}**"
            )

        with col2:
            q_sem[pregunta["id"]] = st.selectbox(
                "Relación",
                opciones_semantica,
                key=pregunta["id"]
            )


    # ========================================================
    # 4. TEXTOS
    # ========================================================

    st.divider()
    st.header("4. TEXTOS · 1 punto")

    textos = EXAMEN["2ESO"]["textos"]

    st.write("### Texto A")
    st.info(textos["texto_a"])

    st.write("### Texto B")
    st.info(textos["texto_b"])

    st.write("### Texto C")
    st.info(textos["texto_c"])

    opciones_textos = [
        "",
        "Narrativo",
        "Descriptivo",
        "Expositivo",
        "Argumentativo",
        "Instructivo",
        "Dialogado"
    ]

    q_textos = {}

    q_textos["t1"] = st.selectbox(
        "4.1. Texto A: tipo de texto",
        opciones_textos,
        key="texto_a_tipo"
    )

    q_textos["t2"] = st.selectbox(
        "4.1. Texto B: tipo de texto",
        opciones_textos,
        key="texto_b_tipo"
    )

    q_textos["t3"] = st.selectbox(
        "4.1. Texto C: tipo de texto",
        opciones_textos,
        key="texto_c_tipo"
    )

    q_textos["t4"] = st.text_area(
        "4.2. Explica la finalidad de uno de los textos.",
        key="texto_finalidad"
    )


    # ========================================================
    # 5. LITERATURA
    # ========================================================

    st.divider()
    st.header("5. LITERATURA · 2 puntos")

    st.write("### Lee el poema")

    # IMPORTANTE:
    # Cada verso aparece en una fila independiente.

    poema_df = pd.DataFrame({
        "Verso": [1, 2, 3, 4],
        "Texto": EXAMEN["2ESO"]["literatura"]["poema"]
    })

    st.table(poema_df)


    q_lit = {}

    q_lit["l1"] = st.number_input(
        "Número de versos",
        min_value=0,
        max_value=20,
        value=0,
        step=1,
        key="lit_l1"
    )

    q_lit["l2"] = st.selectbox(
        "Arte mayor o menor",
        [
            "",
            "Arte mayor",
            "Arte menor"
        ],
        key="lit_l2"
    )

    q_lit["l3"] = st.text_input(
        "Esquema métrico",
        key="lit_l3"
    )

    q_lit["l4"] = st.selectbox(
        "Tipo de rima",
        [
            "",
            "Consonante",
            "Asonante",
            "Sin rima"
        ],
        key="lit_l4"
    )

    q_lit["l5"] = st.text_area(
        "Una sinalefa (explicada)",
        key="lit_l5"
    )

    q_lit["l6"] = st.text_area(
        "Una personificación y explicación",
        key="lit_l6"
    )


    # ========================================================
    # 6. SINTAXIS
    # ========================================================

    st.divider()
    st.header("6. SINTAXIS · 1 punto")

    q_syn = {}

    st.subheader("6.1. Frase u oración · 0,5 puntos")

    opciones_frase = [
        "",
        "Frase",
        "Oración"
    ]

    for pregunta in EXAMEN["2ESO"]["sintaxis"][:5]:

        q_syn[pregunta["id"]] = st.selectbox(
            f"{pregunta['frase']} → {pregunta['tipo']}",
            opciones_frase,
            key=pregunta["id"]
        )


    st.subheader("6.2. Modalidad oracional · 0,5 puntos")

    opciones_modalidad = [
        "",
        "Enunciativa",
        "Interrogativa",
        "Exclamativa",
        "Imperativa",
        "Desiderativa",
        "Dubitativa"
    ]

    for pregunta in EXAMEN["2ESO"]["sintaxis"][5:]:

        q_syn[pregunta["id"]] = st.selectbox(
            f"{pregunta['frase']} → {pregunta['tipo']}",
            opciones_modalidad,
            key=pregunta["id"]
        )


    # ========================================================
    # 7. DIÁLOGO
    # ========================================================

    st.divider()
    st.header("7. DIÁLOGO · 0,5 puntos")

    for linea in EXAMEN["2ESO"]["dialogo"]["texto"]:
        st.write(linea)

    q_dialogo = {}

    q_dialogo["d1"] = st.text_input(
        "7.1. Interlocutores",
        key="dialogo_d1"
    )

    q_dialogo["d2"] = st.number_input(
        "7.2. Número de intervenciones",
        min_value=0,
        max_value=20,
        value=0,
        step=1,
        key="dialogo_d2"
    )

    q_dialogo["d3"] = st.text_area(
        "7.3. Pasa a estilo indirecto: Carlos: «Sí, lo hice ayer por la tarde».",
        key="dialogo_d3"
    )


    # ========================================================
    # ENVIAR
    # ========================================================

    st.divider()

    enviar = st.button(
        "📤 ENTREGAR EXAMEN",
        type="primary",
        use_container_width=True
    )


    if enviar:

        if not nombre.strip() or not grupo.strip():

            st.error(
                "Debes introducir nombre y apellidos y grupo."
            )

        else:

            # =================================================
            # CORRECCIÓN
            # =================================================

            resultados = {}

            # -------------------------------------------------
            # COMPRENSIÓN
            # -------------------------------------------------

            comp = 0

            comp += puntuar_texto_por_claves(
                q_comp["c1"],
                ["tren", "vagon", "vagón", "estacion", "estación"],
                0.20
            )

            comp += puntuar_texto_por_claves(
                q_comp["c2"],
                ["madrugada", "amanecer", "noche"],
                0.15
            )

            comp += puntuar_texto_por_claves(
                q_comp["c3"],
                ["silencio", "extraño", "misterioso", "soledad", "tranquilo"],
                0.15
            )

            acciones_clave = [
                "recorria",
                "recorría",
                "detenia",
                "detenía",
                "avanzaba",
                "miraba",
                "sujetaba",
                "dormia",
                "dormía",
                "bajo",
                "respiró",
                "respiro",
                "camino",
                "caminó"
            ]

            comp += puntuar_texto_por_claves(
                q_comp["c4"],
                acciones_clave,
                0.50
            )

            comp += puntuar_texto_por_claves(
                q_comp["c5"],
                [
                    "tren",
                    "viajero",
                    "estacion",
                    "estación",
                    "madrugada",
                    "ciudad",
                    "bajo",
                    "salida"
                ],
                1.00
            )

            resultados["comprension"] = min(2.0, comp)


            # -------------------------------------------------
            # MORFOLOGÍA
            # -------------------------------------------------

            morf = 0

            respuestas_morf = {
                "m1": {
                    "Lexema": ["silenci"],
                    "Morfemas": ["o"],
                    "Tipo de estructura": ["simple"],
                    "Categoría gramatical": ["sustantivo"],
                    "V/I": ["Variable"]
                },

                "m2": {
                    "Lexema": ["lent"],
                    "Morfemas": ["amente", "mente"],
                    "Tipo de estructura": ["derivada"],
                    "Categoría gramatical": ["adverbio"],
                    "V/I": ["Invariable"]
                },

                "m3": {
                    "Lexema": ["conoc"],
                    "Morfemas": ["des", "ido", "desconocido"],
                    "Tipo de estructura": ["derivada"],
                    "Categoría gramatical": ["adjetivo"],
                    "V/I": ["Variable"]
                },

                "m4": {
                    "Lexema": ["mochil"],
                    "Morfemas": ["a", "s"],
                    "Tipo de estructura": ["simple"],
                    "Categoría gramatical": ["sustantivo"],
                    "V/I": ["Variable"]
                }
            }

            for mid, campos in q_morf.items():

                total_campos = len(campos)
                correctos = 0

                for campo, respuesta in campos.items():

                    if contiene_alguna(
                        respuesta,
                        respuestas_morf[mid].get(campo, [])
                    ):
                        correctos += 1

                morf += 0.50 * (
                    correctos / total_campos
                )

            # determinantes/pronombres

            for pregunta in EXAMEN["2ESO"]["determinantes_pronombres"]:

                if corregir_exacta(
                    q_det[pregunta["id"]],
                    pregunta["respuesta"]
                ):
                    morf += pregunta["puntos"]

            resultados["morfologia"] = min(2.5, morf)


            # -------------------------------------------------
            # SEMÁNTICA
            # -------------------------------------------------

            sem = 0

            for pregunta in EXAMEN["2ESO"]["semantica"]:

                if corregir_exacta(
                    q_sem[pregunta["id"]],
                    pregunta["respuesta"]
                ):
                    sem += pregunta["puntos"]

            # 3.2 queda fuera porque en la versión definitiva
            # del examen se eliminan las definiciones.

            resultados["semantica"] = min(1.5, sem)


            # -------------------------------------------------
            # TEXTOS
            # -------------------------------------------------

            textos_score = 0

            for pregunta in textos["preguntas"][:3]:

                if corregir_exacta(
                    q_textos[pregunta["id"]],
                    pregunta["respuesta"]
                ):
                    textos_score += pregunta["puntos"]

            textos_score += puntuar_texto_por_claves(
                q_textos["t4"],
                [
                    "informar",
                    "explicar",
                    "dar instrucciones",
                    "instruir",
                    "convencer",
                    "concienciar",
                    "informar sobre"
                ],
                0.25
            )

            resultados["textos"] = min(1.0, textos_score)


            # -------------------------------------------------
            # LITERATURA
            # -------------------------------------------------

            lit = 0

            if int(q_lit["l1"]) == 4:
                lit += 0.25

            if corregir_exacta(
                q_lit["l2"],
                "Arte menor"
            ):
                lit += 0.25

            if contiene_alguna(
                q_lit["l3"],
                ["8a 8b 8b 8a", "8a8b8b8a"]
            ):
                lit += 0.40

            if corregir_exacta(
                q_lit["l4"],
                "Consonante"
            ):
                lit += 0.30

            lit += puntuar_texto_por_claves(
                q_lit["l5"],
                [
                    "sinalefa",
                    "vocal",
                    "vocales",
                    "union",
                    "unión"
                ],
                0.40
            )

            lit += puntuar_texto_por_claves(
                q_lit["l6"],
                [
                    "viento juega",
                    "viento",
                    "juega",
                    "personificacion",
                    "personificación",
                    "atribuir",
                    "humano"
                ],
                0.40
            )

            resultados["literatura"] = min(2.0, lit)


            # -------------------------------------------------
            # SINTAXIS
            # -------------------------------------------------

            syn = 0

            for pregunta in EXAMEN["2ESO"]["sintaxis"]:

                if corregir_exacta(
                    q_syn[pregunta["id"]],
                    pregunta["respuesta"]
                ):

                    if pregunta["id"] in [
                        "x1",
                        "x2",
                        "x3",
                        "x4",
                        "x5"
                    ]:
                        syn += 0.10

                    else:
                        syn += 0.10

            resultados["sintaxis"] = min(1.0, syn)


            # -------------------------------------------------
            # DIÁLOGO
            # -------------------------------------------------

            dialogo_score = 0

            if contiene_alguna(
                q_dialogo["d1"],
                ["lucia y carlos", "lucía y carlos", "lucia", "carlos"]
            ):
                dialogo_score += 0.10

            if int(q_dialogo["d2"]) == 6:
                dialogo_score += 0.10

            dialogo_score += puntuar_texto_por_claves(
                q_dialogo["d3"],
                [
                    "dijo que",
                    "habia",
                    "había",
                    "hecho",
                    "dia anterior",
                    "día anterior"
                ],
                0.30
            )

            resultados["dialogo"] = min(0.50, dialogo_score)


            # =================================================
            # NOTA
            # =================================================

            nota_inicial = sum(resultados.values())

            # Ortografía
            penalizacion_ortografia = faltas_ortografia * 0.2
            penalizacion_tildes = faltas_tildes * 0.1

            if nee:
                penalizacion_ortografia *= 0.5
                penalizacion_tildes *= 0.5

            descuento_ortografia = min(
                2.0,
                penalizacion_ortografia + penalizacion_tildes
            )

            nota_final = max(
                0,
                nota_inicial
                - descuento_ortografia
                - float(presentacion)
            )

            # La prueba suma 10 puntos
            nota_final = min(10, nota_final)

            resultados["total"] = round(
                nota_final,
                2
            )


            # =================================================
            # GUARDAR
            # =================================================

            fila = {
                "name": nombre,
                "group": grupo,
                "date": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                ),
                "comprension": resultados["comprension"],
                "morfologia": resultados["morfologia"],
                "semantica": resultados["semantica"],
                "textos": resultados["textos"],
                "literatura": resultados["literatura"],
                "sintaxis": resultados["sintaxis"],
                "dialogo": resultados["dialogo"],
                "total": resultados["total"]
            }

            df = pd.concat(
                [
                    df,
                    pd.DataFrame([fila])
                ],
                ignore_index=True
            )

            df.to_csv(
                "results.csv",
                index=False
            )


            # =================================================
            # RESULTADOS
            # =================================================

            st.success(
                "Examen corregido y guardado correctamente."
            )

            st.metric(
                "NOTA FINAL",
                f"{nota_final:.2f} / 10"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.subheader("Resultados por apartado")

                st.dataframe(
                    pd.DataFrame({
                        "Apartado": [
                            "Comprensión",
                            "Morfología",
                            "Semántica",
                            "Textos",
                            "Literatura",
                            "Sintaxis",
                            "Diálogo"
                        ],
                        "Puntuación": [
                            resultados["comprension"],
                            resultados["morfologia"],
                            resultados["semantica"],
                            resultados["textos"],
                            resultados["literatura"],
                            resultados["sintaxis"],
                            resultados["dialogo"]
                        ]
                    }),
                    hide_index=True
                )

            with col2:

                st.subheader("Perfil competencial")

                competencias = {
                    "comprension": resultados["comprension"] / 2 * 10,
                    "morfologia": resultados["morfologia"] / 2.5 * 10,
                    "semantica": resultados["semantica"] / 1.5 * 10,
                    "literatura": resultados["literatura"] / 2 * 10,
                    "sintaxis": resultados["sintaxis"] / 1 * 10
                }

                st.plotly_chart(
                    radar_chart(
                        competencias,
                        nombre
                    ),
                    use_container_width=True
                )

            perfil = generar_perfil(
                competencias
            )

            st.subheader("🧠 Perfil diagnóstico")

            for item in perfil:
                st.write(item)


            # =================================================
            # PDF
            # =================================================

            pdf_file = generar_pdf(
                nombre,
                grupo,
                resultados,
                perfil,
                faltas_ortografia,
                faltas_tildes,
                presentacion,
                nota_inicial,
                nota_final
            )

            with open(pdf_file, "rb") as archivo:

                st.download_button(
                    "📄 Descargar informe completo en PDF",
                    archivo,
                    file_name=pdf_file,
                    mime="application/pdf"
                )


# ============================================================
# DASHBOARD
# ============================================================

with tab_dashboard:

    st.header("📊 Dashboard de clase")

    if df.empty:

        st.info(
            "Todavía no hay exámenes registrados."
        )

    else:

        competencias = [
            "comprension",
            "morfologia",
            "semantica",
            "literatura",
            "sintaxis"
        ]

        st.subheader("Media de la clase")

        medias = df[competencias].mean()

        st.bar_chart(
            medias
        )

        alumno_dashboard = st.selectbox(
            "Selecciona un alumno",
            df["name"].unique(),
            key="dashboard_alumno"
        )

        user = df[
            df["name"] == alumno_dashboard
        ].iloc[-1]

        st.subheader(
            f"Perfil de {alumno_dashboard}"
        )

        scores_user = {
            c: float(user[c])
            for c in competencias
        }

        st.plotly_chart(
            radar_chart(
                scores_user,
                alumno_dashboard
            ),
            use_container_width=True
        )

        st.subheader(
            "Alumno vs media de la clase"
        )

        st.plotly_chart(
            comparativa(
                user,
                df
            ),
            use_container_width=True
        )


# ============================================================
# ALUMNO
# ============================================================

with tab_alumno:

    st.header("👤 Seguimiento individual")

    if df.empty:

        st.info(
            "No hay alumnos registrados todavía."
        )

    else:

        alumno = st.selectbox(
            "Selecciona alumno",
            df["name"].unique(),
            key="historial_alumno"
        )

        historial = df[
            df["name"] == alumno
        ].copy()

        st.dataframe(
            historial,
            use_container_width=True
        )

        ultimo = historial.iloc[-1]

        st.metric(
            "Última nota",
            f"{float(ultimo['total']):.2f} / 10"
        )
