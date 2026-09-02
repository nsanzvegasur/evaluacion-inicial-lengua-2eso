import streamlit as st
import pandas as pd
from datetime import datetime

from analytics import radar_chart, comparativa, generar_perfil
from pdf_report import generar_pdf
from examen2ESO import EXAMEN

# ============================================================

# CONFIGURACIÓN

# ============================================================

st.set_page_config(
page_title="Evaluación Inicial Lengua 2º ESO",
page_icon="📘",
layout="wide"
)

st.title("📘 Evaluación Inicial – Lengua Castellana y Literatura")
st.caption("2.º ESO")

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
"literatura",
"sintaxis",
"dialogo",
"total"
]

try:
df = pd.read_csv("results.csv")
except Exception:
df = pd.DataFrame(columns=COLUMNAS)

# ============================================================

# TABS

# ============================================================

tab1, tab2, tab3 = st.tabs(
["🧑‍🎓 Examen", "📊 Dashboard", "👤 Alumno"]
)

# ============================================================

# VARIABLES

# ============================================================

q_comp = {}
q_morf = {}
q_dp = {}
q_sem = {}
q_textos = {}
q_lit = {}
q_syn = {}
q_dialogo = {}

# ============================================================

# EXAMEN

# ============================================================

with tab1:

```
st.header("EVALUACIÓN INICIAL")
st.subheader("2.º ESO – Lengua Castellana y Literatura")

# --------------------------------------------------------
# DATOS DEL ALUMNO
# --------------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    name = st.text_input(
        "NOMBRE Y APELLIDOS",
        key="nombre"
    )

with col2:
    group = st.text_input(
        "GRUPO",
        key="grupo"
    )

st.divider()

# ========================================================
# 1. COMPRENSIÓN LECTORA
# ========================================================

st.header("1. COMPRENSIÓN LECTORA")

st.markdown("### Lee el siguiente texto:")

st.info(EXAMEN["2ESO"]["comprension"]["texto"])

st.markdown("### 1.1. Lugar, personajes, tiempo y ambiente")

for p in EXAMEN["2ESO"]["comprension"]["preguntas"]:

    if p["id"].startswith("c1_"):

        q_comp[p["id"]] = st.text_input(
            p["enunciado"],
            key=f"comp_{p['id']}"
        )

st.markdown("### 1.2. Tres acciones")

for p in EXAMEN["2ESO"]["comprension"]["preguntas"]:

    if p["id"].startswith("c2_"):

        q_comp[p["id"]] = st.text_input(
            p["enunciado"],
            key=f"comp_{p['id']}"
        )

st.markdown("### 1.3. Resumen")

q_comp["c3_resumen"] = st.text_area(
    "Resume el texto con tus palabras.",
    height=150,
    key="comp_c3_resumen"
)


# ========================================================
# 2. MORFOLOGÍA
# ========================================================

st.header("2. MORFOLOGÍA Y CATEGORÍAS GRAMATICALES")

st.markdown(
    "### 2.1. Análisis morfológico"
)

st.write(
    "Completa cada apartado para las siguientes palabras."
)

for p in EXAMEN["2ESO"]["morfologia"]:

    st.markdown(f"#### {p['palabra']}")

    cols = st.columns(5)

    respuestas = {}

    for i, campo in enumerate(p["campos"]):

        with cols[i]:

            respuestas[campo] = st.text_input(
                campo,
                key=f"morf_{p['id']}_{i}"
            )

    q_morf[p["id"]] = respuestas

# --------------------------------------------------------
# 2.2 DETERMINANTES Y PRONOMBRES
# --------------------------------------------------------

st.markdown("### 2.2. Determinantes y pronombres")

st.write(
    "Indica si la palabra destacada es determinante o pronombre."
)

for p in EXAMEN["2ESO"]["determinantes_pronombres"]:

    st.markdown(f"**{p['frase']}**")

    q_dp[p["id"]] = st.radio(
        f"¿Qué es «{p['palabra']}»?",
        ["Determinante", "Pronombre"],
        key=f"dp_{p['id']}",
        horizontal=True
    )


# ========================================================
# 3. SEMÁNTICA
# ========================================================

st.header("3. SEMÁNTICA")

st.write(
    "Indica el nombre de la relación semántica que corresponde."
)

for p in EXAMEN["2ESO"]["semantica"]:

    st.markdown(
        f"**{p['elemento']}**"
    )

    q_sem[p["id"]] = st.text_input(
        "Relación semántica:",
        key=f"sem_{p['id']}"
    )


# ========================================================
# 4. TEXTOS
# ========================================================

st.header("4. TEXTOS")

for p in EXAMEN["2ESO"]["textos"]:

    if "texto" in p:

        st.markdown(
            f"**{p['texto']}**"
        )

        q_textos[p["id"]] = st.text_input(
            p["texto"].split(":")[0] + " → Tipo de texto",
            key=f"texto_{p['id']}"
        )

    else:

        q_textos[p["id"]] = st.text_area(
            p["enunciado"],
            key=f"texto_{p['id']}",
            height=100
        )


# ========================================================
# 5. LITERATURA
# ========================================================

st.header("5. LITERATURA")

st.markdown("### Lee el siguiente poema:")

# POEMA EN TABLA, UN VERSO POR FILA
poema_df = pd.DataFrame(
    {
        "Verso": EXAMEN["2ESO"]["literatura"]["poema"]
    }
)

st.table(poema_df)

st.markdown("### Responde:")

for p in EXAMEN["2ESO"]["literatura"]["preguntas"]:

    q_lit[p["id"]] = st.text_input(
        p["enunciado"],
        key=f"lit_{p['id']}"
    )


# ========================================================
# 6. SINTAXIS
# ========================================================

st.header("6. SINTAXIS")

st.markdown("### 6.1. Frase u oración")

for p in EXAMEN["2ESO"]["sintaxis"]:

    if p["id"] in ["x1", "x2", "x3", "x4", "x5"]:

        st.markdown(
            f"**{p['frase']}**"
        )

        q_syn[p["id"]] = st.radio(
            p["enunciado"],
            ["Frase", "Oración"],
            key=f"syn_{p['id']}",
            horizontal=True
        )

st.markdown("### 6.2. Modalidad oracional")

for p in EXAMEN["2ESO"]["sintaxis"]:

    if p["id"] in ["x6", "x7", "x8", "x9", "x10"]:

        st.markdown(
            f"**{p['frase']}**"
        )

        q_syn[p["id"]] = st.selectbox(
            p["enunciado"],
            [
                "Enunciativa",
                "Interrogativa",
                "Exclamativa",
                "Exhortativa / imperativa",
                "Desiderativa",
                "Dubitativa"
            ],
            key=f"syn_{p['id']}"
        )


# ========================================================
# 7. DIÁLOGO
# ========================================================

st.header("7. DIÁLOGO")

st.info(
    EXAMEN["2ESO"]["dialogo"]["texto"]
)

for p in EXAMEN["2ESO"]["dialogo"]["preguntas"]:

    if p["id"] == "d2":

        q_dialogo[p["id"]] = st.number_input(
            p["enunciado"],
            min_value=0,
            max_value=20,
            step=1,
            key="dialogo_d2"
        )

    else:

        q_dialogo[p["id"]] = st.text_area(
            p["enunciado"],
            key=f"dialogo_{p['id']}",
            height=100
        )


# ========================================================
# ENVÍO
# ========================================================

st.divider()

if st.button(
    "📤 ENTREGAR EXAMEN",
    type="primary",
    use_container_width=True
):

    if not name.strip() or not group.strip():

        st.error(
            "Debes introducir el nombre y los apellidos y el grupo."
        )

    else:

        # ------------------------------------------------
        # CORRECCIÓN DE RESPUESTAS CERRADAS
        # ------------------------------------------------

        def normalizar(texto):

            return (
                str(texto)
                .strip()
                .lower()
                .replace("á", "a")
                .replace("é", "e")
                .replace("í", "i")
                .replace("ó", "o")
                .replace("ú", "u")
            )


        # =================================================
        # COMPRENSIÓN
        # =================================================

        # Se reserva la puntuación del apartado para
        # corrección posterior de respuestas abiertas.
        comprension = 0


        # =================================================
        # MORFOLOGÍA
        # =================================================

        morfologia = 0


        # =================================================
        # DETERMINANTES / PRONOMBRES
        # =================================================

        dp_correctas = 0

        for p in EXAMEN["2ESO"]["determinantes_pronombres"]:

            respuesta_usuario = normalizar(
                q_dp.get(p["id"], "")
            )

            respuesta_correcta = normalizar(
                p["respuesta"]
            )

            if respuesta_usuario == respuesta_correcta:
                dp_correctas += 1

        # 0,5 puntos
        nota_dp = (dp_correctas / 3) * 0.5


        # =================================================
        # SEMÁNTICA
        # =================================================

        sem_correctas = 0

        for p in EXAMEN["2ESO"]["semantica"]:

            respuesta_usuario = normalizar(
                q_sem.get(p["id"], "")
            )

            respuesta_correcta = normalizar(
                p["respuesta"]
            )

            if (
                respuesta_usuario == respuesta_correcta
                or respuesta_correcta in respuesta_usuario
            ):
                sem_correctas += 1

        # 1,5 puntos
        nota_semantica = (sem_correctas / 5) * 1.5


        # =================================================
        # TEXTOS
        # =================================================

        textos_correctos = 0

        for p in EXAMEN["2ESO"]["textos"]:

            if "respuesta" not in p:
                continue

            respuesta_usuario = normalizar(
                q_textos.get(p["id"], "")
            )

            respuesta_correcta = normalizar(
                p["respuesta"]
            )

            if (
                respuesta_usuario == respuesta_correcta
                or respuesta_correcta in respuesta_usuario
            ):
                textos_correctos += 1

        # 0,75 puntos para clasificación
        nota_textos = (textos_correctos / 3) * 0.75


        # =================================================
        # LITERATURA
        # =================================================

        literatura = 0


        # =================================================
        # SINTAXIS
        # =================================================

        respuestas_sintaxis = {
            "x1": "frase",
            "x2": "oracion",
            "x3": "frase",
            "x4": "oracion",
            "x5": "oracion",

            "x6": "interrogativa",
            "x7": "desiderativa",
            "x8": "exclamativa",
            "x9": "enunciativa",
            "x10": "exhortativa / imperativa"
        }

        syn_correctas = 0

        for identificador, correcta in respuestas_sintaxis.items():

            usuario = normalizar(
                q_syn.get(identificador, "")
            )

            correcta = normalizar(correcta)

            if usuario == correcta:
                syn_correctas += 1

        nota_sintaxis = (syn_correctas / 10) * 1


        # =================================================
        # DIÁLOGO
        # =================================================

        dialogo = 0

        if str(q_dialogo.get("d2", "")) == "6":
            dialogo += 0.1


        # =================================================
        # NOTAS SOBRE 10
        # =================================================

        scores = {

            "comprension": round(
                comprension / 2 * 10,
                2
            ),

            "morfologia": round(
                morfologia / 2.5 * 10,
                2
            ),

            "semantica": round(
                nota_semantica / 1.5 * 10,
                2
            ),

            "literatura": round(
                literatura / 2 * 10,
                2
            ),

            "sintaxis": round(
                nota_sintaxis / 1 * 10,
                2
            )
        }

        total = round(
            sum(scores.values()) / len(scores),
            2
        )


        # =================================================
        # GUARDAR RESULTADO
        # =================================================

        row = {
            "name": name,
            "group": group,
            "date": datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            ),
            **scores,
            "dialogo": round(dialogo, 2),
            "total": total
        }

        df = pd.concat(
            [
                df,
                pd.DataFrame([row])
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
            "✅ Examen guardado correctamente."
        )

        st.metric(
            "Nota global",
            f"{total}/10"
        )

        st.subheader(
            "📊 Perfil competencial"
        )

        st.plotly_chart(
            radar_chart(scores, name),
            use_container_width=True
        )


        # =================================================
        # PERFIL
        # =================================================

        perfil = generar_perfil(scores)

        st.subheader(
            "🧠 Perfil del alumno"
        )

        for item in perfil:
            st.write(item)


        # =================================================
        # PDF
        # =================================================

        try:

            pdf_file = generar_pdf(
                name,
                group,
                scores,
                perfil
            )

            with open(pdf_file, "rb") as f:

                st.download_button(
                    "📄 Descargar informe PDF",
                    data=f,
                    file_name=pdf_file,
                    mime="application/pdf"
                )

        except Exception as e:

            st.warning(
                f"No se pudo generar el PDF: {e}"
            )
```

# ============================================================

# DASHBOARD

# ============================================================

with tab2:

```
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

    st.bar_chart(
        df[competencias].mean()
    )

    st.subheader("Alumnos")

    alumno = st.selectbox(
        "Selecciona alumno",
        df["name"].dropna().unique(),
        key="dashboard_alumno"
    )

    user = df[
        df["name"] == alumno
    ].iloc[-1]

    st.dataframe(
        user.to_frame("Resultado")
    )

    st.subheader(
        "📊 Alumno frente a la clase"
    )

    st.plotly_chart(
        comparativa(user, df),
        use_container_width=True
    )
```

# ============================================================

# ALUMNO

# ============================================================

with tab3:

```
st.header("📋 Historial del alumno")

if df.empty:

    st.info(
        "Todavía no hay resultados."
    )

else:

    alumno = st.selectbox(
        "Selecciona alumno",
        df["name"].dropna().unique(),
        key="historial_alumno"
    )

    historial = df[
        df["name"] == alumno
    ]

    st.dataframe(
        historial,
        use_container_width=True
    )
```
