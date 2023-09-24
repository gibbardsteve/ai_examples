import logging.config
import os
from os import path

import openai
from dotenv import load_dotenv

load_dotenv

log_config_path = path.join(path.dirname(path.abspath(__file__)), "logging.conf")
logging.config.fileConfig(log_config_path)

# Create logger
logger = logging.getLogger("ai_examples")

openai.api_key = os.getenv("OPENAI_API_KEY")


def main():
    """Example Four - update the command line interface to retain context of prior messages.
    The program continues until the user quits.
    """
    continuation = False
    messages = []

    print("Command Line Assistant v2")
    print("=========================")
    while True:
        if continuation is False:
            # First time through, display a simple menu
            choice = simple_menu()

        else:
            # The user wants to continue
            choice = "1"

        if choice == "1":
            continuation = question(messages)

            if continuation is False:
                logger.debug("Messages Object")
                logger.debug("===============")
                logger.debug(messages)
                break

        elif choice.lower() == "q":
            print("Cheerio!")
            break
        else:
            print("Enter a valid option")


def simple_menu() -> str:
    """A simple menu driven by user input. The user choice is returned.

    :return: choice
    :rtype: str
    """
    print("1: Ask a question")
    print("Q/q: Quit")

    return input("Enter choice: ")


def question(messages: list) -> bool:
    """Prompt for a question at the cli, take the input and ask the question to AI.
    The response from AI is printed to the user and they are asked if they have another
    question.

    :param messages: a list of message objects which includes the user and assistant objects
    :type messages: list

    :return: continuation - does the user want to continue or exit
    :rtype: bool
    """
    user_question = input("What is your question? \n")

    print("Replying....")

    response = ask_question(user_question, messages)

    print("Answer....")
    print(response)

    another_question = input(
        "Do you have another question? (Y/y to continue, anything else to quit) \n"
    )

    if another_question.lower() != "y":
        logger.debug(another_question)
        print("Come back soon!")
        continuation = False
    else:
        print("\n")
        continuation = True

    return continuation


# """ Format up a message object to send to the ChatGPT API.
#     The API message object can have the following attributes:
#     role: system|user|assistant
#     content: message string
#     """
def format_messages(role: str, message: str, messages: list):
    """_summary_

    :param role: The role to send to the chatGPT API, one of system, user or assistant
    :type role: str
    :param message: The message associated with the role
    :type message: str
    :param messages: The list of message objects that make up the conversation
    :type messages: list
    """
    messages.append({"role": role, "content": message})

    logger.debug(messages[-1])


def ask_question(question: str, messages: list) -> str:
    """Accepts a string input that is used as the content parameter passed to the
    chatGPT endpoint using the ChatCompletion API.

    The reply is extracted from the content field of the API response,
    which is found in the choices array, messages object.

    :param question: the query to ask AI
    :type question: str
    :param messages: the list of message objects that make up the AI conversation
    :type messages: list
    :return: response, the string returned from AI
    :rtype: str
    """
    format_messages("user", question, messages)

    # Use the openai ChatCompletion endpoint
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

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
    logger.info("Response Object")
    logger.info("---------------")
    logger.info(response)

    # Add the response to the messages list
    messages.append(response["choices"][0]["message"])

    return response["choices"][0]["message"]["content"]


main()
