import os
import openai
import streamlit as st
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration Azure OpenAI
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")  # doit être une string dans .env
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")  # clé API dans .env

# Remplace par le nom de TON déploiement sur Azure (ex : "gpt-4-deployment")
DEPLOYMENT_NAME = "AIgrp15"  # <-- modifie cette ligne avec ton vrai nom de déploiement

# Fonction pour expliquer un fichier Python via Azure OpenAI
def expliquer_code(code, question="Explique ce code"):
    try:
        response = openai.ChatCompletion.create(
            engine=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "Tu es un assistant expert en Python."},
                {"role": "user", "content": f"{question}\n\n{code}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"Erreur lors de l'explication: {str(e)}"

# Interface de l'application avec Streamlit
st.title("Explique ton fichier Python")
st.markdown("Envoie un fichier `.py` et pose des questions sur son contenu.")

# Upload du fichier Python
uploaded_file = st.file_uploader("Choisir un fichier Python", type=["py"])

if uploaded_file is not None:
    # Lire le contenu du fichier
    code = uploaded_file.getvalue().decode("utf-8")

    st.text_area("Code Python", code, height=300)

    # Demande de l'utilisateur pour l'explication
    question = st.text_input("Pose une question sur ce code", "Explique ce code")

    if question:
        explication = expliquer_code(code, question)
        st.write(explication)
else:
    st.info("Aucun fichier téléchargé. Veuillez télécharger un fichier Python.")
