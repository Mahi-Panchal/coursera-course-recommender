import streamlit as st
from recommender import CourseEngine

# Load the engine once
@st.cache_resource
def load_engine():
    return CourseEngine('courses_data.csv')

engine = load_engine()

# --- UX STYLING ---
st.set_page_config(page_title="Coursera Pro", page_icon="🎓", layout="wide")
st.markdown("""
    <style>
    .course-card {
        background-color: white; padding: 20px; border-radius: 10px;
        border: 1px solid #e6e9ef; margin-bottom: 20px; height: 250px;
    }
    .badge {
        padding: 4px 8px; border-radius: 4px; font-size: 12px;
        font-weight: bold; color: white; background-color: #0056D2;
    }
    </style>
""", unsafe_allow_html=True)

# --- UI LAYOUT ---
st.title("🎓 Premium Course Recommender")
st.subheader("Personalized learning paths based on your budget and schedule.")

# Input Section (Sidebar for better UX)
with st.sidebar:
    st.header("🎯 Preferences")
    d_input = st.selectbox("Select Domain*", engine.df['domain'].unique())
    dur_input = st.selectbox("Max Duration*", ["1-4 Weeks", "1-3 Months", "6+ Months"])
    p_input = st.radio("Price Type*", ["Free", "Paid"])
    
    st.divider()
    st.header("🔍 Optional Details")
    s_input = st.text_input("Subdomain (e.g. AI, Finance)")
    m_input = st.text_input("Specific Mentor/University")
    
    search_btn = st.button("Generate Recommendations", type="primary", use_container_width=True)

# Output Section
if search_btn:
    recs = engine.recommend(d_input, dur_input, p_input, s_input, m_input)
    
    if not recs.empty:
        st.success(f"Found {len(recs)} courses matching your criteria!")
        
        # Displaying 3 courses per row
        cols = st.columns(3)
        for i, (idx, row) in enumerate(recs.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                    <div class="course-card">
                        <span class="badge">{row['price']}</span>
                        <h3>{row['title']}</h3>
                        <p><b>Institution:</b> {row['mentor']}</p>
                        <p><b>Estimated Time:</b> {row['duration']}</p>
                        <a href="{row['url']}" target="_blank">
                            <button style="width:100%; background-color:#0056D2; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer;">
                                View Course
                            </button>
                        </a>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("No courses match those exact filters. Try changing the Duration or Price setting.")
