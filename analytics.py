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

```
categorias = [
    NOMBRES.get(k, k)
    for k in alumno_scores.keys()
]

valores = list(alumno_scores.values())

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
```

# ============================================================

# COMPARATIVA

# ============================================================

def comparativa(alumno, df):

```
competencias = [
    "comprension",
    "morfologia",
    "semantica",
    "literatura",
    "sintaxis"
]

media_clase = (
    df[competencias]
    .mean()
    .to_dict()
)

alumno_vals = {
    c: float(alumno[c])
    for c in competencias
}

nombres = [
    NOMBRES[c]
    for c in competencias
]

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=nombres,
        y=[
            alumno_vals[c]
            for c in competencias
        ],
        name="Alumno"
    )
)

fig.add_trace(
    go.Bar(
        x=nombres,
        y=[
            media_clase[c]
            for c in competencias
        ],
        name="Media clase"
    )
)

fig.update_layout(
    title="📊 Alumno vs clase",
    barmode="group",
    yaxis=dict(
        range=[0, 10]
    )
)

return fig
```

# ============================================================

# PERFIL PEDAGÓGICO

# ============================================================

def generar_perfil(scores):

```
perfil = []

if scores["comprension"] < 5:
    perfil.append(
        "🔴 Dificultades en comprensión lectora."
    )
elif scores["comprension"] >= 7:
    perfil.append(
        "🟢 Buen nivel de comprensión lectora."
    )

if scores["morfologia"] < 5:
    perfil.append(
        "🔴 Necesita refuerzo en morfología y categorías gramaticales."
    )
elif scores["morfologia"] >= 7:
    perfil.append(
        "🟢 Buen dominio de la morfología."
    )

if scores["semantica"] < 5:
    perfil.append(
        "🟠 Necesita reforzar las relaciones semánticas."
    )
elif scores["semantica"] >= 7:
    perfil.append(
        "🟢 Buen dominio de los conceptos semánticos."
    )

if scores["literatura"] < 5:
    perfil.append(
        "🔴 Necesita refuerzo en análisis literario."
    )
elif scores["literatura"] >= 7:
    perfil.append(
        "🟢 Buen dominio de los recursos literarios."
    )

if scores["sintaxis"] < 5:
    perfil.append(
        "🔴 Necesita refuerzo en sintaxis y modalidad oracional."
    )
elif scores["sintaxis"] >= 7:
    perfil.append(
        "🟢 Buen dominio de la sintaxis."
    )

if not perfil:

    perfil.append(
        "🟢 Nivel equilibrado en las competencias evaluadas."
    )

return perfil
```
