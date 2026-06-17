# AI Resume Matcher & Job Recommender

This project is an AI-powered recruitment tool designed to bridge the gap between job seekers and their ideal roles. Unlike traditional ATS systems that rely solely on exact keyword matching, this application utilizes Natural Language Processing (NLP) and Semantic Search to understand the context of a resume and compare it against a database of job descriptions.

## 🚀 Key Features

* **Hybrid Ranking System:** Combines Semantic Similarity (70%) and Keyword Matching (30%) to provide a balanced and fair match score.
* **Semantic Intelligence:** Uses the all-MiniLM-L6-v2 SBERT model to understand meaning beyond just keywords.
* **Automatic Skill Extraction:** Identifies technical skills from resumes using a predefined taxonomy and handles aliases (e.g., recognizing "JS" as "JavaScript").
* **Skill Gap Analysis:** Highlights exactly which skills a candidate possesses for a specific job and which ones are missing.
* **Interactive Dashboard:** Built with Streamlit, featuring real-time metrics, match distribution charts, and skill category breakdowns.
* **Multi-format Support:** Seamlessly parses both .pdf and .docx resume files.
* **Resume Optimization Tips:** Provides actionable advice on which skills to add to increase the match score for specific roles.

## 📂 Project Structure

```text
├── data/
│   ├── jobs_cache.json       # Database of 100+ job listings
│   └── skills.json           # Technical skill taxonomy and aliases
├── modules/
│   ├── hybrid_ranker.py      # Logic for combining semantic and keyword scores
│   ├── matcher.py            # SBERT embedding generation and cosine similarity
│   ├── parser.py             # PDF and DOCX text extraction logic
│   ├── processor.py          # Text cleaning (removing emails, URLs, special chars)
│   └── skill_extractor.py    # Regex-based skill extraction and categorization
├── app.py                    # Streamlit frontend and main application entry point
└── requirements.txt          # Project dependencies
```

## ⚙️ Functionalities

### 1. Extraction & Cleaning (parser.py & processor.py)

The system extracts raw text from uploaded files and cleans it by removing "noise" such as email addresses, website links, phone numbers, and non-ASCII characters to ensure the AI focuses only on relevant professional content.

### 2. Semantic Matching (matcher.py)

Using Sentence-Transformers, the system converts the resume and job descriptions into high-dimensional vectors (embeddings). It then calculates the Cosine Similarity between these vectors to find how closely the candidate's experience aligns with the job requirements.

### 3. Skill Intelligence (skill_extractor.py)

Matches text against a curated skills.json file. It categorizes found skills into groups like "Programming Languages," "Databases," or "Cloud Computing," providing a structured overview of the candidate's profile.

### 4. Hybrid Ranking (hybrid_ranker.py)

To prevent "keyword stuffing" from gaming the system, the final score is a weighted average:

* **Semantic Score (70%):** Measures overall contextual fit.
* **Keyword Score (30%):** Measures specific technical requirement fulfillment.

## 🔄 Project Workflow

### User Upload

The user uploads a resume (PDF or DOCX) via the sidebar.

### Processing

* Text is extracted and cleaned.
* Skills are identified and categorized.

### Analysis

The engine compares the cleaned resume against every job in the jobs_cache.json.

### Scoring

The Hybrid Ranker calculates a match percentage for every job.

### Visualization

* The top matched jobs are displayed.
* Plotly charts show the distribution of match scores.
* A "Missing Skills" chart highlights what the user should learn next.

## 💡 Use Cases

### For Job Seekers

Upload your resume to see which types of roles you are currently qualified for and identify the exact "missing skills" you need to acquire to land your dream job.

### For Recruiters

Quickly rank a pool of candidates against a job description based on actual experience and context rather than just "buzzword" counting.

### For Career Coaches

Visualize a student's skill distribution to help them pivot into new tech domains (e.g., from Frontend to DevOps).

## 🛠️ Local Setup and Installation

Follow these steps to get the project running on your local machine:

### Prerequisites

* Python 3.8 or higher installed.
* pip (Python package manager).

### Step 1: Clone the Project

Create a folder and place the project files inside.

### Step 2: Install Dependencies

Open your terminal/command prompt in the project root directory and run:

```bash
pip install -r requirements.txt
```

### Step 3: Prepare the Data

Ensure the data/ folder contains jobs_cache.json and skills.json. The application requires these to function correctly.

### Step 4: Run the Application

Launch the Streamlit dashboard by running:

```bash
streamlit run app.py
```

### Step 5: Access the UI

Once the command runs, a local URL will be provided (usually http://localhost:8501). Open this in your web browser to start matching resumes!

## 📊 Technologies Used

* **Language:** Python
* **Framework:** Streamlit
* **NLP:** Sentence-Transformers (SBERT), Scikit-learn
* **Data Handling:** Pandas, JSON
* **Visuals:** Plotly, Analysis Metrics
* **File Parsing:** pdfplumber, python-docx
