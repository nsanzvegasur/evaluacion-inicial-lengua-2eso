import pandas as pd
import plotly.graph_objects as go


# ============================================================
# COMPETENCIAS
# ============================================================

COMPETENCIAS = [
    "comprension",
    "morfologia",
    "semantica",
    "textos",
    "literatura",
    "sintaxis",
]


NOMBRES = {
    "comprension": "Comprensión",
    "morfologia": "Morfología",
    "semantica": "Semántica",
    "textos": "Textos",
    "literatura": "Literatura",
    "sintaxis": "Sintaxis",
}


# ============================================================
# GRÁFICO RADAR
# ============================================================

def radar_chart(datos, titulo="Perfil competencial"):

    valores = [
        float(datos.get(c, 0) or 0)
        for c in COMPETENCIAS
    ]

    etiquetas = [
        NOMBRES[c]
        for c in COMPETENCIAS
    ]

    valores.append(valores[0])
    etiquetas.append(etiquetas[0])

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=valores,
            theta=etiquetas,
            fill="toself",
            name="Alumno"
        )
    )

    fig.update_layout(
        title=titulo,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=False,
        margin=dict(
            l=40,
            r=40,
            t=60,
            b=40
        ),
    )

    return fig


# ============================================================
# COMPARATIVA DEL GRUPO
# ============================================================

def comparativa(df):

    if df is None or df.empty:
        return None

    if "Nota" not in df.columns:
        return None

    valores = pd.to_numeric(
        df["Nota"],
        errors="coerce"
    ).dropna()

    if valores.empty:
        return None

    alumnos = [
        f"Alumno {i + 1}"
        for i in range(len(valores))
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=alumnos,
            y=valores,
            name="Nota"
        )
    )

    fig.update_layout(
        title="Resultados del grupo",
        xaxis=dict(
            title="Alumnos"
        ),
        yaxis=dict(
            title="Nota sobre 10",
            range=[0, 10]
        ),
        showlegend=False,
        margin=dict(
            l=40,
            r=40,
            t=60,
            b=80
        ),
    )

    return fig


# ============================================================
# PERFIL COMPETENCIAL
# ============================================================

def generar_perfil(datos):

    resultado = []

    for c in COMPETENCIAS:

        nota = round(
            float(
                datos.get(c, 0) or 0
            ),
            2
        )

        if nota < 5:

            nivel = "Necesita refuerzo"

            texto = (
                f"{NOMBRES[c]}: necesita refuerzo."
            )

        elif nota < 8:

            nivel = "Nivel adecuado"

            texto = (
                f"{NOMBRES[c]}: nivel adecuado."
            )

        else:

            nivel = "Fortaleza"

            texto = (
                f"{NOMBRES[c]}: fortaleza."
            )

        resultado.append(
            {
                "competencia": c,
                "nombre": NOMBRES[c],
                "nota": nota,
                "nivel": nivel,
                "texto": texto,
            }
        )

    return resultado
