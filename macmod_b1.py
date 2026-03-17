import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, date, timedelta
from pathlib import Path
import unittest
import sys

# 尝试导入 FPDF 用于生成 PDF 报表。如果没安装，系统会优雅降级
try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

# ===================== 高清 SVG 矢量图标库 =====================
SVG_ICONS = {
    "cog": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"></path><circle cx="12" cy="12" r="3"></circle></svg>',
    "chart": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>',
    "server": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>',
    "alert": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
    "check": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
    "db": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>',
    "cpu": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg>',
    "wrench": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>',
    "map": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon><line x1="8" y1="2" x2="8" y2="18"></line><line x1="16" y1="6" x2="16" y2="22"></line></svg>',
    "calendar": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>',
    "download": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>',
    "file": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>',
    "pulse": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>',
    "plus": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>',
    "clock": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
    "user": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "mail": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>',
    "briefcase": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/><line x1="8" y1="11" x2="16" y2="11"/></svg>',
    "shield": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "user-plus": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>',
    "key": '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2l-2 2-2-2-2 2-2-2v4a7 7 0 1 0 10 0V2z"/><circle cx="10" cy="10" r="3"/><circle cx="16" cy="16" r="3"/></svg>'
}

# ===================== 真实 RUL 数据库 =====================
REAL_RUL_DATA = {
    "FD001": [112, 98, 69, 82, 91, 93, 91, 95, 111, 96, 97, 124, 95, 107, 83, 84, 50, 28, 87, 16, 57, 111, 113, 20, 145, 119, 66, 97, 90, 115, 8, 48, 106, 7, 11, 19, 21, 50, 142, 28, 18, 10, 59, 109, 114, 47, 135, 92, 21, 79, 114, 29, 26, 97, 137, 15, 103, 37, 114, 100, 21, 54, 72, 28, 128, 14, 77, 8, 121, 94, 118, 50, 131, 126, 113, 10, 34, 107, 63, 90, 8, 9, 137, 58, 118, 89, 116, 115, 136, 28, 38, 20, 85, 55, 128, 137, 82, 59, 117, 20],
    "FD002": [18, 79, 106, 110, 15, 155, 6, 90, 11, 79, 6, 73, 30, 11, 37, 67, 68, 99, 22, 54, 97, 10, 142, 77, 88, 163, 126, 138, 83, 78, 75, 11, 53, 173, 63, 100, 151, 55, 48, 37, 44, 27, 18, 6, 15, 112, 131, 13, 122, 13, 98, 53, 52, 106, 103, 152, 123, 26, 178, 73, 169, 39, 39, 14, 11, 121, 86, 56, 115, 17, 148, 104, 78, 86, 98, 36, 94, 52, 91, 15, 141, 74, 146, 17, 47, 194, 21, 79, 97, 8, 9, 73, 183, 97, 73, 49, 31, 97, 9, 14, 106, 8, 8, 106, 116, 120, 61, 168, 35, 80, 9, 50, 151, 78, 91, 7, 181, 150, 106, 15, 67, 145, 180, 7, 179, 124, 82, 108, 79, 121, 120, 39, 38, 9, 167, 87, 88, 7, 51, 55, 155, 47, 81, 43, 98, 10, 92, 11, 165, 34, 115, 59, 99, 103, 108, 83, 171, 15, 9, 42, 13, 41, 88, 14, 155, 188, 96, 82, 135, 182, 36, 107, 14, 95, 142, 23, 6, 144, 35, 97, 68, 14, 67, 191, 19, 10, 158, 183, 43, 12, 148, 13, 37, 122, 80, 93, 132, 32, 103, 174, 111, 68, 192, 121, 134, 48, 85, 8, 23, 8, 6, 57, 83, 172, 101, 81, 86, 165, 73, 121, 139, 75, 151, 145, 11, 108, 14, 126, 61, 85, 8, 101, 153, 89, 190, 12, 62, 134, 101, 121, 167, 17, 161, 181, 16, 152, 148, 56, 111, 23, 84, 12, 43, 48, 122, 191, 56, 131, 51],
    "FD003": [44, 51, 27, 120, 101, 99, 71, 55, 55, 66, 77, 115, 115, 31, 108, 56, 136, 132, 85, 56, 18, 119, 78, 9, 58, 11, 88, 144, 124, 89, 79, 55, 71, 65, 87, 137, 145, 22, 8, 41, 131, 115, 128, 69, 111, 7, 137, 55, 135, 11, 78, 120, 87, 87, 55, 93, 88, 40, 49, 128, 129, 58, 117, 28, 115, 87, 92, 103, 100, 63, 35, 45, 99, 117, 45, 27, 86, 20, 18, 133, 15, 6, 145, 104, 56, 25, 68, 144, 41, 51, 81, 14, 67, 10, 127, 113, 123, 17, 8, 28],
    "FD004": [22, 39, 107, 75, 149, 78, 94, 14, 99, 162, 143, 7, 71, 105, 12, 160, 162, 104, 194, 82, 91, 11, 26, 142, 39, 92, 76, 124, 64, 118, 6, 22, 147, 126, 36, 73, 89, 11, 151, 10, 97, 30, 42, 60, 85, 134, 34, 45, 24, 86, 119, 151, 142, 176, 157, 67, 97, 8, 154, 139, 51, 33, 184, 46, 12, 133, 46, 46, 12, 33, 15, 176, 23, 89, 124, 163, 25, 74, 78, 114, 96, 10, 172, 166, 115, 70, 94, 56, 86, 96, 50, 73, 154, 129, 171, 71, 105, 113, 37, 7, 13, 22, 9, 120, 100, 107, 41, 153, 126, 59, 18, 66, 13, 14, 139, 13, 75, 8, 109, 137, 41, 192, 23, 86, 184, 15, 195, 126, 120, 165, 101, 116, 126, 36, 7, 122, 159, 88, 173, 146, 130, 108, 53, 162, 59, 100, 56, 145, 76, 57, 31, 88, 173, 34, 7, 133, 172, 6, 22, 83, 82, 84, 95, 174, 111, 72, 109, 87, 179, 158, 126, 12, 8, 10, 123, 103, 12, 106, 12, 32, 37, 116, 15, 10, 46, 142, 24, 135, 56, 43, 178, 71, 104, 15, 166, 89, 36, 11, 92, 96, 59, 13, 167, 151, 154, 109, 116, 91, 11, 88, 108, 76, 14, 89, 145, 17, 66, 154, 41, 182, 73, 39, 58, 14, 145, 88, 162, 189, 120, 98, 33, 184, 110, 68, 24, 75, 18, 16, 166, 98, 176, 81, 118, 35, 131, 194, 112, 26]
}

