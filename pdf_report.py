from fpdf import FPDF
from datetime import datetime
import os
import re
import unicodedata


def limpiar_texto(texto):

    if texto is None:
        return ""

    texto = str(texto)

    # Normalización Unicode
    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    # Sustituir caracteres problemáticos
    reemplazos = {
        "\u00a0": " ",
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
        "ü": "u",
        "Ü": "U",
        "¿": "?",
        "¡": "!",
        "«": '"',
        "»": '"',
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "–": "-",
        "—": "-",
        "•": "-",
        "→": "->",
        "✓": "OK",
        "✗": "X"
    }

    for original, nuevo in reemplazos.items():
        texto = texto.replace(
            original,
            nuevo
        )

    # Eliminar caracteres que FPDF no puede manejar
    texto = texto.encode(
        "latin-1",
        errors="ignore"
    ).decode(
        "latin-1"
    )

    # Limpiar espacios repetidos
    texto = re.sub(
        r"[ \t]+",
        " ",
        texto
    )

    # Limpiar saltos repetidos
    texto = re.sub(
        r"\n\s*\n+",
        "\n",
        texto
    )

    return texto.strip()


class InformePDF(FPDF):

    def texto_seguro(
        self,
        texto,
        alto=7
    ):
        texto = limpiar_texto(texto)

        if not texto:
            return

        self.multi_cell(
            0,
            alto,
            texto
        )


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

    pdf = InformePDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    pdf.add_page()

    # =====================================================
    # CABECERA
    # =====================================================

    pdf.set_font(
        "Arial",
        "B",
        16
    )

    pdf.cell(
        0,
        10,
        "INFORME DE EVALUACION INICIAL",
        ln=True
    )

    pdf.set_font(
        "Arial",
        "B",
        12
    )

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

    pdf.set_font(
        "Arial",
        size=11
    )

    pdf.texto_seguro(
        f"Nombre: {nombre}"
    )

    pdf.texto_seguro(
        f"Grupo: {grupo}"
    )

    pdf.texto_seguro(
        f"Fecha: {datetime.now().strftime('%d/%m/%Y')}"
    )

    pdf.ln(5)

    # =====================================================
    # RESULTADOS
    # =====================================================

    pdf.set_font(
        "Arial",
        "B",
        13
    )

    pdf.cell(
        0,
        8,
        "RESULTADOS",
        ln=True
    )

    pdf.set_font(
        "Arial",
        size=11
    )

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

        pdf.texto_seguro(
            f"{texto}: {float(valor):.2f}/10"
        )

    pdf.ln(3)

    # =====================================================
    # NOTA FINAL
    # =====================================================

    if nota_inicial is not None:

        pdf.set_font(
            "Arial",
            "B",
            11
        )

        pdf.texto_seguro(
            f"Nota inicial: {float(nota_inicial):.2f}/10"
        )

        pdf.set_font(
            "Arial",
            size=11
        )

        pdf.texto_seguro(
            f"Faltas de ortografia detectadas: {faltas_ortografia}"
        )

        pdf.texto_seguro(
            f"Faltas de tilde detectadas: {faltas_tildes}"
        )

        pdf.texto_seguro(
            f"Descuento ortografico: -{float(descuento_ortografia):.2f}"
        )

        pdf.set_font(
            "Arial",
            "B",
            12
        )

        if nota_final is not None:

            pdf.texto_seguro(
                f"Nota final: {float(nota_final):.2f}/10"
            )

    pdf.ln(5)

    # =====================================================
    # DIAGNÓSTICO PEDAGÓGICO
    # =====================================================

    pdf.set_font(
        "Arial",
        "B",
        13
    )

    pdf.cell(
        0,
        8,
        "DIAGNOSTICO PEDAGOGICO",
        ln=True
    )

    pdf.set_font(
        "Arial",
        size=11
    )

    for item in perfil:

        pdf.texto_seguro(
            "- " + str(item),
            alto=7
        )

    pdf.ln(5)

    # =====================================================
    # OBSERVACIÓN GENERAL
    # =====================================================

    pdf.set_font(
        "Arial",
        "B",
        13
    )

    pdf.cell(
        0,
        8,
        "OBSERVACION GENERAL",
        ln=True
    )

    pdf.set_font(
        "Arial",
        size=11
    )

    if nota_final is not None:

        nota = float(nota_final)

        if nota < 5:

            observacion = (
                "El alumno necesita refuerzo en varias de las "
                "competencias basicas evaluadas."
            )

        elif nota < 7:

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

    pdf.texto_seguro(
        observacion,
        alto=7
    )

    # =====================================================
    # GUARDAR
    # =====================================================

    nombre_archivo = limpiar_texto(
        nombre
    )

    nombre_archivo = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        nombre_archivo
    )

    nombre_archivo = nombre_archivo.strip(
        "_"
    )

    if not nombre_archivo:
        nombre_archivo = "alumno"

    filename = (
        f"informe_{nombre_archivo}.pdf"
    )

    pdf.output(
        filename
    )

    return filename
