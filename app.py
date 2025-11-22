"""
MediSage - Medical Question Answering System

A RAG-based application for answering medical questions using FDA medication leaflets.

Usage:
    streamlit run app.py
"""

import streamlit as st
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "medications"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_PROVIDER = "openai" if OPENAI_API_KEY else "ollama"

# Ollama fallback
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "mistral"


@st.cache_resource
def load_embedding_model():
    """Load sentence transformer model for embeddings."""
    return SentenceTransformer(EMBEDDING_MODEL)


@st.cache_resource
def get_qdrant_client():
    """Initialize Qdrant client connection."""
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


@st.cache_resource
def get_openai_client():
    """Initialize OpenAI client."""
    if not OPENAI_API_KEY:
        return None
    return OpenAI(api_key=OPENAI_API_KEY)


def check_llm_available():
    """Check if LLM (OpenAI or Ollama) is available."""
    if LLM_PROVIDER == "openai":
        return OPENAI_API_KEY is not None
    else:
        try:
            import requests
            response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False


def translate_query_if_needed(query: str) -> str:
    """
    Translate query to English if it contains Polish characters.

    Args:
        query: User question

    Returns:
        Query in English
    """
    polish_chars = set('ąćęłńóśźżĄĆĘŁŃÓŚŹŻ')
    has_polish = any(char in polish_chars for char in query)

    if not has_polish:
        return query

    if LLM_PROVIDER == "openai":
        try:
            client = get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Translate the following Polish medical question to English. Return ONLY the translation."},
                    {"role": "user", "content": query}
                ],
                temperature=0,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except:
            return query
    else:
        return query


def search_medications(query: str, top_k: int = 3):
    """
    Search medication leaflets using vector similarity.

    Args:
        query: User question
        top_k: Number of results to return

    Returns:
        List of search results from Qdrant
    """
    search_query = translate_query_if_needed(query)

    model = load_embedding_model()
    client = get_qdrant_client()

    query_embedding = model.encode(search_query).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k
    ).points

    return results


def generate_answer(query: str, search_results):
    """
    Generate answer using LLM based on retrieved context.

    Args:
        query: User question
        search_results: Search results from Qdrant

    Returns:
        Generated answer or None if LLM unavailable
    """
    if not check_llm_available():
        return None

    context_parts = []
    for i, result in enumerate(search_results, 1):
        drug_name = result.payload['drug_name']
        section = result.payload['section']
        text = result.payload['text']
        score = result.score

        context_parts.append(
            f"Fragment {i} (drug: {drug_name}, section: {section}, score: {score:.3f}):\n{text}"
        )

    context = "\n\n---\n\n".join(context_parts)

    system_prompt = """You are MediSage, a medical assistant for medication questions.

IMPORTANT RULES:
- Answer ONLY based on provided leaflet fragments
- DO NOT make up information not present in the fragments
- If information is not in the fragments, state this clearly
- Always recommend consulting a doctor or pharmacist when in doubt
- Be specific and precise"""

    user_prompt = f"""User question: {query}

Available leaflet fragments:

{context}

Answer the user's question based on the above fragments. If the answer is in the fragments, provide it clearly. If there's insufficient information, say so."""

    try:
        if LLM_PROVIDER == "openai":
            client = get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content

        else:
            import requests
            full_prompt = f"{system_prompt}\n\n{user_prompt}"

            response = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 500
                    }
                },
                timeout=180
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response from model.")
            else:
                return f"Ollama error (status {response.status_code}): {response.text}"

    except Exception as e:
        return f"Error generating answer: {str(e)}"


