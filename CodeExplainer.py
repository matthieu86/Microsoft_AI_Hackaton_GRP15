import streamlit as st
import openai
from dotenv import load_dotenv

load_dotenv()

# Configuration d'Azure OpenAI


# Fonction pour expliquer un fichier Python via OpenAI
def expliquer_code(code, question="Explique ce code"):
    try:
        response = openai.Completion.create(
            model="gpt-4",  # Utilise GPT-4 pour de meilleures réponses
            prompt=f"{question}\n\n{code}",
            max_tokens=500,  # Limite de tokens
            temperature=0.7  # Niveau de créativité dans la réponse
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Erreur lors de l'explication: {str(e)}"

# Interface de l'application avec Streamlit
st.title("Explique ton fichier Python")
st.markdown("Envoie un fichier python '.py' et pose des questions sur son contenu.")

# Upload du fichier Python
uploaded_file = st.file_uploader("Choisir un fichier Python", type=["py"])

if uploaded_file is not None:
    # Lire le contenu du fichier
    code = uploaded_file.getvalue().decode("utf-8")

    st.text_area("Code Python", code, height=300)

    # Demande de l'utilisateur pour l'explication
    question = st.text_input("Pose une question sur ce code", "Explique ce code")

    if question:
        # Générer une explication avec OpenAI
        explication = expliquer_code(code, question)
        st.write(explication)

# Si aucune question n'est posée, afficher un message par défaut
else:
    st.info("Aucun fichier téléchargé. Veuillez télécharger un fichier Python.")