import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CourseEngine:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path).fillna('General')
        self.tfidf = TfidfVectorizer(stop_words='english')
        # Metadata for matching optional fields
        self.df['metadata'] = self.df['subdomain'] + " " + self.df['mentor'] + " " + self.df['title']
        self.matrix = self.tfidf.fit_transform(self.df['metadata'])

    def recommend(self, domain, duration, price, subdomain, mentor):
        # 1. COMPULSORY FILTERS (Hard Logic)
        mask = (self.df['domain'] == domain) & \
               (self.df['duration'] == duration) & \
               (self.df['price'] == price)
        
        filtered_df = self.df[mask].copy()
        
        if filtered_df.empty:
            return pd.DataFrame()

        # 2. OPTIONAL MATCHING (Vector Similarity)
        # If user provides subdomain/mentor, we rank the filtered list
        query_text = f"{subdomain} {mentor}"
        if query_text.strip():
            query_vec = self.tfidf.transform([query_text])
            subset_matrix = self.tfidf.transform(filtered_df['metadata'])
            scores = cosine_similarity(query_vec, subset_matrix).flatten()
            filtered_df['score'] = scores
            return filtered_df.sort_values('score', ascending=False).head(9)
        
        return filtered_df.head(9)
