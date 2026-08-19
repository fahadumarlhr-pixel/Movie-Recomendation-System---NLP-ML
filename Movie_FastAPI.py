from fastapi import FastAPI
from sklearn.metrics.pairwise import cosine_similarity
from main import tfidf_matrix, indices, df

app = FastAPI(title="Movie Recommendation System")

# Home Page :- 
@app.get("/")
def home():
    return {"message": "Movie Recommendation API is running!"}

# Recomendations :-
@app.get("/recommend/{title}")
def recommend(title: str, n: int = 10):
    # Plan B :- 
    if title not in indices:
        return {"movie": title, "recommendations": ["Movie Not Found"]}

    # Prcoess :-
    idx = indices[title]
    sim_score = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    similar_idx = sim_score.argsort()[::-1][1:n+1]
    recommendations = df["title"].iloc[similar_idx].tolist()

    # Return 
    return {
        "movie": title,
        "recommendations": recommendations
    }