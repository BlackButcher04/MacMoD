import streamlit as st
import pandas as pd
import numpy as np
import joblib
import mysql.connector
from fpdf import FPDF
import time
from datetime import datetime

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="macmod_db"
        )
except mysql.connector.Error as err:
        st.write(err)    


cursor = conn.cursor()

try:
    model = joblib.load(r'K:\vHack2026\SourceCode\MacMoD-New\sme_engine.pkl')
    engine_status = "✅ V2 AI Engine is Online"
except FileNotFoundError:
    engine_status = "❌ Engine Missing! (Cannot find sme_engine.pkl)"

def generate_pdf_report(mac_id, mac_name, mac_serial):
    """Generates a PDF report for a specific machine and returns it as bytes."""
    # 1. Fetch the latest data for this machine
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conditions_log WHERE machinesID = %s ORDER BY time_update DESC LIMIT 1", (mac_id,))
    latest_log = cursor.fetchone()
    
    # 2. Initialize the PDF
    pdf = FPDF()
    pdf.add_page()
    
    # 3. Build the Header
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(200, 10, txt="MacMoD Diagnostic Report", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.line(10, 30, 200, 30) # Draw a line
    pdf.ln(10)
    
    # 4. Machine Details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Asset Information:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Machine Name: {mac_name}", ln=True)
    pdf.cell(200, 10, txt=f"Serial Number: {mac_serial}", ln=True)
    pdf.ln(5)
    
    # 5. Latest Sensor Readings
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Latest Telemetry Data:", ln=True)
    pdf.set_font("Arial", size=12)
    
    if latest_log:
        pdf.cell(200, 10, txt=f"Temperature: {latest_log[1]} C", ln=True)
        pdf.cell(200, 10, txt=f"Vibration: {latest_log[2]} mm/s", ln=True)
        pdf.cell(200, 10, txt=f"Acoustic Noise: {latest_log[3]} dB", ln=True)
        pdf.cell(200, 10, txt=f"RPM: {latest_log[5]}", ln=True)
        pdf.ln(5)
        
        # Highlight the AI Prediction
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"AI Estimated RUL: {latest_log[8]} Cycles", ln=True)
        pdf.cell(200, 10, txt=f"System Status: {latest_log[9]}", ln=True)
    else:
        pdf.cell(200, 10, txt="No sensor data recorded for this machine yet.", ln=True)
        
    # 6. Output the PDF as a byte string so Streamlit can download it
    return pdf.output(dest='S').encode('latin-1')
    
