import pandas as pd
import plotly.graph_objects as go

COMPETENCIAS = [
    "comprension", "morfologia", "determinantes", "semantica",
    "textos", "literatura", "sintaxis", "dialogo"
]

NOMBRES = {
    "comprension": "Comprensión",
    "morfologia": "Morfología",
    "determinantes": "Determinantes y pronombres",
    "semantica": "Semántica",
    "textos": "Textos",
    "literatura": "Literatura",
    "sintaxis": "Sintaxis",
    "dialogo": "Diálogo",
}


def radar_chart(datos, titulo="Perfil competencial"):
    valores = [float(datos.get(c, 0)) for c in COMPETENCIAS]
    # Cada apartado ya está expresado en puntos de un examen sobre 10.
    escala = {
        "comprension": 2, "morfologia": 2, "determinantes": 0.5,
        "semantica": 1, "textos": 1, "literatura": 2,
        "sintaxis": 1, "dialogo": 0.5
    }
    valores = [min(10, valores[i] / escala[c] * 10) if escala[c] else 0 for i, c in enumerate(COMPETENCIAS)]
    etiquetas = [NOMBRES[c] for c in COMPETENCIAS]
    valores.append(valores[0])
    etiquetas.append(etiquetas[0])
    figura = go.Figure(go.Scatterpolar(r=valores, theta=etiquetas, fill="toself"))
    figura.update_layout(title=titulo, polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=False)
    return figura


def comparativa_clase(df):
    if df is None or df.empty:
        return None
    maximos = {"comprension":2,"morfologia":2,"determinantes":0.5,"semantica":1,"textos":1,"literatura":2,"sintaxis":1,"dialogo":0.5}
    x, y = [], []
    for c in COMPETENCIAS:
        if c in df.columns:
            media = pd.to_numeric(df[c], errors="coerce").mean()
            y.append(min(10, media / maximos[c] * 10))
            x.append(NOMBRES[c])
    if not x:
        return None
    fig = go.Figure(go.Bar(x=x, y=y))
    fig.update_layout(title="Media de la clase por apartado", yaxis=dict(title="Nota sobre 10", range=[0,10]))
    return fig


def generar_perfil(datos):
    maximos = {"comprension":2,"morfologia":2,"determinantes":0.5,"semantica":1,"textos":1,"literatura":2,"sintaxis":1,"dialogo":0.5}
    resultado = {}
    for c in COMPETENCIAS:
        nota = min(10, float(datos.get(c,0)) / maximos[c] * 10)
        nivel = "Fortaleza" if nota >= 8 else "Nivel adecuado" if nota >= 5 else "Necesita refuerzo"
        resultado[c] = {"nombre":NOMBRES[c], "nota":round(nota,1), "nivel":nivel}
    return resultado
