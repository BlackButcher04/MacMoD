import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

st.set_page_config(page_title="MacMoD Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)

st.markdown("""<style>
[data-testid="stSidebar"]::-webkit-scrollbar { display: none; }
[data-testid="stSidebar"] { scrollbar-width: none; -ms-overflow-style: none; }
.block-container { padding-top: 3rem; padding-bottom: 2rem; }

div[data-testid="stButton"] button[kind="secondary"] {
    display: flex !important; justify-content: flex-start !important; padding-left: 20px !important;
    border-radius: 8px !important; font-weight: 600 !important; color: #111827 !important; border-color: #e5e7eb !important;
}
div[data-testid="stButton"] button[kind="secondary"]:hover { background-color: #f8fafc !important; border-color: #cbd5e1 !important; }
</style>""", unsafe_allow_html=True)


@st.cache_data
def get_live_factory_snapshot():
    columns = ['unit_number', 'time_cycles', 'setting_1', 'setting_2', 'setting_3']
    columns += [f'sensor_{i}' for i in range(1, 22)]
    url = 'https://raw.githubusercontent.com/hankroark/Turbofan-Engine-Degradation/master/CMAPSSData/train_FD001.txt' 
    df = pd.read_csv(url, sep='\s+', header=None, names=columns)
    
    max_cycles = df.groupby('unit_number')['time_cycles'].max().reset_index()
    max_cycles.columns = ['unit_number', 'max_cycle']
    df = pd.merge(df, max_cycles, on='unit_number', how='left')
    
    df['RUL'] = df['max_cycle'] - df['time_cycles']
    
    current_cycle_sim = 160
    active_machines = df[df['time_cycles'] == current_cycle_sim].copy()
    
    conditions = [
        (active_machines['RUL'] > 60),
        (active_machines['RUL'] > 15) & (active_machines['RUL'] <= 60),
        (active_machines['RUL'] <= 15)
    ]
    choices = ['Healthy', 'Warning', 'Critical']
    active_machines['Status'] = np.select(conditions, choices, default='Unknown')
    
    active_machines['Machine_Name'] = 'Turbofan Unit #' + active_machines['unit_number'].astype(str)
    active_machines['Type'] = np.where(active_machines['unit_number'] % 2 == 0, 'Heavy Duty', 'Standard')
    active_machines['Health_Pct'] = (active_machines['RUL'] / active_machines['max_cycle'] * 100).astype(int)
    
    return active_machines

with st.spinner("🔄 Connecting to Factory Sensors & Loading AI Models..."):
    factory_data = get_live_factory_snapshot()

active_count = len(factory_data)
sensor_count = active_count * 21
warning_count = len(factory_data[factory_data['Status'] == 'Warning'])
critical_count = len(factory_data[factory_data['Status'] == 'Critical'])


@st.dialog("🗄️ Upload Factory Raw Data")
def dialog_upload_data():
    st.write("Upload telemetry CSV or Excel files from your local directory.")
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])
    if st.button("Submit", type="primary"):
        if uploaded_file:
            st.success(f"File '{uploaded_file.name}' uploaded successfully!")
            time.sleep(1.5); st.rerun()
        else:
            st.error("❗ Please select a file first.")

@st.dialog("🖲️ Upload Machine & Spare Parts")
def dialog_upload_machine():
    st.write("Register a new machine asset and map telemetry sensors to its spare parts.")
    error_placeholder = st.empty()
    st.markdown("**Machine Information**")
    col1, col2 = st.columns(2)
    mac_name = col1.text_input("Machine Name", placeholder="e.g. Robot Arm X1")
    mac_type = col2.text_input("Machine Type", placeholder="e.g. Assembly")
    st.text_input("Machine-Level Sensors", placeholder="Add sensor ID (e.g. S11)")
    st.divider()
    st.markdown("**Spare Parts Subsystem**")
    st.text_input("Part Name", placeholder="e.g. Servo Motor")
    st.text_input("Sensors for new part (Optional)", placeholder="Add sensor (e.g. TEMP_01)")
    _, col_btn = st.columns([2, 1])
    if col_btn.button("Confirm & Upload", type="primary", use_container_width=True):
        if not mac_name or not mac_type:
            error_placeholder.error("❗ Please provide machine name and type.")
        else:
            st.success(f"Machine '{mac_name}' registered successfully!")
            time.sleep(1.5); st.rerun()

