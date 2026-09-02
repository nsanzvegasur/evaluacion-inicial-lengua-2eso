```python
import os
import re
import unicodedata

from fpdf import FPDF


# ==========================================================
# LIMPIEZA DE TEXTO
# ==========================================================

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
        "ª": "a",
    }

    for antiguo, nuevo in reemplazos.items():
        texto = texto.replace(
            antiguo,
            nuevo
        )

    # FPDF con Arial utiliza latin-1.
    texto = (
        texto
        .encode("latin-1", "replace")
        .decode("latin-1")
    )

    return texto


# ==========================================================
# NOMBRE SEGURO PARA EL ARCHIVO
# ==========================================================

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


# ==========================================================
# ESCRIBIR BLOQUES
# ==========================================================

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


# ==========================================================
# GENERADOR DEL PDF
# ==========================================================

def generar_pdf(
    nombre=None,
    curso=None,
    resultados=None,
    respuestas=None,
    faltas_ortografia=0,
    descuento_ortografia=0,
    nota_inicial=0,
    nota_final=0,
    **kwargs
):
    """
    Genera el informe PDF del alumno.

    Compatible con las distintas versiones de app.py:
    - nombre
    - curso / grupo
    - resultados / scores
    - respuestas
    - faltas_ortografia
    - descuento_ortografia
    - nota_inicial
    - nota_final
    """

    # ------------------------------------------------------
    # COMPATIBILIDAD CON "grupo"
    # ------------------------------------------------------

    if curso is None:
        curso = kwargs.get(
            "grupo",
            ""
        )

    # ------------------------------------------------------
    # COMPATIBILIDAD CON "scores"
    # ------------------------------------------------------

    if resultados is None:
        resultados = kwargs.get(
            "scores",
            {}
        )

    # Evitar errores si no llegan resultados
    if not isinstance(resultados, dict):
        resultados = {}

    # Evitar errores con respuestas
    if respuestas is None:
        respuestas = {}

    # Evitar valores None
    if nombre is None:
        nombre = "Alumno"

    if curso is None:
        curso = ""

    # ======================================================
    # CREAR PDF
    # ======================================================

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

    # ======================================================
    # CABECERA
    # ======================================================

    pdf.set_font(
        "Arial",
        "B",
        16
    )

    pdf.cell(
        0,
        10,
        limpiar_texto(
            "EVALUACION INICIAL DE LENGUA CASTELLANA"
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
            "2.º ESO - Curso 2026-2027"
        ),
        ln=True,
        align="C"
    )

    pdf.ln(5)

    # ======================================================
    # DATOS DEL ALUMNO
    # ======================================================

    escribir_bloque(
        pdf,
        "Alumno",
        nombre
    )

    escribir_bloque(
        pdf,
        "Grupo",
        curso
    )

    # ======================================================
    # RESULTADOS POR COMPETENCIA
    # ======================================================

    pdf.set_font(
        "Arial",
        "B",
        13
    )

    pdf.cell(
        0,
        8,
        limpiar_texto(
            "RESULTADOS POR COMPETENCIA"
        ),
        ln=True
    )

    pdf.ln(2)

    nombres = {
        "comprension": "Comprension lectora",
        "morfologia": "Morfologia",
        "semantica": "Semantica",
        "literatura": "Literatura",
        "sintaxis": "Sintaxis",
    }

    for clave, nombre_comp in nombres.items():

        valor = resultados.get(
            clave,
            0
        )

        try:
            valor = float(valor)
        except (
            TypeError,
            ValueError
        ):
            valor = 0

        pdf.set_font(
            "Arial",
            "",
            10
        )

        pdf.cell(
            0,
            7,
            limpiar_texto(
                f"{nombre_comp}: {valor:.2f}/10"
            ),
            ln=True
        )

    # ======================================================
    # NOTA
    # ======================================================

    pdf.ln(4)

    try:
        nota_inicial_num = float(
            nota_inicial
        )
    except (
        TypeError,
        ValueError
    ):
        nota_inicial_num = 0

    try:
        descuento_num = float(
            descuento_ortografia
        )
    except (
        TypeError,
        ValueError
    ):
        descuento_num = 0

    try:
        nota_final_num = float(
            nota_final
        )
    except (
        TypeError,
        ValueError
    ):
        nota_final_num = 0

    pdf.set_font(
        "Arial",
        "B",
        13
    )

    pdf.cell(
        0,
        9,
        limpiar_texto(
            f"Nota inicial: {nota_inicial_num:.2f}/10"
        ),
        ln=True
    )

    pdf.cell(
        0,
        9,
        limpiar_texto(
            f"Descuento de ortografia: -{descuento_num:.2f} puntos"
        ),
        ln=True
    )

    pdf.cell(
        0,
        9,
        limpiar_texto(
            f"Nota final: {nota_final_num:.2f}/10"
        ),
        ln=True
    )

    # ======================================================
    # ORTOGRAFIA
    # ======================================================

    pdf.ln(3)

    try:
        faltas_num = int(
            faltas_ortografia
        )
    except (
        TypeError,
        ValueError
    ):
        faltas_num = 0

    escribir_bloque(
        pdf,
        "Correccion ortografica",
        (
            f"Faltas detectadas: {faltas_num}\n"
            f"Descuento aplicado: "
            f"-{descuento_num:.2f} puntos"
        )
    )

    # ======================================================
    # RESPUESTAS DEL ALUMNO
    # ======================================================

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
            limpiar_texto(
                "RESPUESTAS DEL ALUMNO"
            ),
            ln=True
        )

        pdf.ln(3)

        # Si por algún motivo llegan respuestas
        # anidadas, también las convertimos en texto.

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

            if isinstance(
                respuesta,
                dict
            ):
                partes = []

                for clave, valor in respuesta.items():
                    partes.append(
                        f"{clave}: {valor}"
                    )

                texto_respuesta = "\n".join(
                    partes
                )

            else:
                texto_respuesta = str(
                    respuesta
                )

            # Evitar respuestas gigantes
            if len(texto_respuesta) > 1000:
                texto_respuesta = (
                    texto_respuesta[:1000]
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

    # ======================================================
    # GUARDAR
    # ======================================================

    carpeta = "pdf_resultados"

    os.makedirs(
        carpeta,
        exist_ok=True
    )

    nombre_archivo = (
        "resultado_"
        + nombre_seguro(nombre)
        + "_"
        + nombre_seguro(curso)
        + ".pdf"
    )

    ruta = os.path.abspath(
        os.path.join(
            carpeta,
            nombre_archivo
        )
    )

    pdf.output(ruta)

    return ruta
```
