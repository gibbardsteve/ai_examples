import json
import time
from string import Template

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
#from langchain_community.chat_models import ChatOpenAI
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI

CHUNK_SIZE = 500
OVERLAP = 100

# Load the prompt template
def load_prompt_config(template_file, response_file=None):
    # Load the prompt template from a file
    with open(template_file, 'r') as file:
        prompt_template = file.read()
    
    if response_file is not None:
        # Load the response structure from a JSON file
        with open(response_file, 'r') as json_file:
            response_structure_data = json.load(json_file)
            response_structure = json.dumps(response_structure_data, indent=2)  

            # Not sure how parenthesis work in prompt templates, but adding 4 for each 
            # parenthesis seems to work, these escape the character but I suspect there is
            # multiple escapes happening.
            response_structure = response_structure.replace("{", "{{{{").replace("}", "}}}}")

            prompt_with_response_structure = prompt_template.replace("[response_structure]", response_structure)

            prompt_template = prompt_with_response_structure 

    formatted_prompt = prompt_template.format(
            context="{context}",  # Replace with actual context
            scoring_system="{scoring_system}",  # Replace with actual scoring system
            input="{assessment}"  # Replace with the actual assessment text
        )

    # Create the PromptTemplate object with the formatted prompt
    prompt = PromptTemplate(template=formatted_prompt, input_variables=["context", "scoring_system", "assessment"])

    return prompt


# Retry function to handle rate limit errors
def embed_with_retry(texts, embeddings):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            # Embed documents using OpenAI
            return embeddings.embed_documents(texts)
        except Exception as e:  # Catch all OpenAI API-related errors
            if "rate limit" in str(e).lower():
                if attempt < max_retries - 1:
                    # Wait and retry
                    wait_time = 5 * (attempt + 1)  # Exponential backoff
                    print(f"Rate limit error, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise e  # Exceeded retries
            else:
                raise e  # Reraise other exceptions

# Step 1: Load user-provided criteria document
def load_criteria_document(criteria_pdf_path):
    # Load the criteria PDF document
    loader = PyPDFLoader(criteria_pdf_path)
    pages = loader.load_and_split()  # Split pages to analyze criteria

    # Extract criteria text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=OVERLAP)
    criteria_docs = text_splitter.split_documents(pages)
    return criteria_docs

# Step 2: Upload and process the assessment
def process_assessment(assessment_pdf_path):
    loader = PyPDFLoader(assessment_pdf_path)
    pages = loader.load_and_split()  # Split pages to analyze the assessment
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=OVERLAP)
    assessment_docs = text_splitter.split_documents(pages)
    return assessment_docs

# Step 3: Define the comparison function (NLP model)
def compare_assessment_to_criteria(criteria_docs, assessment_docs, scoring_system):
    # Embed both criteria and assessment using OpenAI embeddings
    embeddings = OpenAIEmbeddings()

    # Extract text from documents for embedding
    criteria_texts = [doc.page_content for doc in criteria_docs]
    assessment_texts = [doc.page_content for doc in assessment_docs]

    # Use FAISS to create a vector store with criteria embeddings
    criteria_embeddings = embed_with_retry(criteria_texts, embeddings)
    criteria_vector_store = FAISS.from_documents(criteria_docs, embeddings)

    # Build prompt from config
    prompt = load_prompt_config("ai_examples/langchain_examples/v0.3/example_prompt.txt",
                                "ai_examples/langchain_examples/v0.3/response_structure.json")

    if debug:
        for i in range(15):
            print("PROMPT FOLLOWS")
        print(f"PROMPT {prompt}")
        print("PROMPTEND")

    model_name = "gpt-4o-mini"  # Specify your desired model here
    # Initialize the LLM chain
    llm = ChatOpenAI(temperature=0.7, model_name=model_name)

    print(f"Using OpenAI model: {model_name}")  # Print the model being used

    # Create a chain to combine documents using the provided prompt
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    
    # Create the retrieval chain
    rag_chain = create_retrieval_chain(criteria_vector_store.as_retriever(), combine_docs_chain)

    # Prepare the input for the chain
    input_data = {
        "input": "\n".join(assessment_texts),
        "assessment": "\n".join(assessment_texts),
        "context": "\n".join(criteria_texts),
        "scoring_system": scoring_system
    }

    if debug:
        # log the input data to the console
        print(f"INPUT DATA: {input_data}")

    # Run comparison between criteria and assessment using the RAG chain
    response = rag_chain.invoke(input_data)

    if debug:
        for i in range(15):
            print("RESPONSE FOLLOWS")
        print(f"RESPONSE:{response}")

    return response['answer'] 

def generate_json_response(criteria, assessment, scoring_system):
    comparison_result = compare_assessment_to_criteria(criteria, assessment, scoring_system)

    if debug:
        for i in range(15):
            print("COMPARISON FOLLOWS")
        print(f"COMPARISON {comparison_result}")

    # If comparison_result is a string, convert it to a dictionary
    if isinstance(comparison_result, str):
     # Remove the surrounding backticks and extra spaces
        comparison_result = comparison_result.strip()

        # Check if it starts with ``` followed by a newline and json
        if comparison_result.startswith("```json\n"):
            # Extract the JSON part by splitting the string
            comparison_result = comparison_result.split("```")[1].strip()  # Get the JSON part
            comparison_result = comparison_result.split("json\n")[1].strip()  # Get the JSON part

            if debug:
                print(comparison_result)
        else:
            raise ValueError("The comparison result does not contain valid JSON format.")

        try:
            comparison_result = json.loads(comparison_result)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON: {e}")
        
    return json.dumps({
        "skills": comparison_result.get('skills'),
        "summary": comparison_result.get('summary')
    }, indent=4)

# Step 5: Running the AI agent
debug = False
if __name__ == "__main__":
    # Define paths
    criteria_pdf = "ai_examples/langchain_examples/data/criteria/lead/LeadAssessmentRequirements.pdf"
    assessment_pdf = "ai_examples/langchain_examples/data/assessment/lead/ChaswickJohnLeadSoftwareEngineer.pdf"
    
    # Load documents
    criteria = load_criteria_document(criteria_pdf)
    assessment = process_assessment(assessment_pdf)

    # Define scoring system (for example, 1-4 scale)
    scoring_system = {
        "1": "Does not meet criteria",
        "2": "Partially meets criteria",
        "3": "Mostly meets criteria",
        "4": "Fully meets criteria"
    }
    
    # Run the comparison and get JSON result
    result_json = generate_json_response(criteria, assessment, scoring_system)
    
    # Output result
    print(result_json)
