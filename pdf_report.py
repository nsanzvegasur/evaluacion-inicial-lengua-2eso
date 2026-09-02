import os
import re
import unicodedata
from datetime import datetime

from fpdf import FPDF


def limpiar_texto(texto):
    if texto is None:
        return ""

    texto = str(texto)
    texto = unicodedata.normalize("NFKC", texto)

    reemplazos = {
        "\u00a0": " ",
        "–": "-",
        "—": "-",
        "…": "...",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "•": "-",
        "→": "->",
        "←": "<-",
        "✓": "OK",
        "✔": "OK",
        "€": "EUR",
        "º": "o",
        "ª": "a",
    }

    for antiguo, nuevo in reemplazos.items():
        texto = texto.replace(antiguo, nuevo)

    return texto.encode("latin-1", "replace").decode("latin-1")


def nombre_seguro(nombre):
    nombre = limpiar_texto(nombre)
    nombre = re.sub(r"[^A-Za-z0-9_-]+", "_", nombre)
    nombre = nombre.strip("_")
    return (nombre or "alumno")[:60]


def _numero(valor):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return 0.0


def generar_pdf(
    nombre=None,
    curso=None,
    resultados=None,
    respuestas=None,
    faltas_ortografia=0,
    descuento_ortografia=0,
    nota_inicial=0,
    nota_final=0,
    **kwargs,
):
    """
    Genera un PDF plano, sin formularios ni campos editables.
    Admite 'grupo' en lugar de 'curso' y 'scores' en lugar de 'resultados'
    por compatibilidad con versiones anteriores.
    """

    if curso is None:
        curso = kwargs.get("grupo", "")

    if resultados is None:
        resultados = kwargs.get("scores", {})

    if not isinstance(resultados, dict):
        resultados = {}

    if respuestas is None or not isinstance(respuestas, dict):
        respuestas = {}

    nombre = nombre or "Alumno"
    curso = curso or ""

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Cabecera
    pdf.set_font("Arial", "B", 16)
    pdf.cell(
        0,
        10,
        limpiar_texto("EVALUACION INICIAL DE LENGUA CASTELLANA"),
        ln=True,
        align="C",
    )

    pdf.set_font("Arial", "", 11)
    pdf.cell(
        0,
        7,
        limpiar_texto("2.º ESO - Curso 2026-2027"),
        ln=True,
        align="C",
    )

    pdf.ln(5)

    # Datos
    pdf.set_font("Arial", "B", 11)
    pdf.cell(35, 7, "Alumno:")
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, limpiar_texto(nombre), ln=True)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(35, 7, "Grupo:")
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, limpiar_texto(curso), ln=True)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(35, 7, "Fecha:")
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, datetime.now().strftime("%d/%m/%Y %H:%M"), ln=True)

    pdf.ln(5)

    # Resultados
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "RESULTADOS POR APARTADO", ln=True)
    pdf.ln(2)

    nombres = {
        "comprension": "Comprension lectora",
        "morfologia": "Morfologia",
        "determinantes": "Determinantes y pronombres",
        "semantica": "Semantica",
        "textos": "Textos",
        "literatura": "Literatura",
        "sintaxis": "Sintaxis",
        "dialogo": "Dialogo",
    }

    for clave, etiqueta in nombres.items():
        valor = _numero(resultados.get(clave, 0))
        pdf.set_font("Arial", "", 10)
        pdf.cell(
            0,
            7,
            limpiar_texto(f"{etiqueta}: {valor:.2f} puntos"),
            ln=True,
        )

    pdf.ln(3)

    nota_inicial_num = _numero(nota_inicial)
    descuento_num = _numero(descuento_ortografia)
    nota_final_num = _numero(nota_final)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(
        0,
        8,
        limpiar_texto(f"Nota inicial: {nota_inicial_num:.2f}/10"),
        ln=True,
    )

    pdf.cell(
        0,
        8,
        limpiar_texto(f"Descuento de ortografia: -{descuento_num:.2f}"),
        ln=True,
    )

    pdf.cell(
        0,
        8,
        limpiar_texto(f"Nota final: {nota_final_num:.2f}/10"),
        ln=True,
    )

    try:
        faltas_num = int(faltas_ortografia)
    except (TypeError, ValueError):
        faltas_num = 0

    pdf.ln(2)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(
        0,
        5,
        limpiar_texto(
            f"Faltas de ortografia detectadas automaticamente: {faltas_num}. "
            "La revision automatica es orientativa."
        ),
    )

    # Respuestas
    if respuestas:
        pdf.add_page()
        pdf.set_font("Arial", "B", 13)
        pdf.cell(0, 8, "RESPUESTAS DEL ALUMNO", ln=True)
        pdf.ln(3)

        for pregunta, respuesta in respuestas.items():
            pdf.set_font("Arial", "B", 9)
            pdf.multi_cell(0, 5, limpiar_texto(str(pregunta)))

            pdf.set_font("Arial", "", 9)

            if isinstance(respuesta, dict):
                partes = [
                    f"{clave}: {valor}"
                    for clave, valor in respuesta.items()
                ]
                texto_respuesta = "\n".join(partes)
            else:
                texto_respuesta = str(respuesta or "")

            if len(texto_respuesta) > 2000:
                texto_respuesta = texto_respuesta[:2000] + "..."

            pdf.multi_cell(0, 5, limpiar_texto(texto_respuesta))
            pdf.ln(2)

    # Aviso de documento de entrega
    pdf.ln(4)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(
        0,
        4,
        limpiar_texto(
            "Documento generado automaticamente por la aplicacion. "
            "No contiene campos de formulario editables."
        ),
    )

    carpeta = "pdf_resultados"
    os.makedirs(carpeta, exist_ok=True)

    nombre_archivo = (
        "resultado_"
        + nombre_seguro(nombre)
        + "_"
        + nombre_seguro(curso)
        + ".pdf"
    )

    ruta = os.path.abspath(
        os.path.join(carpeta, nombre_archivo)
    )

    pdf.output(ruta)
    return ruta
