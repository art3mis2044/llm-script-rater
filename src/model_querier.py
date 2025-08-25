# model_querier.py
#
# A script to query different large language models for text generation.
#
# Installation:
# You need to install the required Python libraries.
# pip install google-generativeai openai python-dotenv
#
# API Key Setup:
# For this script to work, you need to have your API keys set as
# environment variables. Create a file named `.env` in the same directory
# as this script and add your keys like this:
#
# GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
# OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
#

import os
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

def query_gemini(prompt_text: str, model_version: str) -> str:
    """
    Sends a prompt to a specified Gemini model and returns the response.

    Args:
        prompt_text: The text prompt to send to the model.
        model_version: The specific Gemini model to use (e.g., 'gemini-1.5-pro-latest').

    Returns:
        The generated text from the model as a string.
        Returns an error message if the API call fails.
    """
    try:
        # Configure the Gemini API key
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            return "Error: GOOGLE_API_KEY not found in environment variables."
        genai.configure(api_key=google_api_key)

        # Initialize the specified model
        model = genai.GenerativeModel(model_version)

        # Generate the content
        response = model.generate_content(prompt_text)

        return response.text

    except Exception as e:
        return f"An error occurred with the Gemini API: {e}"

def query_openai(prompt_text: str, model_version: str) -> str:
    """
    Sends a prompt to a specified OpenAI GPT model and returns the response.

    Args:
        prompt_text: The text prompt to send to the model.
        model_version: The specific GPT model to use (e.g., 'gpt-4o', 'gpt-5').

    Returns:
        The generated text from the model as a string.
        Returns an error message if the API call fails.
    """
    try:
        # The OpenAI library automatically looks for the OPENAI_API_KEY
        # environment variable, so no explicit configuration is needed if it's set.
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            return "Error: OPENAI_API_KEY not found in environment variables."

        client = OpenAI(api_key=openai_api_key)

        # Create the chat completion request
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant, skilled in creative writing and generating theatrical scripts.",
                },
                {
                    "role": "user",
                    "content": prompt_text,
                }
            ],
            model=model_version, # Use the specified model version
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"An error occurred with the OpenAI API: {e}"

# --- Example Usage ---
if __name__ == "__main__":
    # A sample prompt for generating a short script scene
    script_prompt = """
    Write a short theatrical scene (1-2 pages) with two characters:
    - ANNA (30s), a pragmatic and slightly stressed architect.
    - LEO (30s), her free-spirited and perpetually optimistic brother.
    
    Setting: A cluttered attic.
    
    Situation: They are sorting through their late grandmother's belongings and discover a locked, ornate wooden box. Anna wants to find the key; Leo wants to break it open.
    """

    gemini_model_to_test = "gemini-1.5-pro-latest"
    print(f"--- Querying {gemini_model_to_test} ---")
    gemini_response = query_gemini(script_prompt, model_version=gemini_model_to_test)
    print(gemini_response)
    print("\n" + "="*50 + "\n")

    openai_model_to_test = "gpt-5"
    print(f"--- Querying {openai_model_to_test} ---")
    openai_response = query_openai(script_prompt, model_version=openai_model_to_test)
    print(openai_response)