def main():
    """Main application function."""

    st.set_page_config(
        page_title="MediSage",
        page_icon="💊",
        layout="wide"
    )

    st.title("💊 MediSage")
    st.subheader("Medical Question Answering System")
    st.markdown("---")

    with st.sidebar:
        st.header("📋 Information")
        st.markdown("""
        **MediSage** answers medication questions based on official FDA leaflets.

        **Available medications:**
        - Ibuprofen
        - Acetaminophen
        - Aspirin
        - Naproxen
        - Metformin
        - Lisinopril
        - Amlodipine
        - Atorvastatin
        - Omeprazole
        - Sertraline

        **Example questions:**
        - Can I drink alcohol with ibuprofen?
        - What is the dosage for aspirin?
        - What are the side effects of metformin?
        - Can I take ibuprofen with aspirin?
        """)

        st.markdown("---")
        st.markdown("🔧 **Status:**")

        try:
            client = get_qdrant_client()
            collection_info = client.get_collection(COLLECTION_NAME)
            st.success(f"✅ Qdrant: {collection_info.points_count} fragments")
        except Exception as e:
            st.error(f"❌ Qdrant: {str(e)}")

        if LLM_PROVIDER == "openai":
            if OPENAI_API_KEY:
                st.success("✅ LLM: OpenAI (gpt-4o-mini)")
            else:
                st.error("❌ LLM: Missing OPENAI_API_KEY in .env")
        else:
            if check_llm_available():
                st.success(f"✅ LLM: Ollama ({OLLAMA_MODEL})")
            else:
                st.warning("⚠️ LLM: Ollama not running")

    st.markdown("### 🤔 Ask a question about medication:")

    user_question = st.text_input(
        "Your question:",
        placeholder="e.g. Can I drink alcohol with ibuprofen?",
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([3, 1])
    with col2:
        top_k = st.slider("Number of results:", 1, 5, 3)

    if st.button("🔍 Ask MediSage", type="primary", use_container_width=True):
        if not user_question:
            st.warning("⚠️ Please enter a question!")
            return

        with st.spinner("🔍 Searching for answer..."):
            try:
                results = search_medications(user_question, top_k=top_k)

                if not results:
                    st.error("❌ No results found.")
                    return

                st.markdown("---")

                llm_available = check_llm_available()

                if llm_available:
                    llm_name = "OpenAI" if LLM_PROVIDER == "openai" else "Ollama"
                    with st.spinner(f"🤖 Generating answer ({llm_name})..."):
                        answer = generate_answer(user_question, results)

                    if answer:
                        st.markdown("### 💊 MediSage Answer:")
                        st.markdown(
                            f"""<div style='background-color: #f0f8ff; padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50; color: #000000;'>
                            {answer}
                            </div>""",
                            unsafe_allow_html=True
                        )
                        st.markdown("")
                else:
                    st.info("""💡 **Tip:** Configure OpenAI API key to enable AI-generated answers.

1. Create API key at https://platform.openai.com/api-keys
2. Create `.env` file in project root
3. Add: `OPENAI_API_KEY=your-api-key-here`
4. Refresh page""")

                with st.expander(f"📊 View search details (Top {top_k} fragments)", expanded=not llm_available):
                    for i, result in enumerate(results, 1):
                        drug_name = result.payload['drug_name']
                        section = result.payload['section']
                        text = result.payload['text']
                        score = result.score

                        st.markdown(f"#### {i}. {drug_name} - {section}")

                        if score > 0.5:
                            st.success(f"🎯 Very good match: {score:.3f}")
                        elif score > 0.4:
                            st.info(f"✅ Good match: {score:.3f}")
                        else:
                            st.warning(f"⚠️ Weak match: {score:.3f}")

                        st.markdown("**Leaflet content:**")
                        st.markdown(f"> {text}")
                        st.markdown("---")

                st.markdown("---")
                st.warning("""
                ⚠️ **IMPORTANT:** Information is from official medication leaflets.
                MediSage **does not replace** medical consultation.
                Consult a doctor or pharmacist if you have any doubts.
                """)

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.exception(e)

    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
            <small>
            MediSage v0.1 | Deep Learning & AI Project |
            Data: OpenFDA | Vector DB: Qdrant | Embeddings: sentence-transformers
            </small>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
