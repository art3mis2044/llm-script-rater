# Art3mis2044 Theatrical Script Rater & Benchmark

This project is a comprehensive framework for automatically benchmarking and ranking large language models (LLMs) based on their ability to generate creative theatrical scripts. It provides a modular, extensible system for generating text, evaluating it against multiple weighted criteria, and displaying the results on a dynamic leaderboard.

## Current Rankings

[**Click here to view the live Leaderboard **](https://art3mis2044.github.io/llm-script-rater/)

*Note: The leaderboard is updated every time new results are pushed to the main branch.*

## Features



* **Multi-Model Script Generation**: Generate scripts from various LLM providers (Google, OpenAI, etc.) using a simple JSON configuration.
* **Modular Auto-Rater System**: Define custom "auto-raters," each with its own evaluation prompt, LLM, and weight.
* **Weighted Scoring**: The final score for each script is a weighted sum of all auto-rater scores, allowing for nuanced evaluations.
* **Automated Pipeline**: Includes separate, easy-to-run scripts for each stage of the process:
    1. Generating scripts from prompts.
    2. Rating the generated scripts.
    3. Calculating final scores and generating the leaderboard.
* **Dynamic Web Leaderboard**: A clean, sortable HTML page that dynamically loads and displays the benchmark results from a JSON file.

## How It Works

The project follows a three-step pipeline:



1. **script_prompt_processor.py**: Reads prompts from the script_prompts/ directory and queries every model defined in config/models_config.json. The generated scripts are saved in the script_responses/ directory.
2. **autorater_processor.py**: For every generated script, this script runs each auto-rater defined in config/autoraters_config.json. Each rater uses its specific prompt and LLM to generate a score, which is saved as a JSON file in autorater_responses/.
3. **leaderboard_generator.py**: This script reads all the individual rating files, applies the configured weights, calculates the total and average scores for each model, and saves the final sorted data to leaderboard/leaderboard.json.


## Project Structure

llm-script-rater/ \
├── config/ \
│   ├── models_config.json      # Define models to test \
│   └── autoraters_config.json  # Define raters, their prompts, and weights \
├── leaderboard/ \
│   ├── leaderboard.html        # The web page to display results \
│   └── leaderboard.json        # The final generated data (gitignored by default) \
├── script_prompts/ \
│   └── ... (your .txt prompt files for script generation) \
├── script_responses/ \
│   └── ... (output from the script processor) \
├── autorater_prompts/ \
│   └── ... (your .txt prompt files for each rater) \
├── autorater_responses/ \
│   └── ... (output from the rater processor) \
├── src/ \
│   ├── model_querier.py \
│   ├── script_prompt_processor.py \
│   ├── autorater_processor.py \
│   └── leaderboard_generator.py \
├── .gitignore \
├── LICENSE \
└── README.md \



## How to Use


### 1. Setup



* **Clone the repository:** \
  git clone [https://github.com/YOUR_USERNAME/llm-script-rater.git](https://github.com/YOUR_USERNAME/llm-script-rater.git) \
  cd llm-script-rater \

* **Install dependencies:** \
  pip install google-generativeai openai \

* **Set API Keys:** Create a .env file in the root directory and add your API keys: \
  GOOGLE_API_KEY="your_google_api_key" \
  OPENAI_API_KEY="your_openai_api_key" \



### 2. Configuration



* **Add Models:** Edit config/models_config.json to add or remove the LLMs you want to benchmark.
* **Add Script Prompts:** Place .txt files containing your script-writing prompts into the script_prompts/ directory.
* **Configure Raters:** Edit config/autoraters_config.json and the corresponding prompt files in autorater_prompts/ to define your evaluation criteria.


### 3. Running the Benchmark

Execute the scripts in order from the root directory:

1. **Generate the scripts** from all models 
python3 src/script_prompt_processor.py 

2. **Run the auto-raters on all generated scripts**
python3 src/autorater_processor.py

3. **Calculate the final scores and create the leaderboard.json file**
python3 src/leaderboard_generator.py

4. **Viewing the Leaderboard**

* **Locally:** To view the leaderboard.html file, you need to run a simple local web server from the leaderboard directory. \
  cd leaderboard \
  python3 -m http.server \
  \
  Then, open your browser and navigate to http://localhost:8000/leaderboard.html.
* **On GitHub (Live):** On the project page.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Credits

This project was assisted by vibe coding. 
