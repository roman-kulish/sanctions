import pandas as pd
import re
import argparse
from tqdm import tqdm
from transliterate import translit
from fuzzywuzzy import fuzz

# Enable tqdm integration with Pandas
tqdm.pandas()

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Process a CSV file and add confidence scores.')
parser.add_argument('-i', '--input_file', required=True, help='The path to the second CSV file')
parser.add_argument('-d', '--input_dictionary', required=True, help='The path to the dictionary CSV file')
args = parser.parse_args()

# Load data from CSV files
english_df = pd.read_csv(args.input_dictionary)

# Deduplicate the English dictionary
english_df.drop_duplicates(subset=['Dictionary'], inplace=True)

# Normalise text (including trimming and space normalization)
english_df['normalized'] = (
  english_df['Dictionary']
  .astype(str)
  .str.lower()
  .str.replace(r'[^a-zA-Z0-9 ]', '', regex=True)  # Remove non-alphanumeric characters except spaces
  .str.strip()  # Trim leading/trailing spaces
  .str.replace(r'\s+', ' ', regex=True)  # Normalize multiple spaces to single space
)

# Load data from the second CSV (specified by the user)
ukrainian_df = pd.read_csv(args.input_file)

# Transliterate and normalize Ukrainian words with progress bar
ukrainian_df['ukrainian_transliteration'] = ukrainian_df['Ім\'я/назва суб\'єкта'].progress_apply(
  lambda word: re.sub(r'\s+', ' ', re.sub(r'[^a-zA-Z0-9 ]', '', translit(word, 'uk', reversed=True).lower()).strip())
)

ukrainian_df['russian_transliteration'] = ukrainian_df['russian_name'].progress_apply(
  lambda word: re.sub(r'\s+', ' ', re.sub(r'[^a-zA-Z0-9 ]', '', translit(word, 'ru', reversed=True).lower()).strip())
)

# Function to calculate confidence score with normalization
def calculate_confidence(english_word, translated_word):
  return fuzz.ratio(english_word, translated_word) / 100  # Normalize to 0-1 range

# Calculate confidence scores
confidence_scores = []
matched_words = []
for index, row in tqdm(ukrainian_df.iterrows(), total=ukrainian_df.shape[0], desc="Calculating Confidence Scores"):
  max_score = 0
  last_word = ''
  for english_index, english_word in english_df['normalized'].items():  # Iterate over index and value
    score_ukrainian = calculate_confidence(english_word, row['ukrainian_transliteration'])
    score_russian = calculate_confidence(english_word, row['russian_transliteration'])
    score = max(score_ukrainian, score_russian)  # Take the higher score

    if score > max_score:
      max_score = score
      last_word = english_df.loc[english_index, 'Dictionary']  # Retrieve original word
  matched_words.append(last_word)
  confidence_scores.append(max_score)

# Append scores to the dataframe
ukrainian_df['matched_word'] = matched_words
ukrainian_df['confidence_score'] = confidence_scores

# Drop the transliteration columns
ukrainian_df.drop('russian_name', axis=1, inplace=True)
ukrainian_df.drop('ukrainian_transliteration', axis=1, inplace=True)
ukrainian_df.drop('russian_transliteration', axis=1, inplace=True)

# Construct the output file name
output_file_name = args.input_file.split('.')[0] + "_with_scores.csv"

# Save the updated CSV
ukrainian_df.to_csv(output_file_name, index=False)

print("Confidence scores appended and saved!")