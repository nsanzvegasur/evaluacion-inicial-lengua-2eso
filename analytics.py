import plotly.graph_objects as go
import pandas as pd

# =========================
# RADAR CHART (PERFIL ALUMNO)
# =========================
def radar_chart(alumno_scores, nombre="Alumno"):
    """
    alumno_scores = dict con competencias:
    {
        "comprension": 6,
        "morfologia": 4,
        "semantica": 7,
        "literatura": 5,
        "sintaxis": 3
    }
    """

    categorias = list(alumno_scores.keys())
    valores = list(alumno_scores.values())

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=valores,
        theta=categorias,
        fill='toself',
        name=nombre
    ))

    fig.update_layout(
        title=f"📊 Perfil competencial: {nombre}",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=False
    )

    return fig


# =========================
# COMPARATIVA ALUMNO VS CLASE
# =========================
def comparativa(alumno, df):
    """
    alumno = fila del dataframe
    df = dataset completo
    """

    competencias = ["comprension", "morfologia", "semantica", "literatura", "sintaxis"]

    media_clase = df[competencias].mean().to_dict()

    alumno_vals = {c: alumno[c] for c in competencias}

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=competencias,
        y=[alumno_vals[c] for c in competencias],
        name="Alumno"
    ))

    fig.add_trace(go.Bar(
        x=competencias,
        y=[media_clase[c] for c in competencias],
        name="Media clase"
    ))

    fig.update_layout(
        title="📊 Alumno vs Clase",
        barmode='group'
    )

    return fig


# =========================
# PERFIL INTERPRETABLE
# =========================
def generar_perfil(scores):
    """
    Devuelve diagnóstico pedagógico automático
    """

    perfil = []

    if scores["comprension"] < 5:
        perfil.append("🔴 Dificultades en comprensión lectora")

    if scores["morfologia"] < 5:
        perfil.append("🔴 Problemas en identificación gramatical")

    if scores["semantica"] < 5:
        perfil.append("🟠 Dificultades en conceptos semánticos")

    if scores["literatura"] >= 7:
        perfil.append("🟢 Buen dominio de recursos literarios")

    if scores["sintaxis"] < 5:
        perfil.append("🔴 Dificultades en estructura oracional")

    if not perfil:
        perfil.append("🟢 Nivel equilibrado en todas las competencias")

    return perfil
