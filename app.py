import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from models.database import JobListing, SystemSettings, init_db
from config.settings import settings
import plotly.express as px
from datetime import datetime
import json
import sys

# Initialize Database
init_db()

# Page config
st.set_page_config(
    page_title="Job Aggregator Multi-Tenant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        background-color: rgba(128, 128, 128, 0.05);
        min-height: 120px;
    }
    .job-card {
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #2980b9;
        margin-bottom: 10px;
        background-color: rgba(128, 128, 128, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_engine():
    return create_engine(f"sqlite:///./{settings.database_path}")

engine = get_engine()
SessionLocal = sessionmaker(bind=engine)

def load_settings(user_key):
    db = SessionLocal()
    s = db.query(SystemSettings).filter(SystemSettings.user_key == user_key).first()
    db.close()
    if not s:
        return {
            "keywords": [],
            "locations": [],
            "min_salary": 0,
            "target_email": ""
        }
    return {
        "keywords": json.loads(s.keywords),
        "locations": json.loads(s.locations),
        "min_salary": s.min_salary,
        "target_email": s.target_email
    }

def save_settings(user_key, k, l, s_val, e):
    db = SessionLocal()
    s = db.query(SystemSettings).filter(SystemSettings.user_key == user_key).first()
    if not s:
        s = SystemSettings(user_key=user_key)
        db.add(s)
    s.keywords = json.dumps(k)
    s.locations = json.dumps(l)
    s.min_salary = s_val
    s.target_email = e
    s.updated_at = datetime.utcnow()
    db.commit()
    db.close()

def load_data(user_key):
    db = SessionLocal()
    jobs = db.query(JobListing).filter(JobListing.user_key == user_key).all()
    db.close()
    if not jobs:
        return pd.DataFrame()
    df = pd.DataFrame([{
        'ID': j.id, 'Title': j.title, 'Company': j.company, 'Location': j.location,
        'Source': j.source, 'Score': j.match_score, 'Status': j.status,
        'Description': j.description, 'Date': j.scraped_at, 'URL': j.url
    } for j in jobs])
    return df

def update_status(job_id, new_status):
    db = SessionLocal()
    db.execute(update(JobListing).where(JobListing.id == job_id).values(status=new_status))
    db.commit()
    db.close()

import secrets
import string

# Sidebar - User Access Logic
def get_user_key():
    # Check if key exists in URL
    if "user" in st.query_params:
        return st.query_params["user"]
    
    # If not, generate a new random one
    new_key = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    st.query_params["user"] = new_key
    return new_key

user_access_key = get_user_key()

# Main UI setup
st.sidebar.title("🔐 Secure Access")
st.sidebar.info(f"Your Unique Key: **{user_access_key}**")
st.sidebar.caption("Bookmark this URL to return to your data!")

if st.sidebar.button("Reset / New Account"):
    # Clear query params to trigger new key generation
    st.query_params.clear()
    st.rerun()

# --- Main App Logic ---
df = load_data(user_access_key)
current_settings = load_settings(user_access_key)

st.sidebar.markdown(f"**Current User:** `{user_access_key}`")
st.sidebar.markdown("---")

# Metrics & Tabs...
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
today_jobs = 0
applied_jobs = 0
avg_score = 0

if not df.empty:
    today_jobs = len(df[df['Date'].dt.date == datetime.now().date()])
    applied_jobs = len(df[df['Status'] == 'Applied'])
    avg_score = df['Score'].mean()

metrics = [
    ("Total Jobs", len(df), "💼"),
    ("New Today", today_jobs, "✨"),
    ("Applied", applied_jobs, "📨"),
    ("Match Score", f"{avg_score:.2f}", "🎯")
]

for col, (label, value, icon) in zip([m_col1, m_col2, m_col3, m_col4], metrics):
    with col:
        st.markdown(f"""
            <div style="background: rgba(128, 128, 128, 0.05); padding: 20px; border-radius: 10px; border: 1px solid rgba(128, 128, 128, 0.2); height: 140px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                <div style="font-size: 28px; margin-bottom: 5px;">{icon}</div>
                <div style="font-size: 14px; opacity: 0.8; font-weight: 500;">{label}</div>
                <div style="font-size: 26px; font-weight: bold;">{value}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📋 Job Explorer", "📊 Analytics", "⚙️ Control Center"])

with tab1:
    if df.empty:
        st.warning("No jobs found for this key. Run the scraper in 'Control Center'!")
    else:
        st.subheader("Explore Your Opportunities")
        search_query = st.text_input("🔍 Search titles or companies", "")
        table_df = df[(df['Title'].str.contains(search_query, case=False) | df['Company'].str.contains(search_query, case=False))].sort_values(by='Score', ascending=False)
        
        view_mode = st.radio("View Mode", ["Elegant Cards", "Data Table"], horizontal=True, label_visibility="collapsed")

        if view_mode == "Elegant Cards":
            for _, job in table_df.iterrows():
                status_colors = {"New": "#3498db", "Applied": "#2ecc71", "Interviewing": "#f1c40f", "Rejected": "#e74c3c", "Offer": "#9b59b6"}
                s_color = status_colors.get(job['Status'], "#95a5a6")
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"#### {job['Title']}")
                        st.markdown(f"🏢 **{job['Company']}** | 📍 {job['Location']} | 📅 {job['Date'].strftime('%d %b, %H:%M')}")
                        st.progress(job['Score'], text=f"Match Score: {int(job['Score']*100)}%")
                    with c2:
                        st.markdown(f'<div style="background:{s_color}; color:white; padding:5px 10px; border-radius:15px; text-align:center; font-size:12px; font-weight:bold; margin-bottom:10px;">{job["Status"]}</div>', unsafe_allow_html=True)
                        st.link_button("Apply Now ↗️", job['URL'], use_container_width=True)
                    with st.expander("🔍 View Job Details"):
                        st.markdown(job.get('Description', 'No description available.'), unsafe_allow_html=True)

        else:
            st.data_editor(table_df[['Title', 'Company', 'Location', 'Score', 'Status', 'Date', 'URL']], hide_index=True, use_container_width=True)

with tab2:
    if df.empty: st.info("Run scraper to see analytics")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(px.pie(df['Source'].value_counts().reset_index(), names='Source', values='count', title="Distribution by Source"), use_container_width=True)
        with col_b:
            st.plotly_chart(px.bar(df['Company'].value_counts().head(10).reset_index(), x='count', y='Company', orientation='h', title="Top 10 Hiring Companies"), use_container_width=True)

with tab3:
    st.subheader("Personal System Configuration")
    if "settings_saved" in st.session_state:
        st.success("✅ Settings saved successfully!")
        del st.session_state["settings_saved"]

    with st.form("settings_form"):
        new_email = st.text_input("Target Email for Digest", value=current_settings['target_email'])
        new_keywords = st.text_area("Keywords (comma separated)", value=", ".join(current_settings['keywords']))
        new_locations = st.text_area("Locations (comma separated)", value=", ".join(current_settings['locations']))
        new_salary = st.number_input("Minimum Salary", value=current_settings['min_salary'])
        
        if st.form_submit_button("💾 Save Settings"):
            k_list = [x.strip() for x in new_keywords.split(",") if x.strip()]
            l_list = [x.strip() for x in new_locations.split(",") if x.strip()]
            save_settings(user_access_key, k_list, l_list, new_salary, new_email)
            st.session_state["settings_saved"] = True
            st.rerun()
    
    st.markdown("---")
    
    # Placeholder for logs if they exist in session state
    if "scraper_logs" in st.session_state:
        st.subheader("Last Scraper Execution Log")
        st.code(st.session_state["scraper_logs"])
        if st.button("Clear Logs"):
            del st.session_state["scraper_logs"]
            st.rerun()

    if st.button("🚀 Run Scraper for This Key", use_container_width=True):
        with st.spinner(f"Scraping for user: {user_access_key}..."):
            import subprocess
            # Use subprocess to run the main pipeline
            result = subprocess.run([sys.executable, "main.py", "--user-key", user_access_key], capture_output=True, text=True)
            
            # Save logs to session state so they survive the rerun
            st.session_state["scraper_logs"] = result.stdout + result.stderr
            st.success("Scraper finished successfully!")
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Job Aggregator Multi-Tenant v2.0")
