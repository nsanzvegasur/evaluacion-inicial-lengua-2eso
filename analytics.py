import pandas as pd
import plotly.graph_objects as go


# ============================================================
# COMPETENCIAS DEL EXAMEN
# ============================================================

COMPETENCIAS = [
    "comprension",
    "morfologia",
    "semantica",
    "textos",
    "literatura",
    "sintaxis",
    "dialogo"
]


# ============================================================
# NOMBRES QUE SE MOSTRARÁN EN LA APP
# ============================================================

def nombres_competencias():
    return {
        "comprension": "Comprensión",
        "morfologia": "Morfología",
        "semantica": "Semántica",
        "textos": "Textos",
        "literatura": "Literatura",
        "sintaxis": "Sintaxis",
        "dialogo": "Diálogo"
    }


# ============================================================
# CONVERSIÓN SEGURA A NÚMERO
# ============================================================

def numero(valor):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return 0.0


# ============================================================
# RADAR DEL ALUMNO
# ============================================================

def radar_chart(datos, titulo="Perfil competencial"):
    nombres = nombres_competencias()

    valores = [
        numero(datos.get(c, 0))
        for c in COMPETENCIAS
    ]

    etiquetas = [
        nombres[c]
        for c in COMPETENCIAS
    ]

    # Cerramos el radar
    valores.append(valores[0])
    etiquetas.append(etiquetas[0])

    figura = go.Figure()

    figura.add_trace(
        go.Scatterpolar(
            r=valores,
            theta=etiquetas,
            fill="toself",
            name="Resultado"
        )
    )

    figura.update_layout(
        title=titulo,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=False
    )

    return figura


# ============================================================
# COMPARATIVA DE LA CLASE
# ============================================================

def comparativa_clase(df):
    if df is None or df.empty:
        return None

    columnas = [
        c for c in COMPETENCIAS
        if c in df.columns
    ]

    if not columnas:
        return None

    medias = []

    for columna in columnas:
        serie = pd.to_numeric(
            df[columna],
            errors="coerce"
        )

        medias.append(
            serie.mean()
        )

    nombres = nombres_competencias()

    etiquetas = [
        nombres[c]
        for c in columnas
    ]

    figura = go.Figure()

    figura.add_trace(
        go.Bar(
            x=etiquetas,
            y=medias
        )
    )

    figura.update_layout(
        title="Media de la clase por competencia",
        yaxis=dict(
            title="Nota",
            range=[0, 10]
        )
    )

    return figura


# ============================================================
# RESUMEN DE LA CLASE
# ============================================================

def resumen_clase(df):
    if df is None or df.empty:
        return {}

    resultado = {}

    if "nota_final" in df.columns:
        notas = pd.to_numeric(
            df["nota_final"],
            errors="coerce"
        ).dropna()

        if not notas.empty:

            resultado["media"] = round(
                notas.mean(),
                2
            )

            resultado["aprobados"] = int(
                (notas >= 5).sum()
            )

            resultado["suspensos"] = int(
                (notas < 5).sum()
            )

            resultado["alumnos"] = int(
                notas.count()
            )

    return resultado


# ============================================================
# PERFIL DEL ALUMNO
# ============================================================

def generar_perfil(datos):
    resultado = {}

    for competencia in COMPETENCIAS:

        valor = numero(
            datos.get(competencia, 0)
        )

        if valor >= 8:
            nivel = "Fortaleza"

        elif valor >= 5:
            nivel = "Nivel adecuado"

        else:
            nivel = "Necesita refuerzo"

        resultado[competencia] = {
            "nota": round(valor, 2),
            "nivel": nivel
        }

    return resultado
