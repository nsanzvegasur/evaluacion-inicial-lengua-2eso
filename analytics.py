import pandas as pd
import plotly.graph_objects as go

COMPETENCIAS = [
    "comprension",
    "morfologia",
    "semantica",
    "textos",
    "literatura",
    "sintaxis",
    "dialogo",
]

MAXIMOS = {
    "comprension": 2.0,
    "morfologia": 2.5,
    "semantica": 1.5,
    "textos": 1.0,
    "literatura": 2.0,
    "sintaxis": 1.0,
    "dialogo": 0.5,
}


def nombres_competencias():
    return {
        "comprension": "Comprensión",
        "morfologia": "Morfología",
        "semantica": "Semántica",
        "textos": "Textos",
        "literatura": "Literatura",
        "sintaxis": "Sintaxis",
        "dialogo": "Diálogo",
    }


def numero(valor):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return 0.0


def normalizar_nota_area(valor, competencia):
    maximo = MAXIMOS.get(competencia, 1.0)
    if maximo <= 0:
        return 0.0
    return max(0.0, min(10.0, numero(valor) / maximo * 10.0))


def radar_chart(datos, titulo="Perfil competencial"):
    nombres = nombres_competencias()
    valores = [
        normalizar_nota_area(datos.get(c, 0), c)
        for c in COMPETENCIAS
    ]
    etiquetas = [nombres[c] for c in COMPETENCIAS]
    valores.append(valores[0])
    etiquetas.append(etiquetas[0])

    figura = go.Figure()
    figura.add_trace(
        go.Scatterpolar(
            r=valores,
            theta=etiquetas,
            fill="toself",
            name="Resultado",
        )
    )
    figura.update_layout(
        title=titulo,
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=False,
    )
    return figura


def comparativa_clase(df):
    if df is None or df.empty:
        return None

    columnas = [c for c in COMPETENCIAS if c in df.columns]
    if not columnas:
        return None

    medias = [
        pd.to_numeric(df[c], errors="coerce").mean()
        / MAXIMOS[c] * 10
        for c in columnas
    ]
    etiquetas = [nombres_competencias()[c] for c in columnas]

    figura = go.Figure()
    figura.add_trace(go.Bar(x=etiquetas, y=medias))
    figura.update_layout(
        title="Media de la clase por área",
        yaxis=dict(title="Nivel sobre 10", range=[0, 10]),
    )
    return figura


def comparativa(alumno, df):
    if df is None or df.empty:
        return None

    columnas = [c for c in COMPETENCIAS if c in df.columns]
    if not columnas:
        return None

    medias = [
        pd.to_numeric(df[c], errors="coerce").mean()
        / MAXIMOS[c] * 10
        for c in columnas
    ]
    alumno_vals = [
        normalizar_nota_area(alumno.get(c, 0), c)
        for c in columnas
    ]
    etiquetas = [nombres_competencias()[c] for c in columnas]

    figura = go.Figure()
    figura.add_trace(go.Bar(name="Alumno", x=etiquetas, y=alumno_vals))
    figura.add_trace(go.Bar(name="Clase", x=etiquetas, y=medias))
    figura.update_layout(
        title="Alumno frente a la media de la clase",
        yaxis=dict(title="Nivel sobre 10", range=[0, 10]),
        barmode="group",
    )
    return figura


def resumen_clase(df):
    if df is None or df.empty:
        return {}

    resultado = {"alumnos": len(df)}
    columna = "nota_final" if "nota_final" in df.columns else "total"

    if columna in df.columns:
        notas = pd.to_numeric(df[columna], errors="coerce").dropna()
        if not notas.empty:
            resultado["media"] = round(notas.mean(), 2)
            resultado["aprobados"] = int((notas >= 5).sum())
            resultado["suspensos"] = int((notas < 5).sum())

    return resultado


def generar_perfil(datos):
    resultado = {}
    nombres = nombres_competencias()

    for competencia in COMPETENCIAS:
        valor = normalizar_nota_area(
            datos.get(competencia, 0),
            competencia
        )

        if valor >= 8:
            nivel = "Fortaleza"
        elif valor >= 5:
            nivel = "Nivel adecuado"
        else:
            nivel = "Necesita refuerzo"

        resultado[competencia] = {
            "nombre": nombres[competencia],
            "nota": round(valor, 2),
            "nivel": nivel,
        }

    return resultado
