import streamlit as st

from langchain.agents import initialize_agent, load_tools, AgentType, Tool
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.utilities import GoogleSerperAPIWrapper

import random
import logging.config
import os
from os import path

from dotenv import load_dotenv


load_dotenv(dotenv_path=".env")

# Create logger
logger = logging.getLogger("langchain_examples")

# Get the environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")

# Create custom logging
log_config_path = path.join(path.dirname(path.abspath(__file__)), "../logging.conf")

print(f"Log path: :{log_config_path}")

logging.config.fileConfig(log_config_path)

logger.warning("Langchain Example Two")


def random_animal(query: str = "Get Animal"):
    """A simple Random Animal Generator, useful when you need to pick are random animal"""
    print(query)
    answers = ["Cats", "Turtles", "Dogs", "Snakes", "Buffalo", "Orangutans", "Hippo"]
    return f"My random animal is: {random.choice(answers)}"


if "langchain_search_api_key_openai" not in st.session_state:
    st.session_state["langchain_search_api_key_openai"] = openai_api_key

st.title("🔎 LangChain - Chat with search")

"""
In this example, we're using `StreamlitCallbackHandler` to display the thoughts and actions of an agent in an
interactive Streamlit app.
Built upon the LangChain 🤝 Streamlit Agent examples at
[github.com/langchain-ai/streamlit-agent](https://github.com/langchain-ai/streamlit-agent).
"""

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Hi, I'm a chatbot who can search the web. How can I help you?",
        }
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(
    placeholder="Tell me a fact about a random animal from my list of animals?"
):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info(
            "Please add your OpenAI API key to the environment variable OPENAI_API_KEY continue."
        )
        st.stop()

    if not serper_api_key:
        st.info(
            "Please add your SERPER API key to the environment variable SERPER_API_KEY continue."
        )
        st.stop()

    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo", openai_api_key=openai_api_key, streaming=True
    )
    search = GoogleSerperAPIWrapper(name="Search")

    tools = [
        Tool(
            name="Search",
            func=search.run,
            description="""useful when you need to answer questions about current events or the \
                        current state of the world""",
        ),
        Tool.from_function(
            name="Random Animal Generator",
            func=random_animal,
            description="useful when you are asked to provide a random animal",
            return_direct=False,
        ),
    ]

    native_tools = load_tools(["llm-math"], llm=llm)

    for item in native_tools:
        tools.append(item)

    search_agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        handle_parsing_errors=True,
    )
    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response = search_agent.run(st.session_state.messages, callbacks=[st_cb])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
