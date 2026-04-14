import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

class CourseRecommender:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.df['sub_domain'] = self.df['sub_domain'].fillna('')
        self.df['course_title'] = self.df['course_title'].fillna('')
        
        # Combine title and subdomain for text-based filtering
        self.df['combined_features'] = self.df['course_title'] + " " + self.df['sub_domain']
        
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        self.is_fitted = False

    def get_domains(self):
        """Returns a sorted list of unique domains."""
        return sorted(self.df['domain'].unique().tolist())

    def get_subdomains(self, domain=None):
        """Returns subdomains, optionally filtered by domain."""
        if domain:
            subset = self.df[self.df['domain'] == domain]
            return sorted(subset['sub_domain'].unique().tolist())
        return sorted(self.df['sub_domain'].unique().tolist())

    def recommend(self, domain, subdomain=None, max_price=None, max_duration=None, top_n=6):
        """
        Main recommendation logic.
        1. Hard filter by Domain.
        2. Calculate content similarity based on Subdomain.
        3. Adjust score based on Price and Duration proximity.
        """
        # 1. Hard Filter by Domain
        filtered_df = self.df[self.df['domain'] == domain].copy()
        
        if filtered_df.empty:
            return pd.DataFrame()

        # Reset indices for the subset to match the local TF-IDF matrix
        filtered_df = filtered_df.reset_index(drop=True)
        
        # 2. Vectorize the filtered subset
        tfidf_subset = self.vectorizer.fit_transform(filtered_df['combined_features'])
        
        # 3. Create a query vector based on subdomain and intent
        query_text = subdomain if subdomain else ""
        query_vec = self.vectorizer.transform([query_text])
        
        # 4. Calculate Content Similarity
        content_scores = cosine_similarity(query_vec, tfidf_subset).flatten()
        
        # 5. Numerical Scoring (Optional Fields)
        # Normalize scores to [0, 1]
        
        # Price Score: 1.0 if price <= max_price, else decreasing
        if max_price is not None and max_price > 0:
            # Simple inverse relationship: the closer to 0 or max_price (from below), the better.
            # Here we just check if it's within budget.
            price_scores = filtered_df['price'].apply(lambda x: 1.0 if x <= max_price else np.exp(-(x - max_price) / 1000))
        else:
            price_scores = np.ones(len(filtered_df))

        # Duration Score: similar logic
        if max_duration is not None and max_duration > 0:
            duration_scores = filtered_df['duration'].apply(lambda x: 1.0 if x <= max_duration else np.exp(-(x - max_duration) / 2))
        else:
            duration_scores = np.ones(len(filtered_df))

        # 6. Combined Score
        # We give high weight to content similarity and moderate weight to price/duration
        final_scores = (content_scores * 0.6) + (price_scores * 0.2) + (duration_scores * 0.2)
        
        filtered_df['score'] = final_scores
        
        # Sort and return top N
        recommendations = filtered_df.sort_values(by='score', ascending=False).head(top_n)
        
        return recommendations[['course_title', 'sub_domain', 'level', 'duration', 'price', 'url', 'score']]

if __name__ == "__main__":
    # Test execution
    recommender = CourseRecommender('coursera_courses.csv')
    print("Domains:", recommender.get_domains()[:5])
    recs = recommender.recommend(domain='Data Science', subdomain='Machine Learning', max_price=5000, max_duration=2)
    print("\nTop Recommendations for Data Science / Machine Learning:")
    print(recs[['course_title', 'price', 'score']])