@st.dialog("🔧 Schedule Maintenance")
def dialog_schedule():
    st.write("Create a new predictive maintenance task.")
    desc = st.text_input("Task Description", placeholder="e.g. Replace Bearings")
    date = st.date_input("Start Date")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)
    _, col_btn = st.columns([2, 1])
    if col_btn.button("Schedule", type="primary", use_container_width=True):
        if not desc:
            st.error("❗ Please provide a task description.")
        else:
            st.success(f"Task scheduled for {date} with {priority} priority.")
            time.sleep(1.5); st.rerun()

@st.dialog("⚙️ Adjust Anomaly Thresholds")
def dialog_thresholds():
    st.write("Configure AI detection sensitivities for predictive maintenance.")
    rul = st.number_input("Alert Threshold (RUL Cycles)", value=12, step=1)
    zscore = st.number_input("Anomaly Z-Score", value=3.5, step=0.1)
    _, col_btn = st.columns([2, 1])
    if col_btn.button("Save Changes", type="primary", use_container_width=True):
        st.success(f"Thresholds updated! RUL: {rul}, Z-Score: {zscore}")
        time.sleep(1.5); st.rerun()

@st.dialog("📅 Facility Maintenance Calendar")
def dialog_calendar():
    st.write("Overview of scheduled maintenance and facility events.")
    selected_date = st.date_input("Select a date to view events:", value=datetime.today())
    
    st.divider()
    st.markdown(f"**Agenda for {selected_date.strftime('%Y-%m-%d')}**")
    
    st.info("🔧 **10:00 AM** - Preventive maintenance on CNC Milling Alpha")
    st.error("🚨 **01:30 PM** - Urgent inspection for Hydraulic Press Beta (RUL Critical)")
    st.success("✅ **05:00 PM** - End of shift system backup")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Close Calendar", use_container_width=True):
        st.rerun()


st.sidebar.markdown("<h2 style='margin-bottom: 0px;'>〽️ MacMoD</h2><span style='color: #38bdf8; font-size: 14px;'>Predictive Maintenance</span>", unsafe_allow_html=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)
selected_page = st.sidebar.radio(" ", ["🏠 Dashboard", "🖥️ Machines", "🔧 Maintenance", "📊 Reports", "⚙️ Settings"], label_visibility="collapsed")
st.sidebar.markdown('<div style="height: 25vh;"></div>', unsafe_allow_html=True)
st.sidebar.divider()

if 'username' not in st.session_state: st.session_state.username = 'aaaa'
if 'job_title' not in st.session_state: st.session_state.job_title = 'tech'
first_letter = st.session_state.username[0].upper()

st.sidebar.markdown(f"""<div style="display: flex; align-items: center; margin-bottom: 15px;">
<div style="background-color: #1d4ed8; color: white; width: 42px; height: 42px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 18px; font-weight: bold; margin-right: 15px;">{first_letter}</div>
<div style="line-height: 1.2;">
<div style="color: #111827; font-size: 16px; font-weight: bold;">{st.session_state.username}</div>
<div style="color: #3b82f6; font-size: 14px; font-weight: 500;">{st.session_state.job_title}</div>
</div></div>""", unsafe_allow_html=True)

if st.sidebar.button("[\u2192] Logout", use_container_width=True):
    st.sidebar.success("成功登出！")


