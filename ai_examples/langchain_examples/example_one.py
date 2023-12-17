import streamlit as st
from langchain.llms import OpenAI

import logging.config
import os
from os import path

from dotenv import load_dotenv

load_dotenv()

log_config_path = path.join(path.dirname(path.abspath(__file__)), "../logging.conf")
logging.config.fileConfig(log_config_path)

# Create logger
logger = logging.getLogger("langchain_examples")

openai_api_key = os.getenv("OPENAI_API_KEY")

logger.warning("Langchain Example One")

st.title("🦜🔗 Langchain Quickstart App")


def generate_response(input_text):
    llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)

    print(llm)
    st.info(llm(input_text))


# A simple streamlit form hardcoded with a question
# From the example at: https://blog.streamlit.io/langchain-tutorial-1-build-an-llm-powered-app-in-18-lines-of-code/
with st.form("my_form"):
    text = st.text_area("Enter text:", "3 key things for learning how to code?")
    submitted = st.form_submit_button("Submit")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
    elif submitted:
        generate_response(text)
