from fpdf import FPDF
from datetime import datetime
import os


# ============================================================
# PDF
# ============================================================

def limpiar(texto):

    texto = str(texto)

    reemplazos = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n",
        "Á": "A",
        "É": "E",
        "Í": "I",
        "Ó": "O",
        "Ú": "U",
        "Ñ": "N",
        "🔴": "",
        "🟠": "",
        "🟡": "",
        "🟢": ""
    }

    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(
            viejo,
            nuevo
        )

    return texto


def generar_pdf(
    nombre,
    grupo,
    scores,
    perfil,
    faltas_ortografia=0,
    faltas_tildes=0,
    presentacion=0,
    nota_inicial=0,
    nota_final=0
):

    pdf = FPDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    pdf.add_page()

    # ========================================================
    # TÍTULO
    # ========================================================

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
        "",
        11
    )

    pdf.cell(
        0,
        8,
        "Lengua Castellana y Literatura - 2 ESO",
        ln=True
    )

    pdf.ln(5)


    # ========================================================
    # DATOS
    # ========================================================

    pdf.set_font(
        "Arial",
        "B",
        11
    )

    pdf.cell(
        0,
        8,
        "DATOS DEL ALUMNO",
        ln=True
    )

    pdf.set_font(
        "Arial",
        "",
        11
    )

    pdf.cell(
        0,
        7,
        f"Nombre y apellidos: {limpiar(nombre)}",
        ln=True
    )

    pdf.cell(
        0,
        7,
        f"Grupo: {limpiar(grupo)}",
        ln=True
    )

    pdf.cell(
        0,
        7,
        f"Fecha: {datetime.now().strftime('%d/%m/%Y')}",
        ln=True
    )

    pdf.ln(5)


    # ========================================================
    # CALIFICACIÓN
    # ========================================================

    pdf.set_font(
        "Arial",
        "B",
        11
    )

    pdf.cell(
        0,
        8,
        "CALIFICACION",
        ln=True
    )

    pdf.set_font(
        "Arial",
        "",
        11
    )

    pdf.cell(
        0,
        7,
        f"Nota inicial: {nota_inicial:.2f} / 10",
        ln=True
    )

    pdf.cell(
        0,
        7,
        f"Faltas de ortografia: {faltas_ortografia}",
        ln=True
    )

    pdf.cell(
        0,
        7,
        f"Faltas de tilde: {faltas_tildes}",
        ln=True
    )

    descuento_ortografia = min(
        2,
        faltas_ortografia * 0.2
        + faltas_tildes * 0.1
    )

    pdf.cell(
        0,
        7,
        f"Descuento ortografico: -{descuento_ortografia:.2f}",
        ln=True
    )

    pdf.cell(
        0,
        7,
        f"Descuento por presentacion: -{float(presentacion):.2f}",
        ln=True
    )

    pdf.set_font(
        "Arial",
        "B",
        14
    )

    pdf.cell(
        0,
        10,
        f"NOTA FINAL: {nota_final:.2f} / 10",
        ln=True
    )

    pdf.ln(5)


    # ========================================================
    # RESULTADOS
    # ========================================================

    nombres = {
        "comprension": "Comprension lectora",
        "morfologia": "Morfologia",
        "semantica": "Semantica",
        "textos": "Textos",
        "literatura": "Literatura",
        "sintaxis": "Sintaxis",
        "dialogo": "Dialogo"
    }

    pdf.set_font(
        "Arial",
        "B",
        11
    )

    pdf.cell(
        0,
        8,
        "RESULTADOS POR APARTADO",
        ln=True
    )

    pdf.set_font(
        "Arial",
        "",
        11
    )

    for clave, valor in scores.items():

        if clave == "total":
            continue

        nombre_apartado = nombres.get(
            clave,
            clave
        )

        pdf.cell(
            0,
            7,
            f"{nombre_apartado}: {float(valor):.2f}",
            ln=True
        )

    pdf.ln(5)


    # ========================================================
    # DIAGNÓSTICO
    # ========================================================

    pdf.set_font(
        "Arial",
        "B",
        11
    )

    pdf.cell(
        0,
        8,
        "DIAGNOSTICO PEDAGOGICO",
        ln=True
    )

    pdf.set_font(
        "Arial",
        "",
        10
    )

    for item in perfil:

        pdf.multi_cell(
            0,
            7,
            limpiar("- " + item)
        )

    pdf.ln(5)


    # ========================================================
    # OBSERVACIÓN
    # ========================================================

    pdf.set_font(
        "Arial",
        "B",
        11
    )

    pdf.cell(
        0,
        8,
        "OBSERVACION GENERAL",
        ln=True
    )

    pdf.set_font(
        "Arial",
        "",
        10
    )

    if nota_final < 5:

        observacion = (
            "El alumno presenta areas que requieren "
            "refuerzo dentro de las competencias evaluadas."
        )

    elif nota_final < 7:

        observacion = (
            "El alumno presenta un nivel adecuado, "
            "aunque existen algunas areas susceptibles de mejora."
        )

    else:

        observacion = (
            "El alumno presenta un buen nivel general "
            "en las competencias evaluadas."
        )

    pdf.multi_cell(
        0,
        7,
        observacion
    )


    # ========================================================
    # GUARDAR
    # ========================================================

    nombre_archivo = limpiar(
        nombre.replace(" ", "_")
    )

    nombre_archivo = (
        f"informe_{nombre_archivo}.pdf"
    )

    pdf.output(
        nombre_archivo
    )

    return nombre_archivo
