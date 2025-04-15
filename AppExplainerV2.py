import streamlit as st
import openai
import faiss
import numpy as np

# === Azure OpenAI Config ===
client = openai.AzureOpenAI(
    api_key="ecrivez la cle",
    api_version="2023-05-15",
    azure_endpoint="mettre le endpoint"
)

EMBEDDING_DEPLOYMENT = "text-embedding-ada-002"
GPT_DEPLOYMENT = "gpt-4"

# === Session State Init ===
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'chunks' not in st.session_state:
    st.session_state['chunks'] = []
if 'embeddings' not in st.session_state:
    st.session_state['embeddings'] = None

# === Python File Processing ===
def extract_text_from_python(file):
    text = file.read().decode('utf-8')  # lecture et décodage du fichier .py
    return text

def split_text(text, max_chars=1000):
    lines = text.split("\n")
    chunks, current = [], ""
    for line in lines:
        if len(current) + len(line) < max_chars:
            current += line + "\n"
        else:
            chunks.append(current.strip())
            current = line + "\n"
    if current:
        chunks.append(current.strip())
    return chunks

def get_embedding(text):
    response = client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=text
    )
    return np.array(response.data[0].embedding, dtype="float32")

def embed_chunks(chunks):
    return np.array([get_embedding(c) for c in chunks], dtype="float32")

def search_similar_chunks(query, chunks, chunk_embeddings, k=4):
    query_embedding = get_embedding(query)
    index = faiss.IndexFlatL2(len(query_embedding))
    index.add(chunk_embeddings)
    _, I = index.search(np.array([query_embedding]), k)
    return [chunks[i] for i in I[0]]

def ask_gpt(context, question):
    prompt = f"""Tu es une IA spécialisée en analyse de code Python. En te basant uniquement sur le contenu suivant :

{context}

Réponds à la question suivante :
{question}

Réponds clairement en français sans inventer.
"""
    response = client.chat.completions.create(
        model=GPT_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500
    )
    return response.choices[0].message.content

# === Streamlit UI ===
st.title("🐍 Posez vos questions à un fichier Python (.py)")

uploaded_file = st.file_uploader("📎 Téléchargez un fichier Python", type=["py"])

if uploaded_file:
    with st.spinner("🧠 Analyse du code..."):
        raw_text = extract_text_from_python(uploaded_file)
        chunks = split_text(raw_text)
        embeddings = embed_chunks(chunks)
        st.session_state['chunks'] = chunks
        st.session_state['embeddings'] = embeddings
    st.success(f"✅ {len(chunks)} morceaux extraits et encodés.")

prompt = st.chat_input("💬 Posez votre question sur ce fichier Python...")

if prompt:
    st.session_state.past.append(prompt)
    top_chunks = search_similar_chunks(prompt, st.session_state['chunks'], st.session_state['embeddings'])
    context = "\n---\n".join(top_chunks)
    answer = ask_gpt(context, prompt)

    st.markdown(f"**👤 Vous :** {prompt}")
    st.markdown(f"**🤖 IA :** {answer}")

if st.button("🔁 Réinitialiser la session"):
    st.session_state.past.clear()
    st.session_state.chunks.clear()
    st.session_state.embeddings = None
