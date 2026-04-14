import streamlit as st
import pandas as pd
from recommender import CourseRecommender
import time

# Page Configuration
st.set_page_config(
    page_title="Coursera Recommender | AI-Powered",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize Recommender
@st.cache_resource
def init_recommender():
    return CourseRecommender('coursera_courses.csv')

def main():
    try:
        load_css('style.css')
    except:
        pass # Fallback to default if CSS missing

    recommender = init_recommender()

    # --- Sidebar Filters ---
    st.sidebar.markdown("### 🔍 Discovery Filters")
    
    # Domain (Required)
    domains = recommender.get_domains()
    selected_domain = st.sidebar.selectbox("Choose a Domain", ["Select Domain"] + domains)

    # Optional Fields
    subdomains = []
    if selected_domain != "Select Domain":
        subdomains = recommender.get_subdomains(selected_domain)
    
    selected_subdomain = st.sidebar.selectbox("Subdomain (Optional)", ["All Subdomains"] + subdomains)
    
    max_price = st.sidebar.number_input("Max Price (Rupees)", min_value=0, value=10000, step=500)
    
    max_duration = st.sidebar.slider("Maximum Duration (Months)", 1, 12, 6)

    st.sidebar.markdown("---")
    recommend_btn = st.sidebar.button("✨ Get Recommendations")

    # --- Main Content ---
    st.markdown("<h1 class='main-title'>Coursera Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9699a3; margin-top: -1.5rem;'>Discover your next career milestone with AI-driven course matching.</p>", unsafe_allow_html=True)

    if selected_domain == "Select Domain":
        st.info("👈 Please select a **Domain** in the sidebar to start your learning journey.")
        
        # UI Placeholder / Intro
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 🚀 Fast Growth")
            st.write("Top-tier courses from industry leaders.")
        with col2:
            st.markdown("### 💎 Premium Content")
            st.write("Expertly curated for maximum impact.")
        with col3:
            st.markdown("### 📊 Data Driven")
            st.write("Matched to your specific goals.")
    
    else:
        if recommend_btn:
            with st.spinner("Analyzing catalogs and matching your profile..."):
                time.sleep(1) # Aesthetic delay
                
                # Process empty values
                sub_query = selected_subdomain if selected_subdomain != "All Subdomains" else None
                
                results = recommender.recommend(
                    domain=selected_domain,
                    subdomain=sub_query,
                    max_price=max_price,
                    max_duration=max_duration
                )

                if results.empty:
                    st.warning("No courses found matching these specific criteria. Try broadening your price or duration filters.")
                else:
                    st.markdown(f"### top recommendations for **{selected_domain}**")
                    
                    # Display Grid
                    cols = st.columns(3)
                    for idx, (_, row) in enumerate(results.iterrows()):
                        col = cols[idx % 3]
                        with col:
                            # Render custom card
                            st.markdown(f"""
                                <div class="course-card animate-in" style="animation-delay: {idx * 0.1}s">
                                    <div class="course-sub">{row['sub_domain']}</div>
                                    <div class="course-title">{row['course_title']}</div>
                                    <div class="course-meta">
                                        <span>📍 {row['level']}</span>
                                        <span>⏳ {row['duration']} Months</span>
                                    </div>
                                    <div class="course-meta">
                                        <span class="price-tag">₹{row['price']:,.2f}</span>
                                        <a href="{row['url']}" target="_blank" style="text-decoration: none; color: #bb9af7; font-weight: 600;">View Course →</a>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.success("Configuration set! Click 'Get Recommendations' to see results.")

if __name__ == "__main__":
    main()
