
import streamlit as st
import os, re, base64, fitz
from groq import Groq
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI NutriCare",
    page_icon="🥗",
    layout="wide"
)

# ---------------- STYLES ----------------
st.markdown("""
<style>
body, .stApp {
    background-color: #EDF3F8;
}

.header {
    background-color: #1B5E20;
    padding: 22px 40px;
    border-radius: 14px;
    color: white;
    margin-bottom: 25px;
}

.section {
    padding: 12px 0;
    border-bottom: 1px solid #D0D7DE;
    margin-bottom: 15px;
}

h3 { color: #1B5E20; }

.badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 18px;
    color: white;
    font-size: 13px;
    margin-right: 8px;
}

.alert { background: #C62828; }
.normal { background: #2E7D32; }

.meal {
    background: #F7FAFC;
    padding: 12px;
    border-left: 4px solid #2E7D32;
    margin-bottom: 10px;
    border-radius: 8px;
}

.stButton>button {
    background-color: #1B5E20;
    color: white;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ---------------- API ----------------
os.environ["GROQ_API_KEY"] = API
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ---------------- HELPERS ----------------
def clean_text(t): 
    return re.sub(r"\s+", " ", t.lower())

@st.cache_data(show_spinner=False)
def ocr_image(img):
    encoded = base64.b64encode(img).decode()
    r = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract medical text."},
                {"type": "image_url",
                 "image_url": {"url": f"data:image/png;base64,{encoded}"}}
            ]
        }]
    )
    return r.choices[0].message.content

def fast_pdf_text(pdf):
    doc = fitz.open(stream=pdf, filetype="pdf")
    return "".join(p.get_text() for p in doc)

def extract_patient(text):
    return {
        "name": re.search(r"name[:\s]+([a-z\s]+)", text).group(1).title()
        if re.search(r"name[:\s]+([a-z\s]+)", text) else "Unknown",
        "age": re.search(r"(\d{1,3})\s*(years|yrs|year)", text).group(1)
        if re.search(r"(\d{1,3})\s*(years|yrs|year)", text) else "Unknown",
        "gender": re.search(r"\b(male|female)\b", text).group(1).title()
        if re.search(r"\b(male|female)\b", text) else "Unknown"
    }

def detect_conditions(text):
    c = []
    if re.search(r"hba1c[^0-9]*(6\.5|[7-9])", text): c.append("Diabetes")
    if re.search(r"cholesterol[^0-9]*(2[0-9]{2}|[3-9][0-9]{2})", text): c.append("High Cholesterol")
    return c if c else ["Normal"]

def generate_7_day_diet(patient, conditions, region):
    prompt = f"""
Generate STRICT 7-day diet plan.
NO notes or explanations.

FORMAT:

Day 1:
Breakfast:
- item – quantity
Lunch:
- item – quantity
Snacks:
- item – quantity
Dinner:
- item – quantity

Repeat till Day 7.

Age:{patient['age']}
Gender:{patient['gender']}
Region:{region}
Conditions:{', '.join(conditions)}
"""
    r = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return r.choices[0].message.content.strip()

# ---------------- PDF ----------------
def create_pdf(day, content):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    text = c.beginText(40, 800)
    text.setFont("Helvetica", 11)

    text.textLine(f"{day} Diet Plan")
    text.textLine("-" * 40)
    for line in content.splitlines():
        text.textLine(line)

    c.drawText(text)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ---------------- UI ----------------
st.markdown("""
<div class="header">
<h1>🥗 AI NutriCare</h1>
<p>Personalized Diet Planning from Medical Reports</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1.1, 1.4, 2.3])

# -------- INPUT --------
with col1:
    st.markdown("### Upload Report")
    uploaded = st.file_uploader("PDF / Image ", type=["pdf","png","jpg","jpeg"])
    region = st.selectbox("Diet Region", ["Indian","Mediterranean","Western"])
    if st.button("Generate Diet"):
        st.session_state.generate = True

# -------- PROCESS --------
if uploaded and st.session_state.get("generate"):
    if "diet_text" not in st.session_state:
        with st.spinner(""):
            if uploaded.type == "application/pdf":
                text = fast_pdf_text(uploaded.read())
            elif uploaded.type.startswith("image/"):
                text = ocr_image(uploaded.read())
            else:
                text = uploaded.read().decode()

            text = clean_text(text)
            st.session_state.patient = extract_patient(text)
            st.session_state.conditions = detect_conditions(text)
            st.session_state.diet_text = generate_7_day_diet(
                st.session_state.patient,
                st.session_state.conditions,
                region
            )

# -------- PATIENT --------
with col2:
    if "patient" in st.session_state:
        st.markdown("### Patient Details")
        p = st.session_state.patient
        st.write(f"Name: {p['name']}")
        st.write(f"Age: {p['age']}")
        st.write(f"Gender: {p['gender']}")

        st.markdown("### Conditions")
        for c in st.session_state.conditions:
            cls = "alert" if c != "Normal" else "normal"
            st.markdown(f"<span class='badge {cls}'>{c}</span>", unsafe_allow_html=True)

# -------- DIET --------
with col3:
    if "diet_text" in st.session_state:
        day = st.selectbox("Select Day", [f"Day {i}" for i in range(1,8)])

        match = re.search(rf"{day}:(.*?)(Day \d+:|$)", st.session_state.diet_text, re.S)
        if match:
            content = match.group(1).strip()

            st.markdown(f"### {day} Diet Plan")
            for meal in ["Breakfast","Lunch","Snacks","Dinner"]:
                m = re.search(rf"{meal}:(.*?)(Breakfast|Lunch|Snacks|Dinner|$)", content, re.S)
                if m:
                    st.markdown(f"<div class='meal'><b>{meal}</b><ul>" +
                                "".join(f"<li>{i.strip('- ')}</li>" for i in m.group(1).splitlines() if i.strip()) +
                                "</ul></div>", unsafe_allow_html=True)

            pdf = create_pdf(day, content)
            st.download_button(
                f"Download {day} PDF",
                pdf,
                file_name=f"{day}_Diet_Plan.pdf",
                mime="application/pdf"
            )