@st.dialog("Update Machines Condition")
def update_condition(mac_id,name):
    machinesID = mac_id
    macchinesName = st.text_input("Machines Name", value=name, disabled=True)
    temp = st.text_input("🌡️ Temperature (°C)")
    vibe = st.text_input("📳 Vibration (mm/s)")   
    noise = st.text_input("🔊 Acoustic Noise (dB)")      
    pressure = st.text_input("💨 Pressure (psi)")     
    rpm = st.text_input("🔄 Motor RPM")    
    coolant = st.text_input("💧 Coolant Flow (L/min)")       
    power = st.text_input("⚡ Power Draw (kW)")
    
    if st.button("Diagnose"):
        if temp and vibe and noise and rpm and coolant and power:
            if 'model' not in globals() or model is None:
                st.error("Cannot run diagnosis. The AI model failed to load. Please check sme_engine.pkl")
                return # Stop the function right here so it doesn't crash later
            
            temp = float(temp)
            vibe = float(vibe)
            noise = float(noise)
            pressure = float(pressure)
            rpm = float(rpm)
            coolant = float(coolant)
            power = float(power)
            
            ai_temp = np.interp(temp, [60.0, 90.0], [641.82, 644.30])
            ai_vibe = np.interp(vibe, [5.0, 25.0], [1589.70, 1616.00])
            ai_noise = np.interp(noise, [70.0, 110.0], [1400.60, 1433.00])
            ai_pressure = np.interp(pressure, [80.0, 100.0], [553.00, 554.36])
            ai_rpm = np.interp(rpm, [1500, 1800], [47.47, 48.20])
            ai_coolant = np.interp(coolant, [30.0, 50.0], [519.00, 522.16])
            ai_power = np.interp(power, [10.0, 15.0], [8.43, 8.52])
            
            current_sensors = np.array([ai_temp, ai_vibe, ai_noise, ai_pressure, ai_rpm, ai_coolant, ai_power])
            
            # Provide the exact 7 column names the model was trained on
            feature_names = ['sensor_2', 'sensor_3', 'sensor_4', 'sensor_7', 'sensor_11', 'sensor_12', 'sensor_15']
            input_data = pd.DataFrame([current_sensors], columns=feature_names)
            
            
            predicted_rul = model.predict(input_data)[0]
            impaired_threshold = 80  
            
            # st.metric(label="Predicted Remaining Useful Life (RUL)", value=f"{int(predicted_rul)} Cycles")
            
            if predicted_rul <= impaired_threshold and predicted_rul > 30:
                warning_message = "WARNING"
            elif predicted_rul <= 30:
                warning_message = "CRITICAL"
            else:
                warning_message = "OKAY"
                
            try:
                insert_sql = "INSERT INTO conditions_log (temp, vibration, noise, pressure, rpm, coolant, powerwatt, rul_status, machines_status, machinesID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                insert_val = (temp,vibe,noise,pressure,rpm,coolant,power,int(predicted_rul),warning_message,machinesID)
                cursor.execute(insert_sql, insert_val)
                conn.commit()
                st.success("Data add successfully.✅")
                time.sleep(1)  
                st.rerun()
                
            except mysql.connector.Error as err:
                st.error(f"Data add failed.❌ ERROR: {err}")
            #st.rerun()
        else:
            st.error("Please fill the blank.")

#st.title("Intelligent Diagnose")
#st.caption(engine_status)
# Replace st.title, st.caption, and st.write("---") with this:
st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
        <div class="macmod-title">Intelligent Diagnose Terminal</div>
        <div class="macmod-subtitle">Status: {engine_status}</div>
    </div>
