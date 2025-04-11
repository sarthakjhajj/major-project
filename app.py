import streamlit as st
from utils import init_openai, init_pinecone, create_index, upsert_resumes, query_resumes
import fitz  


init_openai()
init_pinecone()

INDEX_NAME = "resumes-index"
index = create_index(INDEX_NAME)

st.title("Major Projet - Resume Selector")

st.subheader("Step 1: Enter Job Description")
job_desc = st.text_area("Paste the job description or required qualifications here", height=200)

st.subheader("Step 2: Upload Resumes")
uploaded_files = st.file_uploader("Upload resumes (PDF or TXT format)", type=["pdf", "txt"], accept_multiple_files=True)

st.subheader("Step 3: Select Number of Candidates")
num_resumes_to_select = st.number_input("How many resumes to select?", min_value=1, step=1)


def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

if st.button("🔍 Find Matching Resumes"):
    if not job_desc.strip():
        st.warning("Please enter a job description.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        texts = []
        for file in uploaded_files:
            if file.name.endswith(".pdf"):
                text = extract_text_from_pdf(file)
            else:
                text = file.read().decode("utf-8")
            texts.append(text)

        with st.spinner("Indexing resumes..."):
            upsert_resumes(index, texts)

        with st.spinner("Finding the most relevant resumes..."):
            results = query_resumes(index, job_desc, top_k=num_resumes_to_select)
            st.success(f"Top {len(results['matches'])} matching resumes found!")

            for i, match in enumerate(results["matches"]):
                st.subheader(f"📄 Resume #{i+1}")
                st.write(match['metadata']['text'][:1500] + "...")
