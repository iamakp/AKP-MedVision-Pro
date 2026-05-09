from fpdf import FPDF
import datetime
import os

class ProfessionalPDF(FPDF):
    def add_watermark(self):
        if os.path.exists("logo.jpg"):
            # 0.05 opacity matlab bahut hi halka watermark (sirf 5% visibility)
            with self.local_context(fill_opacity=0.05):
                # Center placement
                self.image("logo.jpg", x=45, y=90, w=120)

def generate_professional_pdf(p_name, p_id, p_age, p_gender, mode, result, confidence, filename="report.pdf"):
    """
    Generates a professional medical report with SMVDU branding and patient details.
    """
    pdf = ProfessionalPDF()
    pdf.add_page()
    
    # 1. Background faded watermark
    pdf.add_watermark()
    
    # --- 2. HEADER SECTION (Solid Color) ---
    pdf.set_fill_color(26, 95, 122) # Dark Medical Blue
    pdf.rect(0, 0, 210, 45, 'F')
    
    # Logo in header
    if os.path.exists("logo.jpg"):
        pdf.image("logo.jpg", x=10, y=8, w=25) 
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 20)
    pdf.set_xy(40, 12)
    # Header title wapas SMVDU kar diya gaya hai
    pdf.cell(0, 10, "SMVDU CLINICAL AI LAB", ln=True)
    
    pdf.set_font("Arial", '', 10)
    pdf.set_x(40)
    pdf.cell(0, 5, "Shri Mata Vaishno Devi University, Katra", ln=True)
    pdf.ln(25)

    # --- 3. PATIENT & RESULT SECTION ---
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "MEDICAL DIAGNOSTIC ANALYSIS", ln=True, align='C')
    pdf.ln(5)

    # Table data placement (Including Gender)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(60, 10, "Patient Name", 1); pdf.cell(130, 10, str(p_name), 1, 1)
    pdf.cell(60, 10, "Patient ID", 1); pdf.cell(130, 10, str(p_id), 1, 1)
    pdf.cell(60, 10, "Gender", 1); pdf.cell(130, 10, str(p_gender), 1, 1)
    pdf.cell(60, 10, "Age / Mode", 1); pdf.cell(130, 10, f"{p_age}Y / {mode}", 1, 1)
    pdf.cell(60, 10, "Report Date", 1); pdf.cell(130, 10, str(datetime.date.today()), 1, 1)
    pdf.ln(10)

    # Result logic (Color coding)
    is_normal = "NORMAL" in result.upper() or "NO TUMOR" in result.upper()
    pdf.set_font("Arial", 'B', 16)
    if is_normal:
        pdf.set_text_color(39, 174, 96) # Green for Normal
    else:
        pdf.set_text_color(192, 57, 43) # Red for Detected
    
    pdf.cell(0, 20, f"DIAGNOSIS: {result}", 1, 1, 'C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 10, f"AI Confidence Score: {confidence:.2f}%", 0, 1, 'C')

    # --- 4. FOOTER ---
    pdf.set_y(-25)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, "Disclaimer: This is an AI-generated research report. Clinical correlation by a certified medical professional is required.", align='C')
    
    pdf.set_y(-15)
    pdf.cell(0, 10, f"Developed by: Abhishek Kumar Prajapati (23BCS006) | {datetime.date.today()}", 0, 0, 'C')

    pdf.output(filename)
    return filename