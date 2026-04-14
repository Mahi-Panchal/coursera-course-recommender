import streamlit as st
from recommender import CourseEngine

@st.cache_resource
def init_engine():
    return CourseEngine('courses_data.csv')

engine = init_engine()

st.set_page_config(page_title="Course AI", layout="wide")
st.title("🎓 Smart Course Finder")

with st.sidebar:
    st.header("Search Parameters")
    sel_domain = st.selectbox("Industry/Domain*", engine.df['domain'].unique())
    sel_sub = st.text_input("Subdomain (Optional)")
    sel_mentor = st.text_input("University/Instructor (Optional)")
    search_btn = st.button("Find Courses", type="primary")

if search_btn:
    results = engine.get_recs(sel_domain, sel_sub, sel_mentor)
    if not results.empty:
        # Create a 3-column grid for the UI
        cols = st.columns(3)
        for idx, (_, row) in enumerate(results.iterrows()):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.subheader(row['title'])
                    st.write(f"🏫 **{row['mentor']}**")
                    st.write(f"📂 {row['subdomain']}")
                    st.link_button("View on Coursera", row['url'])
    else:
        st.error("No matches found for that specific criteria.")
