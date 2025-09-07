# script_prompt_processor.py
#
# This script reads a 'models_config.json' file from a 'config' directory
# to determine which models to query. It then reads all prompt files from a
# 'script_prompts' directory, sends them to the specified LLMs, and saves
# the output to a 'script_responses' directory.
#
# Assumed Directory Structure:
# .
# ├── .env
# ├── config/
# │   └── models_config.json
# ├── script_prompts/
# │   └── prompt1.txt
# └── src/
#     ├── model_querier.py
#     └── script_prompt_processor.py
#

import os
import time
import json
import model_querier

# --- Configuration ---
# Define the paths for the config, prompts, and output directories.
# The '../' means "go up one level" from the 'src' directory.
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'models_config.json')
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'script_prompts')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'script_responses')

def load_models_config():
    """Loads the model configurations from the JSON file."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get("models", [])
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {CONFIG_FILE}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {CONFIG_FILE}")
        return None

def process_prompts():
    """
    Reads prompt files, queries models based on the config file, and saves the generated scripts.
    """
    models_to_process = load_models_config()
    if models_to_process is None:
        return # Stop execution if config is invalid

    # Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

    # Check if the prompts directory exists
    if not os.path.exists(PROMPTS_DIR):
        print(f"Error: Prompts directory not found at {PROMPTS_DIR}")
        print("Please create the 'script_prompts' directory and add your prompt files.")
        return

    prompt_files = [f for f in os.listdir(PROMPTS_DIR) if f.endswith('.txt')]
    if not prompt_files:
        print(f"No .txt prompt files found in {PROMPTS_DIR}")
        return

    print(f"Found {len(prompt_files)} prompts to process against {len(models_to_process)} models.")

    # Loop through each prompt file
    for filename in prompt_files:
        base_name = os.path.splitext(filename)[0]
        prompt_path = os.path.join(PROMPTS_DIR, filename)

        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_text = f.read()
                if not prompt_text.strip():
                    print(f"Skipping empty prompt file: {filename}")
                    continue

            # Loop through each model from the configuration file
            for model_config in models_to_process:
                model_version = model_config["model_version"]
                query_function_name = model_config["query_function"]

                output_path = os.path.join(OUTPUT_DIR, f"{base_name}_{model_version}.txt")

                if not os.path.exists(output_path):
                    print(f"Querying {model_version} for '{filename}'...")

                    # Dynamically get the query function from the model_querier module
                    try:
                        query_function = getattr(model_querier, query_function_name)
                    except AttributeError:
                        print(f"  -> Error: Query function '{query_function_name}' not found in model_querier.py. Skipping.")
                        continue

                    # Define the system prompt for script generation.
                    system_prompt_for_generation = "You are a helpful assistant, skilled in creative writing and generating theatrical scripts."

                    # Call the function with the prompt and model version
                    response = query_function(
                        prompt_text,
                        model_version=model_version,
                        system_prompt=system_prompt_for_generation
                    )

                    with open(output_path, 'w', encoding='utf-8') as out_f:
                        out_f.write(response)

                    print(f"  -> Saved response to {output_path}")
                    time.sleep(1) # Add a small delay to avoid hitting rate limits
                else:
                    print(f"Skipping {model_version} for '{filename}' (output already exists).")

        except Exception as e:
            print(f"An unexpected error occurred while processing {filename}: {e}")

    print("\nBatch processing complete.")

if __name__ == "__main__":
    process_prompts()

