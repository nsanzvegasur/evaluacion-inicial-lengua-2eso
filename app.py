import streamlit as st
import pandas as pd
from datetime import datetime

from analytics import radar_chart
from pdf_report import generate_pdf
from ai_correction import ai_score

st.set_page_config(layout="wide")

st.title("📘 Evaluación Inicial Lengua ESO (PRO IA)")

# ======================
# CARGA DATOS
# ======================
try:
    df = pd.read_csv("results.csv")
except:
    df = pd.DataFrame()

tab1, tab2, tab3 = st.tabs(["🧑‍🎓 Examen", "📊 Dashboard", "👤 Alumno"])

# ======================
# EXAMEN
# ======================
with tab1:

    name = st.text_input("Nombre")
    group = st.text_input("Grupo")

    q1 = st.text_area("Define sustantivo")
    q2 = st.text_area("Resumen del texto")
    q3 = st.text_area("Tipo de texto")
    q4 = st.text_area("Análisis del poema")

    if st.button("Enviar"):

        scores = {
            "morfologia": len(q1.split())/2,
            "comprension": len(q2.split())/2,
            "textos": len(q3.split())/2,
            "literatura": len(q4.split())/2
        }

        # LIMITAMOS A 10
        scores = {k: min(10, v) for k, v in scores.items()}

        total = sum(scores.values())

        row = {
            "name": name,
            "group": group,
            "date": datetime.now(),
            **scores,
            "total": total
        }

        df = pd.concat([df, pd.DataFrame([row])])
        df.to_csv("results.csv", index=False)

        st.success("Guardado")

        # RADAR
        st.plotly_chart(radar_chart(scores))

        # PDF
        pdf_file = generate_pdf(name, scores, "Diagnóstico automático")
        st.download_button("Descargar informe PDF", open(pdf_file, "rb"), file_name=pdf_file)

# ======================
# DASHBOARD CLASE
# ======================
with tab2:

    st.subheader("📊 Comparativa clase vs alumno")

    if not df.empty:

        st.bar_chart(df[["morfologia","comprension","textos","literatura"]].mean())

        alumno = st.selectbox("Alumno", df["name"].unique())

        user = df[df["name"] == alumno].iloc[-1]

        st.write("Perfil alumno vs clase")

        st.write(user)

# ======================
# ALUMNO
# ======================
with tab3:

    st.subheader("Detalle alumno")

    if not df.empty:
        alumno = st.selectbox("Selecciona alumno", df["name"].unique())

        st.dataframe(df[df["name"] == alumno])
