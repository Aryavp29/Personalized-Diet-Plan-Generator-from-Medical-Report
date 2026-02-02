import streamlit as st
from fpdf import FPDF
import PyPDF2
import re
import tempfile
import random

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI-NutriCare Dashboard", layout="wide")

# ---------------- MEDICAL RULES ----------------
MEDICAL_RULES = {
    "Diabetes": {
        "Avoid": "Sugar, White Rice, Maida",
        "Include": "Millets, Fenugreek, Vegetables",
        "Advice": "Low Glycemic Index diet recommended"
    },
    "Cholesterol": {
        "Avoid": "Fried food, Butter, Ghee",
        "Include": "Oats, Garlic, Nuts",
        "Advice": "Reduce saturated fats"
    },
    "Hypertension": {
        "Avoid": "Salt, Pickles, Processed food",
        "Include": "Banana, Spinach, Fruits",
        "Advice": "Follow DASH diet"
    },
    "Uric Acid": {
        "Avoid": "Red meat, Mushrooms",
        "Include": "Cherries, Cucumber, Water",
        "Advice": "Low purine diet"
    }
}

# ---------------- CALORIE FUNCTIONS ----------------
def calculate_bmr(weight, height, age, gender):
    return 10*weight + 6.25*height - 5*age + (5 if gender=="Male" else -161)

def calculate_tdee(bmr, activity):
    factors = {"Sedentary":1.2, "Moderate":1.55, "Active":1.725}
    return bmr * factors[activity]

# ---------------- PDF GENERATION ----------------
def generate_pdf(name, bmi, calories, issues, weekly_meal_plan):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "AI-NutriCare Personalized Clinical Report", ln=True, align="C")

    pdf.set_font("Arial", size=12)
    pdf.ln(8)
    pdf.cell(0, 8, f"Patient Name: {name}", ln=True)
    pdf.cell(0, 8, f"BMI: {bmi:.2f}", ln=True)
    pdf.cell(0, 8, f"Daily Calorie Requirement: {int(calories)} kcal", ln=True)

    pdf.ln(5)
    if issues:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Detected Medical Conditions:", ln=True)
        pdf.set_font("Arial", size=11)
        for issue in issues:
            pdf.multi_cell(0, 7, f"- {issue}: {MEDICAL_RULES[issue]['Advice']}")

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "7-Day Personalized Meal Plan:", ln=True)
    pdf.set_font("Arial", size=11)
    for day, meals in weekly_meal_plan.items():
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 7, f"{day}:", ln=True)
        pdf.set_font("Arial", size=10)
        for meal, info in meals.items():
            pdf.multi_cell(0, 6, f"  {meal}: {info['Food']} ({info['Portion']})")
        pdf.ln(2)
    return pdf.output(dest="S").encode("latin-1")

# ---------------- FILE EXTRACTION ----------------
def extract_values(file_path):
    text = ""
    reader = PyPDF2.PdfReader(file_path)
    for page in reader.pages:
        text += page.extract_text()
    sugar = re.search(r"(Sugar|Glucose|HbA1c).*?(\d+)", text, re.I)
    chol = re.search(r"(Cholesterol|LDL).*?(\d+)", text, re.I)
    bp = re.search(r"(BP|Systolic).*?(\d+)", text, re.I)
    return {
        "sugar": int(sugar.group(2)) if sugar else 100,
        "chol": int(chol.group(2)) if chol else 180,
        "bp": int(bp.group(2)) if bp else 120
    }

# ---------------- WEEKLY MEAL PLAN ----------------
def generate_detailed_weekly_plan(issues):
    breakfasts = [
        {"Food":"Oats / Millets + Fruits", "Portion":"1 bowl + 1 cup fruits"},
        {"Food":"Smoothie + Nuts", "Portion":"250ml smoothie + 10 almonds"},
        {"Food":"Millet Porridge", "Portion":"1 bowl"},
        {"Food":"Veg Sandwich with Whole Grain Bread", "Portion":"2 slices"}
    ]
    mid_morning = [
        {"Food":"Fruit Salad", "Portion":"1 cup"},
        {"Food":"Nuts and Seeds", "Portion":"10-15 pieces"},
        {"Food":"Green Tea + Biscuit", "Portion":"1 cup + 1 biscuit"},
        {"Food":"Yogurt + Berries", "Portion":"1 cup"}
    ]
    lunches = [
        {"Food":"Brown rice + Vegetables + Dal", "Portion":"1 cup rice + 1 cup veg + 1 cup dal"},
        {"Food":"Quinoa Salad + Grilled Veggies", "Portion":"1 plate"},
        {"Food":"Chapati + Mixed Veg Curry", "Portion":"2 chapatis + 1 cup curry"},
        {"Food":"Lentil Soup + Brown Rice", "Portion":"1 bowl soup + 1 cup rice"}
    ]
    evening_snack = [
        {"Food":"Sprouts Salad", "Portion":"1 cup"},
        {"Food":"Roasted Chickpeas", "Portion":"1/2 cup"},
        {"Food":"Fruit Smoothie", "Portion":"200ml"},
        {"Food":"Vegetable Sticks + Hummus", "Portion":"1 cup"}
    ]
    dinners = [
        {"Food":"Soup + Salad + Protein source", "Portion":"1 bowl + 1 cup + 100g protein"},
        {"Food":"Steamed fish/tofu + greens", "Portion":"150g protein + 1 cup greens"},
        {"Food":"Grilled Chicken + Veggies", "Portion":"150g chicken + 1 cup veggies"},
        {"Food":"Vegetable Stir Fry + Quinoa", "Portion":"1 cup"}
    ]

    if "Diabetes" in issues:
        breakfasts = [{"Food":"Millet dosa + vegetables","Portion":"2 pieces"}]
        mid_morning = [{"Food":"Apple + Almonds","Portion":"1 apple + 10 almonds"}]
    if "Cholesterol" in issues:
        dinners = [{"Food":"Steamed fish/tofu + greens","Portion":"150g protein + 1 cup greens"}]
    if "Hypertension" in issues:
        lunches = [{"Food":"Brown rice + veggies + dal","Portion":"1 cup rice + 1 cup veg + 1 cup dal"}]

    weekly_plan = {}
    for day in range(1, 8):
        weekly_plan[f"Day {day}"] = {
            "Breakfast": random.choice(breakfasts),
            "Mid-Morning Snack": random.choice(mid_morning),
            "Lunch": random.choice(lunches),
            "Evening Snack": random.choice(evening_snack),
            "Dinner": random.choice(dinners)
        }
    return weekly_plan

