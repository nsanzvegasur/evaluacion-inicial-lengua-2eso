from fpdf import FPDF
from datetime import datetime

# ============================================================

# GENERADOR DE INFORME PDF

# ============================================================

def generar_pdf(nombre, grupo, scores, perfil):

```
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

pdf.ln(5)

# ========================================================
# DATOS
# ========================================================

pdf.set_font(
    "Arial",
    size=11
)

pdf.cell(
    0,
    8,
    f"Nombre y apellidos: {nombre}",
    ln=True
)

pdf.cell(
    0,
    8,
    f"Grupo: {grupo}",
    ln=True
)

pdf.cell(
    0,
    8,
    f"Fecha: {datetime.now().strftime('%d/%m/%Y')}",
    ln=True
)

pdf.ln(8)

# ========================================================
# RESULTADOS
# ========================================================

pdf.set_font(
    "Arial",
    "B",
    13
)

pdf.cell(
    0,
    8,
    "RESULTADOS POR COMPETENCIA",
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

    nombre_competencia = nombres.get(
        clave,
        clave
    )

    pdf.cell(
        0,
        8,
        f"{nombre_competencia}: {valor:.2f}/10",
        ln=True
    )

pdf.ln(5)

# ========================================================
# NOTA GLOBAL
# ========================================================

nota_global = (
    sum(scores.values())
    / len(scores)
)

pdf.set_font(
    "Arial",
    "B",
    14
)

pdf.cell(
    0,
    10,
    f"NOTA GLOBAL: {nota_global:.2f}/10",
    ln=True
)

pdf.ln(5)

# ========================================================
# DIAGNÓSTICO
# ========================================================

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

    # Quitamos emojis para evitar errores de codificacion
    texto = (
        item
        .replace("🔴", "")
        .replace("🟠", "")
        .replace("🟢", "")
    )

    pdf.multi_cell(
        0,
        8,
        "- " + texto.strip()
    )

pdf.ln(5)

# ========================================================
# OBSERVACIÓN
# ========================================================

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

if nota_global < 5:

    observacion = (
        "El alumno necesita refuerzo en varias "
        "competencias basicas de Lengua."
    )

elif nota_global < 7:

    observacion = (
        "El alumno presenta un nivel adecuado, "
        "aunque existen areas concretas de mejora."
    )

else:

    observacion = (
        "El alumno presenta un buen dominio general "
        "de las competencias evaluadas."
    )

pdf.multi_cell(
    0,
    8,
    observacion
)

# ========================================================
# GUARDAR
# ========================================================

nombre_archivo = (
    nombre
    .strip()
    .replace(" ", "_")
    .replace("/", "_")
    .replace("\\", "_")
)

filename = (
    f"informe_{nombre_archivo}.pdf"
)

pdf.output(filename)

return filename
```
