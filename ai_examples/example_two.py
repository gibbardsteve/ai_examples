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

# Use the openai ChatCompletion endpoint
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello ChatGPT!"}],
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
logger.debug(response)

# print the response message
print(response["choices"][0]["message"]["content"])
