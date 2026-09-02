import os
import re
import unicodedata

from fpdf import FPDF


def limpiar_texto(texto):
    """
    Convierte el texto a una versión compatible
    con las fuentes básicas de FPDF.
    """

    if texto is None:
        return ""

    texto = str(texto)

    texto = unicodedata.normalize(
        "NFKC",
        texto
    )

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
        "ª": "a"
    }

    for antiguo, nuevo in reemplazos.items():
        texto = texto.replace(
            antiguo,
            nuevo
        )

    texto = texto.encode(
        "latin-1",
        "replace"
    ).decode(
        "latin-1"
    )

    return texto


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

    return nombre[:60]


def escribir_bloque(
    pdf,
    titulo,
    contenido,
    alto=6
):
    pdf.set_font(
        "Arial",
        "B",
        11
    )

    pdf.multi_cell(
        0,
        alto,
        limpiar_texto(titulo)
    )

    pdf.set_font(
        "Arial",
        "",
        10
    )

    pdf.multi_cell(
        0,
        alto,
        limpiar_texto(contenido)
    )

    pdf.ln(2)


def generar_pdf(
    nombre,
    curso,
    resultados,
    respuestas=None,
    faltas_ortografia=0,
    descuento_ortografia=0,
    nota_inicial=0,
    nota_final=0
):
    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.set_margins(
        15,
        15,
        15
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    pdf.add_page()

    # ==========================================================
    # CABECERA
    # ==========================================================

    pdf.set_font(
        "Arial",
        "B",
        16
    )

    pdf.cell(
        0,
        10,
        limpiar_texto(
            "Evaluación inicial de Lengua Castellana"
        ),
        ln=True,
        align="C"
    )

    pdf.set_font(
        "Arial",
        "",
        11
    )

    pdf.cell(
        0,
        7,
        limpiar_texto(
            "2.º ESO"
        ),
        ln=True,
        align="C"
    )

    pdf.ln(5)

    escribir_bloque(
        pdf,
        "Alumno",
        nombre
    )

    escribir_bloque(
        pdf,
        "Curso",
        curso
    )

    # ==========================================================
    # RESULTADOS
    # ==========================================================

    pdf.set_font(
        "Arial",
        "B",
        13
    )

    pdf.cell(
        0,
        8,
        "Resultados",
        ln=True
    )

    pdf.ln(2)

    nombres = {
        "comprension": "Comprension",
        "morfologia": "Morfologia",
        "semantica": "Semantica",
        "literatura": "Literatura",
        "sintaxis": "Sintaxis"
    }

    for clave, nombre_comp in nombres.items():

        valor = resultados.get(
            clave,
            0
        )

        try:
            valor = float(valor)
        except (TypeError, ValueError):
            valor = 0

        texto = (
            f"{nombre_comp}: "
            f"{valor:.2f}/10"
        )

        pdf.set_font(
            "Arial",
            "",
            10
        )

        pdf.cell(
            0,
            7,
            limpiar_texto(texto),
            ln=True
        )

    pdf.ln(3)

    # ==========================================================
    # NOTA
    # ==========================================================

    pdf.set_font(
        "Arial",
        "B",
        14
    )

    pdf.cell(
        0,
        9,
        limpiar_texto(
            f"Nota inicial: {float(nota_inicial):.2f}/10"
        ),
        ln=True
    )

    pdf.cell(
        0,
        9,
        limpiar_texto(
            f"Descuento de ortografia: -{float(descuento_ortografia):.2f}"
        ),
        ln=True
    )

    pdf.cell(
        0,
        9,
        limpiar_texto(
            f"Nota final: {float(nota_final):.2f}/10"
        ),
        ln=True
    )

    pdf.ln(3)

    # ==========================================================
    # ORTOGRAFÍA
    # ==========================================================

    escribir_bloque(
        pdf,
        "Correccion ortografica",
        (
            f"Faltas detectadas: {faltas_ortografia}\n"
            f"Descuento aplicado: "
            f"-{float(descuento_ortografia):.2f} puntos"
        )
    )

    # ==========================================================
    # RESPUESTAS
    # ==========================================================

    if respuestas:
        pdf.add_page()

        pdf.set_font(
            "Arial",
            "B",
            13
        )

        pdf.cell(
            0,
            8,
            "Respuestas del alumno",
            ln=True
        )

        pdf.ln(3)

        for pregunta, respuesta in respuestas.items():

            pdf.set_font(
                "Arial",
                "B",
                9
            )

            pdf.multi_cell(
                0,
                5,
                limpiar_texto(
                    str(pregunta)
                )
            )

            pdf.set_font(
                "Arial",
                "",
                9
            )

            texto_respuesta = str(
                respuesta
            )

            if len(texto_respuesta) > 500:
                texto_respuesta = (
                    texto_respuesta[:500]
                    + "..."
                )

            pdf.multi_cell(
                0,
                5,
                limpiar_texto(
                    texto_respuesta
                )
            )

            pdf.ln(2)

    # ==========================================================
    # GUARDAR
    # ==========================================================

    carpeta = "pdf_resultados"

    os.makedirs(
        carpeta,
        exist_ok=True
    )

    nombre_archivo = (
        f"resultado_"
        f"{nombre_seguro(nombre)}_"
        f"{nombre_seguro(curso)}.pdf"
    )

    ruta = os.path.abspath(
        os.path.join(
            carpeta,
            nombre_archivo
        )
    )

    pdf.output(ruta)

    return ruta