# ---------------- STYLES ----------------
st.markdown("""
<style>
.big-title {font-size:40px; font-weight:bold; color:#1f77b4;}
.sub-title {font-size:18px; color:gray;}
.accordion {margin-bottom: 15px;}
.meal-box {padding:15px; border-radius:12px; background-color:#000000; margin-bottom:10px;}
.meal-name {color:#1f77b4; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🧠 AI-NutriCare Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Personalized Diet Planning from Medical Reports</div>', unsafe_allow_html=True)
st.divider()

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📂 Upload & Inputs",
    "📊 Health Analysis",
    "🍽️ Meal Plan",
    "📄 Report"
])

# ---------------- TAB 1 ----------------
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📂 Upload Medical Report")
        uploaded = st.file_uploader("Upload PDF", type=["pdf"])
        file_path = None
        if uploaded:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded.read())
                file_path = tmp.name
    with col2:
        st.subheader("👤 Patient Details")
        name = st.text_input("Name", "Patient")
        gender = st.selectbox("Gender", ["Male", "Female"])
        age = st.number_input("Age", 10, 100, 25)

    st.subheader("⚖️ Body Details")
    c1, c2, c3 = st.columns(3)
    weight = c1.number_input("Weight (kg)", 30.0, 150.0, 70.0)
    height = c2.number_input("Height (cm)", 120.0, 220.0, 170.0)
    activity = c3.selectbox("Activity Level", ["Sedentary", "Moderate", "Active"])

submit = st.button("🚀 Generate AI Diet Report")

# ---------------- PROCESSING ----------------
if submit:
    if file_path:
        values = extract_values(file_path)
        sugar, chol, bp = values.values()
    else:
        sugar, chol, bp = 100, 180, 120

    bmi = weight / ((height / 100) ** 2)
    bmr = calculate_bmr(weight, height, age, gender)
    calories = calculate_tdee(bmr, activity)

    issues = []
    if sugar > 140: issues.append("Diabetes")
    if chol > 200: issues.append("Cholesterol")
    if bp > 130: issues.append("Hypertension")

    weekly_meal_plan = generate_detailed_weekly_plan(issues)

    st.session_state.update({
        'generated': True,
        'bmi': bmi,
        'calories': calories,
        'issues': issues,
        'weekly_meal_plan': weekly_meal_plan,
        'name': name
    })

# ---------------- TAB 2: Health Analysis ----------------
with tab2:
    if st.session_state.get('generated', False):
        bmi = st.session_state['bmi']
        calories = st.session_state['calories']
        issues = st.session_state['issues']

        st.subheader("📊 Clinical Health Overview")

        # Metrics
        m1, m2, m3 = st.columns(3)
        bmi_status = "✅ Healthy" if 18.5 <= bmi <= 24.9 else "⚠️ Needs Attention"
        m1.metric("BMI", f"{bmi:.2f}", bmi_status)
        m2.metric("Daily Calories", f"{int(calories)} kcal")
        m3.metric("Medical Conditions", f"{len(issues)} condition(s) detected")

        # Progress
        st.markdown("**Condition Severity Progress:**")
        st.progress(min(len(issues)/4, 1.0))

        st.divider()

        # Medical Alerts
        st.subheader("🚩 Medical Alerts")
        if issues:
            for issue in issues:
                st.error(f"{issue}: {MEDICAL_RULES[issue]['Advice']}")
        else:
            st.success("All clinical values are normal 🎉")
    else:
        st.info("Please click 🚀 Generate AI Diet Report to see Health Analysis")

# ---------------- TAB 3: Meal Plan ----------------
with tab3:
    if st.session_state.get('generated', False):
        weekly_meal_plan = st.session_state['weekly_meal_plan']
        st.subheader("🍽️ 7-Day Personalized Meal Plan")
        for day, meals in weekly_meal_plan.items():
            with st.expander(day, expanded=False):
                for meal, info in meals.items():
                    st.markdown(
                        f"""
                        <div class="meal-box">
                            <div class="meal-name">{meal}</div>
                            <div>{info['Food']} <br><small>Portion: {info['Portion']}</small></div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
    else:
        st.info("Please click 🚀 Generate AI Diet Report to see Meal Plan")

# ---------------- TAB 4: PDF Report ----------------
with tab4:
    if st.session_state.get('generated', False):
        pdf = generate_pdf(
            st.session_state['name'],
            st.session_state['bmi'],
            st.session_state['calories'],
            st.session_state['issues'],
            st.session_state['weekly_meal_plan']
        )
        st.subheader("📄 Export Clinical Report")
        st.info("Download your personalized AI-generated diet report")
        st.download_button(
            "⬇️ Download PDF",
            pdf,
            file_name="AI_NutriCare_Report.pdf"
        )
    else:
        st.info("Please click 🚀 Generate AI Diet Report to download PDF")
