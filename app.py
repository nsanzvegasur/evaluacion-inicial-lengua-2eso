import streamlit as st
import pandas as pd
from datetime import datetime

from analytics import radar_chart, comparativa, generar_perfil
from pdf_report import generar_pdf

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
        "textos", "literatura", "sintaxis",
        "total"
    ])

tab1, tab2, tab3 = st.tabs(["🧑‍🎓 Examen", "📊 Dashboard", "👤 Alumno"])

# ======================
# EXAMEN
# ======================
with tab1:

    st.subheader("Evaluación inicial")

    name = st.text_input("Nombre")
    group = st.text_input("Grupo")

    q1 = st.text_area("Define sustantivo")
    q2 = st.text_area("Resumen del texto")
    q3 = st.text_area("Tipo de texto")
    q4 = st.text_area("Análisis del poema")
    q5 = st.text_area("Sintaxis (frase u oración)")

    if st.button("Enviar examen"):

        if not name or not group:
            st.error("Introduce nombre y grupo")
        else:

            scores = {
                "comprension": min(10, len(q2.split()) / 3),
                "morfologia": min(10, len(q1.split()) / 2),
                "textos": min(10, len(q3.split()) / 2),
                "literatura": min(10, len(q4.split()) / 2),
                "sintaxis": min(10, len(q5.split()) / 2),
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
            # RADAR CHART
            # ======================
            st.plotly_chart(radar_chart(scores, name))

            # ======================
            # PERFIL
            # ======================
            perfil = generar_perfil(scores)
            st.write("### 🧠 Perfil del alumno")
            for p in perfil:
                st.write(p)

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
# DASHBOARD CLASE
# ======================
with tab2:

    st.subheader("📊 Comparativa clase")

    if not df.empty:

        competencias = ["comprension", "morfologia", "textos", "literatura", "sintaxis"]

        st.bar_chart(df[competencias].mean())

        alumno = st.selectbox("Selecciona alumno", df["name"].unique())

        user = df[df["name"] == alumno].iloc[-1]

        st.write("### 👤 Perfil individual")
        st.write(user)

        st.write("### 📊 Comparativa alumno vs clase")
        st.plotly_chart(comparativa(user, df))

# ======================
# ALUMNO
# ======================
with tab3:

    st.subheader("📋 Historial alumno")

    if not df.empty:

        alumno = st.selectbox("Selecciona alumno", df["name"].unique())

        st.dataframe(df[df["name"] == alumno])
