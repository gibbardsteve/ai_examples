import logging.config
import os
from os import path

import openai

log_config_path = path.join(path.dirname(path.abspath(__file__)), "logging.conf")
logging.config.fileConfig(log_config_path)

# Create logger
logger = logging.getLogger("ai_examples")


def get_openai_models():
    """Retrieve the list of OpenAI models using the API.
    The API key is set as an environment variable which is reead in before the API call is made.
    """
    openai.api_key = os.getenv("OPENAI_KEY")

    if openai.api_key is None:
        logger.error("API key not configured in environment variables")
    else:
        logger.debug(f"API key is {openai.api_key}")
        model_data = openai.Model.list()

        for entry in model_data["data"]:
            logger.info(entry["id"])


get_openai_models()
