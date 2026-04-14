import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CourseEngine:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path).fillna('')
        self.tfidf = TfidfVectorizer(stop_words='english')
        # Combine text for matching
        self.df['metadata'] = self.df['title'] + " " + self.df['mentor'] + " " + self.df['subdomain']
        self.matrix = self.tfidf.fit_transform(self.df['metadata'])

    def get_recs(self, domain, sub, mentor):
        # 1. Hard Filter for Domain
        subset = self.df[self.df['domain'] == domain].copy()
        if subset.empty: return pd.DataFrame()

        # 2. Similarity calculation
        query = f"{sub} {mentor}"
        query_vec = self.tfidf.transform([query])
        subset_matrix = self.tfidf.transform(subset['metadata'])
        
        scores = cosine_similarity(query_vec, subset_matrix).flatten()
        subset['score'] = scores
        return subset.sort_values('score', ascending=False).head(12)