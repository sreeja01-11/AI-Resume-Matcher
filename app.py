import streamlit as st
import json
import os
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List
from collections import Counter

from modules import parser, processor, skill_extractor, hybrid_ranker

st.set_page_config(
    page_title="AI Resume Matcher",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def load_extractor():
    return skill_extractor.SkillExtractor("data/skills.json")

@st.cache_data
def load_jobs_data():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/jobs_cache.json"):
        return None 
    with open("data/jobs_cache.json", "r") as f:
        return json.load(f)

def sidebar_settings():
    st.sidebar.header("📁 Upload Section")
    uploaded_file = st.sidebar.file_uploader(
        "Upload your Resume", 
        type=["pdf", "docx"],
        help="Supported formats: PDF, DOCX"
    )
    st.sidebar.divider()
    st.sidebar.header("⚙️ Matching Settings")
    top_k = st.sidebar.slider("Top Jobs to Display", 5, 20, 10)
    st.sidebar.divider()
    return uploaded_file, top_k

def render_metrics(skills_data, ranked_jobs, jobs_list):
    top_match = (round(ranked_jobs[0]["final_score"] * 100, 1)if ranked_jobs else 0)
    avg_match = (
        round(sum(j["final_score"] for j in ranked_jobs)/ len(ranked_jobs)* 100,1)
        if ranked_jobs else 0
    )
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎯 Top Match", f"{top_match}%")
    col2.metric("🧠 Skills Extracted", skills_data["count"])
    col3.metric("💼 Jobs Analyzed", len(jobs_list))
    col4.metric("📊 Average Match", f"{avg_match}%")
    if top_match >= 85:
        st.success("Excellent Resume Match")
    elif top_match >= 70:
        st.info("Good Resume Match")
    else:
        st.warning("Resume Needs Improvement")

def render_skills_dashboard(skills_data, extractor):
    st.subheader("🎯 Resume Skills Summary")
    if skills_data["skills"]:
        skills = skills_data["skills"]
        st.write(", ".join(skill.title() for skill in skills))
        if len(skills) > 20:
            st.caption(f"+ {len(skills)-20} more skills")
    else:
        st.warning("No skills recognized.")

def render_missing_skills_chart(ranked_jobs):
    st.subheader("📈 Most In-Demand Missing Skills")
    counter = Counter()
    for job in ranked_jobs:
        counter.update(job["missing_skills"])
    if not counter:
        st.success("No major skill gaps found.")
        return
    df = pd.DataFrame(counter.most_common(10),columns=["Skill", "Frequency"])
    fig = px.bar(
        df,
        x="Frequency",
        y="Skill",
        orientation="h"
    )
    st.plotly_chart(fig,use_container_width=True)

def render_visualizations(ranked_jobs: List[Dict], skills_data: Dict, extractor):
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Match Score Distribution")
        df_plot = pd.DataFrame(ranked_jobs[:10])
        fig = px.bar(
            df_plot, 
            x='final_score', 
            y='title', 
            orientation='h',
            color='final_score',
            labels={'final_score': 'Match Score', 'title': 'Job Title'},
            color_continuous_scale='Viridis'
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("🥧 Skill Category Breakdown")
        grouped = extractor.group_by_category(skills_data)
        if grouped:
            pie_data = [{"Category": k, "Count": len(v)} for k, v in grouped.items()]
            fig_pie = px.pie(pie_data, values='Count', names='Category', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Not enough skill data for visualization.")

def display_job_recommendations(ranked_jobs: List[Dict]):
    st.subheader("💼 Top Job Recommendations")
    for i, job in enumerate(ranked_jobs):
        with st.expander(f"#{i+1}: {job['title']} at {job['company']} - Match: {int(job['final_score']*100)}%"):
            c1, c2, c3 = st.columns(3)
            c1.write("**Semantic Match**")
            c1.progress(job['semantic_score'])
            c2.write("**Keyword Match**")
            c2.progress(job['keyword_score'])
            c3.write("**Final Hybrid Score**")
            c3.progress(job['final_score'])
            st.write("**Job Description Snippet:**")
            st.caption(f"{job['description'][:250]}...")
            if job["final_score"] >= 0.85:
                st.success("🔥 Strong Match")
            elif job["final_score"] >= 0.70:
                st.info("✅ Good Match")
            else:
                st.warning("⚠️ Moderate Match")
            sc1, sc2 = st.columns(2)
            with sc1:
                st.write("🟢 **Matched Skills**")
                if job['matched_skills']:
                    st.write(", ".join([f"`{s}`" for s in job['matched_skills']]))
                else:
                    st.write("None")
            with sc2:
                st.write("🟠 **Missing Skills**")
                if job['missing_skills']:
                    st.write(", ".join([f"`{s}`" for s in job['missing_skills']]))
                else:
                    st.success("No missing skills! Perfect match.")
            if job['missing_skills']:
                st.divider()
                st.info(f"💡 **Resume Tip:** To increase your match for this role, consider highlighting your experience with: {', '.join([f'**{s}**' for s in job['missing_skills']])}")

def main():
    st.title("🚀 AI Resume Matcher & Job Recommender")
    st.markdown("Optimize your job search using AI-powered semantic matching and skill gap analysis.")
    uploaded_file, top_k = sidebar_settings()
    try:
        extractor = load_extractor()
    except Exception as e:
        st.error(f"Error loading skills.json: {e}")
        return
    jobs_list = load_jobs_data()
    if jobs_list is None:
        st.error("🛑 **Jobs dataset not found!** Please create `data/jobs_cache.json` and add your job listings.")
        st.stop()
    if uploaded_file is not None:
        temp_filename = ""
        try:
            with st.spinner("🧠 Processing Resume with AI..."):
                file_ext = uploaded_file.name.split('.')[-1].lower()
                temp_filename = f"temp_resume.{file_ext}"
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                raw_text = parser.extract_text(temp_filename)
                if not raw_text or not raw_text.strip():
                    st.error("Could not extract any text from the file. Is it a scanned image?")
                    return
                cleaned_text = processor.clean_text(raw_text)
                resume_skills = extractor.extract_skills(raw_text)
                results = hybrid_ranker.rank_jobs_hybrid(cleaned_text, resume_skills['skills'], jobs_list)
                top_results = results[:top_k]
            render_metrics(resume_skills,top_results,jobs_list)
            tab1, tab2 = st.tabs(["🎯 Results & Analysis", "📊 Data Visualizations"])
            with tab1:
                render_skills_dashboard(resume_skills,extractor)
                st.divider()
                render_missing_skills_chart(top_results)
                st.divider()
                display_job_recommendations(top_results)
            with tab2:
                render_visualizations(top_results, resume_skills, extractor)
        except Exception as e:
            st.error(f"❌ **An error occurred:** {e}")
            st.info("Check if your parser, processor, and ranker modules are working correctly.")
        finally:
            if temp_filename and os.path.exists(temp_filename):
                os.remove(temp_filename)
    else:
        st.info("👈 Please upload a resume in the sidebar to begin analysis.")
    st.divider()

if __name__ == "__main__":
    main()