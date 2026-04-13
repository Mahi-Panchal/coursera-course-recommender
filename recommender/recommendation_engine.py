import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================
# LOAD DATASET
# =========================
df = pd.read_csv("data/coursera_courses.csv")


# =========================
# CLEAN MISSING VALUES
# =========================
text_columns = [
    "course_name",
    "domain",
    "subdomain",
    "mentor",
    "skills",
    "description",
    "level"
]

for col in text_columns:
    df[col] = df[col].fillna("")


# =========================
# CREATE COMBINED TEXT
# =========================
df["combined_text"] = (
    df["course_name"] + " " +
    df["domain"] + " " +
    df["subdomain"] + " " +
    df["mentor"] + " " +
    df["skills"] + " " +
    df["description"] + " " +
    df["level"]
)


# =========================
# TF-IDF VECTORIZATION
# =========================
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(df["combined_text"])


# =========================
# RECOMMENDATION FUNCTION
# =========================
def recommend_courses(domain, subdomain="", mentor="", top_n=5):
    # Hard filter by domain
    filtered_df = df[df["domain"].str.lower() == domain.lower()].copy()

    if subdomain.strip():
        filtered_df = filtered_df[
            filtered_df["combined_text"].str.lower().str.contains(subdomain.lower())
        ]

    if mentor.strip():
        filtered_df = filtered_df[
            filtered_df["combined_text"].str.lower().str.contains(mentor.lower())
        ]

    if filtered_df.empty:
        return pd.DataFrame()

    user_query = f"{domain} {subdomain} {mentor}"

    user_vector = vectorizer.transform([user_query])

    filtered_indices = filtered_df.index.tolist()
    filtered_matrix = tfidf_matrix[filtered_indices]

    similarity_scores = cosine_similarity(user_vector, filtered_matrix).flatten()

    filtered_df["score"] = similarity_scores

    recommendations = filtered_df.sort_values(
        by="score",
        ascending=False
    ).head(top_n)

    return recommendations[
        ["course_name", "domain", "mentor", "level", "course_url", "score"]
    ]