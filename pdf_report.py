from fpdf import FPDF
from datetime import datetime

# =========================
# GENERADOR DE INFORME PDF
# =========================

def generar_pdf(nombre, grupo, scores, perfil):

    pdf = FPDF()
    pdf.add_page()

    # =====================
    # TÍTULO
    # =====================
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INFORME DE EVALUACIÓN INICIAL", ln=True)

    pdf.ln(5)

    # =====================
    # DATOS ALUMNO
    # =====================
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Nombre: {nombre}", ln=True)
    pdf.cell(0, 10, f"Grupo: {grupo}", ln=True)
    pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%Y-%m-%d')}", ln=True)

    pdf.ln(5)

    # =====================
    # NOTAS POR COMPETENCIA
    # =====================
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "RESULTADOS POR COMPETENCIA", ln=True)

    pdf.set_font("Arial", size=11)

    for k, v in scores.items():
        pdf.cell(0, 8, f"{k.capitalize()}: {v}/10", ln=True)

    pdf.ln(5)

    # =====================
    # PERFIL
    # =====================
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "DIAGNÓSTICO PEDAGÓGICO", ln=True)

    pdf.set_font("Arial", size=11)

    for item in perfil:
        pdf.multi_cell(0, 8, f"- {item}")

    pdf.ln(5)

    # =====================
    # OBSERVACIÓN FINAL
    # =====================
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "OBSERVACIÓN GENERAL", ln=True)

    pdf.set_font("Arial", size=11)

    if any("🔴" in p for p in perfil):
        obs = "El alumno necesita refuerzo en competencias básicas de Lengua."
    elif any("🟠" in p for p in perfil):
        obs = "El alumno presenta un nivel medio con áreas de mejora."
    else:
        obs = "El alumno presenta un buen dominio general de las competencias evaluadas."

    pdf.multi_cell(0, 8, obs)

    # =====================
    # GUARDAR PDF
    # =====================
    filename = f"informe_{nombre.replace(' ', '_')}.pdf"
    pdf.output(filename)

    return filename
