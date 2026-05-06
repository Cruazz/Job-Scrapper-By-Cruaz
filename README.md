# 🚀 AI Job Aggregator & Digest System

A professional, multi-tenant automated job scraper and dashboard designed for modern job seekers. This system aggregates remote job listings from multiple sources, scores them based on user preferences, and delivers a daily email digest.

## ✨ Features

- **Multi-Source Aggregation**: Automatically fetches jobs from *We Work Remotely* and *Remotive API*.
- **Intelligent Matching**: Uses a weighted scoring algorithm to match jobs based on keywords, location, and salary.
- **Interactive Dashboard**: Built with Streamlit, featuring:
  - **Elegant Cards View**: Modern UI for browsing job listings.
  - **Live Analytics**: Visual insights into job trends and sources.
  - **Application Tracking**: Manage your application status (Applied, Interviewing, etc.).
- **Multi-Tenant Isolation**: Unique URL-based access keys to keep your data and settings private.
- **Email Digest**: Daily automated emails with the best matches of the day.
- **Dynamic Configuration**: Change your search criteria and email settings directly from the dashboard.

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: Python 3.11+
- **Database**: SQLite with SQLAlchemy ORM
- **Visualization**: Plotly
- **Emailing**: Jinja2 & Smtplib

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/job-aggregator.git
cd job-aggregator
```

### 2. Install dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file based on `.env.example`:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
```

### 4. Run the application
```bash
# Start the dashboard
streamlit run app.py
```

## 📸 Dashboard Preview
*(Add screenshots here after deploying!)*

## 🛡️ License
Distributed under the MIT License.

---
Built with ❤️ by [Your Name]
