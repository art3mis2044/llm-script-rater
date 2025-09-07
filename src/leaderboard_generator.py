# leaderboard_generator.py
#
# This script processes all the individual rater responses, applies the
# configured weights, and calculates a final score for each model. It
# now includes provider info, script counts, and total scores in the final output.
#

import os
import json
from collections import defaultdict

# --- Configuration ---
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')
RATINGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'autorater_responses')
LEADERBOARD_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')
OUTPUT_FILE = os.path.join(LEADERBOARD_DIR, 'leaderboard.json')

def load_config(filename):
    """Loads a JSON configuration file."""
    config_path = os.path.join(CONFIG_DIR, filename)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading or parsing {filename}: {e}")
        return None

def calculate_leaderboard():
    """
    Calculates the weighted scores for each model and generates the leaderboard data.
    """
    rater_config = load_config('autoraters_config.json')
    models_config = load_config('models_config.json')

    if not rater_config or not models_config:
        print("Could not load configuration files. Aborting.")
        return

    # Create mappings for easy lookup
    rater_weights = {rater['name']: rater['weight'] for rater in rater_config.get('raters', [])}
    model_providers = {model['model_version']: model['provider'] for model in models_config.get('models', [])}

    model_scores = defaultdict(lambda: defaultdict(list))

    # --- Step 1: Ingest all rater responses ---
    for filename in os.listdir(RATINGS_DIR):
        if not filename.endswith('.json'):
            continue

        parts = filename.replace('.json', '').split('_rater_')
        if len(parts) != 2: continue

        script_base_info = parts[0]
        rater_name = parts[1]
        model_version = '_'.join(script_base_info.split('_')[1:])

        try:
            rating_path = os.path.join(RATINGS_DIR, filename)
            with open(rating_path, 'r', encoding='utf-8') as f:
                rating_data = json.load(f)

            score = float(rating_data.get('score', 0))
            weight = float(rater_weights.get(rater_name, 1.0))
            weighted_score = score * weight

            model_scores[model_version][script_base_info].append(weighted_score)

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Warning: Could not process file {filename}. Error: {e}")

    # --- Step 2: Calculate the final score for each script and then average for each model ---
    final_model_stats = []
    for model_version, script_ratings in model_scores.items():
        total_script_scores = []
        for script_base_info, weighted_scores in script_ratings.items():
            final_script_score = sum(weighted_scores)
            total_script_scores.append(final_script_score)

        if total_script_scores:
            total_score = sum(total_script_scores)
            script_count = len(total_script_scores)
            average_score = total_score / script_count
            provider = model_providers.get(model_version, "Unknown")

            final_model_stats.append({
                "model_version": model_version,
                "provider": provider,
                "total_score": total_score,
                "average_score": average_score,
                "script_count": script_count
            })

    # --- Step 3: Sort the leaderboard by average_score ---
    final_model_stats.sort(key=lambda x: x['average_score'], reverse=True)

    # --- Step 4: Save the final leaderboard to a file ---
    if not os.path.exists(LEADERBOARD_DIR):
        os.makedirs(LEADERBOARD_DIR)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_model_stats, f, indent=2)

    print(f"\nLeaderboard successfully generated at: {OUTPUT_FILE}")
    for i, entry in enumerate(final_model_stats, 1):
        print(f"  {i}. {entry['model_version']} ({entry['provider']}) | Total: {entry['total_score']:.2f} | Avg: {entry['average_score']:.2f} ({entry['script_count']} scripts)")

if __name__ == "__main__":
    calculate_leaderboard()
