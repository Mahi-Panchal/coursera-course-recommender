import streamlit as st
from recommender.recommendation_engine import recommend_courses

st.set_page_config(
    page_title="Course Recommender",
    page_icon="🎓",
    layout="wide"
)

# =========================
# CREATIVE HEADER
# =========================
st.markdown("""
    <h1 style='text-align:center; color:#4F46E5;'>
        🎓 Smart Course Recommender
    </h1>
    <p style='text-align:center; font-size:18px; color:gray;'>
        Discover the best courses based on your learning goals
    </p>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================
# FILTER SECTION
# =========================
col1, col2 = st.columns(2)

with col1:
    domain = st.selectbox(
        "📚 Select Domain",
        [
            "Artificial Intelligence",
            "Data Science",
            "Web Development",
            "Cloud Computing",
            "Cybersecurity",
            "Mobile Development",
            "Blockchain",
            "UI UX",
            "DevOps",
            "Programming"
        ]
    )

    subdomain = st.text_input("🔍 Subdomain (Optional)")

with col2:
    mentor = st.text_input("👨‍🏫 Preferred Mentor (Optional)")
    duration = st.number_input("⏱ Max Duration Hours", min_value=0, value=0)
    price = st.selectbox("💰 Price", ["Any", "Free", "Paid"])

top_n = st.slider("⭐ Number of Recommendations", 1, 10, 5)

# =========================
# BUTTON
# =========================
if st.button("🚀 Recommend Courses"):
    results = recommend_courses(
        domain=domain,
        subdomain=subdomain,
        mentor=mentor,
        top_n=top_n
    )

    if results.empty:
        st.warning("No matching courses found.")
    else:
        st.success(f"Found {len(results)} best matching courses")

        for _, row in results.iterrows():
            st.markdown(f"""
            <div style="
                border:1px solid #ddd;
                border-radius:12px;
                padding:20px;
                margin-bottom:15px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.08);
            ">
                <h3>{row['course_name']}</h3>
                <p><b>📚 Domain:</b> {row['domain']}</p>
                <p><b>👨‍🏫 Mentor:</b> {row['mentor'] if row['mentor'] else "Not Available"}</p>
                <p><b>🎯 Level:</b> {row['level']}</p>
                <p><b>📈 Match Score:</b> {row['score']:.2f}</p>
                <a href="{row['course_url']}" target="_blank">🔗 Open Course</a>
            </div>
            """, unsafe_allow_html=True)
