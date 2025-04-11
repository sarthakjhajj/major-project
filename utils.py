import streamlit as st
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec

# Set up clients
openai_client = OpenAI(api_key=st.secrets["OPENAI_KEY"])
pc = Pinecone(api_key=st.secrets["PINECONE_API"])

def init_openai():
    pass  # no longer needed

def init_pinecone():
    pass  # no longer needed

def embed_text(text: str) -> list:
    response = openai_client.embeddings.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def create_index(index_name: str, dimension: int = 1536):
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region=st.secrets["PINECONE_ENV"]
            )
        )
    return pc.Index(index_name)

def upsert_resumes(index, resumes: list):
    vectors = [(f"id-{i}", embed_text(text), {"text": text}) for i, text in enumerate(resumes)]
    index.upsert(vectors)

def query_resumes(index, query: str, top_k: int = 5):
    query_vector = embed_text(query)
    return index.query(vector=query_vector, top_k=top_k, include_metadata=True)
