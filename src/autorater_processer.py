# autorater_processor.py
#
# This script orchestrates the rating process. It reads the generated scripts,
# loads the auto-rater configurations, and uses the model specified for each
# rater to evaluate each script against that rater's criteria.
#
# Assumed Directory Structure:
# .
# ├── config/
# │   └── autoraters_config.json
# ├── autorater_prompts/
# │   └── dialogue_rater_prompt.txt
# │   └── ...
# ├── script_responses/
# │   └── prompt1_gpt-5.txt
# │   └── ...
# └── src/
#     ├── model_querier.py
#     └── autorater_processor.py
#

import os
import time
import json
import model_querier

# --- Configuration ---
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'autorater_prompts')
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'script_responses')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'autorater_responses')

def load_config():
    """Loads the main auto-rater configuration file."""
    config_path = os.path.join(CONFIG_DIR, 'autoraters_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found at {config_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {config_path}")
        return None

def get_rater_prompt(filename: str) -> str:
    """Loads the text content of a rater prompt file."""
    prompt_path = os.path.join(PROMPTS_DIR, filename)
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: Rater prompt file not found: {filename}")
        return None

def run_all_raters():
    """
    Iterates through all generated scripts and applies all configured auto-raters.
    """
    config = load_config()
    if not config:
        return

    raters = config.get("raters", [])

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created rater output directory: {OUTPUT_DIR}")

    script_files = [f for f in os.listdir(SCRIPTS_DIR) if f.endswith('.txt')]
    print(f"Found {len(script_files)} scripts to rate with {len(raters)} raters.")

    for script_filename in script_files:
        script_path = os.path.join(SCRIPTS_DIR, script_filename)
        script_base_name = os.path.splitext(script_filename)[0]

        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()

        for rater in raters:
            rater_name = rater["name"]
            rater_prompt_file = rater["prompt_file"]
            model_version = rater["model_version"]
            query_function_name = rater["query_function"]

            output_filename = f"{script_base_name}_rater_{rater_name}.json"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            if os.path.exists(output_path):
                print(f"Skipping '{rater_name}' for '{script_filename}' (already rated).")
                continue

            print(f"Running rater '{rater_name}' on '{script_filename}' using {model_version}...")

            rater_prompt_template = get_rater_prompt(rater_prompt_file)
            if not rater_prompt_template:
                continue

            # Inject the script content into the rater's prompt template
            full_prompt = rater_prompt_template.replace("{{script_text}}", script_content)

            try:
                # Dynamically get the correct query function and call it
                query_function = getattr(model_querier, query_function_name)
                raw_response = query_function(full_prompt, model_version=model_version)

                # Save the raw JSON response from the rater
                with open(output_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(raw_response)
                print(f"  -> Saved rating to {output_path}")

            except AttributeError:
                print(f"  -> Error: Query function '{query_function_name}' not found in model_querier.py.")
            except Exception as e:
                print(f"  -> An error occurred: {e}")

            time.sleep(1) # Delay to manage API rate limits

    print("\nAuto-rating process complete.")

if __name__ == "__main__":
    run_all_raters()
