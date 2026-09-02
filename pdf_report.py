from fpdf import FPDF
from datetime import datetime
import os


def limpiar_texto(texto):

    reemplazos = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "Á": "A",
        "É": "E",
        "Í": "I",
        "Ó": "O",
        "Ú": "U",
        "ñ": "n",
        "Ñ": "N",
        "¿": "?",
        "¡": "!",
        "«": '"',
        "»": '"',
        "–": "-",
        "—": "-"
    }

    texto = str(texto)

    for original, nuevo in reemplazos.items():
        texto = texto.replace(original, nuevo)

    return texto


def generar_pdf(
    nombre,
    grupo,
    scores,
    perfil,
    nota_inicial=None,
    descuento_ortografia=0,
    faltas_ortografia=0,
    faltas_tildes=0,
    nota_final=None
):

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # =====================================================
    # CABECERA
    # =====================================================

    pdf.set_font("Arial", "B", 16)
    pdf.cell(
        0,
        10,
        "INFORME DE EVALUACION INICIAL",
        ln=True
    )

    pdf.set_font("Arial", "B", 12)
    pdf.cell(
        0,
        8,
        "2o ESO - Lengua Castellana y Literatura",
        ln=True
    )

    pdf.ln(5)

    # =====================================================
    # DATOS
    # =====================================================

    pdf.set_font("Arial", size=11)

    pdf.cell(
        0,
        7,
        f"Nombre: {limpiar_texto(nombre)}",
        ln=True
    )

    pdf.cell(
        0,
        7,
        f"Grupo: {limpiar_texto(grupo)}",
        ln=True
    )

    pdf.cell(
        0,
        7,
        f"Fecha: {datetime.now().strftime('%d/%m/%Y')}",
        ln=True
    )

    pdf.ln(5)

    # =====================================================
    # NOTAS
    # =====================================================

    pdf.set_font("Arial", "B", 13)
    pdf.cell(
        0,
        8,
        "RESULTADOS",
        ln=True
    )

    pdf.set_font("Arial", size=11)

    nombres = {
        "comprension": "Comprension lectora",
        "morfologia": "Morfologia",
        "semantica": "Semantica",
        "literatura": "Literatura",
        "sintaxis": "Sintaxis"
    }

    for clave, valor in scores.items():

        if clave in nombres:
            texto = nombres[clave]
        else:
            texto = clave.capitalize()

        pdf.cell(
            0,
            7,
            f"{texto}: {float(valor):.2f}/10",
            ln=True
        )

    pdf.ln(3)

    if nota_inicial is not None:

        pdf.set_font("Arial", "B", 11)

        pdf.cell(
            0,
            7,
            f"Nota inicial: {nota_inicial:.2f}/10",
            ln=True
        )

        pdf.set_font("Arial", size=11)

        pdf.cell(
            0,
            7,
            f"Faltas de ortografia detectadas: {faltas_ortografia}",
            ln=True
        )

        pdf.cell(
            0,
            7,
            f"Faltas de tilde detectadas: {faltas_tildes}",
            ln=True
        )

        pdf.cell(
            0,
            7,
            f"Descuento ortografico: -{descuento_ortografia:.2f}",
            ln=True
        )

        pdf.set_font("Arial", "B", 12)

        pdf.cell(
            0,
            8,
            f"Nota final: {nota_final:.2f}/10",
            ln=True
        )

    pdf.ln(5)

    # =====================================================
    # PERFIL
    # =====================================================

    pdf.set_font("Arial", "B", 13)

    pdf.cell(
        0,
        8,
        "DIAGNOSTICO PEDAGOGICO",
        ln=True
    )

    pdf.set_font("Arial", size=11)

    for item in perfil:

        pdf.multi_cell(
            0,
            7,
            "- " + limpiar_texto(item)
        )

    pdf.ln(5)

    # =====================================================
    # OBSERVACION GENERAL
    # =====================================================

    pdf.set_font("Arial", "B", 13)

    pdf.cell(
        0,
        8,
        "OBSERVACION GENERAL",
        ln=True
    )

    pdf.set_font("Arial", size=11)

    if nota_final is not None:

        if nota_final < 5:
            observacion = (
                "El alumno necesita refuerzo en varias de las "
                "competencias basicas evaluadas."
            )

        elif nota_final < 7:
            observacion = (
                "El alumno presenta un nivel medio y cuenta con "
                "algunas areas concretas de mejora."
            )

        else:
            observacion = (
                "El alumno presenta un buen dominio general "
                "de las competencias evaluadas."
            )

    else:

        observacion = (
            "Informe correspondiente a la evaluacion inicial."
        )

    pdf.multi_cell(
        0,
        7,
        limpiar_texto(observacion)
    )

    # =====================================================
    # GUARDAR
    # =====================================================

    nombre_archivo = limpiar_texto(nombre)
    nombre_archivo = nombre_archivo.replace(" ", "_")

    if not nombre_archivo:
        nombre_archivo = "alumno"

    filename = f"informe_{nombre_archivo}.pdf"

    pdf.output(filename)

    return filename
