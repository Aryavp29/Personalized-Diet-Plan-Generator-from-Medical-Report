import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-3-flash-preview')

# 2. UI Layout
st.set_page_config(page_title="AI Diet Master", page_icon="🥗")
st.title("🥗 My Personal AI Diet Planner")

# Sidebar for user info
with st.sidebar:
    st.header("Your Stats")
    weight = st.number_input("Weight (kg)", 40, 150, 70)
    height = st.number_input("Height (cm)", 120, 220, 170)
    age = st.number_input("Age", 10, 100, 25)
    goal = st.selectbox("Your Goal", ["Weight Loss", "Muscle Gain", "Maintenance"])

# 3. Logic & AI Call
if st.button("Create My Diet Plan"):
    with st.spinner("Calculating calories..."):
        # Calculate BMR (Basic math)
        calories = (10 * weight) + (6.25 * height) - (5 * age) + 5
        
        # Ask Gemini
        prompt = f"Act as a nutritionist. Create a 1-day {goal} meal plan for {calories} calories."
        response = model.generate_content(prompt)
        
        st.success(f"Target Calories: {calories}")
        st.markdown(response.text) # Display AI result nicely