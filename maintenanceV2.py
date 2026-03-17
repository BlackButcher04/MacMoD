import streamlit as st
import mysql.connector
from datetime import datetime
from fpdf import FPDF

# --- 1. Apply Your Team's Custom Design ---
def apply_enterprise_theme():
    st.markdown("""
        <style>
        html, body, [class*="ViewBlock"], .main { background-color: #f8fafc !important; color: #0f172a !important; font-family: system-ui, -apple-system, sans-serif; font-size: 14px; }
        .macmod-title { font-size: 28px !important; font-weight: 800 !important; color: #0f172a !important; margin-bottom: 0.25rem !important; line-height: 1.2 !important; }
        .macmod-subtitle { font-size: 15px !important; color: #64748b !important; margin-bottom: 1.5rem !important; }
        [data-testid="stVerticalBlockBorderWrapper"] { background-color: #ffffff !important; border-radius: 12px !important; border: 1px solid #e2e8f0 !important; box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important; padding: 1.25rem 1.5rem !important; margin-bottom: 1rem !important; }
        div.stButton > button { border-radius: 0.5rem; border: 1px solid #2563eb !important; background: #2563eb !important; color: #ffffff !important; padding: 0.35rem 0.9rem; font-weight: 500; box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05); transition: all 0.2s; }
        div.stButton > button:hover { background: #1d4ed8 !important; border-color: #1d4ed8 !important; }
        .block-container { padding-top: 4rem !important; padding-bottom: 2rem !important; padding-left: 2rem !important; padding-right: 2rem !important; }
        </style>
    """, unsafe_allow_html=True)

apply_enterprise_theme()

# --- 2. Database Connection ---
try:
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="macmod_db")
    cursor = conn.cursor()
except mysql.connector.Error as err:
    st.error(f"Database Connection Error: {err}")
    st.stop()

# --- 3. PDF Generator Function ---
def generate_work_order_pdf(mac_name, mac_serial, job_desc, priority):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(241, 245, 249) 
    pdf.set_draw_color(150, 150, 150) 
    
    # Header
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(20, 30, 60) 
    pdf.cell(120, 15, "MacMoD Job Order", ln=0)
    pdf.set_font("Arial", '', 16)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(70, 15, "MAINTENANCE", ln=1, align='R')
    pdf.ln(5)
    
    # Top Grid
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 10, "Machine Name", border=1, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(80, 10, f" {mac_name}", border=1)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(35, 10, "Date Issued", border=1, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(35, 10, f" {datetime.now().strftime('%Y-%m-%d')}", border=1, ln=1)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 10, "Serial Number", border=1, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(80, 10, f" {mac_serial}", border=1)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(35, 10, "Priority Level", border=1, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(35, 10, f" {priority}", border=1, ln=1)
    pdf.ln(5)
    
    # Job Description
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 20, "Job Description", border=1, fill=True)
    pdf.set_font("Arial", '', 10)
    x, y = pdf.get_x(), pdf.get_y()
    pdf.multi_cell(150, 20, f" {job_desc}", border=1)
    pdf.set_xy(x, y + 20) 
    pdf.ln(5)
    
    # Blank Tables for Technicians
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 8, "LABOR DESCRIPTION", border=1, fill=True)
    pdf.cell(50, 8, "HOURS", border=1, align='C', fill=True, ln=1)
    for _ in range(4):
        pdf.cell(140, 8, "", border=1)
        pdf.cell(50, 8, "", border=1, ln=1)
    pdf.ln(15)
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(90, 8, "Technician Signature: ______________________", ln=0)
    pdf.cell(100, 8, "Manager Approval: ______________________", ln=1)

    return pdf.output(dest='S').encode('latin-1')

# --- 4. Streamlit UI ---

# Initialize a session state to control the two-step workflow
if "work_order_ready" not in st.session_state:
    st.session_state.work_order_ready = False
    st.session_state.wo_pdf_bytes = None
    st.session_state.wo_filename = ""
    st.session_state.wo_message = ""

st.markdown('<div style="margin-bottom:1.5rem;"><div class="macmod-title">Machines Maintenance</div><div class="macmod-subtitle">Review AI condition logs and schedule official work orders.</div></div>', unsafe_allow_html=True)

