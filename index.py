import streamlit as st
from PIL import Image
st.set_page_config(page_title="MacMoD Dashboard", layout="wide")

# The paths are relative to where container.py is located
dashboard_page = st.Page("dashboard.py", title="Dashboard Overview", icon="🏠")
diagnose_page = st.Page("diagnose.py", title="Intelligent Diagnose", icon="🧠")
machines_page = st.Page("machines.py", title="Machines", icon="🎛️")

# Create the navigation menu and run the app
pg = st.navigation([dashboard_page,diagnose_page, machines_page], position="hidden")


#img = Image.open(r"K:\vHack2026\SourceCode\macmod.png")
#st.sidebar.image(img)
st.sidebar.title("MacMoD")
st.sidebar.write("Machine Condition Monitoring Dashboard")
st.sidebar.markdown("---") # Adds a clean horizontal divider line

# place the navigation links exactly where you want them
st.sidebar.page_link(dashboard_page, label="Dashboard Overview", icon="🏠")
st.sidebar.page_link(diagnose_page, label="Intelligent Diagnose", icon="🧠")
st.sidebar.page_link(machines_page, label="Machines", icon="🎛️")


pg.run()