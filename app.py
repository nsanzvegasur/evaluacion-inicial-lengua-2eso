import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

from analytics import radar_chart, comparativa, generar_perfil
from pdf_report import generar_pdf
from examen2ESO import EXAMEN

st.set_page_config(layout="wide")

st.title("📘 Evaluación Inicial Lengua ESO")

# ======================
# CARGA DATOS
# ======================
try:
    df = pd.read_csv("results.csv")
except:
    df = pd.DataFrame(columns=[
        "name", "group", "date",
        "comprension", "morfologia",
        "semantica", "literatura", "sintaxis",
        "total"
    ])

tab1, tab2, tab3 = st.tabs(["🧑‍🎓 Examen", "📊 Dashboard", "👤 Alumno"])

# ======================
# VARIABLES RESPUESTAS
# ======================
q_comp = {}
q_morf = {}
q_sem = {}
q_lit = {}
q_syn = {}

# ======================
# EXAMEN
# ======================
with tab1:

    st.subheader("📘 Evaluación inicial Lengua Castellana")

    name = st.text_input("Nombre y apellidos")
    group = st.text_input("Grupo")

    # =====================================================
    # 1. COMPRENSIÓN
    # =====================================================
    st.write("## 1. Comprensión lectora")

    st.write(EXAMEN["2ESO"]["comprension"]["texto"])

    for p in EXAMEN["2ESO"]["comprension"]["preguntas"]:
        q_comp[p["id"]] = st.text_area(p["enunciado"], key=f"comp_{p['id']}")

    # =====================================================
    # 2. MORFOLOGÍA
    # =====================================================
    st.write("## 2. Morfología")

    for p in EXAMEN["2ESO"]["morfologia"]:

        st.write(f"📌 Palabra: **{p['palabra']}**")

        respuestas = {}

        for campo in p["campos"]:
            respuestas[campo] = st.text_area(
                f"{p['palabra']} → {campo}",
                key=f"morf_{p['id']}_{campo}"
            )

        q_morf[p["id"]] = respuestas

    # =====================================================
    # 3. SEMÁNTICA
    # =====================================================
    st.write("## 3. Semántica")

    for p in EXAMEN["2ESO"]["semantica"]:
        q_sem[p["id"]] = st.text_area(p["enunciado"], key=f"sem_{p['id']}")

    # =====================================================
    # 4. LITERATURA
    # =====================================================
    st.write("## 4. Literatura")

    for p in EXAMEN["2ESO"]["literatura"]:

        if "texto" in p:
            st.info(p["texto"])

        q_lit[p["id"]] = st.text_area(p["enunciado"], key=f"lit_{p['id']}")

    # =====================================================
    # 5. SINTAXIS
    # =====================================================
    st.write("## 5. Sintaxis")

    for p in EXAMEN["2ESO"]["sintaxis"]:
        label = p.get("frase", p["enunciado"])
        q_syn[p["id"]] = st.text_area(
            f"{label} → {p['enunciado']}",
            key=f"syn_{p['id']}"
        )

    # =====================================================
    # ENVIAR EXAMEN
    # =====================================================
    if st.button("📤 Enviar examen"):

        if not name or not group:
            st.error("Introduce nombre y grupo")
        else:

            # ======================
            # SCORING SEGURO
            # ======================

            def safe_score_dict(d):
                return sum(len(str(v).split()) for v in d.values())

            def safe_score_morf(d):
                total = 0
                count = 0
                for v in d.values():
                    for x in v.values():
                        if str(x).strip():
                            total += 1
                        count += 1
                return (total / count) * 10 if count else 0

            scores = {
                "comprension": min(10, safe_score_dict(q_comp) / 8),
                "morfologia": min(10, safe_score_morf(q_morf)),
                "semantica": min(10, safe_score_dict(q_sem) / 6),
                "literatura": min(10, safe_score_dict(q_lit) / 6),
                "sintaxis": min(10, safe_score_dict(q_syn) / 6),
            }

            total = sum(scores.values())

            row = {
                "name": name,
                "group": group,
                "date": datetime.now(),
                **scores,
                "total": total
            }

            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            df.to_csv("results.csv", index=False)

            st.success("Examen guardado correctamente")

            # ======================
            # RADAR
            # ======================
            st.plotly_chart(radar_chart(scores, name))

            # ======================
            # PERFIL
            # ======================
            perfil = generar_perfil(scores)

            st.write("### 🧠 Perfil del alumno")
            for p in perfil:
                st.write("•", p)

            # ======================
            # PDF
            # ======================
            pdf_file = generar_pdf(name, group, scores, perfil)

            with open(pdf_file, "rb") as f:
                st.download_button(
                    "📄 Descargar informe PDF",
                    f,
                    file_name=pdf_file
                )

# ======================
# DASHBOARD
# ======================
with tab2:

    st.subheader("📊 Comparativa clase")

    if not df.empty:

        competencias = ["comprension", "morfologia", "semantica", "literatura", "sintaxis"]

        st.bar_chart(df[competencias].mean())

        alumno = st.selectbox("Selecciona alumno", df["name"].unique())

        user = df[df["name"] == alumno].iloc[-1]

        st.write("### 👤 Perfil individual")
        st.dataframe(user)

        st.write("### 📊 Comparativa alumno vs clase")
        st.plotly_chart(comparativa(user, df))

# ======================
# ALUMNO
# ======================
with tab3:

    st.subheader("📋 Historial alumno")

    if not df.empty:

        alumno = st.selectbox("Selecciona alumno", df["name"].unique(), key="alumno_tab3")

        st.dataframe(df[df["name"] == alumno])
