import streamlit as st
from fpdf import FPDF
import PyPDF2
import re

st.set_page_config(page_title="NutriCare Master Clinical", layout="wide")

# 1. ENHANCED DATABASES
MEDICAL_RULES = {
    "Diabetes": {"Avoid": "Sugar, White Rice, Maida", "Include": "Millet, Fenugreek", "Advice": "Low GI focus.", "Color": "red"},
    "Cholesterol": {"Avoid": "Ghee, Butter, Fried Food", "Include": "Oats, Garlic", "Advice": "Heart-healthy fats.", "Color": "orange"},
    "Hypertension": {"Avoid": "Salt, Pickles, Papad", "Include": "Banana, Spinach", "Advice": "DASH Diet focus.", "Color": "red"},
    "PCOD/PCOS": {"Avoid": "Dairy, Soy, Sugar", "Include": "Flax Seeds, Cinnamon", "Advice": "Hormone balance.", "Color": "blue"},
    "Uric Acid": {"Avoid": "Red Meat, Mushrooms", "Include": "Cherries, Berries", "Advice": "Low Purine diet.", "Color": "orange"},
    "Thyroid (Hypo)": {"Avoid": "Raw Cabbage, Soy", "Include": "Iodized Salt, Seafood", "Advice": "Avoid raw goitrogens.", "Color": "blue"}
}

# (Keep your existing CUISINES dictionary here...)

# 2. IMPROVED SYNC LOGIC (With Auto-Rerun)
def sync_data():
    if st.session_state.uploader is not None:
        file = st.session_state.uploader
        text = ""
        try:
            if file.type == "application/pdf":
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages: text += page.extract_text()
            elif file.type == "text/plain":
                text = str(file.read(), "utf-8")
            
            # Clinical Regex Extraction
            sugar_m = re.search(r"(Glucose|Sugar|HbA1c)\s*[:\-]?\s*(\d+)", text, re.I)
            chol_m = re.search(r"(Cholesterol|LDL)\s*[:\-]?\s*(\d+)", text, re.I)
            bp_m = re.search(r"(BP|Pressure|Systolic)\s*[:\-]?\s*(\d{2,3})", text, re.I)
            
            if sugar_m: st.session_state.sugar_val = int(sugar_m.group(2))
            if chol_m: st.session_state.chol_val = int(chol_m.group(2))
            if bp_m: st.session_state.bp_val = int(bp_m.group(2))
            
            st.toast("🚨 Dangerous biomarkers detected! Analyzing...")
            st.rerun() # Forces the UI to update immediately
        except Exception:
            st.error("Extraction failed. Please adjust markers manually.")

# 3. PDF GENERATOR (Unchanged)
def create_master_pdf(name, info, plan, warnings):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="MASTER CLINICAL DIET & HEALTH AUDIT", ln=True, align='C')
    pdf.set_font("Arial", size=11)
    pdf.ln(10)
    pdf.cell(0, 10, txt=f"Patient: {name} | Goal: {info['goal']} | Cuisine: {info['cuisine']}", ln=True)
    if warnings:
        pdf.set_text_color(220, 50, 50)
        pdf.cell(0, 10, txt="MEDICAL RESTRICTIONS:", ln=True)
        pdf.set_text_color(0, 0, 0)
        for w in warnings:
            pdf.multi_cell(0, 8, txt=f"- {w}: Avoid {MEDICAL_RULES[w]['Avoid']}. Advice: {MEDICAL_RULES[w]['Advice']}")
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="CUSTOMIZED MEAL PLAN:", ln=True)
    pdf.set_font("Arial", size=11)
    for meal, food in plan.items():
        pdf.cell(0, 10, txt=f"{meal}: {food}", ln=True)
    return pdf.output(dest="S").encode("latin-1")

# 4. APP UI
st.title("🏥 NutriCare Master: Universal Clinical Audit")

if 'sugar_val' not in st.session_state: st.session_state.sugar_val = 100
if 'chol_val' not in st.session_state: st.session_state.chol_val = 180
if 'bp_val' not in st.session_state: st.session_state.bp_val = 120

with st.sidebar:
    st.header("📂 Universal File Upload")
    st.file_uploader("Upload Lab Report", type=["pdf", "txt"], key="uploader", on_change=sync_data)
    
    st.header("🔬 Clinical Markers")
    sugar = st.number_input("Blood Sugar (mg/dL)", 0, 500, key="sugar_val")
    cholesterol = st.number_input("Cholesterol (mg/dL)", 0, 600, key="chol_val")
    bp = st.number_input("Systolic BP (mmHg)", 0, 250, key="bp_val")
    uric = st.number_input("Uric Acid (mg/dL)", 0.0, 15.0, 5.0)
    other_issues = st.multiselect("Other Conditions", list(MEDICAL_RULES.keys()))

with st.form("main_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("Name", "User")
        weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0)
    with c2:
        goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "Maintenance"])
        height = st.number_input("Height (cm)", 100.0, 250.0, 175.0)
    with c3:
        cuisine = st.selectbox("Cuisine", ["North Indian", "South Indian", "Western"])
        age = st.number_input("Age", 5, 100, 25)
    submit = st.form_submit_button("🚀 Generate Clinical Health Audit")

# 5. EXECUTION & DISPLAY
# BMI Calculation
bmi = weight / ((height/100)**2)

if submit or st.session_state.uploader:
    detected = []
    if sugar > 140: detected.append("Diabetes")
    if cholesterol > 200: detected.append("Cholesterol")
    if bp > 130: detected.append("Hypertension")
    if uric > 7.0: detected.append("Uric Acid")
    all_issues = list(set(detected + other_issues))

    # BMI Meter
    st.subheader("⚖️ Body Composition")
    bmi_color = "green" if 18.5 <= bmi <= 24.9 else "orange" if bmi < 18.5 else "red"
    st.markdown(f"Your BMI is **{bmi:.1f}** (<span style='color:{bmi_color}'>{'Healthy' if bmi_color=='green' else 'Action Required'}</span>)", unsafe_allow_html=True)

    st.subheader("🚩 Clinical Health Status")
    
    if all_issues:
        for issue in all_issues:
            with st.expander(f"⚠️ {issue} Detected", expanded=True):
                st.write(f"**Avoid:** {MEDICAL_RULES[issue]['Avoid']}")
                st.info(f"💡 {MEDICAL_RULES[issue]['Advice']}")
    else: 
        st.success("✅ All markers are within the normal clinical range.")

    st.subheader(f"📅 Daily {cuisine} Meal Plan")
    # Display logic for food...
    # (Keep your existing r1_c1, r1_c2 etc. grid here)