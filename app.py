import streamlit as st
from recommender.recommendation_engine import recommend_courses


st.set_page_config(page_title="Coursera Course Recommender", layout="wide")

st.title("🎓 Coursera Course Recommender")
st.write("Find the best courses based on your interests")


# =========================
# USER INPUTS
# =========================
domain = st.selectbox(
    "Select Domain",
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

subdomain = st.text_input("Enter Subdomain (Optional)")
mentor = st.text_input("Preferred Mentor (Optional)")

top_n = st.slider("Number of Recommendations", 1, 10, 5)


# =========================
# RECOMMEND BUTTON
# =========================
if st.button("Recommend Courses"):
    results = recommend_courses(
        domain=domain,
        subdomain=subdomain,
        mentor=mentor,
        top_n=top_n
    )

    if results.empty:
        st.warning("No matching courses found.")
    else:
        st.success(f"Top {len(results)} Recommended Courses")

        for _, row in results.iterrows():
            st.markdown("---")
            st.subheader(row["course_name"])
            st.write(f"**Domain:** {row['domain']}")
            st.write(f"**Mentor:** {row['mentor']}")
            st.write(f"**Level:** {row['level']}")
            st.write(f"**Similarity Score:** {row['score']:.2f}")
            st.markdown(f"[Go to Course]({row['course_url']})")