# model_querier.py
#
# A script to query different large language models for text generation.
#
# Installation:
# You need to install the required Python libraries.
# pip install google-generativeai openai python-dotenv anthropic
#
# API Key Setup:
# For this script to work, you need to have your API keys set as
# environment variables. Create a file named `.env` in the root directory
# and add your keys like this:
#
# GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
# OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
# ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
#

import os
import google.generativeai as genai
from openai import OpenAI
import anthropic
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from a .env file
load_dotenv()

def query_gemini(prompt_text: str, model_version: str, system_prompt: Optional[str] = None) -> str:
    """
    Sends a prompt to a specified Gemini model and returns the response.

    Args:
        prompt_text: The text prompt to send to the model.
        model_version: The specific Gemini model to use (e.g., 'gemini-1.5-pro-latest').
        system_prompt: An optional system message. For Gemini, this is prepended to the user prompt.

    Returns:
        The generated text from the model as a string.
        Returns an error message if the API call fails.
    """
    try:
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            return "Error: GOOGLE_API_KEY not found in environment variables."
        genai.configure(api_key=google_api_key)

        model = genai.GenerativeModel(model_version)

        # For Gemini, we combine the system and user prompts into a single prompt.
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt_text}"
        else:
            full_prompt = prompt_text

        response = model.generate_content(full_prompt)

        return response.text

    except Exception as e:
        return f"An error occurred with the Gemini API: {e}"

def query_openai(prompt_text: str, model_version: str, system_prompt: Optional[str] = None) -> str:
    """
    Sends a prompt to a specified OpenAI GPT model and returns the response.

    Args:
        prompt_text: The text prompt to send to the model (user message).
        model_version: The specific GPT model to use (e.g., 'gpt-4o').
        system_prompt: An optional system message to guide the model's behavior.

    Returns:
        The generated text from the model as a string.
        Returns an error message if the API call fails.
    """
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            return "Error: OPENAI_API_KEY not found in environment variables."

        client = OpenAI(api_key=openai_api_key)

        messages = []
        # The OpenAI API works best when a system message is explicitly provided.
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt_text})

        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model_version,
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"An error occurred with the OpenAI API: {e}"

def query_anthropic(prompt_text: str, model_version: str, system_prompt: Optional[str] = None) -> str:
    """
    Sends a prompt to a specified Anthropic Claude model and returns the response.

    Args:
        prompt_text: The text prompt to send to the model (user message).
        model_version: The specific Claude model to use (e.g., 'claude-3-opus-20240229').
        system_prompt: An optional system message to guide the model's behavior.

    Returns:
        The generated text from the model as a string.
        Returns an error message if the API call fails.
    """
    try:
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            return "Error: ANTHROPIC_API_KEY not found in environment variables."

        client = anthropic.Anthropic(api_key=anthropic_api_key)

        message = client.messages.create(
            model=model_version,
            max_tokens=4096,  # Anthropic requires a max_tokens value
            system=system_prompt if system_prompt else "", # Pass system prompt if it exists
            messages=[
                {
                    "role": "user",
                    "content": prompt_text
                }
            ]
        )
        return message.content[0].text

    except anthropic.NotFoundError as e:
        return (f"An error occurred with the Anthropic API: Model '{model_version}' not found. "
                f"This may be due to a typo in your config file or your API key may not have access to this model. "
                f"Original error: {e}")

    except Exception as e:
        return f"An error occurred with the Anthropic API: {e}"


# --- Example Usage ---
if __name__ == "__main__":
    script_prompt = "Write a short theatrical scene with two characters..." # Omitted for brevity

    # Example for Gemini with a system prompt
    gemini_response = query_gemini(
        prompt_text=script_prompt,
        model_version="gemini-2.5-pro",
        system_prompt="Your response should be in the style of a 1940s noir film."
    )
    print(f"--- Gemini Response ---\n{gemini_response}\n")

    # Example for OpenAI
    openai_response = query_openai(
        prompt_text=script_prompt,
        model_version="gpt-4o",
        system_prompt="Your response should be in the style of a Shakespearean comedy."
    )
    print(f"--- OpenAI Response ---\n{openai_response}\n")

    # Example for Anthropic
    anthropic_response = query_anthropic(
        prompt_text=script_prompt,
        model_version="claude-3-haiku-20240307", # Using Haiku for testing as it is widely available
        system_prompt="Your response should be in the style of a modern absurdist play."
    )
    print(f"--- Anthropic Response (Haiku) ---\n{anthropic_response}\n")

