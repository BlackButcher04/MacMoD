import streamlit as st
import pandas as pd
import mysql.connector

# --- 1. Icons & Styling Helpers ---
SVG_ICONS = {
    "server": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>',
    "alert": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
    "cpu": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg>',
    "wrench": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>',
    "pulse": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>'
}

def make_metric(title, val, svg, bg, color):
    return f"""
    <div style="background:#ffffff; border-radius:12px; border:1px solid #e2e8f0; padding:1.25rem; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 3px rgba(0,0,0,0.05); margin-bottom:1rem;">
        <div>
            <div style="font-size:13px; color:#64748b; font-weight:500; margin-bottom:0.4rem;">{title}</div>
            <div class="break-text" style="font-size:26px; font-weight:700; color:#0f172a; line-height:1;">{val}</div>
        </div>
        <div style="width:46px; height:46px; border-radius:10px; background:{bg}; color:{color}; display:flex; align-items:center; justify-content:center; padding:10px; flex-shrink:0;">
            {svg}
        </div>
    </div>
    """

# --- 2. Database Connection ---
try:
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="macmod_db")
    cursor = conn.cursor()
except mysql.connector.Error as err:
    st.error(f"Database Connection Error: {err}")
    st.stop()

# --- 3. Retrieve Live Data Counts ---
active_machines_count = 0
pending_count = 0
critical_count = 0
machine_details = []

try:
    # A. Get total ACTIVE machines
    cursor.execute("SELECT COUNT(*) FROM machines WHERE status_use = 'ACTIVE'")
    active_machines_count = cursor.fetchone()[0]

    # B. Get the LATEST condition status and RUL for EVERY machine using a JOIN
    status_query = """
        SELECT m.machinesName, c.rul_status, c.machines_status
        FROM machines m
        LEFT JOIN (
            SELECT machinesID, rul_status, machines_status, time_update
            FROM conditions_log
            WHERE (machinesID, time_update) IN (
                SELECT machinesID, MAX(time_update) FROM conditions_log GROUP BY machinesID
            )
        ) c ON m.machinesID = c.machinesID
        WHERE m.status_use = 'ACTIVE'
    """
    cursor.execute(status_query)
    machine_details = cursor.fetchall()
    
    # C. Tally up the warnings and critical alerts
    for machine in machine_details:
        status = machine[2]
        if status == "WARNING":
            pending_count += 1
        elif status == "CRITICAL":
            critical_count += 1

except mysql.connector.Error as err:
    st.error(f"Error fetching dashboard data: {err}")

# --- 4. Render the Dashboard ---

# Page Header
st.markdown('<div style="margin-bottom:1.5rem;"><div class="macmod-title">Welcome back to MacMoD!</div><div class="macmod-subtitle">Here is the real-time health overview of your industrial assets.</div></div>', unsafe_allow_html=True)

# 4 Metric Cards (Top Row)
c1, c2, c3, c4 = st.columns(4)
sensors_monitored = active_machines_count * 7 # Since you have 7 sensors per machine

with c1: st.markdown(make_metric("Active Machines", active_machines_count, SVG_ICONS["server"], "#eff6ff", "#2563eb"), unsafe_allow_html=True)
with c2: st.markdown(make_metric("Sensors Monitored", sensors_monitored, SVG_ICONS["cpu"], "#dcfce7", "#16a34a"), unsafe_allow_html=True)
with c3: st.markdown(make_metric("Pending Warnings", pending_count, SVG_ICONS["wrench"], "#ffedd5", "#ea580c"), unsafe_allow_html=True)
with c4: st.markdown(make_metric("Critical Alerts", critical_count, SVG_ICONS["alert"], "#fee2e2", "#dc2626"), unsafe_allow_html=True)

# Main Body Split (Left: Asset Health List | Right: Map)
left_col, right_col = st.columns([2, 1])

with left_col:
    # Start the Asset Health Card
    html = f"""<div class="macmod-card">
                <div class="macmod-title" style="font-size:18px;margin-bottom:0.25rem;display:flex;align-items:center;gap:8px;">
                    <div style="width:20px;height:20px;color:#2563eb;">{SVG_ICONS["pulse"]}</div> Asset Health & RUL
                </div>
                <div class="macmod-subtitle" style="margin-bottom:1rem;">Real-time Remaining Useful Life estimates</div>"""
    
    # Loop through the database results and generate a list item for each machine
    if not machine_details:
        html += "<div style='color:#64748b; font-size:13px;'>No active machines found in database.</div>"
    else:
        for mac in machine_details:
            name = mac[0]
            rul = mac[1] if mac[1] is not None else "N/A"
            status = mac[2] if mac[2] is not None else "NO DATA"
            
            # Determine the color of the badge based on your AI status
            if status == "OKAY":
                badge = "background:#dcfce7;color:#166534;border-color:#bbf7d0;"
            elif status == "WARNING":
                badge = "background:#fef3c7;color:#92400e;border-color:#fde68a;"
            elif status == "CRITICAL":
                badge = "background:#fee2e2;color:#991b1b;border-color:#fecaca;"
            else:
                badge = "background:#f1f5f9;color:#334155;border-color:#e2e8f0;"
                
            html += f"""
            <div style="margin-top:0.6rem;border-radius:0.75rem;border:1px solid #e2e8f0;padding:0.8rem;background:#f8fafc;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.3rem;">
                            <span style="font-size:15px;font-weight:700;color:#0f172a;">{name}</span>
                            <span class="macmod-badge" style="{badge}">{status}</span>
                        </div>
                        <div style="font-size:13px;color:#64748b;">
                            Estimated RUL: <span style="font-weight:700;color:#0f172a;">{rul} cycles</span>
                        </div>
                    </div>
                    <div style="text-align:right;font-size:12px;color:#64748b;">
                        <div style="font-weight:700;color:#0f172a;">Live Status</div>
                        <div style="margin-top:2px;">Monitored</div>
                    </div>
                </div>
            </div>"""
            
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="macmod-title" style="font-size:18px;">Facility Map</div><div class="macmod-subtitle">Asset Geolocation</div>', unsafe_allow_html=True)
    
    # We wrap your map in a container to give it a border to match the rest of the design
    with st.container(border=True):
        map_data = pd.DataFrame({
            "Machine ID": ["M-01", "M-02", "M-03"],
            "lat": [3.1576, 3.1174, 3.1073],   
            "lon": [101.7116, 101.6775, 101.6067],
            "size": [150, 250, 150],  
            "color": ["#00ff00", "#ff0000", "#00ff00"] 
        })
        st.map(map_data, latitude="lat", longitude="lon", size="size", color="color")