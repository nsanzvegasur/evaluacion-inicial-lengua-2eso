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
    valores = [float(datos.get(c, 0) or 0) for c in COMPETENCIAS]
    etiquetas = [NOMBRES[c] for c in COMPETENCIAS]
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
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


# ============================================================
# COMPARATIVA DEL GRUPO
# ============================================================

def comparativa(df, fila=None):
    """Genera la comparativa de notas del grupo.

    Acepta tanto la columna antigua ``Nota`` como la columna real que
    guarda actualmente la aplicación: ``nota_final_10``.
    ``fila`` se mantiene como argumento opcional para compatibilidad.
    """
    if df is None or getattr(df, "empty", True):
        return None

    columna = None
    for candidata in ("nota_final_10", "Nota", "nota_examen_9"):
        if candidata in df.columns:
            columna = candidata
            break
    if columna is None:
        return None

    valores = pd.to_numeric(df[columna], errors="coerce")
    validos = valores.dropna()
    if validos.empty:
        return None

    alumnos = [f"Alumno {i + 1}" for i in range(len(df))]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=alumnos,
            y=valores,
            name="Nota"
        )
    )

    media = float(validos.mean())
    fig.add_hline(
        y=media,
        line_dash="dash",
        annotation_text=f"Media de la clase: {media:.2f}",
        annotation_position="top left"
    )
    fig.update_layout(
        title="Comparativa con la clase",
        xaxis=dict(title="Alumnos"),
        yaxis=dict(title="Nota sobre 10", range=[0, 10]),
        showlegend=False,
        margin=dict(l=40, r=40, t=70, b=80),
    )
    return fig


# ============================================================
# PERFIL COMPETENCIAL
# ============================================================

def generar_perfil(datos):
    resultado = []
    for c in COMPETENCIAS:
        nota = round(float(datos.get(c, 0) or 0), 2)
        if nota < 5:
            nivel = "Necesita refuerzo"
            texto = f"{NOMBRES[c]}: necesita refuerzo."
        elif nota < 8:
            nivel = "Nivel adecuado"
            texto = f"{NOMBRES[c]}: nivel adecuado."
        else:
            nivel = "Fortaleza"
            texto = f"{NOMBRES[c]}: fortaleza."
        resultado.append({
            "competencia": c,
            "nombre": NOMBRES[c],
            "nota": nota,
            "nivel": nivel,
            "texto": texto,
        })
    return resultado
