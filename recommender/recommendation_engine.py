import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz


df = pd.read_csv("data/coursera_courses.csv")

for col in df.columns:
    df[col] = df[col].fillna("")


# =========================
# WEIGHTED TEXT CREATION
# =========================
df["combined_text"] = (
    (df["course_name"] + " ") * 3 +
    (df["domain"] + " ") * 3 +
    (df["subdomain"] + " ") * 2 +
    (df["mentor"] + " ") * 2 +
    (df["skills"] + " ") * 3 +
    (df["description"] + " ") * 1 +
    (df["level"] + " ") * 2
)

vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
tfidf_matrix = vectorizer.fit_transform(df["combined_text"])


def recommend_courses(domain, subdomain="", mentor="", duration="", top_n=5):
    filtered_df = df[df["domain"].str.lower() == domain.lower()].copy()

    if filtered_df.empty:
        return pd.DataFrame()

    user_query = f"{domain} {subdomain} {mentor}"
    user_vector = vectorizer.transform([user_query])

    filtered_indices = filtered_df.index.tolist()
    filtered_matrix = tfidf_matrix[filtered_indices]

    similarity_scores = cosine_similarity(user_vector, filtered_matrix).flatten()
    filtered_df["content_score"] = similarity_scores

    # fuzzy mentor boost
    if mentor:
        filtered_df["mentor_boost"] = filtered_df["mentor"].apply(
            lambda x: fuzz.partial_ratio(mentor.lower(), x.lower()) / 100
        )
    else:
        filtered_df["mentor_boost"] = 0

    # fuzzy subdomain boost
    if subdomain:
        filtered_df["subdomain_boost"] = filtered_df["subdomain"].apply(
            lambda x: fuzz.partial_ratio(subdomain.lower(), x.lower()) / 100
        )
    else:
        filtered_df["subdomain_boost"] = 0

    # rating boost
    filtered_df["rating_num"] = pd.to_numeric(filtered_df["rating"], errors="coerce").fillna(0)
    filtered_df["rating_boost"] = filtered_df["rating_num"] / 5

    # final weighted score
    filtered_df["final_score"] = (
        0.6 * filtered_df["content_score"]
        + 0.15 * filtered_df["mentor_boost"]
        + 0.15 * filtered_df["subdomain_boost"]
        + 0.10 * filtered_df["rating_boost"]
    )

    if duration:
        filtered_df = filtered_df[
            filtered_df["duration"].str.contains(duration, case=False, na=False)
        ]

    recommendations = filtered_df.sort_values(
        by="final_score",
        ascending=False
    ).head(top_n)

    return recommendations[
        [
            "course_name",
            "domain",
            "subdomain",
            "mentor",
            "duration",
            "rating",
            "level",
            "course_url",
            "final_score"
        ]
    ]
