# Generative AI Examples in Python
This repository contains a series of examples to investigate the use of the Open AI API and Langchain packages in Python.

## Example One
Use the Open AI API to retrieve a list of the available LLM models

```
poetry run python example_one.py
```

## Example Two
Use the python_dotenv package to work with the API secret.  

Create a .env file in the repository root and add:
```
OPENAI_API_KEY=<your_key>
```

Ensure your .env file is *never* checked in to source control, it needs to be added to the .gitignore to ensure this.

example_two.py then uses the Open AI API ChatCompletion endpoint to send a message to ChatGPT and interrogate the response.

```
poetry run python example_two.py
```

## License
See [LICENSE](LICENSE)