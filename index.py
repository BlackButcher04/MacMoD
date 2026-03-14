import streamlit as st
from PIL import Image


# The paths are relative to where container.py is located
dashboard_page = st.Page("dashboard.py", title="Dashboard Overview", icon="🏠")
machines_page = st.Page("machines.py", title="Machines", icon="🎛️")

# Create the navigation menu and run the app
pg = st.navigation([dashboard_page, machines_page], position="hidden")


#img = Image.open(r"K:\vHack2026\SourceCode\macmod.png")
#st.sidebar.image(img)
st.sidebar.title("MacMoD")
st.sidebar.write("Machine Condition Monitoring Dashboard")
st.sidebar.markdown("---") # Adds a clean horizontal divider line

# Manually place the navigation links exactly where you want them
st.sidebar.page_link(dashboard_page, label="Dashboard Overview", icon="🏠")
st.sidebar.page_link(machines_page, label="Machines", icon="🎛️")


pg.run()