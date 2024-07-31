import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
import PyPDF2

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def analyze_resume(job_description, resume_text):
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""
    Analyze the given resume text and compare it with the following job description:

    Job Description:
    {job_description}

    Resume Text:
    {resume_text}

    Provide the following information:
    1. CV Score (out of 100)
    2. Job Match Percentage
    3. Things that can be improved in the CV
    4. Skills Improvement Suggestions

    Format the response as JSON with keys: "score", "job_match", "improvements", and "skill_suggestions".
    """

    response = model.generate_content(prompt)
    return response.text

def format_response(response_text):
    try:
        # First, try to parse the entire response as JSON
        response_json = json.loads(response_text)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON from the text
        try:
            start = response_text.index('{')
            end = response_text.rindex('}') + 1
            response_json = json.loads(response_text[start:end])
        except (ValueError, json.JSONDecodeError):
            # If JSON extraction fails, return an error
            return {"error": "Failed to parse response", "raw_response": response_text}

    # Extract values with default fallbacks
    formatted_response = {
        "score": str(response_json.get("score", "N/A")),
        "job_match": str(response_json.get("job_match", "N/A")),
        "improvements": response_json.get("improvements", []),
        "skill_suggestions": response_json.get("skill_suggestions", [])
    }

    # Ensure improvements and skill_suggestions are lists
    if not isinstance(formatted_response["improvements"], list):
        formatted_response["improvements"] = [str(formatted_response["improvements"])]
    if not isinstance(formatted_response["skill_suggestions"], list):
        formatted_response["skill_suggestions"] = [str(formatted_response["skill_suggestions"])]

    return formatted_response

def is_meaningful_text(text, min_length=50):
    """Check if the text is meaningful (not just random characters and long enough)"""
    if len(text.strip()) < min_length:
        return False
    # You could add more sophisticated checks here if needed
    return True

def main():
    st.set_page_config(page_title="ATS Resume Analyzer", page_icon="🔎", layout="wide")

    # Apply custom CSS for styling
    st.markdown("""
    <style>
    .main-title1 {
        color: cyan;
        font-size: 50px;
        text-align: center;
        margin-top: -70px;
        margin-bottom: 40px;
    }
    .main-title2 {
        text-align: center;
        color: cyan;
    }
    .sub-title1 {
        color: lightblue;
    }
    .sub-title2 {
        color: lightblue;
        text-align: center;
    }
    .reportview-container {
        background-color: #0E1117;
    }
    .sidebar .sidebar-content {
        background-color: #1E2126;
    }
    .css-18e3th9, .css-1y4p8pa {
        color: #FAFAFA;
    }
    .stButton>button {
        font-weight: bold;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 20px;
        width: 66%;
    }
    .stTextInput>div>div>input, .stTextArea>div>textarea {
        color: #FAFAFA;
        background-color: #2C3138;
        border: 1px solid #4A4F57;
    }
    .stMetric>div>span {
        color: #00BFFF;
        font-size: 50px;
    }
    .st-bb {
        font-size: 24px;
        font-weight: bold;
        color: #00BFFF;
        margin-bottom: 20px;
    }
    .st-tt {
        font-size: 18px;
        color: #FAFAFA;
    }
    .section-title {
        font-size: 42px;
        font-weight: bold;
        color: #00BFFF;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    .result-item {
        background-color: #2C3138;
        padding: 15px;
        font-size: 20px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .custom-metric .stMetric>div>span {
        font-size: 80px; /* Adjust the font size as needed */
    }
    .vertical-line {
        border-left: 2px solid #00BFFF;
        height: 100%;
        position: absolute;
        left: 50%;
        top: 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="main-title1">AI 🤖 Powered Resume Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid lightblue; border-radius: 1px;'>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<h2 class="sub-title1">Job 💼 Description</h2>', unsafe_allow_html=True)
        job_description = st.text_area("", placeholder="Enter the job description here", height=250)

    with col2:
        st.markdown('<h2 class="sub-title2"> 📂 Upload Resume</h2>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type=["pdf"])

        if uploaded_file:
            st.success("✅ Resume uploaded successfully!")
        else:
            st.info("Please upload your resume (PDF format)")

    # Add vertical line between columns using Streamlit's container
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="vertical-line"></div>', unsafe_allow_html=True)

    if st.button("🔍 Analyze Resume"):
        if uploaded_file and job_description:
            with st.spinner("Analyzing resume... Please wait."):
                resume_text = extract_text_from_pdf(uploaded_file)
                
                if not is_meaningful_text(job_description):
                    st.warning("⚠️ Please enter a more detailed job description.")
                elif not is_meaningful_text(resume_text):
                    st.warning("⚠️ The uploaded resume doesn't contain enough text. Please check the PDF file.")
                else:
                    response = analyze_resume(job_description, resume_text)
                    formatted_response = format_response(response)
                    for i in range(6):
                        st.markdown(" ")
                    st.markdown("<hr style='border: 1px solid lightblue; border-radius: 2px;'>", unsafe_allow_html=True)
                    st.markdown('<h1 class="main-title2">📊 Analysis Results</h1>', unsafe_allow_html=True)
                    st.markdown("<hr style='border: 1px solid lightblue; border-radius: 2px;'>", unsafe_allow_html=True)

                    if "error" in formatted_response:
                        st.error(f"An error occurred: {formatted_response['error']}")
                        st.text("Raw response:")
                        st.text(formatted_response.get("raw_response", "No raw response available"))
                    else:
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col1:
                            st.markdown(f"""
                            <div class="custom-metric">
                                <h2 style="margin-left: 40px; color: #00BFFF; font-size: 120px;">{formatted_response["job_match"]}%</h2>
                                <p style="margin-left: 40px; font-size: 40px; font-weight: bold;">Job Match Per%</p>
                                <div style="margin-top: 60px;"></div>
                                <h2 style="margin-left: 40px; color: #00BFFF; font-size: 120px;">{formatted_response["score"]}</h2>
                                <p style="margin-left: 40px; font-size: 40px; font-weight: bold;">CV Score</p> 
                            </div>
                            """, unsafe_allow_html=True)

                        with col2:
                            st.markdown('<p class="section-title">🚀 Improvements</p>', unsafe_allow_html=True)
                            for improvement in formatted_response["improvements"]:
                                st.markdown(f'<div class="result-item">✅ {improvement}</div>', unsafe_allow_html=True)

                        with col3:
                            st.markdown('<p class="section-title">💡 Skill Suggestions</p>', unsafe_allow_html=True)
                            for suggestion in formatted_response["skill_suggestions"]:
                                st.markdown(f'<div class="result-item">🔹 {suggestion}</div>', unsafe_allow_html=True)

        elif not uploaded_file:
            st.warning("⚠️ Please upload a resume PDF before analyzing!")
        elif not job_description:
            st.warning("⚠️ Please enter a job description before analyzing!")

if __name__ == "__main__":
    main() 