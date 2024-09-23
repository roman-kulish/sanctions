# Confidence Score Calculator

## Installation

1. **Clone the repository:**

```bash
git clone <repository_url>
```

2. **Navigate to the project directory:**

```bash
cd <project_directory>
```

3. **Install the required libraries:**

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py -i <path_to_your_data_file.csv> -d <path_to_your_dictionary_file.csv>
```

* Replace `<path_to_your_data_file.csv>` and `<path_to_your_dictionary_file.csv>` with the actual paths to your files.

3. **Output:**

* The script will generate a new CSV file named `<your_data_file_name>_with_scores.csv` in the same directory. This file will contain the original data along with two additional columns:
    * `matched_word`: The closest matching word from the English dictionary.
    * `confidence_score`: A score between 0 and 1 indicating the confidence of the match.

**Important Notes:**

* **Transliteration:** The script currently assumes that the Ukrainian text can be directly compared to the English dictionary after basic normalization. If you need more accurate matching, you might consider incorporating a transliteration library like `transliterate` (if available in your environment).
