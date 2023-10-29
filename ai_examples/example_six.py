import streamlit as st

import logging.config
import os
from os import path

import openai
import tiktoken
from dotenv import load_dotenv

load_dotenv()

log_config_path = path.join(path.dirname(path.abspath(__file__)), "logging.conf")
logging.config.fileConfig(log_config_path)

# Create logger
logger = logging.getLogger("ai_examples")

openai.api_key = os.getenv("OPENAI_API_KEY")


def format_messages(role: str, message: str, messages: list):
    """Format up a message object to send to the ChatGPT API.
    The API message object can have the following attributes:
    role: system|user|assistant
    content: message string

    :param role: The role to send to the chatGPT API, one of system, user or assistant
    :type role: str
    :param message: The message associated with the role
    :type message: str
    :param messages: The list of message objects that make up the conversation
    :type messages: list
    """
    messages.append({"role": role, "content": message})

    logger.debug(messages[-1])


# Example reply from OpenAI
# JSON reply structure
# {
#   "id": "chatcmpl-7xHKegP1246BrABCDE...xample",
#   "object": "chat.completion",
#   "created": 1694362332,
#   "model": "gpt-3.5-turbo-0613",
#   "choices": [
#     {
#       "index": 0,
#       "message": {
#         "role": "assistant",
#         "content": "Nice to meet you too! How can I assist you today?"
#       },
#       "finish_reason": "stop"
#     }
#   ],
#   "usage": {
#     "prompt_tokens": 12,
#     "completion_tokens": 13,
#     "total_tokens": 25
#   }
# }


def ask_question(
    question: str, messages: list, model: str, count_tokens: bool = False
) -> str:
    """Accepts a string input that is used as the content parameter passed to the
    chatGPT endpoint using the ChatCompletion API.

    The reply is extracted from the content field of the API response,
    which is found in the choices array, messages object.

    :param question: the query to ask AI
    :type question: str
    :param messages: the list of message objects that make up the AI conversation
    :type messages: list
    :param model: the LLM model to be used (e.g gpt-3.5-turbo)
    :type model: str
    :param print_tokens: output the token usage from the response
    :type print_tokens: str
    :return: response, the string returned from AI
    :rtype: str
    """
    format_messages("user", question, messages)

    # github how_to_count_tokens_with_tiktoken
    if count_tokens:
        token_info = calculate_tokens(model, messages)

    # Use the openai ChatCompletion endpoint
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
    )

    ai_response = response["choices"][0]["message"]["content"]

    if count_tokens:
        ans_tokens = calculate_tokens_in_question(
            token_info["encoding"], response["choices"][0]["message"]["content"]
        )

        print_tokens(token_info, ans_tokens, response)
        token_string = format_tokens(token_info, ans_tokens, response)

        ai_response += "\n" + token_string

        print(ai_response)

    logger.debug("Response Object")
    logger.debug("---------------")
    logger.debug(response)

    # Add the response to the messages list
    messages.append(response["choices"][0]["message"])

    return ai_response


def get_encoding(model: str):
    # Get the encoding associated with the model being used
    encoding = tiktoken.encoding_for_model(model)
    logger.debug(f"For {model} the encoding is {encoding}")

    return encoding


def calculate_tokens_in_question(encoding, question: str) -> int:
    # How many tokens in the question?
    # tokens_integer is a list of the int encoded tokens from the question
    tokens_integer = encoding.encode(question)
    question_length = len(tokens_integer)
    logger.debug(f"{question_length} tokens are used in the question: {question}")

    # The byte encoded token strings can be decoded from the list of token integers
    tokens_string = [
        encoding.decode_single_token_bytes(token) for token in tokens_integer
    ]
    logger.debug(tokens_string)

    return question_length


