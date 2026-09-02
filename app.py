import streamlit as st
import pandas as pd
from datetime import datetime

from analytics import radar_chart, comparativa, generar_perfil
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

st.title("📘 Evaluación Inicial — Lengua Castellana y Literatura")
st.caption("2.º ESO")


# =========================================================
# CARGAR RESULTADOS
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
    "dialogo",
    "total"
]

try:
    df = pd.read_csv("results.csv")

    # Si el CSV antiguo no tiene alguna columna,
    # la añadimos automáticamente.
    for columna in COLUMNAS:
        if columna not in df.columns:
            df[columna] = 0

except Exception:
    df = pd.DataFrame(columns=COLUMNAS)


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
# VARIABLES
# =========================================================

respuestas = {}


# =========================================================
# EXAMEN
# =========================================================

with tab1:

    st.header("📝 Evaluación inicial")

    st.markdown("### Datos del alumno")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input(
            "Nombre y apellidos",
            key="nombre"
        )

    with col2:
        group = st.text_input(
            "Grupo",
            key="grupo"
        )

    st.divider()


    # =====================================================
    # 1. COMPRENSIÓN
    # =====================================================

    st.header("1. COMPRENSIÓN LECTORA — 2 puntos")

    st.markdown("### Lee el siguiente texto")

    st.info(
        EXAMEN["2ESO"]["comprension"]["texto"]
    )

    st.markdown("### 1.1. Lugar, personajes, tiempo y ambiente")

    for pregunta in EXAMEN["2ESO"]["comprension"]["preguntas"]:

        if pregunta["id"] == "c3_resumen":
            continue

        respuestas[pregunta["id"]] = st.text_input(
            pregunta["enunciado"],
            key=f"respuesta_{pregunta['id']}"
        )

    st.markdown("### 1.2. Acciones")

    st.caption(
        "Escribe cada acción en infinitivo."
    )

    for pregunta in EXAMEN["2ESO"]["comprension"]["preguntas"]:

        if pregunta["id"].startswith("c2_"):

            respuestas[pregunta["id"]] = st.text_input(
                pregunta["enunciado"],
                key=f"respuesta_{pregunta['id']}"
            )

    st.markdown("### 1.3. Resumen")

    respuestas["c3_resumen"] = st.text_area(
        "Resume el texto con tus palabras.",
        height=150,
        key="respuesta_c3_resumen"
    )


    # =====================================================
    # 2. MORFOLOGÍA
    # =====================================================

    st.divider()

    st.header("2. MORFOLOGÍA Y CATEGORÍAS GRAMATICALES — 2,5 puntos")

    st.markdown("### 2.1. Análisis morfológico")

    st.caption(
        "Completa cada apartado de cada palabra."
    )

    for pregunta in EXAMEN["2ESO"]["morfologia"]:

        st.markdown(
            f"#### Palabra: **{pregunta['palabra']}**"
        )

        respuestas[pregunta["id"]] = {}

        for campo in pregunta["campos"]:

            clave = f"{pregunta['id']}_{campo}"

            respuestas[pregunta["id"]][campo] = st.text_input(
                campo,
                key=clave
            )

        st.divider()


    # =====================================================
    # 2.2 DETERMINANTES Y PRONOMBRES
    # =====================================================

    st.markdown("### 2.2. Determinantes y pronombres — 0,5 puntos")

    st.write(
        "Indica si la palabra destacada es DETERMINANTE o PRONOMBRE."
    )

    for pregunta in EXAMEN["2ESO"]["determinantes_pronombres"]:

        st.markdown(
            f"**{pregunta['frase']}**"
        )

        respuestas[pregunta["id"]] = st.text_input(
            pregunta["enunciado"],
            key=f"respuesta_{pregunta['id']}"
        )


    # =====================================================
    # 3. SEMÁNTICA
    # =====================================================

    st.divider()

    st.header("3. SEMÁNTICA — 1,5 puntos")

    st.write(
        "Indica únicamente el nombre de la relación semántica."
    )

    for pregunta in EXAMEN["2ESO"]["semantica"]:

        st.markdown(
            f"**{pregunta['elemento']}**"
        )

        respuestas[pregunta["id"]] = st.text_input(
            pregunta["enunciado"],
            key=f"respuesta_{pregunta['id']}"
        )


    # =====================================================
    # 4. TEXTOS
    # =====================================================

    st.divider()

    st.header("4. TEXTOS — 1 punto")

    st.markdown("### Lee los textos")

    for texto in EXAMEN["2ESO"]["textos"]["fragmentos"]:

        st.markdown(
            f"**{texto['nombre']}**"
        )

        st.info(texto["texto"])

    st.markdown("### 4.1. Tipo de texto")

    for pregunta in EXAMEN["2ESO"]["textos"]["preguntas"]:

        if pregunta["id"] in ["t1", "t2", "t3"]:

            respuestas[pregunta["id"]] = st.text_input(
                pregunta["enunciado"],
                key=f"respuesta_{pregunta['id']}"
            )

    st.markdown("### 4.2. Finalidad")

    respuestas["t4"] = st.text_area(
        "Explica la finalidad de UNO de los textos (A, B o C).",
        height=100,
        key="respuesta_t4"
    )


    # =====================================================
    # 5. LITERATURA
    # =====================================================

    st.divider()

    st.header("5. LITERATURA — 2 puntos")

    st.markdown("### Lee el siguiente poema")

    # Cada verso aparece en una fila independiente.
    poema = EXAMEN["2ESO"]["literatura"]["poema"]

    poema_df = pd.DataFrame(
        {"Verso": poema}
    )

    st.table(poema_df)

    st.markdown("### Preguntas sobre el poema")

    for pregunta in EXAMEN["2ESO"]["literatura"]["preguntas"]:

        if pregunta["id"] == "l1":
            respuestas["l1"] = st.text_input(
                pregunta["enunciado"],
                key="respuesta_l1"
            )

        elif pregunta["id"] == "l2":
            respuestas["l2"] = st.text_input(
                pregunta["enunciado"],
                key="respuesta_l2"
            )

        elif pregunta["id"] == "l3":
            respuestas["l3"] = st.text_input(
                pregunta["enunciado"],
                key="respuesta_l3"
            )

        elif pregunta["id"] == "l4":
            respuestas["l4"] = st.text_input(
                pregunta["enunciado"],
                key="respuesta_l4"
            )

        elif pregunta["id"] == "l5":
            respuestas["l5"] = st.text_area(
                pregunta["enunciado"],
                height=100,
                key="respuesta_l5"
            )

        elif pregunta["id"] == "l6":
            respuestas["l6"] = st.text_area(
                pregunta["enunciado"],
                height=100,
                key="respuesta_l6"
            )


    # =====================================================
    # 6. SINTAXIS
    # =====================================================

    st.divider()

    st.header("6. SINTAXIS — 1 punto")

    st.markdown("### 6.1. Frase u oración")

    for pregunta in EXAMEN["2ESO"]["sintaxis"]:

        if pregunta["id"] in ["x1", "x2", "x3", "x4", "x5"]:

            st.markdown(
                f"**{pregunta['frase']}**"
            )

            respuestas[pregunta["id"]] = st.text_input(
                "FRASE u ORACIÓN:",
                key=f"respuesta_{pregunta['id']}"
            )

    st.markdown("### 6.2. Modalidad oracional")

    for pregunta in EXAMEN["2ESO"]["sintaxis"]:

        if pregunta["id"] in ["x6", "x7", "x8", "x9", "x10"]:

            st.markdown(
                f"**{pregunta['frase']}**"
            )

            respuestas[pregunta["id"]] = st.text_input(
                "MODALIDAD ORACIONAL:",
                key=f"respuesta_{pregunta['id']}"
            )


    # =====================================================
    # 7. DIÁLOGO
    # =====================================================

    st.divider()

    st.header("7. DIÁLOGO — 0,5 puntos")

    st.markdown("### Lee el diálogo")

    st.info(
        EXAMEN["2ESO"]["dialogo"]["texto"]
    )

    for pregunta in EXAMEN["2ESO"]["dialogo"]["preguntas"]:

        if pregunta["id"] == "d1":

            respuestas["d1"] = st.text_input(
                pregunta["enunciado"],
                key="respuesta_d1"
            )

        elif pregunta["id"] == "d2":

            respuestas["d2"] = st.text_input(
                pregunta["enunciado"],
                key="respuesta_d2"
            )

        elif pregunta["id"] == "d3":

            respuestas["d3"] = st.text_area(
                pregunta["enunciado"],
                height=120,
                key="respuesta_d3"
            )


    # =====================================================
    # ORTOGRAFÍA
    # =====================================================

    st.divider()

    st.header("✏️ Ortografía")

    st.info(
        "Las faltas de ortografía y de tilde serán detectadas "
        "automáticamente a partir de las respuestas del alumno. "
        "El alumno no puede modificar este resultado."
    )


    # =====================================================
    # CORRECCIÓN
    # =====================================================

    st.divider()

    if st.button(
        "📤 Entregar examen",
        type="primary",
        use_container_width=True
    ):

        if not name.strip():
            st.error("Introduce el nombre y apellidos.")

        elif not group.strip():
            st.error("Introduce el grupo.")

        else:

            # ---------------------------------------------
            # TODAS LAS RESPUESTAS DE TEXTO
            # ---------------------------------------------

            textos_respuestas = []

            def recoger_respuestas(obj):

                if isinstance(obj, dict):

                    for valor in obj.values():
                        recoger_respuestas(valor)

                elif isinstance(obj, str):

                    if obj.strip():
                        textos_respuestas.append(obj)

            recoger_respuestas(respuestas)

            # ---------------------------------------------
            # PUNTUACIÓN PROVISIONAL
            #
            # NO utilizamos número de palabras como nota.
            # Cada pregunta contestada suma proporcionalmente.
            # ---------------------------------------------

            def porcentaje_contestado(lista):

                if not lista:
                    return 0

                contestadas = sum(
                    1 for x in lista
                    if str(x).strip()
                )

                return contestadas / len(lista)

            # Comprensión
            comp_ids = [
                "c1_lugar",
                "c1_personajes",
                "c1_tiempo",
                "c1_ambiente",
                "c2_accion1",
                "c2_accion2",
                "c2_accion3",
                "c3_resumen"
            ]

            comp_respuestas = [
                respuestas.get(x, "")
                for x in comp_ids
            ]

            comprension = porcentaje_contestado(
                comp_respuestas
            ) * 10

            # Morfología
            morf_total = 0
            morf_contestadas = 0

            for palabra in EXAMEN["2ESO"]["morfologia"]:

                datos = respuestas.get(
                    palabra["id"],
                    {}
                )

                for campo in palabra["campos"]:

                    morf_total += 1

                    if str(
                        datos.get(campo, "")
                    ).strip():

                        morf_contestadas += 1

            if morf_total:
                morfologia = (
                    morf_contestadas / morf_total
                ) * 10
            else:
                morfologia = 0

            # Semántica
            sem_ids = [
                "s1",
                "s2",
                "s3",
                "s4",
                "s5"
            ]

            sem_respuestas = [
                respuestas.get(x, "")
                for x in sem_ids
            ]

            semantica = porcentaje_contestado(
                sem_respuestas
            ) * 10

            # Literatura
            lit_ids = [
                "l1",
                "l2",
                "l3",
                "l4",
                "l5",
                "l6"
            ]

            lit_respuestas = [
                respuestas.get(x, "")
                for x in lit_ids
            ]

            literatura = porcentaje_contestado(
                lit_respuestas
            ) * 10

            # Sintaxis
            syn_ids = [
                "x1",
                "x2",
                "x3",
                "x4",
                "x5",
                "x6",
                "x7",
                "x8",
                "x9",
                "x10"
            ]

            syn_respuestas = [
                respuestas.get(x, "")
                for x in syn_ids
            ]

            sintaxis = porcentaje_contestado(
                syn_respuestas
            ) * 10

            # Diálogo
            dialogo_ids = [
                "d1",
                "d2",
                "d3"
            ]

            dialogo_respuestas = [
                respuestas.get(x, "")
                for x in dialogo_ids
            ]

            dialogo = porcentaje_contestado(
                dialogo_respuestas
            ) * 10

            # ---------------------------------------------
            # NOTA GLOBAL
            # ---------------------------------------------

            scores = {
                "comprension": round(comprension, 2),
                "morfologia": round(morfologia, 2),
                "semantica": round(semantica, 2),
                "literatura": round(literatura, 2),
                "sintaxis": round(sintaxis, 2)
            }

            total = round(
                sum(scores.values()) / len(scores),
                2
            )

            # ---------------------------------------------
            # ORTOGRAFÍA
            # ---------------------------------------------

            # De momento dejamos el cálculo preparado.
            # NO se permite que el alumno lo modifique.
            faltas_ortografia = 0
            faltas_tilde = 0

            descuento_ortografia = min(
                2,
                faltas_ortografia * 0.2
                + faltas_tilde * 0.1
            )

            nota_final = max(
                0,
                round(
                    total - descuento_ortografia,
                    2
                )
            )

            # ---------------------------------------------
            # GUARDAR
            # ---------------------------------------------

            fila = {
                "name": name,
                "group": group,
                "date": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                ),
                **scores,
                "dialogo": round(dialogo, 2),
                "total": nota_final
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

            # ---------------------------------------------
            # RESULTADOS
            # ---------------------------------------------

            st.success(
                "✅ Examen guardado correctamente."
            )

            st.metric(
                "Nota final",
                f"{nota_final}/10"
            )

            st.write(
                "### 📊 Resultados por competencia"
            )

            st.dataframe(
                pd.DataFrame(
                    {
                        "Competencia": [
                            "Comprensión",
                            "Morfología",
                            "Semántica",
                            "Literatura",
                            "Sintaxis"
                        ],
                        "Nota": [
                            scores["comprension"],
                            scores["morfologia"],
                            scores["semantica"],
                            scores["literatura"],
                            scores["sintaxis"]
                        ]
                    }
                ),
                use_container_width=True,
                hide_index=True
            )

            # ---------------------------------------------
            # RADAR
            # ---------------------------------------------

            st.plotly_chart(
                radar_chart(
                    scores,
                    name
                ),
                use_container_width=True
            )

            # ---------------------------------------------
            # PERFIL
            # ---------------------------------------------

            perfil = generar_perfil(
                scores
            )

            st.write(
                "### 🧠 Perfil del alumno"
            )

            for item in perfil:
                st.write(
                    f"• {item}"
                )

            # ---------------------------------------------
            # PDF
            # ---------------------------------------------

            try:

                pdf_file = generar_pdf(
                    name,
                    group,
                    scores,
                    perfil
                )

                with open(
                    pdf_file,
                    "rb"
                ) as archivo:

                    st.download_button(
                        "📄 Descargar informe PDF",
                        archivo,
                        file_name=pdf_file,
                        mime="application/pdf"
                    )

            except Exception as e:

                st.warning(
                    f"No se pudo generar el PDF: {e}"
                )


