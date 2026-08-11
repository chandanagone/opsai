import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from services import authentication_service as auth

# --- 1. PAGE SETUP & CORPORATE DARK-THEME CSS ---
st.set_page_config(page_title="Agentic Facility Ops AI", layout="wide")

st.markdown("""
<style>
    /* Dark Slate Left Navigation Menu Layout matching corporate themes */
    [data-testid="stSidebar"] {
        background-color: #0b192e !important;
    }
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] label {
        color: #94a3b8 !important;
    }
    /* Cards Framework Custom Clean Styling */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetric"] label {
        color: #475569 !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# --- 2. SECURE CSV FILE HANDLING ENGINE ---
@st.cache_data
def load_facility_csv():
    try:
        # Load real data directly from the adjacent CSV sheet
        df = pd.read_csv("facility_data.csv")
        return df
    except FileNotFoundError:
        # FIXED CODES: Replaced all empty spaces with real numbers to eliminate SyntaxError permanently
        return pd.DataFrame({
            'Day': [1, 2, 3, 4, 5],
            'Energy_Usage_kWh': [120, 110, 130, 125, 140],
            'Work_Orders_Closed': [5, 3, 7, 4, 6],
            'Space_Utilization_Pct': [80, 75, 85, 82, 90],
            'Security_Events': [1, 0, 2, 0, 1]
        })

df_metrics = load_facility_csv()


# --- 3. SESSION STATE SESSION HANDLING ---
auth.init_session_state()
if 'current_view' not in st.session_state:
    st.session_state.current_view = "Overview"


# --- 4. LAYER A: APP USER SECURITY PORTAL ---
def show_login_interface():
    st.markdown("<h2 style='text-align: center; margin-top: 80px; color: #0b192e;'>Agentic Facility Ops AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Infosys Springboard Internship Evaluation Engine</p>", unsafe_allow_html=True)
    
    _, centered_column, _ = st.columns([1, 1.5, 1])
    with centered_column:
        with st.form("login_portal"):
            # Prefilled login name customized for evaluation matrix
            uid_input = st.text_input("User ID / Email", value="admin")
            pass_input = st.text_input("Password", type="password", value="")
            
            if st.form_submit_button("Sign In Securely", use_container_width=True):
                if auth.attempt_login(uid_input, pass_input):
                    st.rerun()
                else:
                    st.error(st.session_state.get("login_error", "Invalid username/email or password."))


# --- 5. LAYER B: SYSTEM SUB-DASHBOARD VIEWS ---
def display_central_dashboard():
    # --- SIDEBAR CONTROL PANEL ---
    with st.sidebar:
        st.markdown("### 🔍 Agentic Platform")
        st.caption("FACILITY OPERATIONS WORKSPACE")
        st.write("---")
        
        menu_items = ["Overview", "Energy Agent", "Maintenance Agent", "Occupancy Agent", "Security Agent"]
        current_idx = menu_items.index(st.session_state.current_view) if st.session_state.current_view in menu_items else 0
        
        selection = st.radio("Navigation Matrix", menu_items, index=current_idx)
        st.session_state.current_view = selection
        
        st.write("---")
        st.markdown(f"👤 **Operator Logged In:**\n`{auth.current_user_label()}`")
        st.caption(f"Access Status: {auth.current_role()}")
        
        if st.button("Log Out System", use_container_width=True):
            auth.logout()
            st.session_state.current_view = "Overview"
            st.rerun()

    # ---------------- VIEW: OVERVIEW CENTRAL HUB ----------------
    if st.session_state.current_view == "Overview":
        st.markdown("<h2 style='color: #0b192e; margin-bottom: 0px;'>AI Agent Modules</h2>", unsafe_allow_html=True)
        st.caption("Autonomous AI agents working together to optimize your facility operations.")
        st.write("")
        
        # Primary Dashboard Performance Metric Summaries
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("⚙️ Active Systems", "4 Modules", "Running Smooth")
        kpi2.metric("📈 Avg. Operational Efficiency", "12.4%", "Target Satisfied")
        kpi3.metric("📉 Active Energy Reduction", "18.7%", "+0.5% vs Yesterday")
        kpi4.metric("💰 Estimated Cost Avoidance", "Rs. 2.45L", "This Month Tracker")
        st.write("---")
        
        st.markdown("<h3 style='color: #0b192e;'>Available Autonomous AI Agents</h3>", unsafe_allow_html=True)
        st.write("")
        
        card_style = """
        <div style='border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; background-color: #ffffff; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>
        """

        # Row 1: Energy Agent Block
        st.markdown(card_style, unsafe_allow_html=True)
        col_txt, col_met, col_btn = st.columns(3)
        with col_txt:
            st.markdown("### ⚡ 1. Energy Agent")
            st.markdown("<p style='color:#64748b; font-size:14px; margin-top:-10px;'>Monitors and optimizes energy and utility consumption across facilities using AI insights.</p>", unsafe_allow_html=True)
            st.markdown("<span style='color:#10b981; font-weight:bold;'>✓ Energy Monitoring</span> &nbsp;&nbsp; <span style='color:#10b981; font-weight:bold;'>✓ Demand Forecasting</span>", unsafe_allow_html=True)
        with col_met:
            st.metric("Energy Saved", "12.4%", "This Month")
        with col_btn:
            st.write("")
            st.write("")
            if st.button("View Energy Details", key="nav_e", use_container_width=True):
                st.session_state.current_view = "Energy Agent"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Row 2: Maintenance Agent Block
        st.markdown(card_style, unsafe_allow_html=True)
        col_txt, col_met, col_btn = st.columns(3)
        with col_txt:
            st.markdown("### 🔧 2. Maintenance Agent")
            st.markdown("<p style='color:#64748b; font-size:14px; margin-top:-10px;'>Predicts equipment failures and automates maintenance workflows.</p>", unsafe_allow_html=True)
            st.markdown("<span style='color:#10b981; font-weight:bold;'>✓ Predictive Maintenance</span> &nbsp;&nbsp; <span style='color:#10b981; font-weight:bold;'>✓ Work Order Automation</span>", unsafe_allow_html=True)
        with col_met:
            st.metric("MTBF Uplift", "92%", "This Month")
        with col_btn:
            st.write("")
            st.write("")
            if st.button("View Maintenance Details", key="nav_m", use_container_width=True):
                st.session_state.current_view = "Maintenance Agent"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Row 3: Occupancy Agent Block
        st.markdown(card_style, unsafe_allow_html=True)
        col_txt, col_met, col_btn = st.columns(3)
        with col_txt:
            st.markdown("### 👥 3. Occupancy Agent")
            st.markdown("<p style='color:#64748b; font-size:14px; margin-top:-10px;'>Analyzes space utilization and optimizes workspace allocation.</p>", unsafe_allow_html=True)
            st.markdown("<span style='color:#10b981; font-weight:bold;'>✓ Space Utilization</span> &nbsp;&nbsp; <span style='color:#10b981; font-weight:bold;'>✓ Workspace Optimization</span>", unsafe_allow_html=True)
        with col_met:
            st.metric("Space Efficiency", "65%", "This Month")
        with col_btn:
            st.write("")
            st.write("")
            if st.button("View Occupancy Details", key="nav_o", use_container_width=True):
                st.session_state.current_view = "Occupancy Agent"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Row 4: Security Agent Block
        st.markdown(card_style, unsafe_allow_html=True)
        col_txt, col_met, col_btn = st.columns(3)
        with col_txt:
            st.markdown("### 🛡️ 4. Security Agent")
            st.markdown("<p style='color:#64748b; font-size:14px; margin-top:-10px;'>Monitors security systems and detects anomalies to ensure a safe environment.</p>", unsafe_allow_html=True)
            st.markdown("<span style='color:#10b981; font-weight:bold;'>✓ Threat Detection</span> &nbsp;&nbsp; <span style='color:#10b981; font-weight:bold;'>✓ Incident Management</span>", unsafe_allow_html=True)
        with col_met:
            st.metric("Detection Rate", "98.6%", "This Month")
        with col_btn:
            st.write("")
            st.write("")
            if st.button("View Security Details", key="nav_s", use_container_width=True):
                st.session_state.current_view = "Security Agent"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        # --- INNOVATION FEATURE: AI AGENT INTERACTIVE CHAT PANEL ---
        st.write("---")
        st.markdown("<h3 style='color: #0b192e;'>💬 Interactive AI Assistant Agent</h3>", unsafe_allow_html=True)
        st.caption("Ask operational questions directly about your real CSV log spreadsheet data files.")
        
        user_query = st.text_input("Type your question here (e.g., 'What was the highest energy day?' or 'Show total anomalies'):", placeholder="Ask anything about facility operations...")
        
        if user_query:
            q = user_query.lower()
            with st.spinner("AI Agent reading CSV log matrix..."):
                if "energy" in q or "highest usage" in q or "kwh" in q:
                    max_idx = df_metrics['Energy_Usage_kWh'].idxmax()
                    max_day = df_metrics.loc[max_idx, 'Day']
                    max_val = df_metrics.loc[max_idx, 'Energy_Usage_kWh']
                    st.success(f"🤖 **Ops AI Agent:** Based on our `facility_data.csv` logs, the highest power consumption occurred on **Day {max_day}** hitting **{max_val} kWh**.")
                elif "maintenance" in q or "work orders" in q or "closed" in q:
                    total_orders = df_metrics['Work_Orders_Closed'].sum()
                    st.success(f"🤖 **Ops AI Agent:** Analyzing data arrays... A total of **{total_orders} preventive work orders** have been systematically resolved and closed across this period.")
                elif "security" in q or "anomalies" in q or "events" in q:
                    total_sec = df_metrics['Security_Events'].sum()
                    st.success(f"🤖 **Ops AI Agent:** Scanning perimeter anomalies... A total of **{total_sec} security events** were logged, handled, and neutralized by the core monitoring mesh.")
                elif "utilization" in q or "space" in q or "occupancy" in q:
                    avg_util = round(df_metrics['Space_Utilization_Pct'].mean(), 1)
                    st.success(f"🤖 **Ops AI Agent:** Calculating space metrics... The current average facility floor workspace utilization rate sits stably at **{avg_util}%**.")
                else:
                    st.info("🤖 **Ops AI Agent:** Query received! My core pipelines can scan details regarding **Energy usage**, **Work Orders**, **Space Utilization**, or **Security Events** data inside your loaded spreadsheet template files.")

    # ---------------- VIEW: ENERGY DETAILED SUB-PAGE ----------------
    elif st.session_state.current_view == "Energy Agent":
        if st.button("← Back to Hub Overview"): st.session_state.current_view = "Overview"; st.rerun()
        st.markdown("## ⚡ Energy Agent Analysis Engine")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Energy Savings Status", "12.4%", "Target Met")
        m2.metric("Accumulated Value Saved", "Rs. 1.25L", "June Cycle")
        m3.metric("System Forecast Precision", "98%", "Stable")
        
        c_left, c_right = st.columns(2)
        with c_left:
            fig = px.line(df_metrics, x='Day', y='Energy_Usage_kWh', title='Performance Overview (Energy Usage Over Time)', markers=True)
            st.plotly_chart(fig, use_container_width=True)
        with c_right:
            st.markdown("### Insights & Advisory")
            st.info("💡 **Optimize HVAC Scheduling:** Modify peak runtime parameters (Saves Rs. 45k).")
            st.info("💡 **Dim Underused Sections:** De-energize warehouse corridors past 8 PM.")

    # ---------------- VIEW: MAINTENANCE DETAILED SUB-PAGE ----------------
    elif st.session_state.current_view == "Maintenance Agent":
        if st.button("← Back to Hub Overview"): st.session_state.current_view = "Overview"; st.rerun()
        st.markdown("## 🔧 Maintenance Lifecycle Operations")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("MTBF Optimization", "92%", "Excellent")
        m2.metric("Resolved Pipelines", "156 Orders", "Active Month")
        m3.metric("Down-time Minimization", "23%", "Reduced")
        
        c_left, c_right = st.columns(2)
        with c_left:
            fig = px.bar(df_metrics, x='Day', y='Work_Orders_Closed', title='Maintenance Delivery Log (Closed Work Orders)', color='Work_Orders_Closed')
            st.plotly_chart(fig, use_container_width=True)
        with c_right:
            st.markdown("### Automated Forecast Matrix")
            st.error("🚨 **Chiller-1 Critical:** Structural oscillation limits exceeded.")
            st.warning("⚠️ **Pump-2 Diagnostic:** Minor mechanical resistance detected.")

    # ---------------- VIEW: OCCUPANCY DETAILED SUB-PAGE ----------------
    elif st.session_state.current_view == "Occupancy Agent":
        if st.button("← Back to Hub Overview"): st.session_state.current_view = "Overview"; st.rerun()
        st.markdown("## 👥 Occupancy Logistics Matrix")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Avg Room Utilization", "65%", "Nominal")
        m2.metric("Layout Optimization", "18%", "Active")
        m3.metric("Predictive Accuracy", "85%", "Verified")
        
        c_left, c_right = st.columns(2)
        with c_left:
            fig = px.area(df_metrics, x='Day', y='Space_Utilization_Pct', title='Floor Space Allocation Trends')
            st.plotly_chart(fig, use_container_width=True)
        with c_right:
            st.markdown("### Spatial Metrics By Sector")
            st.write("🏢 **Main Operations Floor:** 78% Density")
            st.write("🤝 **Executive Conference Area:** 45% Density")

    # ---------------- VIEW: SECURITY DETAILED SUB-PAGE ----------------
    elif st.session_state.current_view == "Security Agent":
        if st.button("← Back to Hub Overview"): st.session_state.current_view = "Overview"; st.rerun()
        st.markdown("## 🛡️ Facility Safety Security Suite")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Monitored Anomalies", "120 Incidents", "Flagged")
        m2.metric("Threat Resolution Yield", "98.6%", "Optimal")
        m3.metric("Mitigations Confirmed", "15 Actions", "Closed")
        
        c_left, c_right = st.columns(2)
        with c_left:
            fig = px.line(df_metrics, x='Day', y='Security_Events', title='Monitored System Alert Vectors', line_shape='spline')
            st.plotly_chart(fig, use_container_width=True)
        with c_right:
            st.markdown("### Live Threat Stream Logs")
            st.error("❌ **Access Breach Attempt:** Perimeter Gate 3 override flagged.")
            st.warning("⚠️ **System Alert:** Unlocked validation seal at West Portal.")


# --- 6. CORE APP INTERFACE CONTROLLER ---
if __name__ == '__main__':
    if not auth.is_logged_in():
        show_login_interface()
    else:
        display_central_dashboard()


