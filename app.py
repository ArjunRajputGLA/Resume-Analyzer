
import os
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

def get_resume_text(resume_file):
    text = ""
    pdf_reader = PdfReader(resume_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

template = """
You are an AI assistant specialized in analyzing resumes and providing insights about the candidate.
Given the following extracted parts of a resume and a question, create a final answer. If you don't know the answer based on the given context, then say you don't have enough information.

Resume context:
{context}

Question: {question}
Answer:"""

def get_conversational_chain():
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(input_variables=["question", "context"], template=template)
    chains = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chains

def load_faiss_index(pickle_file):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    faiss_index = FAISS.load_local(pickle_file, embeddings=embeddings, allow_dangerous_deserialization=True) 
    return faiss_index

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = load_faiss_index("faiss_index")
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()
    response = chain({"input_documents":docs, "question":user_question})

    st.markdown('<p class="answer-label">Answer:</p>', unsafe_allow_html=True)
    st.text_area("", value=response["output_text"], height=200, key="answer_area", 
                 help="The AI-generated answer will appear here.", disabled=True) 


custom_css = """
<style>
    .main-title {
        font-size: 3rem;
        color: cyan;
        text-align: center;
        margin-bottom: 2rem;
        margin-top: -2rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: cyan;
        text-align: centre;
        margin-top: 17.5rem;
        width: 100%;
    }
    .upload-section {
        color: cyan;
        background-color: #F7F9FC;
        font-weight: bold;
        border-radius: 10px;
    }
    .answer-section {
        padding: 1.8rem;
        border-radius: 10px;
    }
    .sidebar-title {
        font-size: 1.9rem;
        font-weight: bold;
        color: cyan;
        text-align: center;
        margin-bottom: 1rem;
        margin-top: -2rem;
    }
    .sidebar-footer {
        font-size: 1.6rem;
        background-color: black;
        font-weight: bold;
        color: cyan;
        text-align: center;
        position: fixed;
        bottom: 0;
        left: 0;
        width: 22.5rem;  
        padding: 10px;
        z-index: 1000;  
    }
    .sidebar-content {
        margin-bottom: 40px;  /* Add space for the footer */
    }
    .answer-label {
        font-weight: bold;
        color: white;
        font-size: 2.3rem;
    }
    .answer-text-area {
        width: 100%;
        min-height: 100px;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        background-color: #f9f9f9;
        font-size: 2rem;
        line-height: 1.5;
        resize: vertical;
    }
</style> 
"""

st.set_page_config(
    page_title="Resume Analyzer",
    page_icon='🔎',
    layout="wide",
    initial_sidebar_state="auto"
)

st.markdown(custom_css, unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-title">Upload Resume</p>', unsafe_allow_html=True)
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    resume_file = st.file_uploader("Choose a PDF file", type=["pdf"], accept_multiple_files=False)
    if resume_file:
        st.session_state.resume_file = resume_file
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)

    if st.button("Analyze Resume", key="analyze_button", use_container_width=True):
        if 'resume_file' in st.session_state and st.session_state.resume_file is not None:
            with st.spinner("📊 Analyzing Resume..."):
                raw_text = get_resume_text(st.session_state.resume_file)
                text_chunks = get_text_chunks(raw_text)
                vector_store = get_vector_store(text_chunks)
                st.success("✅ Resume analysis complete!")
        else:
            st.sidebar.warning("⚠️ Upload a resume first!") 
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-footer">Powered by SkillCred™</p>', unsafe_allow_html=True)


def main():
    st.markdown('<h2 class="main-title"> AI 🤖 Powered Resume Analyzer </h2>', unsafe_allow_html=True) 
    st.markdown("---")    
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.info("📌 Upload your resume in the sidebar to get started!")
    st.markdown("---")
    st.markdown('</div>', unsafe_allow_html=True)

    st.header("Prompt:")
    user_question = st.text_input("", placeholder="Ask a question about the resume")
    st.markdown('---')

    if user_question:
        st.markdown('<div class="answer-section">', unsafe_allow_html=True)
        if 'resume_file' not in st.session_state or st.session_state.resume_file is None:
            st.warning("⚠️ Please upload a resume first before asking questions.")
        else:
            user_input(user_question)
        st.markdown('</div>', unsafe_allow_html=True) 

if __name__ == "__main__":
    main() 