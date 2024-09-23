import pandas as pd
import re
import argparse
import time
from difflib import SequenceMatcher
from tqdm import tqdm
from transliterate import translit
from fuzzywuzzy import fuzz

# Enable tqdm integration with Pandas
tqdm.pandas()

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Process a CSV file and add confidence scores.')
parser.add_argument('-i', '--input_file', required=True, help='The path to the second CSV file')
args = parser.parse_args()

# Load data from CSV files
english_df = pd.read_csv('dictionary.csv')

# Deduplicate the English dictionary
english_df.drop_duplicates(subset=['Dictionary'], inplace=True)

# Normalise text
english_df['normalized'] = english_df['Dictionary'].astype(str).str.lower().replace(r'[^a-zA-Z0-9 ]', '', regex=True)

# Load data from the second CSV (specified by the user)
ukrainian_df = pd.read_csv(args.input_file)

# Transliterate and normalize Ukrainian words with progress bar
ukrainian_df['english_transliteration'] = ukrainian_df['Ім\'я/назва суб\'єкта'].progress_apply(
    lambda word: re.sub(r'[^a-zA-Z0-9 ]', '', translit(word, 'uk', reversed=True).lower())
)

ukrainian_df = ukrainian_df[0:50]

# Function to calculate confidence score with normalization
def calculate_confidence(english_word, translated_word):
#   return fuzz.ratio(english_word, translated_word) / 100  # Normalize to 0-1 range
  return SequenceMatcher(None, english_word, translated_word.lower()).ratio()

# Calculate confidence scores
confidence_scores = []
matched_words = []
for index, row in tqdm(ukrainian_df.iterrows(), total=ukrainian_df.shape[0], desc="Calculating Confidence Scores"):
  max_score = 0
  last_word = ''
  for english_index, english_word in english_df['normalized'].items():  # Iterate over index and value
    score = calculate_confidence(english_word, row['english_transliteration'])
    if score > max_score:
      max_score = score
      last_word = english_df.loc[english_index, 'Dictionary']  # Retrieve original word
  matched_words.append(last_word)
  confidence_scores.append(max_score)

# Append scores to the dataframe
ukrainian_df['matched_word'] = matched_words
ukrainian_df['confidence_score'] = confidence_scores

# Drop the 'english_transliteration' column
ukrainian_df.drop('english_transliteration', axis=1, inplace=True)

# Construct the output file name
output_file_name = args.input_file.split('.')[0] + "_with_scores.csv"

# Save the updated CSV
ukrainian_df.to_csv(output_file_name, index=False)

print("Confidence scores appended and saved!")