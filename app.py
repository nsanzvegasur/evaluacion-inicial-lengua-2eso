import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

from analytics import radar_chart, comparativa, generar_perfil
from pdf_report import generar_pdf
from examen2ESO import EXAMEN   # ✔ tu archivo real

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
# EXAMEN
# ======================
with tab1:

    st.subheader("📘 Evaluación inicial Lengua Castellana")

    name = st.text_input("Nombre y apellidos")
    group = st.text_input("Grupo")

    if "EXAMEN" in globals():

        # ======================
        # COMPRENSIÓN
        # ======================
        st.write("## 1. Comprensión lectora")
        st.write(EXAMEN["2ESO"]["comprension"]["texto"])

        q_comp = {}
        for p in EXAMEN["2ESO"]["comprension"]["preguntas"]:
            q_comp[p["id"]] = st.text_area(p["enunciado"])

        # ======================
        # MORFOLOGÍA
        # ======================
        st.write("## 2. Morfología")

        q_morf = {}
        for p in EXAMEN["2ESO"]["morfologia"]:
            q_morf[p["id"]] = st.text_area(p["enunciado"])

        # ======================
        # SEMÁNTICA
        # ======================
        st.write("## 3. Semántica")

        q_sem = {}
        for p in EXAMEN["2ESO"]["semantica"]:
            q_sem[p["id"]] = st.text_area(p["enunciado"])

        # ======================
        # LITERATURA
        # ======================
        st.write("## 4. Literatura")

        q_lit = {}
        for p in EXAMEN["2ESO"]["literatura"]:
            q_lit[p["id"]] = st.text_area(p["enunciado"])

        # ======================
        # SINTAXIS
        # ======================
        st.write("## 5. Sintaxis")

        q_syn = {}
        for p in EXAMEN["2ESO"]["sintaxis"]:
            q_syn[p["id"]] = st.text_area(p["enunciado"])

    # ======================
    # ENVIAR EXAMEN
    # ======================
    if st.button("📤 Enviar examen"):

        if not name or not group:
            st.error("Introduce nombre y grupo")
        else:

            # ======================
            # SCORING (BÁSICO SIN IA)
            # ======================
            scores = {
                "comprension": min(10, sum(len(v.split()) for v in q_comp.values()) / 8),
                "morfologia": min(10, sum(len(v.split()) for v in q_morf.values()) / 6),
                "semantica": min(10, sum(len(v.split()) for v in q_sem.values()) / 6),
                "literatura": min(10, sum(len(v.split()) for v in q_lit.values()) / 6),
                "sintaxis": min(10, sum(len(v.split()) for v in q_syn.values()) / 6),
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
