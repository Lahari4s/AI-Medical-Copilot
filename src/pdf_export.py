from fpdf import FPDF

def generate_pdf_report(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    safe_content = content.encode("latin-1", "replace").decode("latin-1")

    for line in safe_content.split("\n"):
        pdf.multi_cell(0, 8, line)

    path = "AI_Healthcare_Report.pdf"
    pdf.output(path)

    return path