import re
from collections import Counter
import pandas as pd

#Script to shorten the description of the books in the dataset

#Importing datasets
#Books
books_file = 'src/datasets/books_rs/books_top1000.csv'
df_books = pd.read_csv(books_file)

def shorten_description(text, max_words=35):

    if not isinstance(text, str):
        return ""  # Return empty string or a placeholder for non-string values
    
    # Tokenize text into words
    words = re.findall(r'\w+', text)
    
    # Get the frequency of each word
    word_freq = Counter(words)
    
    # Split text into sentences
    sentences = re.split(r'(?<=\.)\s+', text)
    
    # Sort sentences by the sum of word frequencies
    sorted_sentences = sorted(sentences, key=lambda s: sum(word_freq[word] for word in re.findall(r'\w+', s)), reverse=True)
    
    # Select sentences until the word count reaches max_words
    selected_sentences = []
    current_word_count = 0
    
    for sentence in sorted_sentences:
        sentence_word_count = len(re.findall(r'\w+', sentence))
        if current_word_count + sentence_word_count <= max_words:
            selected_sentences.append(sentence)
            current_word_count += sentence_word_count
        else:
            break
    
    # Join selected sentences to form the shortened description
    shortened_text = " ".join(selected_sentences)
    return shortened_text

# Create a new dataframe with shortened descriptions
df_books_shortened = df_books.copy()
df_books_shortened['short_description'] = df_books['description'].apply(shorten_description)

# Function to replace old descriptions with new shorter ones
def replace_descriptions(df):
    df['description'] = df['short_description']
    df.drop(columns=['short_description'], inplace=True)
    return df

# Call the function to replace descriptions in the dataframe
df_books_replaced = replace_descriptions(df_books_shortened)

# Save the new dataframe to a CSV file
df_books_replaced.to_csv('src/books_top1000_shortened.csv', index=False)