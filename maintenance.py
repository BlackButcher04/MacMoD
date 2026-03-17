import streamlit as st
import mysql.connector
from datetime import datetime
from fpdf import FPDF

# --- 1. Database Connection ---
try:
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="macmod_db")
    cursor = conn.cursor()
except mysql.connector.Error as err:
    st.error(f"Database Connection Error: {err}")
    st.stop()

# --- 2. The PDF Generation Engine ---
def generate_work_order_pdf(mac_name, mac_serial, job_desc, priority):
    pdf = FPDF()
    pdf.add_page()
    
    # Define colors (matching the mint green from your screenshot)
    pdf.set_fill_color(178, 235, 229) 
    pdf.set_draw_color(150, 150, 150) # Soft grey borders
    
    # --- HEADER ---
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(20, 30, 60) # Dark navy blue text
    pdf.cell(120, 15, "MacMoD Work Order", ln=0)
    pdf.set_font("Arial", '', 16)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(70, 15, "MAINTENANCE", ln=1, align='R')
    pdf.ln(5)
    
    # --- TOP GRID (Asset Details) ---
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 10)
    
    # Row 1
    pdf.cell(40, 10, "Machine Name", border=1, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(80, 10, f" {mac_name}", border=1)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(35, 10, "Date Issued", border=1, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(35, 10, f" {datetime.now().strftime('%Y-%m-%d')}", border=1, ln=1)
    
    # Row 2
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 10, "Serial Number", border=1, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(80, 10, f" {mac_serial}", border=1)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(35, 10, "Priority Level", border=1, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(35, 10, f" {priority}", border=1, ln=1)
    
    pdf.ln(5)
    
    # --- JOB DESCRIPTION BLOCK ---
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 20, "Job Description", border=1, fill=True)
    pdf.set_font("Arial", '', 10)
    # MultiCell allows text to wrap if the description is long
    x, y = pdf.get_x(), pdf.get_y()
    pdf.multi_cell(150, 20, f" {job_desc}", border=1)
    pdf.set_xy(x, y + 20) # Reset position below the multicell
    
    pdf.ln(5)
    
    # --- LABOR TABLE (Blank rows for technician to fill) ---
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 8, "LABOR DESCRIPTION", border=1, fill=True)
    pdf.cell(50, 8, "HOURS", border=1, align='C', fill=True, ln=1)
    
    pdf.set_font("Arial", '', 10)
    for _ in range(4): # 4 blank rows
        pdf.cell(140, 8, "", border=1)
        pdf.cell(50, 8, "", border=1, ln=1)
        
    pdf.ln(5)
    
    # --- MATERIAL TABLE (Blank rows for technician to fill) ---
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 8, "MATERIAL DESCRIPTION", border=1, fill=True)
    pdf.cell(50, 8, "QUANTITY", border=1, align='C', fill=True, ln=1)
    
    pdf.set_font("Arial", '', 10)
    for _ in range(4): # 4 blank rows
        pdf.cell(140, 8, "", border=1)
        pdf.cell(50, 8, "", border=1, ln=1)
        
    pdf.ln(15)
    
    # --- SIGNATURES ---
    pdf.cell(90, 8, "Technician Signature: ______________________", ln=0)
    pdf.cell(100, 8, "Manager Approval: ______________________", ln=1)

    return pdf.output(dest='S').encode('latin-1')


# --- 3. Streamlit UI ---
st.markdown('<div style="margin-bottom:1.5rem;"><div class="macmod-title">Maintenance Dispatch</div><div class="macmod-subtitle">Generate official work orders for flagged machines.</div></div>', unsafe_allow_html=True)

# Fetch machines from DB to populate the dropdown
try:
    cursor.execute("SELECT machinesID, machinesName, serial_number, status_use FROM machines")
    machine_list = cursor.fetchall()
except mysql.connector.Error as err:
    st.error(f"Error fetching machines: {err}")
    machine_list = []

if machine_list:
    # Build a dictionary to easily get machine details from the selected name
    mac_dict = {f"{m[1]} ({m[2]})": {"id": m[0], "name": m[1], "serial": m[2]} for m in machine_list}
    
    with st.container(border=True):
        st.markdown('<div style="font-size:16px; font-weight:700; color:#0f172a; margin-bottom:1rem;">Work Order Configuration</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            selected_mac_label = st.selectbox("Target Machine", options=list(mac_dict.keys()))
            priority = st.selectbox("Priority Level", ["Routine", "High", "CRITICAL"])
            
        with col2:
            job_description = st.text_area("Job Description / AI Findings", placeholder="e.g., AI model flagged high acoustic noise and vibration. Inspect bearings.")

        # Grab the exact details of the selected machine
        target_mac = mac_dict[selected_mac_label]

        st.divider()
        
        # Generate the PDF in the background
        pdf_bytes = generate_work_order_pdf(target_mac["name"], target_mac["serial"], job_description, priority)
        
        # The Download Button
        st.download_button(
            label="📄 Generate & Download PDF Work Order",
            data=pdf_bytes,
            file_name=f"WorkOrder_{target_mac['name']}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
else:
    st.info("No machines available in the database to generate work orders.")