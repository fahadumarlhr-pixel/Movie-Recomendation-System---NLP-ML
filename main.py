import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re    # Regular Expression (useful while working with punchuations)

# Read CSV :-
df = pd.read_csv("movies_metadata.csv")
"""
# print(df.head())
# print(df.shape)
# print(df.info)
# print(df.columns)
# print(df.isnull().sum())
"""

# The goal is to convert overview, genres and tagline in numbers
# using NLP, at once instead of doing indiviually of everything ...

# 1) Drop Names which has no title
df = df.dropna(subset=['title'])

# 2) Filling the miss overview with nothing cause we can't fill it with mean
df['overview'] = df['overview'].fillna('')

# 3) Telling pandas to extract the Name without brackets
df["genres"] = df["genres"].str.extract("'name': '([^']+)'")

# 4) Filling the Taglines as empty str cause no Standard Division can be applied in this case
df['tagline'] = df['tagline'].fillna('')
df['genres'] = df['genres'].fillna('')

# 5) Making one Col to have all these three
df['tag'] = df['tagline'] + " " + df["genres"] + " " + df['overview']
df['tag'] = df['tag'].fillna('')

# =====================================================

# Working with NLP :-

nltk.download("stopwords")
nltk.download("wordnet")

stopwords = set(stopwords.words('english'))  # Identifying Stop Words
lemmatizer = WordNetLemmatizer()    # Setting the Limits

# Preprccessing the text :-
def preprocessor_text(text):
    # Lower Case :-
    text = str(text).lower()

    # Removed the punctuations :-
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # Splitting the text :-
    words = text.split()

    # Remove Stop_Words :-
    words = [word for word in words if word not in stopwords]

    # Lemmatization :-
    new_words = []
    for word in words:
        new_words.append(lemmatizer.lemmatize(word))
    words = new_words

    return " ".join(words)

# Apply this Function on tag :-
df['tag'] = df['tag'].apply(preprocessor_text)

# Reset Index like 0,1,2,3,....
df = df.reset_index(drop=True)

# Indices :-
# It helps in just finiding the Indexes of each ...
indices = pd.Series(df.index, index=df['title']).drop_duplicates()

# Vocabulary Embeddings :-
from sklearn.feature_extraction.text import TfidfVectorizer
tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))

tfidf_matrix = tfidf.fit_transform(df['tag'])

# cosine_similarity & Recomendations :-
from sklearn.metrics.pairwise import cosine_similarity

def recomended(title, n=10): # Number of Recomendations will be 10
    if title not in indices:
        return ['Movie Not Found']

    idx = indices[title]
    sim_score = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    similar_idx = sim_score.argsort()[::-1][1:n+1]
    return df['title'].iloc[similar_idx]

# Pickle :-
import pickle
pickle.dump(tfidf_matrix,open('tfidf_matrix.pkl','wb'))
pickle.dump(indices,open('indices.pkl','wb'))
df.to_pickle('main.pkl')
pickle.dump(tfidf,open('tfidf.pkl','wb'))
