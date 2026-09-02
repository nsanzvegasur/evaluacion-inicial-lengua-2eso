import plotly.graph_objects as go
import pandas as pd


# ============================================================
# NOMBRES BONITOS
# ============================================================

NOMBRES = {
    "comprension": "Comprensión",
    "morfologia": "Morfología",
    "semantica": "Semántica",
    "literatura": "Literatura",
    "sintaxis": "Sintaxis"
}


# ============================================================
# RADAR
# ============================================================

def radar_chart(alumno_scores, nombre="Alumno"):

    categorias = list(alumno_scores.keys())

    etiquetas = [
        NOMBRES.get(c, c)
        for c in categorias
    ]

    valores = [
        float(alumno_scores[c])
        for c in categorias
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=valores,
            theta=etiquetas,
            fill="toself",
            name=nombre
        )
    )

    fig.update_layout(
        title=f"Perfil competencial: {nombre}",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=False
    )

    return fig


# ============================================================
# COMPARATIVA
# ============================================================

def comparativa(alumno, df):

    competencias = [
        "comprension",
        "morfologia",
        "semantica",
        "literatura",
        "sintaxis"
    ]

    etiquetas = [
        NOMBRES[c]
        for c in competencias
    ]

    media_clase = [
        float(df[c].mean())
        for c in competencias
    ]

    valores_alumno = [
        float(alumno[c])
        for c in competencias
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=etiquetas,
            y=valores_alumno,
            name="Alumno"
        )
    )

    fig.add_trace(
        go.Bar(
            x=etiquetas,
            y=media_clase,
            name="Media clase"
        )
    )

    fig.update_layout(
        title="Alumno vs media de la clase",
        barmode="group",
        yaxis=dict(
            range=[0, 10],
            title="Puntuación / 10"
        )
    )

    return fig


# ============================================================
# PERFIL
# ============================================================

def generar_perfil(scores):

    perfil = []

    for competencia, nota in scores.items():

        nombre = NOMBRES.get(
            competencia,
            competencia
        )

        nota = float(nota)

        if nota < 4:

            perfil.append(
                f"🔴 Necesita refuerzo en {nombre} ({nota:.1f}/10)."
            )

        elif nota < 6:

            perfil.append(
                f"🟠 Nivel básico en {nombre} ({nota:.1f}/10)."
            )

        elif nota < 8:

            perfil.append(
                f"🟡 Nivel adecuado en {nombre} ({nota:.1f}/10)."
            )

        else:

            perfil.append(
                f"🟢 Buen dominio de {nombre} ({nota:.1f}/10)."
            )

    return perfil