# ===================== 全局配置 & 样式 =====================
st.set_page_config(page_title="MacMod – Predictive Maintenance", page_icon="💻", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
    html, body, [class*="ViewBlock"], .main { background-color: #f8fafc !important; color: #0f172a !important; font-family: system-ui, -apple-system, sans-serif; font-size: 14px; }
    .macmod-card { background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; padding: 1.25rem 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 1rem; overflow: hidden; }
    .macmod-card-light { background: #f1f5f9; border-radius: 12px; border: 1px solid #e2e8f0; padding: 1.25rem 1.5rem; margin-bottom: 1rem; overflow: hidden; }
    [data-testid="stVerticalBlockBorderWrapper"] { background-color: #ffffff !important; border-radius: 12px !important; border: 1px solid #e2e8f0 !important; box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important; padding: 1.25rem 1.5rem !important; margin-bottom: 1rem !important; }
    [data-testid="stForm"] { background-color: #ffffff !important; border-radius: 12px !important; border: 1px solid #e2e8f0 !important; box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important; padding: 2rem !important; }
    .macmod-badge { display: inline-flex; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; border: 1px solid transparent; white-space: nowrap; }
    .macmod-pill { border-radius: 999px; padding: 0.25rem 0.6rem; font-size: 11px; font-weight: 500; white-space: nowrap; }
    .macmod-title { font-size: 20px; font-weight: 700; color: #0f172a; margin-bottom: 0.3rem; line-height: 1.3; word-wrap: break-word; }
    .macmod-subtitle { font-size: 13px; color: #64748b; line-height: 1.5; word-wrap: break-word; }
    
    div.stButton > button { border-radius: 0.5rem; border: 1px solid #2563eb; background: #2563eb; color: #ffffff !important; padding: 0.35rem 0.9rem; font-weight: 500; box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05); }
    div.stButton > button:hover { background: #1d4ed8; border-color: #1d4ed8; }
    div.stButton > button[kind="secondary"] { background: #ffffff; color: #0f172a !important; border: 1px solid #cbd5e1; }
    div.stButton > button[kind="secondary"]:hover { background: #f8fafc; border-color: #94a3b8; }
    
    .block-container { padding: 1.25rem 1.5rem 1.5rem 1.5rem; }
    .macmod-alert { border-radius: 0.75rem; border: 1px solid #fecaca; background: #fef2f2; padding: 0.75rem 1rem; font-size: 12px; color: #991b1b; margin-bottom: 0.5rem; line-height: 1.5; word-wrap: break-word; }
    hr.macmod-sep { border: none; border-top: 1px solid #e2e8f0; margin: 0.75rem 0; }
    .break-text { overflow-wrap: break-word; word-break: break-word; hyphens: auto; }
    div[data-testid="stForm"] > div:first-child { border: none !important; }
    div[role="radiogroup"] label { font-size: 16px !important; font-weight: 700 !important; color: #0f172a !important; }
    </style>
    """, unsafe_allow_html=True
)

# ===================== 数据 & 状态 =====================
def init_state():
    if "accounts" not in st.session_state:
        st.session_state.accounts = [{"id": "1773569861650", "name": "System Admin", "email": "admin@macmod.com", "position": "Factory Admin", "registeredDate": "2026-03-15", "password": "admin"}]
    if "active_account_id" not in st.session_state: st.session_state.active_account_id = "1773569861650"
    if "is_authenticated" not in st.session_state: st.session_state.is_authenticated = False
    if "auth_mode" not in st.session_state: st.session_state.auth_mode = "login"
    if "active_tab" not in st.session_state: st.session_state.active_tab = "home"
    if "custom_user_data" not in st.session_state: st.session_state.custom_user_data = None
    if "sys_priority_ds" not in st.session_state: st.session_state.sys_priority_ds = "FD001"
    
    if "rep" in st.session_state and "total_assets" not in st.session_state.rep:
        del st.session_state["rep"]

    if "system_logs" not in st.session_state:
        now = datetime.utcnow()
        st.session_state.system_logs = [
            {"id": "l1", "userId": "system", "userName": "System", "action": "Lathe D crossed vibration threshold", "timestamp": (now - timedelta(hours=2)).isoformat(), "type": "alert_critical", "machine": "Industrial Lathe D"},
            {"id": "l3", "userId": "system", "userName": "System", "action": "RUL estimation model retrained (RMSE: 1.2)", "timestamp": (now - timedelta(days=2)).isoformat(), "type": "model_updated", "machine": "System Core"},
        ]
        
    if "maintenance_records" not in st.session_state: st.session_state.maintenance_records = []
        
    if "machines" not in st.session_state:
        st.session_state.machines = [
            {"id": "m1", "name": "CNC Milling Alpha", "type": "Milling", "startDate": "2020-05-12", "repairs": 2, "status": "Warning", "currentCycle": 220, "failureCycle": 250, "healthScore": 45, "lat": 40.7128, "lon": -74.0060, "location": "New York Plant", "spareParts": [{"id": "p1", "name": "Spindle Bearing", "health": 85, "needsRepair": False, "status": "Healthy", "lastReplaced": "2023-01-15", "temperature": 45, "vibration": 2.1, "sensors": []}, {"id": "p2", "name": "Coolant Pump", "health": 18, "needsRepair": True, "status": "Warning", "lastReplaced": "2021-11-20", "temperature": 78, "vibration": 5.4, "sensors": []}]},
            {"id": "m2", "name": "Hydraulic Press Beta", "type": "Press", "startDate": "2018-11-23", "repairs": 5, "status": "Critical", "currentCycle": 310, "failureCycle": 325, "healthScore": 12, "lat": 34.0522, "lon": -118.2437, "location": "LA Facility", "spareParts": [{"id": "p3", "name": "Hydraulic Seal", "health": 5, "needsRepair": True, "status": "Critical", "lastReplaced": "2022-04-10", "temperature": 85, "vibration": 1.2, "sensors": []}, {"id": "p4", "name": "Pressure Valve", "health": 92, "needsRepair": False, "status": "Healthy", "lastReplaced": "2023-08-05", "temperature": 50, "vibration": 0.8, "sensors": []}]},
            {"id": "m3", "name": "Industrial Lathe Gamma", "type": "Lathe", "startDate": "2021-02-10", "repairs": 1, "status": "Healthy", "currentCycle": 120, "failureCycle": 280, "healthScore": 88, "lat": 51.5074, "lon": -0.1278, "location": "London Hub", "spareParts": [{"id": "p6", "name": "Chuck Jaw", "health": 90, "needsRepair": False, "status": "Healthy", "lastReplaced": "2023-05-12", "temperature": 38, "vibration": 1.5, "sensors": []}]},
        ]

init_state()

def get_active_account():
    return next((a for a in st.session_state.accounts if a["id"] == st.session_state.active_account_id), st.session_state.accounts[0])

def add_log(action: str, log_type: str, machine: str | None = None):
    acc = get_active_account()
    st.session_state.system_logs.insert(0, {"id": f"l{int(datetime.utcnow().timestamp()*1000)}", "userId": acc["id"], "userName": acc["name"], "action": action, "timestamp": datetime.utcnow().isoformat(), "type": log_type, "machine": machine})

# ===================== 登录 / 注册 =====================
def render_login():
    _, center_col, _ = st.columns([1, 1.5, 1])
    with center_col:
        st.markdown(f"""<div style="text-align:center;margin-top:4rem;margin-bottom:1rem;"><div style="width:64px;height:64px;border-radius:20px;border:1px solid #bfdbfe;background:#eff6ff;display:flex;align-items:center;justify-content:center;margin:0 auto 0.75rem auto;color:#2563eb;">{SVG_ICONS["cog"]}</div><div class="macmod-title">MacMod</div><div class="macmod-subtitle">Predictive Maintenance Terminal</div></div>""", unsafe_allow_html=True)
        error_placeholder = st.empty()

        if st.session_state.auth_mode == "login":
            with st.form("login_form"):
                st.markdown('<div style="font-size:16px;font-weight:700;margin-bottom:1rem;">Log In to Your Account</div>', unsafe_allow_html=True)
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                if st.form_submit_button("Log In", type="primary", use_container_width=True):
                    if not username or not password: error_placeholder.error("Please enter your username and password.")
                    else:
                        if acc := next((a for a in st.session_state.accounts if a["name"] == username and a.get("password", "") == password), None):
                            st.session_state.active_account_id = acc["id"]; st.session_state.is_authenticated = True; add_log("Logged into MacMod Dashboard", "user_action"); st.session_state.active_tab = "home"; st.rerun()
                        else: error_placeholder.error("Invalid username or password.")
            if st.button("Create an Account", type="secondary", use_container_width=True): st.session_state.auth_mode = "signup"; st.rerun()
        else:
            with st.form("signup_form"):
                st.markdown('<div style="font-size:16px;font-weight:700;margin-bottom:1rem;">Create a New Account</div>', unsafe_allow_html=True)
                username = st.text_input("Username", placeholder="Choose a username"); email = st.text_input("Email Address", placeholder="engineer@factory.com"); position = st.text_input("Job Position", placeholder="e.g. Maintenance Technician"); password = st.text_input("Password", type="password", placeholder="Choose a password")
                if st.form_submit_button("Sign Up", type="primary", use_container_width=True):
                    if not username or not email or not password or not position: error_placeholder.error("Please fill in all fields.")
                    elif any(a["email"] == email for a in st.session_state.accounts): error_placeholder.error("Email is already registered.")
                    else:
                        new_acc = {"id": str(int(datetime.utcnow().timestamp() * 1000)), "name": username, "email": email, "position": position, "registeredDate": datetime.utcnow().date().isoformat(), "password": password}
                        st.session_state.accounts.append(new_acc); st.session_state.active_account_id = new_acc["id"]; st.session_state.is_authenticated = True; add_log("Registered new MacMod account", "user_action"); st.rerun()
            if st.button("Back to Log In", type="secondary", use_container_width=True): st.session_state.auth_mode = "login"; st.rerun()

# ===================== 侧边栏 =====================
def render_sidebar():
    acc = get_active_account()
    with st.sidebar:
        st.markdown(f"""<div style="padding:1rem 0.25rem 0.5rem 0.25rem;border-bottom:1px solid #e2e8f0;margin-bottom:1rem;"><div style="display:flex;align-items:center;gap:0.65rem;"><div style="width:32px;height:32px;border-radius:0.6rem;background:#2563eb;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 6px -1px rgba(37,99,235,0.2);color:white;">{SVG_ICONS["cog"]}</div><div><div style="font-size:15px;font-weight:700;color:#0f172a;line-height:1.2;">MacMod</div><div style="font-size:11px;color:#3b82f6;font-weight:600;line-height:1.2;">Predictive Maintenance</div></div></div></div>""", unsafe_allow_html=True)
        for k, label in {"home": "Dashboard", "machines": "Machines", "maintenance": "Maintenance", "reports": "Reports", "settings": "Settings", "account": "Account"}.items():
            if st.button(label, key=f"nav_{k}", type="primary" if st.session_state.active_tab == k else "secondary", use_container_width=True): st.session_state.active_tab = k; st.rerun()
        st.markdown("---")
        name_parts = acc["name"].split()
        initials = (name_parts[0][0] + name_parts[1][0]).upper() if len(name_parts) >= 2 else (name_parts[0][:2].upper() if name_parts else "??")
        st.markdown(f"""<div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem;"><div style="width:36px;height:36px;flex-shrink:0;border-radius:999px;background:#2563eb;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;color:white;">{initials}</div><div style="min-width:0;flex:1;"><div style="font-size:13px;font-weight:600;color:#0f172a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{acc["name"]}</div><div style="font-size:11px;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{acc["position"]}</div></div></div>""", unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True): st.session_state.is_authenticated = False; st.session_state.auth_mode = "login"; st.session_state.active_tab = "home"; st.rerun()

# ===================== 数据处理与渲染工具 =====================
@st.cache_data(show_spinner=False)
def load_cmapss(dataset: str):
    files = CMAPSS_FILES[dataset]
    cols = ["unit", "cycle"] + [f"op_setting_{i}" for i in range(1, 4)] + [f"s{i}" for i in range(1, 23)]
    if files["train"].exists() and files["test"].exists():
        try:
            train, test = pd.read_csv(files["train"], sep=r"\s+", header=None, names=cols), pd.read_csv(files["test"], sep=r"\s+", header=None, names=cols)
            train["RUL"] = train.groupby("unit")["cycle"].transform(lambda x: x.max() - x)
            test["RUL"] = test.groupby("unit")["cycle"].transform("max") - test["cycle"] + REAL_RUL_DATA[dataset][:len(test.groupby("unit"))]
            return train, test, True
        except Exception: pass 
    sim_test_data = []
    for i, rul_val in enumerate(REAL_RUL_DATA[dataset]):
        unit_id, max_cycles = i + 1, np.random.randint(150, 250)
        for cycle in range(1, max_cycles + 1):
            sim_test_data.append({"unit": unit_id, "cycle": cycle, "s11": 45 + np.sin(cycle / 10) * 15 + np.random.rand() * 5, "s12": 8000 - (cycle / max_cycles) * 400 + np.random.rand() * 50, "RUL": (max_cycles - cycle) + rul_val})
    return pd.DataFrame(), pd.DataFrame(sim_test_data), False 

def generate_telemetry(c, f, noise_multiplier=1.0):
    return pd.DataFrame([{"cycle": i, "s11": 45 + np.sin(i/10)*15 + (np.random.rand()*5 * noise_multiplier) + (20 if i>f-20 else 0), "s12": 8000 - (i/f)*400 + (np.random.rand()*50 * noise_multiplier), "rsi": np.clip(50 + np.sin(i/5)*30 + (30 if i>f-20 else 0), 0, 100), "trueRUL": round(max(0, f-i)), "aiRUL": round(max(0, max(0, f-i)+(np.random.rand()-0.5)*15*(1-max(0, f-i)/max(1, f))))} for i in range(max(0, c-60), c+16, 2)])

def plot_telemetry(df):
    c1, c2 = st.columns(2)
    for fig, col in [(px.line(df, x="cycle", y="s11", title="S11 THROTTLE", markers=True, template="plotly_white"), c1), (px.line(df, x="cycle", y="s12", title="S12 CORE SPEED", markers=True, template="plotly_white"), c1), (px.line(df, x="cycle", y="rsi", title="S11 RSI", markers=True, template="plotly_white"), c2), (px.line(df, x="cycle", y=["trueRUL", "aiRUL"], title="PROGNOSTICS: RUL AI", markers=True, template="plotly_white"), c2)]:
        fig.update_traces(marker_symbol='x', mode='lines+markers'); col.plotly_chart(fig, use_container_width=True)

def generate_pdf_bytes(report_text):
    if HAS_FPDF:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=11)
        for line in report_text.split('\n'):
            safe_line = line.encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 6, txt=safe_line, ln=1)
        out = pdf.output(dest='S')
        return out.encode('latin-1') if isinstance(out, str) else bytes(out)
    return None

# ===================== 子页面视图：地图、日历、手动调度、添加机器等 =====================
def render_map():
    st.markdown('<div style="margin-bottom:1.5rem;"><div class="macmod-title">Facility Map</div><div class="macmod-subtitle">Geospatial overview of your industrial assets.</div></div>', unsafe_allow_html=True)
    with st.container(border=True):
        df_map = pd.DataFrame(st.session_state.machines)
        if "lat" in df_map.columns and "lon" in df_map.columns:
            color_map = {"Healthy": "#16a34a", "Warning": "#ea580c", "Critical": "#dc2626", "Pending Maintenance": "#2563eb"}
            df_map["color"] = df_map["status"].map(color_map).fillna("#64748b")
            fig = px.scatter_mapbox(df_map, lat="lat", lon="lon", hover_name="name", hover_data=["location", "status", "healthScore"], color="status", color_discrete_map=color_map, zoom=2, height=500)
            fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("No geospatial data available for current machines.")
        if st.button("← Back to Dashboard", type="secondary"): st.session_state.active_tab = "home"; st.rerun()

def render_calendar():
    st.markdown('<div style="margin-bottom:1.5rem;"><div class="macmod-title">Facility Calendar</div><div class="macmod-subtitle">Timeline view of scheduled maintenance tasks.</div></div>', unsafe_allow_html=True)
    with st.container(border=True):
        records = st.session_state.maintenance_records
        if not records: st.info("No maintenance schedules available to display.")
        else:
            df_cal = pd.DataFrame(records)
            df_cal["priority"] = df_cal.get("priority", "low") 
            df_cal["dueDate"] = pd.to_datetime(df_cal["dueDate"])
            df_cal["endDate"] = pd.to_datetime(df_cal["endDate"])
            
            mask = df_cal["endDate"] <= df_cal["dueDate"]
            df_cal.loc[mask, "endDate"] = df_cal.loc[mask, "dueDate"] + pd.Timedelta(days=1)
            
            def map_pri(x):
                x = str(x).lower()
                if x in ["high", "critical"]: return "High"
                if x == "medium": return "Medium"
                return "Low"
            df_cal["Priority Level"] = df_cal["priority"].apply(map_pri)
            color_map = {"High": "#dc2626", "Medium": "#eab308", "Low": "#3b82f6"}
            
            fig = px.timeline(df_cal, x_start="dueDate", x_end="endDate", y="task", color="Priority Level", color_discrete_map=color_map, height=400)
            fig.update_yaxes(autorange="reversed"); fig.layout.template = "plotly_white"
            st.plotly_chart(fig, use_container_width=True)
            
        if st.button("← Back to Dashboard", type="secondary"): st.session_state.active_tab = "home"; st.rerun()

def render_manual_schedule():
    st.markdown('<div style="margin-bottom:1.5rem;"><div class="macmod-title">Schedule Maintenance Manually</div><div class="macmod-subtitle">Manually block schedules and plan maintenance for your assigned assets.</div></div>', unsafe_allow_html=True)
    with st.container(border=True):
        with st.form("manual_maint_form"):
            machine_names = [m["name"] for m in st.session_state.machines]
            sel_mac_name = st.selectbox("Select Target Machine", machine_names)
            c1, c2, c3 = st.columns(3); start_date = c1.date_input("Start Date", date.today()); end_date = c2.date_input("End Date", date.today() + timedelta(days=1)); priority_val = c3.selectbox("Priority Level", ["Low", "Medium", "High"], index=1)
            remarks = st.text_area("Remarks (Optional)", placeholder="e.g. Routine inspection and oil change...")
            
            if st.form_submit_button("Confirm Manual Schedule", type="primary", use_container_width=True):
                if end_date < start_date: st.error("End date cannot be earlier than start date.")
                else:
                    target_m = next(m for m in st.session_state.machines if m["name"] == sel_mac_name)
                    target_m["status"] = "Pending Maintenance" 
                    task_str = f"Manual Maint: {target_m['name']}" + (f" ({remarks})" if remarks else "")
                    st.session_state.maintenance_records.append({"task": task_str, "priority": priority_val.lower(), "dueDate": start_date.isoformat(), "endDate": end_date.isoformat()})
                    add_log(f"Manually scheduled maintenance for {target_m['name']}", "maint", target_m["name"])
                    st.session_state.active_tab = "home"; st.rerun()
        if st.button("← Cancel & Back to Dashboard", type="secondary"): st.session_state.active_tab = "home"; st.rerun()

def render_add_machine():
    st.markdown('<div style="margin-bottom:1.5rem;"><div class="macmod-title">Add New Machine</div><div class="macmod-subtitle">Register a new asset into the predictive maintenance fleet.</div></div>', unsafe_allow_html=True)
    with st.container(border=True):
        with st.form("new_machine_form"):
            name = st.text_input("Machine Name", placeholder="e.g. CNC Milling Machine X")
            m_type = st.selectbox("Machine Type", ["Milling", "Press", "Lathe", "Pump", "Other"])
            c1, c2 = st.columns(2); start_date = c1.date_input("Commissioning Date (Start Date)"); repairs = c2.number_input("Prior Repair Count", min_value=0, value=0)
            parts_count = st.number_input("Number of Tracked Spare Parts", min_value=1, max_value=50, value=2)
            if st.form_submit_button("Register Machine", type="primary", use_container_width=True):
                if not name: st.error("Please enter a machine name.")
                else:
                    m_id = f"m_{int(datetime.utcnow().timestamp())}"
                    spare_parts = [{"id": f"p_{m_id}_{i}", "name": f"Component {i+1}", "health": 100, "needsRepair": False, "status": "Healthy", "lastReplaced": start_date.isoformat(), "temperature": 40 + np.random.randint(-5, 10), "vibration": 1.0 + np.random.rand(), "sensors": []} for i in range(parts_count)]
                    new_m = {"id": m_id, "name": name, "type": m_type, "startDate": start_date.isoformat(), "repairs": repairs, "status": "Healthy", "currentCycle": 0, "failureCycle": np.random.randint(150, 400), "healthScore": 100, "rmse": 0.0, "regime": "NEW", "alertThreshold": 30, "lat": 0.0, "lon": 0.0, "location": "Unknown", "sensors": [], "spareParts": spare_parts}
                    st.session_state.machines.append(new_m)
                    add_log(f"Registered new asset: {name}", "machine_added")
                    st.session_state.active_tab = "machines"; st.rerun()
        if st.button("← Cancel & Back to Dashboard", type="secondary"): st.session_state.active_tab = "home"; st.rerun()

def render_upload_data():
    st.markdown('<div style="margin-bottom:1.5rem;"><div class="macmod-title">Upload Factory Raw Data</div><div class="macmod-subtitle">Import your historical CSV/TXT telemetry logs here to test your custom machines.</div></div>', unsafe_allow_html=True)
    with st.container(border=True):
        uploaded_file = st.file_uploader("Choose a file (CSV or TXT)", type=["csv", "txt"])
        if uploaded_file is not None:
            try:
                st.session_state.custom_user_data = pd.read_csv(uploaded_file)
                st.success("Data imported successfully! You can now analyze it in the Machines tab.")
            except Exception as e: st.error(f"Failed to parse file: {e}")
        if st.button("← Back to Dashboard", type="secondary"): st.session_state.active_tab = "home"; st.rerun()

def render_add_account():
    st.markdown('<div style="margin-bottom:1.5rem;"><div class="macmod-title">Add New Account</div><div class="macmod-subtitle">Create a new user account for the system.</div></div>', unsafe_allow_html=True)
    with st.container(border=True):
        error_placeholder = st.empty()
        with st.form("add_account_form"):
            username = st.text_input("Username", placeholder="Choose a username"); email = st.text_input("Email Address", placeholder="engineer@factory.com")
            position = st.text_input("Job Position", placeholder="e.g. Maintenance Technician"); password = st.text_input("Password", type="password", placeholder="Choose a password")
            if st.form_submit_button("Create Account", type="primary", use_container_width=True):
                if not username or not email or not password or not position: error_placeholder.error("Please fill in all fields.")
                elif any(a["email"] == email for a in st.session_state.accounts): error_placeholder.error("Email is already registered.")
                else:
                    new_acc = {"id": str(int(datetime.utcnow().timestamp() * 1000)), "name": username, "email": email, "position": position, "registeredDate": datetime.utcnow().date().isoformat(), "password": password}
                    st.session_state.accounts.append(new_acc); add_log(f"Created new account for {username}", "user_action"); st.session_state.active_tab = "account"; st.rerun()
        if st.button("← Cancel & Back to Accounts", type="secondary"): st.session_state.active_tab = "account"; st.rerun()

def render_change_password():
    st.markdown('<div style="margin-bottom:1.5rem;"><div class="macmod-title">Change Password</div><div class="macmod-subtitle">Update your account security credentials.</div></div>', unsafe_allow_html=True)
    with st.container(border=True):
        error_placeholder = st.empty()
        with st.form("change_pwd_form"):
            old_pwd = st.text_input("Current Password", type="password")
            new_pwd = st.text_input("New Password", type="password")
            confirm_pwd = st.text_input("Confirm New Password", type="password")
            if st.form_submit_button("Update Password", type="primary", use_container_width=True):
                acc = get_active_account()
                if acc.get("password") != old_pwd: error_placeholder.error("Incorrect current password.")
                elif new_pwd != confirm_pwd: error_placeholder.error("New passwords do not match.")
                elif len(new_pwd) < 4: error_placeholder.error("Password must be at least 4 characters long.")
                else:
                    acc["password"] = new_pwd; add_log("User changed password", "security_update"); st.session_state.active_tab = "account"; st.rerun()
        if st.button("← Cancel & Back to Accounts", type="secondary"): st.session_state.active_tab = "account"; st.rerun()

# ===================== 主页面：DashboardHome =====================
def render_dashboard_home():
    acc, machines, logs, maintenance_records = get_active_account(), st.session_state.machines, st.session_state.system_logs, st.session_state.maintenance_records
    st.markdown(f'<div style="margin-bottom:1.5rem;"><div class="macmod-title">Welcome back, <span class="break-text">{acc["name"]}</span>!</div><div class="macmod-subtitle">Here is the real-time health overview of your industrial assets.</div></div>', unsafe_allow_html=True)

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
    
    active_machines_count = sum(1 for m in machines if m["status"] != "Pending Maintenance")
    sensors_count = sum(len(m.get("sensors", [])) + sum(len(p.get("sensors", [])) for p in m["spareParts"]) for m in machines) + 156
    pending_count = sum(1 for m in machines if m["status"] == "Pending Maintenance")
    critical_count = sum(1 for m in machines if m["status"] == "Critical")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(make_metric("Active Machines", active_machines_count, SVG_ICONS["server"], "#eff6ff", "#2563eb"), unsafe_allow_html=True)
    with c2: st.markdown(make_metric("Sensors Monitored", sensors_count, SVG_ICONS["cpu"], "#dcfce7", "#16a34a"), unsafe_allow_html=True)
    with c3: st.markdown(make_metric("Pending Maintenance", pending_count, SVG_ICONS["wrench"], "#ffedd5", "#ea580c"), unsafe_allow_html=True)
    with c4: st.markdown(make_metric("Critical Alerts", critical_count, SVG_ICONS["alert"], "#fee2e2", "#dc2626"), unsafe_allow_html=True)

    left, right = st.columns([2, 1])
    with left:
        html = f"""<div class="macmod-card"><div class="macmod-title" style="font-size:18px;margin-bottom:0.25rem;display:flex;align-items:center;gap:8px;"><div style="width:20px;height:20px;">{SVG_ICONS["pulse"]}</div> Asset Health & RUL</div><div class="macmod-subtitle" style="margin-bottom:1rem;">Real-time Remaining Useful Life estimates</div>"""
        for m in machines:
            badge = {"Healthy": "background:#dcfce7;color:#166534;border-color:#bbf7d0;", "Warning": "background:#fef3c7;color:#92400e;border-color:#fde68a;", "Critical": "background:#fee2e2;color:#991b1b;border-color:#fecaca;", "Pending Maintenance": "background:#dbeafe;color:#1d4ed8;border-color:#bfdbfe;"}.get(m["status"], "background:#f1f5f9;color:#334155;border-color:#e2e8f0;")
            html += f"""<div style="margin-top:0.6rem;border-radius:0.75rem;border:1px solid #e2e8f0;padding:0.8rem;background:#f8fafc;"><div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.75rem;"><div style="flex:1; min-width:0;"><div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.3rem; flex-wrap:wrap;"><span class="break-text" style="font-size:15px;font-weight:700;color:#0f172a;">{m["name"]}</span><span class="macmod-badge" style="{badge}">{m["status"]}</span></div><div style="font-size:13px;color:#64748b;">Estimated RUL: <span style="font-weight:700;color:#0f172a;">{max(0, m["failureCycle"] - m["currentCycle"])} cycles</span></div><div style="font-size:12px;color:#64748b;margin-top:3px;">Health: {m["healthScore"]}% | Spare parts: {len(m["spareParts"])}</div></div><div style="text-align:right;font-size:12px;color:#64748b; flex-shrink:0;"><div style="font-weight:700;color:#0f172a;">Type</div><div style="margin-top:2px;">{m["type"]}</div></div></div></div>"""
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    with right:
        with st.container(border=True):
            st.markdown(f'<div class="macmod-title" style="font-size:18px;margin-bottom:0.25rem;display:flex;align-items:center;gap:8px;"><div style="width:20px;height:20px;">{SVG_ICONS["plus"]}</div> Quick Actions</div><div class="macmod-subtitle" style="margin-bottom:1rem;">Common management tasks</div>', unsafe_allow_html=True)
            if st.button("Upload Factory Raw Data", use_container_width=True): st.session_state.active_tab = "upload_data"; st.rerun()
            if st.button("Add New Machine", use_container_width=True): st.session_state.active_tab = "add_machine"; st.rerun()
            if st.button("Schedule Maintenance Manually", use_container_width=True): st.session_state.active_tab = "manual_schedule"; st.rerun()
            if st.button("View Facility Map", use_container_width=True): st.session_state.active_tab = "map"; st.rerun()
            if st.button("View Facility Calendar", use_container_width=True): st.session_state.active_tab = "calendar"; st.rerun()

    col_a, col_b = st.columns(2)
    with col_a:
        log_html = f"""<div class="macmod-card"><div class="macmod-title" style="font-size:18px;margin-bottom:0.25rem;display:flex;align-items:center;gap:8px;"><div style="width:20px;height:20px;">{SVG_ICONS["clock"]}</div> System Logs</div><div class="macmod-subtitle" style="margin-bottom:1rem;">Recent anomaly detections and events</div>"""
        for log in logs[:8]:
            mins = int((datetime.utcnow() - datetime.fromisoformat(log["timestamp"])).total_seconds() // 60)
            log_html += f"""<div style="margin-top:0.5rem;border-radius:0.75rem;border:1px solid #e2e8f0;padding:0.6rem 0.8rem;background:#ffffff;"><div class="break-text" style="font-size:13px;font-weight:600;color:#0f172a;">{log["action"]}</div><div class="break-text" style="font-size:12px;color:#64748b;margin-top:3px;">{f"{mins} min ago" if mins<60 else f"{mins//60} h ago"} by {log["userName"]}{f" • {log['machine']}" if log.get("machine") else ""}</div></div>"""
        log_html += "</div>"
        st.markdown(log_html, unsafe_allow_html=True)

    with col_b:
        sched = list(st.session_state.maintenance_records)
        sched.sort(key=lambda x: x["dueDate"])
        sched_html = f"""<div class="macmod-card"><div class="macmod-title" style="font-size:18px;margin-bottom:0.25rem;display:flex;align-items:center;gap:8px;"><div style="width:20px;height:20px;">{SVG_ICONS["calendar"]}</div> Scheduled Maintenance</div><div class="macmod-subtitle" style="margin-bottom:1rem;">Upcoming predictive repairs</div>"""
        if not sched: sched_html += '<div style="font-size:13px;color:#64748b;">No maintenance scheduled. All systems nominal.</div>'
        for item in sched[:8]:
            sched_html += f"""<div style="margin-top:0.5rem;border-radius:0.75rem;border:1px solid #bfdbfe;padding:0.6rem 0.8rem;background:#eff6ff;"><div class="break-text" style="font-size:13px;font-weight:600;color:#0f172a;">{item["task"]}</div><div style="font-size:12px;color:#2563eb;margin-top:3px;">Scheduled: {item["dueDate"]} to {item["endDate"]}</div></div>"""
        sched_html += "</div>"
        st.markdown(sched_html, unsafe_allow_html=True)

# ===================== 主页面：Machines =====================
def render_machines():
    st.markdown('<div style="margin-bottom:1.5rem;"><div class="macmod-title">Machine Fleet AI Monitor</div><div class="macmod-subtitle">Predictive maintenance terminal and RUL diagnostics.</div></div>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, m in enumerate(st.session_state.machines):
        with cols[i % 3]:
            with st.container(border=True):
                badge = {"Healthy": "background:#dcfce7;color:#166534;", "Warning": "background:#fef3c7;color:#92400e;", "Critical": "background:#fee2e2;color:#991b1b;", "Pending Maintenance": "background:#dbeafe;color:#1d4ed8;"}.get(m["status"], "background:#f1f5f9;color:#334155;")
                st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:flex-start;"><div style="padding:0.45rem;border-radius:0.5rem;background:#f8fafc;border:1px solid #e2e8f0;width:32px;height:32px;color:#0f172a;">{SVG_ICONS["server"]}</div><div class="macmod-badge" style="{badge}">{m["status"]}</div></div><div class="break-text" style="margin-top:0.8rem;font-size:16px;font-weight:700;color:#0f172a;">{m["name"]}</div><div style="font-size:13px;color:#64748b;margin-bottom:0.8rem;">Type: {m["type"]}</div><div style="font-size:13px;display:flex;justify-content:space-between;margin-bottom:0.4rem;"><span style="color:#64748b;">Started</span><span style="font-weight:600;">{m["startDate"]}</span></div><div style="font-size:13px;display:flex;justify-content:space-between;margin-bottom:1rem;"><span style="color:#64748b;">Repairs</span><span style="font-weight:600;">{m["repairs"]}</span></div>""", unsafe_allow_html=True)
                if st.button("Open Terminal", key=f"open_{m['id']}", use_container_width=True): st.session_state.sel_mac = m["id"]

    if sel := st.session_state.get("sel_mac"):
        if m := next((x for x in st.session_state.machines if x["id"] == sel), None):
            with st.container(border=True):
                st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;margin-bottom:1rem;"><div style="flex:1;min-width:0;"><div style="font-size:13px;color:#2563eb;font-weight:700;letter-spacing:0.1em;">LIVE TELEMETRY TERMINAL</div><div class="break-text" style="font-size:20px;font-weight:700;color:#0f172a;margin-top:4px;">{m["name"]}</div></div><div style="display:flex;gap:2rem;flex-shrink:0;"><div style="text-align:center;"><div style="font-size:12px;color:#64748b;font-weight:700;text-transform:uppercase;">Health</div><div style="font-size:26px;font-weight:700;color:#2563eb;">{m["healthScore"]}%</div></div><div style="text-align:center;"><div style="font-size:12px;color:#64748b;font-weight:700;text-transform:uppercase;">Adj RUL</div><div style="font-size:26px;font-weight:700;color:#16a34a;">{max(0, m["failureCycle"]-m["currentCycle"])}<span style="font-size:13px;color:#64748b;"> cyc</span></div></div></div></div><hr class="macmod-sep" />""", unsafe_allow_html=True)
                
                ctrl_1, ctrl_2 = st.columns([1.5, 1])
                with ctrl_1:
                    test_source = st.radio("Data Source", ["System Data (Built-in)", "Custom Uploaded Data"], horizontal=True, label_visibility="collapsed")
                with ctrl_2:
                    if test_source == "System Data (Built-in)":
                        st.markdown(f"<div style='padding-top:0.3rem;color:#2563eb;font-weight:600;'><i>Using System Profile: {st.session_state.sys_priority_ds}</i></div>", unsafe_allow_html=True)
                st.write("")
                
                if test_source == "System Data (Built-in)":
                    plot_telemetry(generate_telemetry(m["currentCycle"], m["failureCycle"], noise_multiplier=1.0))
                else:
                    if st.session_state.custom_user_data is not None:
                        df_custom = st.session_state.custom_user_data
                        if "cycle" in df_custom.columns and "s11" in df_custom.columns:
                            st.success("Successfully mapped custom columns.")
                            plot_telemetry(df_custom.head(300))
                        else:
                            st.info("No standard columns [cycle, s11] found. System dynamically generated mapped diagnostics.")
                            plot_telemetry(generate_telemetry(m["currentCycle"], m["failureCycle"], noise_multiplier=3.5))
                    else:
                        st.warning("⚠️ No Custom Data Uploaded.")
                        if st.button("Go to Upload Data Page", type="primary"):
                            st.session_state.active_tab = "upload_data"; st.rerun()

# ===================== 主页面：Maintenance =====================
def render_maintenance():
    st.markdown('<div style="margin-bottom:1.5rem;"><div class="macmod-title">Maintenance Queue</div><div class="macmod-subtitle">Review machines and spare parts requiring attention.</div></div>', unsafe_allow_html=True)
    needing = [m for m in st.session_state.machines if any(p["needsRepair"] for p in m["spareParts"])]
    if not needing: return st.markdown(f'<div class="macmod-card" style="text-align:center;padding:4rem 1.5rem;background:#f8fafc;"><div style="width:56px;height:56px;color:#16a34a;margin:0 auto 1rem auto;">{SVG_ICONS["check"]}</div><div style="font-size:20px;font-weight:700;">All Systems Operational</div><div style="font-size:15px;color:#64748b;margin-top:0.5rem;">No machines currently require maintenance.</div></div>', unsafe_allow_html=True)

    cols = st.columns(3)
    for i, m in enumerate(needing):
        bad = [p for p in m["spareParts"] if p["needsRepair"]]
        with cols[i % 3]:
            with st.container(border=True):
                bg = "background:#fee2e2;color:#991b1b;" if m["status"]=="Critical" else "background:#fef3c7;color:#92400e;"
                st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:flex-start;"><div style="padding:0.4rem;border-radius:0.6rem;background:#ffedd5;width:32px;height:32px;color:#c2410c;">{SVG_ICONS["alert"]}</div><span class="macmod-badge" style="{bg}">{m["status"]}</span></div><div class="break-text" style="margin-top:0.8rem;font-size:16px;font-weight:700;">{m["name"]}</div><div style="font-size:13px;color:#64748b;margin-bottom:1rem;">{len(bad)} parts need attention</div><div style="font-size:13px;color:#0f172a;font-weight:600;margin-bottom:0.5rem;">Critical Parts:</div><div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:1rem;">{''.join(f'<span class="macmod-pill break-text" style="background:#fee2e2;color:#991b1b;border:1px solid #fecaca;">{p["name"]}</span>' for p in bad)}</div>""", unsafe_allow_html=True)
                if st.button("Schedule Repair", key=f"rev_{m['id']}", use_container_width=True): st.session_state.sel_maint = m["id"]

    if sel := st.session_state.get("sel_maint"):
        if m := next((x for x in st.session_state.machines if x["id"] == sel), None):
            with st.container(border=True):
                st.markdown(f'<div class="break-text macmod-title" style="font-size:18px;">Target: {m["name"]}</div><div class="macmod-subtitle" style="margin-bottom:1.5rem;">Select part to schedule repair.</div>', unsafe_allow_html=True)
                bad = [p for p in m["spareParts"] if p["needsRepair"]]
                if not bad: return st.info("No parts flagged.")
                part = next(p for p in bad if p["name"] == st.selectbox("Spare Part", [p["name"] for p in bad]))
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Health", f"{part['health']}%"); c2.metric("Replaced", part["lastReplaced"]); c3.metric("Temp", f"{part['temperature']}°C"); c4.metric("Vibration", f"{part['vibration']}mm/s")
                st.markdown('<div class="macmod-alert" style="margin-top:1rem;margin-bottom:1rem;">Threshold crossed. Action required.</div>', unsafe_allow_html=True)
                start, end = st.date_input("Start Date", date.today()), st.date_input("End Date", date.today() + timedelta(days=1))
                if st.button("Confirm Schedule", type="primary"):
                    if end < start: st.error("End date error.")
                    else:
                        part.update({"needsRepair": False, "health": 100, "status": "Pending"})
                        m["status"] = "Pending Maintenance" 
                        st.session_state.maintenance_records.append({"task": f"Repair {part['name']} on {m['name']}", "priority": "high", "dueDate": start.isoformat(), "endDate": end.isoformat()})
                        add_log(f"Scheduled maintenance: {part['name']}", "maint", m["name"])
                        st.session_state.sel_maint = None 
                        st.toast("Scheduled successfully!", icon="✅")
                        st.rerun()

# ===================== 主页面：Reports =====================
def render_reports():
    st.markdown('<div style="margin-bottom:1.5rem;"><div class="macmod-title">Analytics & Reports</div><div class="macmod-subtitle">Generate dynamic health and maintenance reports based on selected assets.</div></div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="macmod-title" style="font-size:16px;">Report Parameters</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: yr = st.selectbox("Year", ["2024", "2025", "2026"], index=2)
        with c2: mo = st.selectbox("Month", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], index=2)
        
        machines = st.session_state.machines
        m_opts = ["All Machines"] + [m["name"] for m in machines]
        with c3: mac_sel = st.selectbox("Machine Target", m_opts)
        
        if st.button("Generate Dynamic Report", type="primary"):
            target_ms = machines if mac_sel == "All Machines" else [m for m in machines if m["name"] == mac_sel]
            
            avg_rul = int(np.mean([max(0, m["failureCycle"] - m["currentCycle"]) for m in target_ms])) if target_ms else 0
            repairs = sum(m["repairs"] for m in target_ms)
            avg_hlth = int(np.mean([m["healthScore"] for m in target_ms])) if target_ms else 0
            anomalies = sum(1 for m in target_ms if m["status"] in ["Warning", "Critical"]) + sum(1 for m in target_ms for p in m["spareParts"] if p["needsRepair"])
            
            total_parts = sum(len(m["spareParts"]) for m in target_ms)
            bad_parts = sum(1 for m in target_ms for p in m["spareParts"] if p["needsRepair"])
            avg_temp = np.mean([p["temperature"] for m in target_ms for p in m["spareParts"]]) if total_parts else 0
            avg_vib = np.mean([p["vibration"] for m in target_ms for p in m["spareParts"]]) if total_parts else 0

            detail_lines = []
            for m in target_ms:
                detail_lines.append(f"  > [{m['id']}] {m['name']} | Health: {m['healthScore']}% | RUL: {max(0, m['failureCycle']-m['currentCycle'])} | Status: {m['status']}")
            machine_details = "\n".join(detail_lines) if detail_lines else "  > No machine data available."

            st.session_state.rep = {
                "rul": avg_rul, "anom": anomalies, "rep": repairs, "hlth": avg_hlth, 
                "yr": yr, "mo": mo, "mac": mac_sel, "total_assets": len(target_ms),
                "total_parts": total_parts, "bad_parts": bad_parts, "avg_temp": avg_temp, "avg_vib": avg_vib,
                "machine_details": machine_details
            }

    if r := st.session_state.get("rep"):
        st.markdown(f"""<div class="macmod-card"><div style="background:#dcfce7;border:1px solid #bbf7d0;border-radius:0.75rem;padding:1rem;margin:-1rem -1.5rem 1.5rem -1.5rem;display:flex;align-items:center;gap:0.7rem;"><div style="width:28px;height:28px;color:#166534;">{SVG_ICONS["chart"]}</div><div><div style="font-size:16px;font-weight:700;color:#166534;">Monitoring Report ({r["mac"]})</div><div style="font-size:13px;color:#15803d;margin-top:2px;">{r["mo"]} {r["yr"]}</div></div></div><div style="display:flex; flex-wrap:wrap; gap:2rem; justify-content:space-between; margin-bottom:1.5rem;"><div><div style="color:#64748b;font-size:13px;margin-bottom:0.2rem;">Avg RUL</div><div style="font-size:26px;font-weight:700;color:#0f172a;">{r["rul"]}</div></div><div><div style="color:#64748b;font-size:13px;margin-bottom:0.2rem;">Anomalies</div><div style="font-size:26px;font-weight:700;color:#0f172a;">{r["anom"]}</div></div><div><div style="color:#64748b;font-size:13px;margin-bottom:0.2rem;">Repairs</div><div style="font-size:26px;font-weight:700;color:#0f172a;">{r["rep"]}</div></div><div><div style="color:#64748b;font-size:13px;margin-bottom:0.2rem;">Fleet Health</div><div style="font-size:26px;font-weight:700;color:#0f172a;">{r["hlth"]}%</div></div></div><hr class="macmod-sep" /><div style="font-size:15px;font-weight:700;color:#0f172a;margin-top:1rem;margin-bottom:0.5rem;">Executive Summary</div><div style="font-size:14px;color:#475569;line-height:1.7;">Based on the real-time aggregation of your selected assets, the temporal feature engineering models have processed current cycles. Adjustments to anomaly Z-score thresholds should be considered if repair rates exceed expected baselines. Immediate proactive maintenance is recommended for any parts flagged in the anomaly count.</div></div>""", unsafe_allow_html=True)
        
        report_text = f"""============================================================
             MACMOD ENTERPRISE CONDITION REPORT
============================================================
Target      : {r['mac']}
Period      : {r['mo']} {r['yr']}
Generated   : {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
------------------------------------------------------------

[ 1. OVERALL FLEET METRICS ]
  > Total Active Assets       : {r['total_assets']}
  > Average Health Score      : {r['hlth']}%
  > Average Remaining Life    : {r['rul']} cycles
  > Total Anomalies Detected  : {r['anom']}
  > Total Historical Repairs  : {r['rep']}

[ 2. SENSOR TELEMETRY & COMPONENT HEALTH ]
  > Monitored Components      : {r['total_parts']}
  > Components At Risk        : {r['bad_parts']}
  > Mean Operating Temp.      : {r['avg_temp']:.2f} C
  > Mean Vibration Ampl.      : {r['avg_vib']:.3f} mm/s

[ 3. DETAILED ASSET BREAKDOWN ]
{r['machine_details']}

[ 4. EXECUTIVE SUMMARY & RECOMMENDATIONS ]
Based on the real-time aggregation of your selected assets, the temporal feature engineering models have processed current cycles. Adjustments to anomaly Z-score thresholds should be considered if repair rates exceed expected baselines. Immediate proactive maintenance is recommended for any parts flagged in the anomaly count.
============================================================
               END OF AUTOMATED REPORT
============================================================
"""
        st.markdown("### Export Options")
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            with st.expander("📄 View Raw Report Document"): st.text(report_text)
        with btn_c2:
            pdf_bytes = generate_pdf_bytes(report_text)
            if pdf_bytes:
                st.download_button(label="📥 Download Report as PDF", data=pdf_bytes, file_name=f"MacMod_Report_{r['mac']}_{r['mo']}{r['yr']}.pdf", mime="application/pdf", use_container_width=True, type="primary")
            else:
                st.download_button(label="📥 Download Report as TXT", data=report_text, file_name=f"MacMod_Report_{r['mac']}_{r['mo']}{r['yr']}.txt", mime="text/plain", use_container_width=True, type="primary")
                st.caption("ℹ️ System note: `fpdf` python library not detected. Defaulting to high-fidelity TXT export. Install fpdf for PDF support.")

# ===================== 主页面：Settings =====================
def render_settings():
    st.markdown('<div style="margin-bottom:1.5rem;"><div class="macmod-title">System Configuration</div></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        with st.container(border=True):
            st.markdown('<div class="macmod-title" style="font-size:16px;">AI Tuning</div>', unsafe_allow_html=True)
            a, b = st.columns(2); a.number_input("Alert Threshold", 1, 500, 30); b.number_input("Z-Score Limit", 0.1, 10.0, 3.5)
        with st.container(border=True):
            st.markdown('<div class="macmod-title" style="font-size:16px;">Data & Upload Configuration</div>', unsafe_allow_html=True)
            st.checkbox("Auto-Retrain Models", True)
            ds_options = ["FD001", "FD002", "FD003", "FD004"]
            current_idx = ds_options.index(st.session_state.sys_priority_ds)
            new_ds = st.selectbox("System Priority Dataset (C-MAPSS Base)", ds_options, index=current_idx)
            if st.button("Confirm Dataset Selection", type="primary", use_container_width=True):
                st.session_state.sys_priority_ds = new_ds
                add_log(f"Changed priority dataset to {new_ds}", "config_update")
                st.success(f"System dataset profile successfully switched to {new_ds}.")
    with c2:
        with st.container(border=True):
            st.markdown('<div class="macmod-title" style="font-size:16px;">Notifications</div>', unsafe_allow_html=True)
            st.checkbox("Critical Alerts", True); st.checkbox("PDF Reports", False)
            if st.button("Save Configurations", type="primary", use_container_width=True): st.success("Saved.")

# ===================== 主页面：Account (极简专业化还原) =====================
def render_account():
    acc, logs = get_active_account(), [l for l in st.session_state.system_logs if l["userId"] == get_active_account()["id"]]
    
    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
        <div style="display:flex; align-items:center; gap:8px; font-size:20px; font-weight:700; color:#0f172a;">
            <div style="width:22px; height:22px; color:#2563eb;">{SVG_ICONS["user"]}</div> Profile Details
        </div>
        <div class="macmod-subtitle" style="margin-top:4px;">Your MacMod account information</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    
    name_parts = acc["name"].split()
    initials = (name_parts[0][0] + name_parts[1][0]).upper() if len(name_parts) >= 2 else (name_parts[0][:2].upper() if name_parts else "??")
    avatar_html = f"""<div style="width:80px;height:80px;flex-shrink:0;border-radius:999px;background:#2563eb;display:flex;align-items:center;justify-content:center;font-size:36px;font-weight:700;color:white;">{initials}</div>"""

    with c1:
        st.markdown(f"""
        <div class="macmod-card" style="padding: 2rem;">
            <div style="display:flex;align-items:flex-start;gap:1.5rem; margin-bottom: 2rem;">
                {avatar_html}
                <div style="flex:1; min-width:0;">
                    <div class="break-text" style="font-size:28px;font-weight:800;color:#0f172a;line-height:1.2;">{acc["name"]}</div>
                    <div class="break-text" style="font-size:16px;color:#64748b;margin-top:6px; font-weight: 500;">{acc["position"]}</div>
                    <span class="macmod-badge" style="margin-top:12px;background:#eff6ff;color:#2563eb;border:1px solid #bfdbfe; font-size: 12px; padding: 4px 10px;">Active Account</span>
                </div>
            </div>
            <hr class="macmod-sep" style="margin: 2rem 0; opacity: 0.5;" />
            <div style="display:flex; flex-wrap:wrap; gap:1.5rem;">
                <div style="flex: 1 1 45%; min-width: 0; display: flex; align-items: flex-start; gap: 0.75rem;">
                    <div style="width: 20px; height: 20px; color: #64748b; margin-top: 2px;">{SVG_ICONS["mail"]}</div>
                    <div><div style="color:#64748b;font-size:13px;font-weight:600;margin-bottom:6px;">Email Address</div><div class="break-text" style="color:#0f172a;font-size:15px;font-weight:700;">{acc["email"]}</div></div>
                </div>
                <div style="flex: 1 1 45%; min-width: 0; display: flex; align-items: flex-start; gap: 0.75rem;">
                    <div style="width: 20px; height: 20px; color: #64748b; margin-top: 2px;">{SVG_ICONS["briefcase"]}</div>
                    <div><div style="color:#64748b;font-size:13px;font-weight:600;margin-bottom:6px;">Job Position</div><div class="break-text" style="color:#0f172a;font-size:15px;font-weight:700;">{acc["position"]}</div></div>
                </div>
                <div style="flex: 1 1 45%; min-width: 0; display: flex; align-items: flex-start; gap: 0.75rem;">
                    <div style="width: 20px; height: 20px; color: #64748b; margin-top: 2px;">{SVG_ICONS["calendar"]}</div>
                    <div><div style="color:#64748b;font-size:13px;font-weight:600;margin-bottom:6px;">Registration Date</div><div class="break-text" style="color:#0f172a;font-size:15px;font-weight:700;">{acc.get("registeredDate",'2024-01-15')}</div></div>
                </div>
                <div style="flex: 1 1 45%; min-width: 0; display: flex; align-items: flex-start; gap: 0.75rem;">
                    <div style="width: 20px; height: 20px; color: #64748b; margin-top: 2px;">{SVG_ICONS["shield"]}</div>
                    <div><div style="color:#64748b;font-size:13px;font-weight:600;margin-bottom:6px;">Account ID</div><div class="break-text" style="color:#0f172a;font-size:15px;font-weight:700;">{acc["id"]}</div></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""<div class="macmod-card-light"><div class="macmod-title" style="font-size:16px;margin-bottom:1rem;">Account Status</div><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;"><span style="color:#64748b;font-weight:600;font-size:14px;">Status</span><span class="macmod-badge" style="background:#dcfce7;color:#166534;border:1px solid #bbf7d0;">Active</span></div><div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;margin-bottom:12px;"><span style="color:#64748b;font-weight:600;font-size:14px;white-space:nowrap;">Role</span><span class="break-text" style="color:#0f172a;font-weight:700;font-size:14px;text-align:right;">{acc["position"]}</span></div><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;"><span style="color:#64748b;font-weight:600;font-size:14px;">Access Level</span><span class="macmod-badge" style="background:#f1f5f9;color:#334155;border:1px solid #e2e8f0;">Full</span></div></div>""", unsafe_allow_html=True)
        st.write("")
        
        # 极简复原：无 Emoji 的标准企业级按钮，回归到 Status 下方紧凑排列
        if st.button("Add New Account", use_container_width=True): st.session_state.active_tab = "add_account"; st.rerun()
        if st.button("Change Password", use_container_width=True): st.session_state.active_tab = "change_pwd"; st.rerun()

    st.write(""); st.write("")
    log_html = '<div class="macmod-card"><div class="macmod-title" style="font-size:18px;margin-bottom:1rem;">Recent Activity</div>'
    if not logs: log_html += '<div style="color:#64748b;">No recent activity found.</div>'
    for log in logs[:10]:
        mins = int((datetime.utcnow() - datetime.fromisoformat(log["timestamp"])).total_seconds() // 60)
        log_html += f"""<div style="border-radius:0.75rem;border:1px solid #e2e8f0;padding:0.8rem 1rem;margin-bottom:0.6rem;background:#f8fafc;"><div class="break-text" style="font-size:14px;font-weight:700;color:#0f172a;">{log["action"]}</div><div style="font-size:12px;color:#64748b;margin-top:4px;">{f"{mins} min ago" if mins<60 else f"{mins//60} h ago"}</div></div>"""
    log_html += '</div>'
    st.markdown(log_html, unsafe_allow_html=True)

# ===================== 主入口与路由 =====================
def main():
    if not st.session_state.is_authenticated: return render_login()
    render_sidebar()
    tab = st.session_state.active_tab
    if tab == "machines": render_machines()
    elif tab == "maintenance": render_maintenance()
    elif tab == "reports": render_reports()
    elif tab == "settings": render_settings()
    elif tab == "account": render_account()
    elif tab == "upload_data": render_upload_data()
    elif tab == "add_machine": render_add_machine()
    elif tab == "manual_schedule": render_manual_schedule()
    elif tab == "add_account": render_add_account()
    elif tab == "change_pwd": render_change_password()
    elif tab == "map": render_map()
    elif tab == "calendar": render_calendar()
    else: render_dashboard_home()


# ===================== 单元测试 (Unit Tests) =====================
class TestMacModApp(unittest.TestCase):
    
    def setUp(self):
        st.session_state.clear()
        init_state()

    def test_dynamic_avatar_initials(self):
        """【动态头像渲染测试】确保系统能正确动态抽取任何用户名的首字母，无论输入多奇怪"""
        
        # 针对一个单词的用户名
        acc1 = {"id": "1", "name": "Admin", "email": "a@b.com", "position": "Tech", "registeredDate": "2026", "password": "123"}
        st.session_state.accounts = [acc1]
        st.session_state.active_account_id = "1"
        current_acc = get_active_account()
        name_parts1 = current_acc["name"].split()
        initials1 = (name_parts1[0][0] + name_parts1[1][0]).upper() if len(name_parts1) >= 2 else (name_parts1[0][:2].upper() if name_parts1 else "??")
        self.assertEqual(initials1, "AD", "单单词应截取前两字母")

        # 针对两个单词的用户名
        acc2 = {"id": "2", "name": "John Doe", "email": "a@b.com", "position": "Tech", "registeredDate": "2026", "password": "123"}
        st.session_state.accounts = [acc2]
        st.session_state.active_account_id = "2"
        current_acc2 = get_active_account()
        name_parts2 = current_acc2["name"].split()
        initials2 = (name_parts2[0][0] + name_parts2[1][0]).upper() if len(name_parts2) >= 2 else (name_parts2[0][:2].upper() if name_parts2 else "??")
        self.assertEqual(initials2, "JD", "双单词应提取各自首字母大写")

    def test_invalid_account_id_graceful_fallback(self):
        """【边界情况测试】如果 active_account_id 指向不存在的 ID，系统是否优雅降级到默认帐户"""
        st.session_state.active_account_id = "non_existent_id"
        acc = get_active_account()
        self.assertEqual(acc["id"], "1773569861650", "回退帐户ID错误")
        self.assertEqual(acc["name"], "System Admin", "找不到ID时应回退到默认帐户")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sys.argv.pop() 
        unittest.main()
    else:
        main()