ui_css = """<style>
.metric-card { background-color: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05); height: 100%; }
.metric-text p { margin: 0; font-size: 14px; color: #6b7280; font-weight: 500; } .metric-text h2 { margin: 0; font-size: 28px; color: #111827; font-weight: 700; padding-top: 5px; }
.metric-icon { width: 48px; height: 48px; border-radius: 10px; display: flex; justify-content: center; align-items: center; font-size: 22px; }
.icon-blue { background-color: #eff6ff; color: #3b82f6; } .icon-green { background-color: #f0fdf4; color: #22c55e; } .icon-orange { background-color: #fff7ed; color: #f97316; } .icon-red { background-color: #fef2f2; color: #ef4444; } .icon-purple { background-color: #faf5ff; color: #a855f7; }
.panel-card { background-color: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); height: 100%; margin-bottom: 25px; }
.panel-header { margin-bottom: 20px; } .panel-header h3 { margin: 0; font-size: 18px; color: #111827; font-weight: 600; display: flex; align-items: center; gap: 10px; } .panel-header p { margin: 5px 0 0 0; font-size: 14px; color: #6b7280; }
.machine-item { border: 1px solid #e5e7eb; border-radius: 10px; padding: 15px 20px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }
.machine-title-row { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; } .machine-title-row h4 { margin: 0; font-size: 16px; color: #111827; font-weight: 600; }
.badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; } .badge-warning { background-color: #fef9c3; color: #854d0e; } .badge-critical { background-color: #fee2e2; color: #991b1b; } .badge-healthy { background-color: #dcfce7; color: #166534; }
.machine-stats p { margin: 0 0 3px 0; font-size: 14px; color: #4b5563; } .machine-stats .sub-stats { font-size: 12px; color: #9ca3af; }
.machine-type { text-align: right; } .machine-type span { font-size: 12px; color: #6b7280; } .machine-type strong { display: block; font-size: 14px; color: #4b5563; font-weight: 500; margin-top: 2px;}
.log-item { border: 1px solid #e5e7eb; border-radius: 10px; padding: 15px 20px; margin-bottom: 12px; display: flex; align-items: flex-start; gap: 15px; }
.log-icon { font-size: 18px; margin-top: 2px; } .log-icon-gray { color: #6b7280; } .log-icon-red { color: #ef4444; } .log-icon-orange { color: #f97316; } .log-icon-green { color: #22c55e; }
.log-content { display: flex; flex-direction: column; } .log-title { margin: 0; font-size: 15px; font-weight: 600; color: #111827; } .log-meta { margin: 4px 0 0 0; font-size: 13px; color: #6b7280; }
.empty-state { display: flex; justify-content: center; align-items: center; height: 280px; color: #9ca3af; font-size: 15px; text-align: center; }
.perf-container { display: flex; justify-content: space-around; align-items: center; padding-top: 15px; }
.perf-item { display: flex; flex-direction: column; align-items: center; text-align: center; } .perf-item h2 { margin: 15px 0 5px 0; font-size: 24px; color: #111827; font-weight: 700; } .perf-item p { margin: 0; font-size: 14px; color: #6b7280; }
</style>"""