def calculate_tokens(model: str, messages: list) -> dict:
    # Get the encoding associated with the model being used
    encoding = get_encoding(model)

    # Calculate the tokens used in the messages list
    # gpt-4 and gpt-3.5 models use 3 tokens if name is not specified or 4 if it is
    # Every message object uses 3 tokens for <|start|>{role/name}\n{content}<|end>\n
    # Token prices are available here https://openai.com/pricing
    # gpt-3.5-turbo-0613 (4k context)
    # input tokens charged at 0.0015 per 1000 tokens
    # output tokens charged at 0.002 per 1000 tokens
    # gpt-3.5-turbo-16k (16k context)
    # input tokens charged at 0.003 per 1000 tokens
    # output tokens charged at 0.004 per 1000 tokens
    tokens_per_message_entry = 3
    tokens_per_name = 1
    tokens_total = 0

    for obj in messages:
        tokens_total += tokens_per_message_entry

        for key, value in obj.items():
            tokens_in_value = calculate_tokens_in_question(encoding, value)
            tokens_total += tokens_in_value
            if key == "name":
                tokens_total += tokens_per_name
            logger.debug(f"{key} is {tokens_in_value} tokens")
            logger.debug(f"Tokens_total {tokens_total}")

    # Every reply uses three tokens <|start|>assistant<|message>
    tokens_total += 3

    token_info = {"encoding": encoding, "tokens_total": tokens_total}
    return token_info


def print_tokens(token_info: dict, ans_tokens: int, response: any):
    print("Tokens calculated")
    print("---------------------------")
    print(f"prompt: {token_info['tokens_total']}")
    print(f"calc reply:{ans_tokens}")
    print(f"calc total tokens:{token_info['tokens_total']+ans_tokens}")
    print("Token usage in reply")
    print("---------------------")
    print(f"prompt tokens: {response['usage']['prompt_tokens']}")
    print(f"completion tokens: {response['usage']['completion_tokens']}")
    print(f"total tokens: {response['usage']['total_tokens']}")


# Note: to add a linebreak with st.markdown the line needs to have two spaces before \n
def format_tokens(token_info: dict, ans_tokens: int, response: any) -> str:
    output_string = (
        f"\n\nTokens calculated  \n"
        f"prompt: {token_info['tokens_total']}  \n"
        f"calc reply: {ans_tokens}  \n"
        f"calc total tokens: {token_info['tokens_total'] + ans_tokens}  \n"
        f"  \n"
        f"Token usage in reply  \n"
        f"prompt tokens: {response['usage']['prompt_tokens']}  \n"
        f"completion tokens: {response['usage']['completion_tokens']}  \n"
        f"total tokens: {response['usage']['total_tokens']}  \n"
    )

    return output_string


# ----- SETTINGS -----
page_title = "AI Chat Interface"
page_icon = ":robot_face:"  # https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
layout = "centered"
# --------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

# ----- DROPDOWN
options = ["Ask Question", "Calculate Tokens"]
ai_models = ["gpt-3.5-turbo"]

# ----- INPUT ---------
st.header("Ask me a question")
if st.button("Clear Answer"):
    st.rerun()
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    col1.selectbox("Chat Option", options, key="option")
    col2.selectbox("AI Model", ai_models, key="ai_model")

    "---"
    with st.expander("Question", expanded=True):
        user_question = st.text_area(
            "",
            placeholder="Add your question here ...",
            help="Write your question here",
        )

    "---"
    answer = ""
    answer_placeholder = st.empty()

    submitted = st.form_submit_button("Submit")

    # Trigger question to AI
    if submitted and user_question:
        option_selection = st.session_state["option"]
        model_selection = st.session_state["ai_model"]

        messages = []
        count_tokens = False

        if option_selection == "Calculate Tokens":
            count_tokens = True

        answer = ask_question(user_question, messages, model_selection, count_tokens)

        st.success(
            "Question Sent, Tokens Calculated" if count_tokens else "Question Sent"
        )

    with st.expander("Answer", expanded=submitted):
        st.markdown(answer)
