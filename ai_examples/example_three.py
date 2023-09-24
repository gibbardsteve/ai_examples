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
    """Example Three - create a simple cli that accepts user input and asks the
    chatGPT endpoint to respond based on it.  The program continues until the
    user quits.
    """
    continuation = False

    print("Command Line Assistant")
    print("======================")
    while True:
        if continuation is False:
            # First time through, display a simple menu
            choice = simple_menu()

        else:
            # The user wants to continue
            choice = "1"

        if choice == "1":
            continuation = question()

            if continuation is False:
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


def question() -> bool:
    """Prompt for a question at the cli, take the input and ask the question to AI.
    The response from AI is printed to the user and they are asked if they have another
    question.

    :return: continuation - does the user want to continue or exit
    :rtype: bool
    """
    user_question = input("What is your question? \n")

    print("Replying....")

    response = ask_question(user_question)

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


def ask_question(question: str) -> str:
    """Accepts a string input that is used as the content parameter passed to the
    chatGPT endpoint using the ChatCompletion API.

    The reply is extracted from the content field of the API response,
    which is found in the choices array, messages object.

    :param question: the query to ask AI
    :type question: str
    :return: response, the string returned from AI
    :rtype: str
    """
    # Use the openai ChatCompletion endpoint
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}],
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
    logger.info(response)

    return response["choices"][0]["message"]["content"]


main()