# =========================================================
# DASHBOARD
# =========================================================

with tab2:

    st.header("📊 Dashboard de la clase")

    if df.empty:

        st.info(
            "Todavía no hay resultados registrados."
        )

    else:

        competencias = [
            "comprension",
            "morfologia",
            "semantica",
            "literatura",
            "sintaxis"
        ]

        st.subheader(
            "Media de la clase"
        )

        st.bar_chart(
            df[competencias].mean()
        )

        st.subheader(
            "Resultados de alumnos"
        )

        st.dataframe(
            df,
            use_container_width=True
        )

        alumno = st.selectbox(
            "Selecciona un alumno",
            sorted(
                df["name"]
                .dropna()
                .unique()
            )
        )

        user = (
            df[
                df["name"] == alumno
            ]
            .iloc[-1]
        )

        st.subheader(
            "👤 Resultado individual"
        )

        st.write(
            user
        )

        st.subheader(
            "📊 Alumno frente a la clase"
        )

        st.plotly_chart(
            comparativa(
                user,
                df
            ),
            use_container_width=True
        )


# =========================================================
# ALUMNO
# =========================================================

with tab3:

    st.header("👤 Historial del alumno")

    if df.empty:

        st.info(
            "Todavía no hay alumnos registrados."
        )

    else:

        alumno = st.selectbox(
            "Selecciona un alumno",
            sorted(
                df["name"]
                .dropna()
                .unique()
            ),
            key="historial_alumno"
        )

        historial = df[
            df["name"] == alumno
        ]

        st.dataframe(
            historial,
            use_container_width=True,
            hide_index=True
        )
