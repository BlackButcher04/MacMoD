import streamlit as st
import pandas as pd
import numpy as np
import joblib

# Load .pkl file
try:
    model = joblib.load(r'K:\vHack2026\SourceCode\sme_engine.pkl')
    engine_status = "✅ AI Engine Online & Connected"
except FileNotFoundError:
    engine_status = "❌ Engine Missing! (Cannot find sme_engine.pkl)" 

#You may start your code here

st.title("Intelligent Diagnose")

st.subheader("Interactive Pitch Demo: Motor 02 (Conveyor Belt)")
st.write("Drag the slider to simulate months of wear and tear on the machine. Watch how the AI analyzes the shifting sensor data to predict the remaining lifespan.")

# --- 3. The Gas Pedal (Simulating machine degradation) ---
wear_level = st.slider("Machine Wear & Tear (%)", min_value=0, max_value=100, value=0)

# --- 4. The Logic (Translating slider into sensor data) ---
# Healthy sensor readings (0% wear) vs Degraded sensor readings (100% wear)
# We use the exact 7 specific sensors our model was trained on
base_sensors = np.array([641.82, 1589.70, 1400.60, 554.36, 47.47, 522.16, 8.43])
degraded_sensors = np.array([644.30, 1616.00, 1433.00, 551.00, 48.00, 519.00, 8.50])

# Calculate what the sensors look like at the current "wear level"
current_sensors = base_sensors + ((degraded_sensors - base_sensors) * (wear_level / 100.0))

# Package the data exactly how the AI expects it (a Pandas DataFrame with 7 columns)
input_data = pd.DataFrame(
    [current_sensors], 
    columns=['sensor_2', 'sensor_3', 'sensor_4', 'sensor_7', 'sensor_11', 'sensor_12', 'sensor_15']
)

# --- 5. The Prediction & Visual Output ---
if 'model' in locals():
    # The AI looks at the 7 sensor readings and calculates the RUL
    predicted_rul = model.predict(input_data)[0]
    
    # Display the result in a massive metric box
    st.metric(label="Predicted Remaining Useful Life (RUL)", value=f"{int(predicted_rul)} Cycles")
    
    # Interpretability for the factory manager (Hits Hackathon Criteria!)
    if predicted_rul < 30:
        st.error("🚨 CRITICAL ALERT: AI detects severe sensor degradation. Machine failure is imminent. Schedule maintenance immediately to prevent downtime!")
    elif predicted_rul < 80:
        st.warning("⚠️ WARNING: The machine is showing significant signs of wear. Maintenance recommended soon.")
    else:
        st.success("✅ Machine is operating smoothly within safe parameters.")
        
    # Show the raw sensor data so the judges see the numbers shifting
    with st.expander("View Live Sensor Telemetry"):
        st.dataframe(input_data)