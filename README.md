AI Powered Resume Analyzer


Overview:
The AI Powered Resume Analyzer is a Streamlit application that leverages AI to analyze resumes and provide insightful answers to user queries. The app uses Google's Generative AI embeddings and FAISS for efficient vector search. It can extract text from PDF resumes, split the text into manageable chunks, and then use these chunks to answer questions about the resume.

Features:
  PDF Resume Upload: Users can upload a PDF resume for analysis.
  Text Extraction: Extracts text from the uploaded PDF resume.  
  Text Chunking: Splits the extracted text into manageable chunks for analysis.
  Vector Store Creation: Creates a FAISS vector store from the text chunks.
  Conversational AI: Uses Google's Generative AI to answer questions about the resume.

Technologies Used:
  Python: Main programming language.
  Streamlit: For the web interface.
  Google Generative AI: For embeddings and conversational AI.
  FAISS: For efficient vector search.
  PyPDF2: For extracting text from PDF files.
  LangChain: For creating AI chains and prompts.

Installation:
  Clone the repository:
git clone https://github.com/yourusername/resume-analyzer.git
cd resume-analyzer

  Create a virtual environment:
python -m venv myenv
source myenv/bin/activate  # On Windows use `myenv\Scripts\activate`

  Install the required packages:
pip install -r requirements.txt
Set up environment variables:

  Create a .env file in the root directory and add your Google API key:
GOOGLE_API_KEY=your_google_api_key


Usage:
  Run the Streamlit app:
streamlit run app.py
