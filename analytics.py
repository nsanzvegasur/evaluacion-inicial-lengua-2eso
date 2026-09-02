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


def numero(valor):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return 0.0


def radar_chart(alumno_scores, nombre="Alumno"):
    etiquetas = nombres_competencias()

    valores = [
        numero(alumno_scores.get(c, 0))
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

    if df is None or df.empty:
        media_clase = {
            c: 0
            for c in COMPETENCIAS
        }
    else:
        media_clase = {}

        for competencia in COMPETENCIAS:
            if competencia in df.columns:
                media_clase[competencia] = pd.to_numeric(
                    df[competencia],
                    errors="coerce"
                ).fillna(0).mean()
            else:
                media_clase[competencia] = 0

    valores_alumno = [
        numero(alumno.get(c, 0))
        for c in COMPETENCIAS
    ]

    valores_clase = [
        numero(media_clase.get(c, 0))
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

    comprension = numero(scores.get("comprension", 0))
    morfologia = numero(scores.get("morfologia", 0))
    semantica = numero(scores.get("semantica", 0))
    literatura = numero(scores.get("literatura", 0))
    sintaxis = numero(scores.get("sintaxis", 0))

    if comprension < 5:
        perfil.append("Dificultades en comprensión lectora.")
    elif comprension >= 7:
        perfil.append("Buen dominio de la comprensión lectora.")

    if morfologia < 5:
        perfil.append(
            "Necesita refuerzo en morfología y categorías gramaticales."
        )
    elif morfologia >= 7:
        perfil.append(
            "Buen dominio del análisis morfológico."
        )

    if semantica < 5:
        perfil.append(
            "Necesita reforzar las relaciones semánticas."
        )
    elif semantica >= 7:
        perfil.append(
            "Buen dominio de las relaciones semánticas."
        )

    if literatura < 5:
        perfil.append(
            "Necesita refuerzo en métrica y recursos literarios."
        )
    elif literatura >= 7:
        perfil.append(
            "Buen dominio de los contenidos literarios."
        )

    if sintaxis < 5:
        perfil.append(
            "Necesita reforzar frase, oración y modalidad oracional."
        )
    elif sintaxis >= 7:
        perfil.append(
            "Buen dominio de los contenidos sintácticos evaluados."
        )

    if not perfil:
        perfil.append(
            "Presenta un nivel equilibrado en las competencias evaluadas."
        )

    return perfil
