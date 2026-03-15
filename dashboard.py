import streamlit as st
import pandas as pd
import numpy as np
import joblib    
    
# You may start your code here
st.title("Dashboard Overview")

row1 = st.columns(4)

with row1[0].container(height=160):
    st.success("Active Machines 🏭")
    st.subheader("12 Machine(s)")
    
with row1[1].container(height=160):
    st.info("Sensors Monitered 📡")
    st.subheader("1002 Sensor(s)")
    
with row1[2].container(height=160):
    st.warning("Pending Maintenance ⚙️")
    st.subheader("1 Pending(s)")
    
with row1[3].container(height=160):
    st.error("Critical Alerts 🚨")
    st.subheader("1 Alert(s)")

st.subheader("Machines' Location")

# 1. Create a dataset with latitude and longitude 
# (Dummy coordinates around Kuala Lumpur for your VM test)
map_data = pd.DataFrame({
    "Machine ID": ["M-01", "M-02", "M-03"],
    "lat": [3.1576, 3.1174, 3.1073],   
    "lon": [101.7116, 101.6775, 101.6067],
    "size": [150, 250, 150],  # Size of the dots
    "color": ["#00ff00", "#ff0000", "#00ff00"] # Green for Online, Red for offline
})

# 2. Display the map!
st.map(map_data, latitude="lat", longitude="lon", size="size", color="color")