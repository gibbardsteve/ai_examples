import logging.config
import os
from os import path
from typing import List

import openai

log_config_path = path.join(path.dirname(path.abspath(__file__)), "logging.conf")
logging.config.fileConfig(log_config_path)

# Create logger
logger = logging.getLogger("ai_examples")


def get_openai_models(api_key_env_name: str) -> List:
    """Retrieve the list of models using the Open AI API
    ------------
    The API key is held in an environment variable

    :param api_key_env_name: Environment variable that contains the API key
    :type model_data: list

    :return: model_data
    :rtype: List
    """

    openai.api_key = os.getenv(api_key_env_name)

    model_data = None

    if openai.api_key is None:
        logger.error("API key not configured in environment variables")
    else:
        logger.debug(f"API key is {openai.api_key}")
        model_data = openai.Model.list()

    return model_data


def print_model_element(model_data: list, entry_id: str):
    """print a list of items that relate to the specified entry id

    :param model_data: JSON object returned from openai.Model.list()
    :type model_data: list
    :param entry_id: Element in the JSON object to print out
    :type entry_id: str
    """
    for entry in model_data:
        logger.info(entry[entry_id])


model_data = get_openai_models("OPENAI_API_KEY")
print_model_element(model_data["data"], "id")
