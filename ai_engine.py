import os
import google.generativeai as genai
from dotenv import load_dotenv

# Paste your actual key from Google AI Studio here
genai.configure(api_key="AIzaSyAfidJSNwsdk587uSzXIvcPe1OQDORDJ6c")
# Change from 'gemini-1.5-flash' to one of these:
model = genai.GenerativeModel('gemini-3-flash-preview')
print("Asking the AI for your plan... please wait...")

# This sends the request to the AI
response = model.generate_content("Give me a 1-day meal plan for 2500 calories.")

print(response.text)