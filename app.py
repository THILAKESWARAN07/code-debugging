import streamlit as st
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential


load_dotenv()
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("API Key not found. Please set GOOGLE_API_KEY in secrets or .env")
    st.stop()

genai.configure(api_key=api_key)


st.set_page_config(page_title="AI Code Master", layout="wide")
st.title("🚀 AI Coding Debugger & Tutor")


mode = st.sidebar.selectbox("Choose Mode", ["Debugger", "Code Explainer", "Learning Assistant"])


@st.cache_data(show_spinner=False)
@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
def get_ai_response(prompt):
    """
    Calls the Gemini API with automatic retries if rate limited (429).
    @st.cache_data ensures that identical prompts don't waste your quota.
    """
   
    time.sleep(1) 
    
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    response = model.generate_content(prompt)
    return response.text


user_code = st.text_area("Paste your code here:", height=200, placeholder="print('Hello World')")


def handle_request(prompt):
    try:
        with st.spinner("🤖 AI is thinking..."):
            result = get_ai_response(prompt)
            st.markdown("### 💡 AI Analysis")
            st.markdown(result)
    except Exception as e:
        if "429" in str(e):
            st.error("🚨 **Quota Exhausted:** You've used all your free requests for now. Please wait 60 seconds or try again tomorrow.")
        else:
            st.error(f"🚨 **Error:** {str(e)}")

if mode == "Debugger":
    error_msg = st.text_input("Paste the error message (optional):")
    if st.button("Debug Code"):
        if user_code.strip():
            prompt = f"Fix this code. Identify the bug and provide the corrected version with a brief explanation:\n\nCode:\n{user_code}\n\nError:\n{error_msg}"
            handle_request(prompt)
        else:
            st.warning("Please paste some code first!")

elif mode == "Code Explainer":
    if st.button("Explain Logic"):
        if user_code.strip():
            prompt = f"Explain how this code works step-by-step for a beginner:\n\n{user_code}"
            handle_request(prompt)
        else:
            st.warning("Please paste some code first!")

elif mode == "Learning Assistant":
    topic = st.text_input("What concept do you want to learn?")
    if st.button("Teach Me"):
        if topic.strip():
            prompt = f"Explain the programming concept '{topic}' using simple analogies and a code example."
            handle_request(prompt)
        else:
            st.warning("Please enter a topic!")