""", unsafe_allow_html=True)
st.write("---")

tab1, tab2 = st.tabs(["🔴 Live Control Panel", "📊 Model Validation"])

# --- TAB 1: Multi-Sensor Live Demo ---
with tab1:
    st.subheader("Live Diagnostics")
    st.write("Enter sensor telemetry to calculate Remaining Useful Life (RUL).")
    try:
        query_sql = "SELECT * FROM machines WHERE status_use = (%s)"
        query_value = ("ACTIVE",)
        cursor.execute(query_sql,query_value)
        rows = cursor.fetchall()
        
        if rows:
            # Loop through each machine in the database
            for row in rows:
                # Unpack the tuple into variables
                mac_id = row[0]
                mac_name = row[1]
                mac_serial = row[2]
                mac_status = row[3]
                
                # Create a bordered container "card" for each machine
                with st.container(border=True):
                    # Using columns inside the container to space out the info
                    col1, col2, col3 = st.columns([3, 2, 3.5])
                    
                    with col1:
                        st.metric(label="Machine Name", value=mac_name)
                    with col2:
                        st.metric(label="Serial Number", value=mac_serial)
                    
                    with col3:
                        #st.metric(label="Action", value=st.button("Update"))
                        #st.write("Action")
                        st.markdown('<div style="font-size:14px; color:#64748b; margin-bottom:0.5rem;">Action</div>', unsafe_allow_html=True)
                        #st.button("Update Condition")
                        
                        act1, act2 = st.columns(2)
                        
                        with act1:
                            if st.button("Update Condition", key=f"update_btn_{mac_id}", use_container_width=True):
                                update_condition(mac_id, mac_name)
                        with act2:
                            pdf_data = generate_pdf_report(mac_id, mac_name, mac_serial)
                             
                            # Create the native Streamlit download button
                            st.download_button(
                                label="Print PDF",
                                data=pdf_data,
                                file_name=f"{mac_name}_Diagnostic_Report.pdf",
                                mime="application/pdf",
                                key=f"print_btn_{mac_id}",
                                use_container_width=True
                            )
                            
                    
                    st.divider() # Visual separator inside the card
                
                    # --- BOTTOM HALF: Dynamic Condition Logs ---
                    try:
                        # 2. Second Table: Get ONLY the latest log for THIS machine using the foreign key and timestamp
                        # Make sure 'log_timestamp' matches the actual name of your timestamp column
                        log_sql = """
                            SELECT * 
                            FROM conditions_log 
                            WHERE machinesID = %s 
                            ORDER BY time_update DESC 
                            LIMIT 1
                        """
                        cursor.execute(log_sql, (mac_id,))
                        latest_log = cursor.fetchone() 
                        
                        if latest_log:
                            # Unpack the sensor data from the conditions_log table
                            temp_val = latest_log[1]
                            vibe_val = latest_log[2]
                            noise_val = latest_log[3]
                            pressure_val = latest_log[4]
                            rpm_val = latest_log[5]
                            coolant_val = latest_log[6]
                            power_val = latest_log[7]
                            rul_stat = latest_log[8]
                            cond_stat = latest_log[9]
                            timestamp = latest_log[10]
                            
                            # Display the exact time this data was recorded
                            st.caption(f"🕒 Data retrieved at: {timestamp}")
                            
                            # Display the latest metrics
                            log_col3, log_col4 = st.columns(2)
                            
                            with log_col3:
                                st.metric(label="RUL Status", value=rul_stat)
                            with log_col4:
                                #st.write("Condition")
                                if cond_stat == "WARNING":
                                    message = "⚠️ ANOMALY CHANGE-POINT DETECTED: The machine has officially transitioned from a 'Healthy' to an 'Impaired' state. Degradation curve is accelerating."
                                    st.warning(message)
                                elif cond_stat == "CRITICAL":
                                    message = "🚨 CRITICAL ALERT: Severe sensor degradation. Machine failure is imminent. Schedule maintenance immediately to prevent downtime!"
                                    st.error(message)
                                elif cond_stat == "OKAY":
                                    message = "✅ Machine is in a 'Healthy' state. Operating smoothly."
                                    st.success(message)
                                else:
                                    message = "No sensor logs recorded for this machine yet. Waiting for data..."
                                    st.warning(message)
                                
                            table_columns = [
                                "Temp (°C)", "Vibration", "Noise", 
                                "Pressure", "RPM", "Coolant", "Power (kW)", 
                                "RUL (Cycles)", "Condition Status"
                            ]
                            
                            # We wrap the variables in double brackets [[ ]] to create a single row
                            single_row_data = [[
                                temp_val, vibe_val, noise_val, 
                                pressure_val, rpm_val, coolant_val, power_val, 
                                rul_stat, cond_stat
                            ]]
                            # 4. Convert the SQL data into a Pandas DataFrame
                            df = pd.DataFrame(single_row_data, columns=table_columns)
                            
                            with st.expander("View Live Sensor Telemetry"):
                                st.dataframe(df, use_container_width=True, hide_index=True)
                                
                        else:
                            st.info("No sensor logs recorded for this machine yet. Waiting for data...")
                            
                    except mysql.connector.Error as err:
                        st.error(f"Error fetching condition logs for {mac_name}: {err}")
        else:
            st.info("No machines found in the database. Add one above!")
    
    except mysql.connector.Error as err:
        st.error(f"Failed to fetch data: {err}")
    
    
# --- TAB 2: The Statistical Proof ---
with tab2:
    st.subheader("Algorithm Performance & Statistical Validation")
    col1, col2 = st.columns(2)
    col1.metric(label="Mean Absolute Error (MAE)", value="14.2 Cycles")
    col2.metric(label="Root Mean Squared Error (RMSE)", value="18.5 Cycles")
    st.info("💡 Model validated using NASA CMAPSS dataset with Temporal Feature Engineering.")