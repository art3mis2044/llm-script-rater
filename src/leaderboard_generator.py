# leaderboard_generator.py
#
# This script processes all the individual rater responses, applies the
# configured weights, and calculates a final score for each model. It
# now includes a detailed breakdown of scores per rater in the final output.
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

def print_leaderboard(leaderboard_data):
    """Prints the leaderboard to the console in a formatted table."""
    print("\n--- Art3mis2044 Theatrical Script Generation Leaderboard ---")

    for i, model in enumerate(leaderboard_data):
        rank = i + 1
        print("-" * 80)
        print(f"Rank {rank}: {model['model_version']} (Provider: {model['provider']})")
        print(f"  Scripts Rated: {model['script_count']}")
        print(f"  Total Score:   {model['total_score']:.2f}")
        print(f"  Average Score: {model['average_score']:.2f}")

        if model.get('rater_breakdown'):
            print("  --- Rater Breakdown (Weighted) ---")
            rater_header = "    | {:<20} | {:<12} | {:<14} |".format("Rater", "Total Score", "Average Score")
            print(rater_header)
            print("    " + "-" * (len(rater_header) - 4))
            for rater in model['rater_breakdown']:
                rater_row = "    | {:<20} | {:<12.2f} | {:<14.2f} |".format(
                    rater['rater_name'],
                    rater['total_score'],
                    rater['average_score']
                )
                print(rater_row)
        print("-" * 80)


def calculate_leaderboard():
    """
    Calculates the weighted scores for each model and generates the leaderboard data,
    including a per-rater breakdown.
    """
    rater_config = load_config('autoraters_config.json')
    models_config = load_config('models_config.json')

    if not rater_config or not models_config:
        print("Could not load configuration files. Aborting.")
        return

    rater_weights = {rater['name']: rater['weight'] for rater in rater_config.get('raters', [])}
    model_providers = {model['model_version']: model['provider'] for model in models_config.get('models', [])}

    # Store more detailed rating information
    model_ratings = defaultdict(list)

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
            model_ratings[model_version].append({
                "script": script_base_info,
                "rater": rater_name,
                "score": score
            })

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Warning: Could not process file {filename}. Error: {e}")

    # --- Step 2: Calculate final stats for each model ---
    final_model_stats = []
    for model_version, ratings in model_ratings.items():
        if not ratings: continue

        # Calculate total and average scores
        script_scores = defaultdict(float)
        for rating in ratings:
            weight = rater_weights.get(rating['rater'], 1.0)
            script_scores[rating['script']] += rating['score'] * weight

        total_score = sum(script_scores.values())
        script_count = len(script_scores)
        average_score = total_score / script_count if script_count > 0 else 0

        # Calculate per-rater total and average scores (weighted)
        rater_scores = defaultdict(list)
        for rating in ratings:
            rater_scores[rating['rater']].append(rating['score'])

        rater_breakdown = []
        for rater_name, scores in rater_scores.items():
            weight = rater_weights.get(rater_name, 1.0)
            total_rater_score_weighted = sum(s * weight for s in scores)
            # Average is the total weighted score for that rater divided by the total number of scripts for the model
            avg_rater_score_weighted = total_rater_score_weighted / script_count if script_count > 0 else 0

            rater_breakdown.append({
                "rater_name": rater_name,
                "total_score": total_rater_score_weighted,
                "average_score": avg_rater_score_weighted
            })
        rater_breakdown.sort(key=lambda x: x['rater_name'])


        final_model_stats.append({
            "model_version": model_version,
            "provider": model_providers.get(model_version, "Unknown"),
            "total_score": total_score,
            "average_score": average_score,
            "script_count": script_count,
            "rater_breakdown": rater_breakdown
        })

    # --- Step 3: Sort the leaderboard by average_score ---
    final_model_stats.sort(key=lambda x: x['average_score'], reverse=True)

    # --- Step 4: Print and save the final leaderboard ---
    print_leaderboard(final_model_stats)

    if not os.path.exists(LEADERBOARD_DIR):
        os.makedirs(LEADERBOARD_DIR)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_model_stats, f, indent=2)

    print(f"\nLeaderboard successfully generated at: {OUTPUT_FILE}")

if __name__ == "__main__":
    calculate_leaderboard()