# Smart Query: Get ACTIVE machines and join their LATEST condition status
try:
    smart_query = """
        SELECT m.machinesID, m.machinesName, m.serial_number, c.machines_status
        FROM machines m
        LEFT JOIN (
            SELECT machinesID, machines_status
            FROM conditions_log
            WHERE (machinesID, time_update) IN (
                SELECT machinesID, MAX(time_update) FROM conditions_log GROUP BY machinesID
            )
        ) c ON m.machinesID = c.machinesID
        WHERE m.status_use = 'ACTIVE'
    """
    cursor.execute(smart_query)
    machine_list = cursor.fetchall()
except mysql.connector.Error as err:
    st.error(f"Error fetching machines: {err}")
    machine_list = []

# --- TWO-STEP WORKFLOW UI ---

# STEP 2: The Success & Download Screen (If a repair was just scheduled)
if st.session_state.work_order_ready:
    with st.container(border=True):
        st.success(st.session_state.wo_message)
        st.markdown('<div style="font-size:16px; font-weight:700; color:#0f172a; margin-bottom:1rem;">Work Order Generated Successfully</div>', unsafe_allow_html=True)
        
        act1, act2 = st.columns(2)
        with act1:
            st.download_button(
                label="📄 Download Official Work Order PDF",
                data=st.session_state.wo_pdf_bytes,
                file_name=st.session_state.wo_filename,
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        with act2:
            if st.button("↺ Schedule Another Repair", use_container_width=True):
                st.session_state.work_order_ready = False
                st.rerun()

# STEP 1: The Scheduling Form (Normal view)
elif machine_list:
    mac_dict = {}
    for m in machine_list:
        status = m[3] if m[3] else "NO DATA"
        label = f"{m[1]} ({m[2]}) - Status: {status}"
        mac_dict[label] = {"id": m[0], "name": m[1], "serial": m[2], "ai_status": status}
    
    with st.container(border=True):
        st.markdown('<div style="font-size:16px; font-weight:700; color:#0f172a; margin-bottom:1rem;">Work Order Configuration</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            selected_mac_label = st.selectbox("Select Machine to Repair", options=list(mac_dict.keys()))
            target_mac = mac_dict[selected_mac_label]
            
            default_prio = 2 if target_mac["ai_status"] == "CRITICAL" else (1 if target_mac["ai_status"] == "WARNING" else 0)
            priority = st.selectbox("Priority Level", ["Routine", "High", "CRITICAL"], index=default_prio)
            
        with col2:
            job_description = st.text_area("Job Description / AI Findings", placeholder="Describe the fault flagged by the AI...", height=110)

        st.divider()
        
        st.markdown('<div style="font-size:14px; color:#64748b; margin-bottom:0.5rem;">Dispatch Actions</div>', unsafe_allow_html=True)
        
        if st.button("🔧 Confirm & Schedule Repair", type="primary", use_container_width=True):
            if not job_description:
                st.error("Please provide a job description for the technician.")
            else:
                try:
                    # 1. Update Database
                    insert_sql = "INSERT INTO maintenance_log (machinesID, job_description, priority) VALUES (%s, %s, %s)"
                    cursor.execute(insert_sql, (target_mac["id"], job_description, priority))
                    
                    update_sql = "UPDATE machines SET status_use = 'MAINTENANCE' WHERE machinesID = %s"
                    cursor.execute(update_sql, (target_mac["id"],))
                    
                    conn.commit()
                    
                    # 2. Generate PDF quietly in the background
                    pdf_bytes = generate_work_order_pdf(target_mac["name"], target_mac["serial"], job_description, priority)
                    
                    # 3. Save to Session State and flip the screen
                    st.session_state.wo_pdf_bytes = pdf_bytes
                    st.session_state.wo_filename = f"WorkOrder_{target_mac['serial']}.pdf"
                    st.session_state.wo_message = f"{target_mac['name']} has been pulled offline and logged into the maintenance queue."
                    st.session_state.work_order_ready = True
                    
                    # 4. Refresh to show the success screen
                    st.rerun()
                    
                except mysql.connector.Error as err:
                    conn.rollback()
                    st.error(f"Database error: {err}")
else:
    st.info("No 'ACTIVE' machines available. They might all be under maintenance!")
    
    
# --- 5. The Active Maintenance Queue ---
st.write("") # Add some spacing
st.markdown('<div style="margin-bottom:1rem; margin-top: 2rem;"><div class="macmod-title" style="font-size:22px;">Active Maintenance Queue</div><div class="macmod-subtitle">Work orders currently pending technician action.</div></div>', unsafe_allow_html=True)

try:
    # Query the maintenance logs and JOIN with the machines table to get the names
    queue_sql = """
        SELECT ml.maint_id, m.machinesName, m.serial_number, ml.job_description, ml.priority, ml.date_issued, ml.status, ml.machinesID 
        FROM maintenance_log ml
        JOIN machines m ON ml.machinesID = m.machinesID
        WHERE ml.status = 'PENDING'
        ORDER BY ml.date_issued DESC
    """
    cursor.execute(queue_sql)
    pending_jobs = cursor.fetchall()
    
    if pending_jobs:
        # Create a 2-column grid so the cards don't stretch too wide
        col1, col2 = st.columns(2)
        
        for index, job in enumerate(pending_jobs):
            maint_id = job[0]
            mac_name = job[1]
            mac_serial = job[2]
            job_desc = job[3]
            priority = job[4]
            date_issued = job[5].strftime("%Y-%m-%d %H:%M") if job[5] else "Unknown"
            mac_id = job[7]
            
            # Determine badge color based on priority
            if priority.upper() == "CRITICAL":
                badge = "background:#fee2e2;color:#991b1b;border-color:#fecaca;"
            elif priority.upper() == "HIGH":
                badge = "background:#fef3c7;color:#92400e;border-color:#fde68a;"
            else:
                badge = "background:#dbeafe;color:#1d4ed8;border-color:#bfdbfe;"
            
            # Alternate placing cards in the left and right columns
            with col1 if index % 2 == 0 else col2:
                with st.container(border=True):
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 0.5rem;">
                        <span style="font-size:16px; font-weight:700; color:#0f172a;">{mac_name}</span>
                        <span class="macmod-badge" style="{badge}">{priority.upper()} PRIORITY</span>
                    </div>
                    <div style="font-size:13px; color:#64748b; margin-bottom: 0.8rem;">Serial: {mac_serial} • Issued: {date_issued}</div>
                    <div style="font-size:14px; color:#334155; background:#f8fafc; padding:0.75rem; border-radius:0.5rem; border:1px solid #e2e8f0; margin-bottom:0.8rem;">
                        <strong>Task:</strong> {job_desc}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # --- NEW: Action Buttons Row ---
                    act_btn1, act_btn2 = st.columns(2)
                    
                    with act_btn1:
                        # Generate the PDF specifically for this pending job
                        card_pdf_bytes = generate_work_order_pdf(mac_name, mac_serial, job_desc, priority)
                        st.download_button(
                            label="📄 Print PDF",
                            data=card_pdf_bytes,
                            file_name=f"WorkOrder_{mac_serial}_Reprint.pdf",
                            mime="application/pdf",
                            key=f"reprint_{maint_id}", # Must be unique!
                            use_container_width=True
                        )
                        
                    with act_btn2:
                        # The Completion Button
                        if st.button(f"✅ Complete", key=f"complete_{maint_id}", use_container_width=True):
                            try:
                                # Update the log to COMPLETED
                                cursor.execute("UPDATE maintenance_log SET status = 'COMPLETED' WHERE maint_id = %s", (maint_id,))
                                # Put the machine back to ACTIVE status
                                cursor.execute("UPDATE machines SET status_use = 'ACTIVE' WHERE machinesID = %s", (mac_id,))
                                conn.commit()
                                st.rerun() # Refresh the page immediately
                            except mysql.connector.Error as err:
                                st.error(f"Failed to update status: {err}")
    else:
        st.info("🎉 All clear! There are no pending maintenance work orders.")
        
except mysql.connector.Error as err:
    st.error(f"Error fetching maintenance queue: {err}")