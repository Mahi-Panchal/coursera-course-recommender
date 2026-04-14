import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher


df = pd.read_csv("data/coursera_courses.csv")

for col in df.columns:
    df[col] = df[col].fillna("")


df["combined_text"] = (
    (df["course_name"] + " ") * 3 +
    (df["domain"] + " ") * 3 +
    (df["subdomain"] + " ") * 2 +
    (df["mentor"] + " ") * 2 +
    (df["skills"] + " ") * 3 +
    (df["description"] + " ") +
    (df["level"] + " ") * 2
)

vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2)
)

tfidf_matrix = vectorizer.fit_transform(df["combined_text"])


def similarity(a, b):
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()


def recommend_courses(
    domain,
    subdomain="",
    mentor="",
    duration="",
    price="",
    level="",
    top_n=5
):
    filtered_df = df[df["domain"].str.lower() == domain.lower()].copy()

    if filtered_df.empty:
        return pd.DataFrame()

    user_query = f"{domain} {subdomain} {mentor} {level}"
    user_vector = vectorizer.transform([user_query])

    filtered_indices = filtered_df.index.tolist()
    filtered_matrix = tfidf_matrix[filtered_indices]

    similarity_scores = cosine_similarity(
        user_vector,
        filtered_matrix
    ).flatten()

    filtered_df["content_score"] = similarity_scores

    filtered_df["mentor_boost"] = 0
    filtered_df["subdomain_boost"] = 0

    if mentor.strip():
        filtered_df["mentor_boost"] = filtered_df["mentor"].apply(
            lambda x: similarity(mentor, x)
        )

    if subdomain.strip():
        filtered_df["subdomain_boost"] = filtered_df["subdomain"].apply(
            lambda x: similarity(subdomain, x)
        )

    filtered_df["rating_num"] = pd.to_numeric(
        filtered_df["rating"],
        errors="coerce"
    ).fillna(0)

    filtered_df["rating_boost"] = filtered_df["rating_num"] / 5

    filtered_df["final_score"] = (
        0.65 * filtered_df["content_score"]
        + 0.15 * filtered_df["mentor_boost"]
        + 0.10 * filtered_df["subdomain_boost"]
        + 0.10 * filtered_df["rating_boost"]
    )

    # optional filters
    if duration:
        filtered_df = filtered_df[
            filtered_df["duration"].str.contains(duration, case=False, na=False)
        ]

    if level:
        filtered_df = filtered_df[
            filtered_df["level"].str.contains(level, case=False, na=False)
        ]

    if price:
        filtered_df = filtered_df[
            filtered_df["price"].str.contains(price, case=False, na=False)
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
