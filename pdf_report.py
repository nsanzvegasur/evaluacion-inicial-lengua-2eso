from fpdf import FPDF
from datetime import datetime
import os
import re
import unicodedata


def limpiar_texto(texto):
    """
    Convierte cualquier texto a una versión segura para
    las fuentes estándar de FPDF.
    """

    if texto is None:
        return ""

    texto = str(texto)

    reemplazos = {
        "\u00a0": " ",
        "º": "o",
        "ª": "a",
        "–": "-",
        "—": "-",
        "−": "-",
        "…": "...",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "•": "-",
        "→": "->",
        "✓": "OK",
        "✗": "X",
        "€": "EUR"
    }

    for original, sustituto in reemplazos.items():
        texto = texto.replace(original, sustituto)

    texto = unicodedata.normalize("NFKC", texto)

    # Convertimos a Latin-1 para que Arial/Helvetica de FPDF
    # no produzcan errores con caracteres Unicode.
    texto = texto.encode(
        "latin-1",
        "replace"
    ).decode("latin-1")

    # Evita cadenas gigantes sin espacios.
    texto = re.sub(
        r"(\S{45})(?=\S)",
        r"\1 ",
        texto
    )

    return texto.strip()


def nombre_seguro(nombre):
    nombre = limpiar_texto(nombre)

    nombre = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        nombre
    )

    nombre = nombre.strip("_")

    if not nombre:
        nombre = "alumno"

    return nombre


def escribir_bloque(pdf, texto, alto=7):
    texto = limpiar_texto(texto)

    if not texto:
        return

    pdf.multi_cell(
        0,
        alto,
        texto
    )


def generar_pdf(
    nombre,
    curso,
    scores,
    nota_inicial,
    descuento_ortografia,
    nota_final,
    perfil
):
    pdf = FPDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    pdf.set_margins(
        left=15,
        top=15,
        right=15
    )

    pdf.add_page()

    # Título
    pdf.set_font(
        "Arial",
        "B",
        18
    )

    escribir_bloque(
        pdf,
        "Informe de Evaluacion Inicial - 2o ESO",
        9
    )

    pdf.ln(3)

    pdf.set_font(
        "Arial",
        "",
        11
    )

    escribir_bloque(
        pdf,
        f"Alumno/a: {nombre}"
    )

    escribir_bloque(
        pdf,
        f"Curso: {curso}"
    )

    escribir_bloque(
        pdf,
        f"Fecha: {datetime.now().strftime('%d/%m/%Y')}"
    )

    pdf.ln(4)

    # Notas
    pdf.set_font(
        "Arial",
        "B",
        13
    )

    escribir_bloque(
        pdf,
        "Resultados"
    )

    pdf.set_font(
        "Arial",
        "",
        11
    )

    competencias = [
        ("Comprension", "comprension"),
        ("Morfologia", "morfologia"),
        ("Semantica", "semantica"),
        ("Literatura", "literatura"),
        ("Sintaxis", "sintaxis")
    ]

    for etiqueta, clave in competencias:
        try:
            valor = float(scores.get(clave, 0))
        except (TypeError, ValueError):
            valor = 0

        escribir_bloque(
            pdf,
            f"{etiqueta}: {valor:.2f} / 10"
        )

    pdf.ln(3)

    escribir_bloque(
        pdf,
        f"Nota inicial: {float(nota_inicial):.2f} / 10"
    )

    escribir_bloque(
        pdf,
        f"Descuento por ortografia: -{float(descuento_ortografia):.2f}"
    )

    escribir_bloque(
        pdf,
        f"Nota final: {float(nota_final):.2f} / 10"
    )

    pdf.ln(5)

    # Perfil
    pdf.set_font(
        "Arial",
        "B",
        13
    )

    escribir_bloque(
        pdf,
        "Perfil del alumno"
    )

    pdf.set_font(
        "Arial",
        "",
        11
    )

    if perfil:
        for observacion in perfil:
            escribir_bloque(
                pdf,
                f"- {observacion}"
            )
    else:
        escribir_bloque(
            pdf,
            "No se han generado observaciones."
        )

    # Pie
    pdf.ln(8)

    pdf.set_font(
        "Arial",
        "I",
        9
    )

    escribir_bloque(
        pdf,
        "Informe generado automaticamente por la aplicacion de Evaluacion Inicial."
    )

    archivo = (
        f"informe_{nombre_seguro(nombre)}.pdf"
    )

    ruta = os.path.abspath(archivo)

    pdf.output(ruta)

    return ruta