if selected_page == "🏠 Dashboard":
    st.markdown(ui_css, unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='color: #111827; margin-bottom: 5px;'>Welcome back, {st.session_state.username}!</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6b7280; font-size: 16px; margin-bottom: 30px;'>Here is the real-time health overview of your industrial assets.</p>", unsafe_allow_html=True)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1: st.markdown(f'<div class="metric-card"><div class="metric-text"><p>Active Machines</p><h2>{active_count}</h2></div><div class="metric-icon icon-blue"><i class="fa-solid fa-server"></i></div></div>', unsafe_allow_html=True)
    with col_m2: st.markdown(f'<div class="metric-card"><div class="metric-text"><p>Sensors Monitored</p><h2>{sensor_count}</h2></div><div class="metric-icon icon-green"><i class="fa-solid fa-microchip"></i></div></div>', unsafe_allow_html=True)
    with col_m3: st.markdown(f'<div class="metric-card"><div class="metric-text"><p>Pending Maintenance</p><h2>{warning_count}</h2></div><div class="metric-icon icon-orange"><i class="fa-solid fa-wrench"></i></div></div>', unsafe_allow_html=True)
    with col_m4: st.markdown(f'<div class="metric-card"><div class="metric-text"><p>Critical Alerts</p><h2>{critical_count}</h2></div><div class="metric-icon icon-red"><i class="fa-solid fa-triangle-exclamation"></i></div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.6, 1])
    with col_left:
        st.markdown('<div class="panel-card" style="margin-bottom: 0;">', unsafe_allow_html=True)
        st.markdown('<div class="panel-header"><h3><i class="fa-solid fa-chart-line" style="color: #4b5563;"></i> Asset Health & RUL</h3><p>Real-time Remaining Useful Life estimates</p></div>', unsafe_allow_html=True)
        top_3_machines = factory_data.sort_values('RUL').head(3)
        for index, row in top_3_machines.iterrows():
            if row['Status'] == 'Critical': badge_class = 'badge-critical'
            elif row['Status'] == 'Warning': badge_class = 'badge-warning'
            else: badge_class = 'badge-healthy'
            html_snippet = f"""<div class="machine-item"><div><div class="machine-title-row"><h4>{row['Machine_Name']}</h4><span class="badge {badge_class}">{row['Status']}</span></div><div class="machine-stats"><p>Estimated RUL: <strong>{row['RUL']} cycles</strong></p><p class="sub-stats">Health: {row['Health_Pct']}% | Spare parts: {row['unit_number'] % 4 + 1}</p></div></div><div class="machine-type"><span>Type</span><strong>{row['Type']}</strong></div></div>"""
            st.markdown(html_snippet, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        with st.container(border=True):
            st.markdown('<div style="margin-bottom: 15px;"><h3 style="margin: 0; font-size: 18px; color: #111827; font-weight: 600;"><i class="fa-solid fa-plus" style="color: #4b5563; margin-right: 10px;"></i>Quick Actions</h3><p style="margin: 5px 0 0 0; font-size: 14px; color: #6b7280;">Common management tasks</p></div>', unsafe_allow_html=True)
            if st.button("🗄️   Upload Factory Raw Data", use_container_width=True): dialog_upload_data()
            if st.button("🖲️   Upload Machine & Spare Parts", use_container_width=True): dialog_upload_machine()
            if st.button("🔧   Schedule Maintenance", use_container_width=True): dialog_schedule()
            if st.button("⚙️   Adjust Anomaly Thresholds", use_container_width=True): dialog_thresholds()
            

            if st.button("📅   View Facility Calendar", use_container_width=True): dialog_calendar()
            
    st.markdown("<br>", unsafe_allow_html=True)

    col_log, col_sched = st.columns(2)
    with col_log:
        st.markdown(f"""<div class="panel-card" style="margin-bottom: 0;">
<div class="panel-header"><h3><i class="fa-regular fa-clock" style="color: #4b5563;"></i> System Logs</h3><p>Recent anomaly detections and events</p></div>
<div class="log-item"><div class="log-icon log-icon-gray"><i class="fa-regular fa-circle-user"></i></div><div class="log-content"><p class="log-title">Registered new MacMoD account</p><p class="log-meta">Just now by {st.session_state.username}</p></div></div>
<div class="log-item"><div class="log-icon log-icon-red"><i class="fa-solid fa-triangle-exclamation"></i></div><div class="log-content"><p class="log-title">Turbofan Unit #3 crossed vibration threshold</p><p class="log-meta">2 hours ago by System • Heavy Duty</p></div></div>
<div class="log-item"><div class="log-icon log-icon-orange"><i class="fa-solid fa-wrench"></i></div><div class="log-content"><p class="log-title">Scheduled predictive maintenance</p><p class="log-meta">4 hours ago by Factory Manager • Turbofan Unit #16</p></div></div>
<div class="log-item" style="margin-bottom: 0;"><div class="log-icon log-icon-green"><i class="fa-solid fa-database"></i></div><div class="log-content"><p class="log-title">RUL estimation model retrained (RMSE: 1.2)</p><p class="log-meta">2 days ago by System • System Core</p></div></div>
</div>""", unsafe_allow_html=True)

    with col_sched:
        st.markdown("""<div class="panel-card" style="margin-bottom: 0;">
<div class="panel-header"><h3><i class="fa-regular fa-calendar-check" style="color: #4b5563;"></i> Scheduled Maintenance</h3><p>Upcoming predictive repairs</p></div>
<div class="empty-state">No maintenance scheduled. All systems nominal.</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""<div class="panel-card">
<div class="panel-header"><h3><i class="fa-solid fa-chart-line" style="color: #4b5563;"></i> Model Performance & Impact</h3><p>Time-series prediction metrics and ROI</p></div>
<div class="perf-container">
    <div class="perf-item"><div class="metric-icon icon-blue"><i class="fa-solid fa-database"></i></div><h2>23.4k</h2><p>Predictions</p></div>
    <div class="perf-item"><div class="metric-icon icon-green"><i class="fa-regular fa-circle-check"></i></div><h2>94.2%</h2><p>Accuracy</p></div>
    <div class="perf-item"><div class="metric-icon icon-purple"><i class="fa-solid fa-chart-simple"></i></div><h2>1.4</h2><p>Avg RMSE</p></div>
    <div class="perf-item"><div class="metric-icon icon-orange"><i class="fa-solid fa-triangle-exclamation"></i></div><h2>18</h2><p>Anomalies</p></div>
    <div class="perf-item"><div class="metric-icon icon-red"><i class="fa-solid fa-arrow-trend-down"></i></div><h2>5</h2><p>Prevented Failures</p></div>
</div>
</div>""", unsafe_allow_html=True)

elif selected_page in ["🖥️ Machines", "🔧 Maintenance", "📊 Reports", "⚙️ Settings"]:
    st.title(selected_page)