import plotly.graph_objects as go
import pandas as pd


COMPETENCIAS = [
    "comprension",
    "morfologia",
    "semantica",
    "literatura",
    "sintaxis"
]


def nombres_competencias():
    return {
        "comprension": "Comprensión",
        "morfologia": "Morfología",
        "semantica": "Semántica",
        "literatura": "Literatura",
        "sintaxis": "Sintaxis"
    }


def radar_chart(alumno_scores, nombre="Alumno"):

    etiquetas = nombres_competencias()

    valores = [
        alumno_scores.get(c, 0)
        for c in COMPETENCIAS
    ]

    categorias = [
        etiquetas[c]
        for c in COMPETENCIAS
    ]

    valores.append(valores[0])
    categorias.append(categorias[0])

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=valores,
            theta=categorias,
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


def comparativa(alumno, df):

    etiquetas = nombres_competencias()

    media_clase = df[COMPETENCIAS].mean()

    valores_alumno = [
        float(alumno.get(c, 0))
        for c in COMPETENCIAS
    ]

    valores_clase = [
        float(media_clase.get(c, 0))
        for c in COMPETENCIAS
    ]

    nombres = [
        etiquetas[c]
        for c in COMPETENCIAS
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=nombres,
            y=valores_alumno,
            name="Alumno"
        )
    )

    fig.add_trace(
        go.Bar(
            x=nombres,
            y=valores_clase,
            name="Media clase"
        )
    )

    fig.update_layout(
        title="Alumno vs. media de la clase",
        barmode="group",
        yaxis=dict(
            title="Nota sobre 10",
            range=[0, 10]
        )
    )

    return fig


def generar_perfil(scores):

    perfil = []

    if scores["comprension"] < 5:
        perfil.append(
            "Dificultades en comprensión lectora."
        )
    elif scores["comprension"] >= 7:
        perfil.append(
            "Buen dominio de la comprensión lectora."
        )

    if scores["morfologia"] < 5:
        perfil.append(
            "Necesita refuerzo en morfología y categorías gramaticales."
        )
    elif scores["morfologia"] >= 7:
        perfil.append(
            "Buen dominio del análisis morfológico."
        )

    if scores["semantica"] < 5:
        perfil.append(
            "Necesita reforzar las relaciones semánticas."
        )
    elif scores["semantica"] >= 7:
        perfil.append(
            "Buen dominio de las relaciones semánticas."
        )

    if scores["literatura"] < 5:
        perfil.append(
            "Necesita refuerzo en métrica y recursos literarios."
        )
    elif scores["literatura"] >= 7:
        perfil.append(
            "Buen dominio de los contenidos literarios."
        )

    if scores["sintaxis"] < 5:
        perfil.append(
            "Necesita reforzar frase, oración y modalidad oracional."
        )
    elif scores["sintaxis"] >= 7:
        perfil.append(
            "Buen dominio de los contenidos sintácticos evaluados."
        )

    if not perfil:
        perfil.append(
            "Presenta un nivel equilibrado en las competencias evaluadas."
        )

    return perfil
