import streamlit as st
import pandas as pd

# You may start your code here
st.title("Machines")
st.write("Here's the place you manage your terminal")

st.button("Add New")

row1 = st.columns(1)
row2 = st.columns(1)
row3 = st.columns(1)

# Tile 1: Machine Status
with row1[0].container(height=140):
    st.metric(label="Machine 01", value="90%", delta="New Replace")
    

# Tile 2: Temperature Reading
with row2[0].container(height=140):
    # Using delta_color="inverse" makes a drop in temp green, and a rise in temp red
    st.metric(label="Machine 02", value="87%", delta="-5%")

with row3[0].container(height=140):
    st.metric(label="Machine 02", value="30%", delta="Critical !",delta_arrow="down", delta_color="red")