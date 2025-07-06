# -------------------- Imports --------------------
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import base64

# -------------------- Setup --------------------
st.set_page_config(page_title="AI Health Assistant", layout="wide")

# Initialize session state
if "health_history" not in st.session_state:
    st.session_state.health_history = []
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}

# -------------------- Helper: PDF Generator --------------------
def generate_pdf_report(analysis_data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y, "AI Health Assistant Report")
    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(100, y, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 20
    c.drawString(100, y, f"Risk Level: {analysis_data['risk_level'].title()}")
    y -= 30

    c.drawString(100, y, "Summary:")
    y -= 20
    for line in analysis_data["summary"].split("\n"):
        c.drawString(120, y, line)
        y -= 15

    y -= 20
    c.drawString(100, y, "Recommendations:")
    y -= 15
    for item in analysis_data["recommendations"]:
        c.drawString(120, y, f"- {item}")
        y -= 15

    y -= 20
    c.drawString(100, y, "When to Seek Help:")
    y -= 15
    for item in analysis_data["when_to_seek_help"]:
        c.drawString(120, y, f"- {item}")
        y -= 15

    c.save()
    buffer.seek(0)
    return buffer

# -------------------- AI Analysis Logic --------------------
def analyze_health_data(symptoms, age, gender, medical_history):
    time.sleep(1)
    risk = "low"
    if "severe" in symptoms.lower():
        risk = "high"
    elif "moderate" in symptoms.lower():
        risk = "moderate"
    return {
        "risk_level": risk,
        "summary": f"Based on symptoms and profile (Age: {age}, Gender: {gender}), risk appears {risk.upper()}.\nPlease monitor and consult a doctor if needed.",
        "recommendations": ["Stay hydrated", "Get enough rest", "Avoid stress", "Eat healthy"],
        "when_to_seek_help": ["If symptoms worsen", "If new symptoms appear"]
    }

# -------------------- Sidebar Navigation --------------------
page = st.sidebar.selectbox("Navigation", ["Home", "Health Analysis", "Dashboard", "User Profile", "Resources"])

# -------------------- Page: Home --------------------
if page == "Home":
    st.title("AI Health Assistant")
    st.markdown("This app provides general health guidance based on AI analysis.")
    st.info("This tool does not replace medical advice. Contact a healthcare provider for medical emergencies.")

# -------------------- Page: Health Analysis --------------------
elif page == "Health Analysis":
    st.header("Health Analysis")

    with st.form("form"):
        symptoms = st.text_area("Describe your symptoms")
        age = st.number_input("Age", 1, 120, 25)
        gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other"])
        history = st.text_area("Medical History (optional)")
        submitted = st.form_submit_button("Analyze")

        if submitted:
            if not symptoms.strip() or gender == "Select":
                st.error("Please enter symptoms and select gender.")
            else:
                with st.spinner("Analyzing your health data..."):
                    result = analyze_health_data(symptoms, age, gender, history)
                    st.session_state.analysis_results = result
                    st.session_state.health_history.append({
                        "date": datetime.now(),
                        "symptoms": symptoms,
                        "age": age,
                        "gender": gender,
                        "risk_level": result["risk_level"]
                    })

    # Show analysis
    if st.session_state.analysis_results:
        result = st.session_state.analysis_results
        st.subheader(f"Risk Level: {result['risk_level'].title()}")
        st.success(result["summary"])
        st.write("Recommendations:")
        for rec in result["recommendations"]:
            st.markdown(f"- {rec}")
        st.write("When to Seek Help:")
        for r in result["when_to_seek_help"]:
            st.markdown(f"- {r}")

        # Export
        st.markdown("Export Report")
        if st.button("Download PDF Report"):
            pdf = generate_pdf_report(result)
            b64 = base64.b64encode(pdf.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="health_report.pdf">Download Report</a>'
            st.markdown(href, unsafe_allow_html=True)

# -------------------- Page: Dashboard --------------------
elif page == "Dashboard":
    st.header("Health Dashboard")

    if st.session_state.health_history:
        df = pd.DataFrame(st.session_state.health_history)
        df['date'] = df['date'].dt.strftime("%Y-%m-%d %H:%M")
        st.dataframe(df)

        # Risk over time
        df['risk_level_numeric'] = df['risk_level'].map({'low': 1, 'moderate': 2, 'high': 3})
        fig = px.line(df, x='date', y='risk_level_numeric', title="Risk Trend")
        fig.update_yaxes(tickvals=[1, 2, 3], ticktext=['Low', 'Moderate', 'High'])

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No history available. Run a health analysis first.")

# -------------------- Page: User Profile --------------------
elif page == "User Profile":
    st.header("User Profile")

    with st.form("profile_form"):
        name = st.text_input("Full Name", st.session_state.user_profile.get("name", ""))
        email = st.text_input("Email", st.session_state.user_profile.get("email", ""))
        dob = st.date_input("Date of Birth", value=datetime.now().date())
        notifications = st.checkbox("Receive Notifications", value=True)
        saved = st.form_submit_button("Save")

        if saved:
            st.session_state.user_profile = {
                "name": name,
                "email": email,
                "dob": dob,
                "notifications": notifications
            }
            st.success("Profile saved!")

    if st.session_state.user_profile:
        st.subheader("Profile Summary")
        profile = st.session_state.user_profile
        st.info(f"Name: {profile.get('name', '')}\nEmail: {profile.get('email', '')}\nDOB: {profile.get('dob')}\nNotifications: {'Yes' if profile.get('notifications') else 'No'}")

# -------------------- Page: Resources --------------------
elif page == "Resources":
    st.header("Health Resources")
    st.markdown("""
    - [CDC](https://www.cdc.gov)
    - [WHO](https://www.who.int)
    - [WebMD](https://www.webmd.com)
    - [Mayo Clinic](https://www.mayoclinic.org)
    - [Healthline](https://www.healthline.com)
    """)
    st.info("Resources are for educational use only.")

# -------------------- Footer --------------------
st.markdown("""---  
<small>This assistant is not a substitute for professional medical advice.  
Built using Streamlit | © 2025 AI Health Assistant</small>  
""", unsafe_allow_html=True)
