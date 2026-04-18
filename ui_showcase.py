# app.py

import streamlit as st
import pandas as pd
import re
from pathlib import Path

# PDF reading
try:
    import pdfplumber
except:
    pdfplumber = None

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Resume Matcher AI",
    page_icon="📄",
    layout="wide"
)

# -----------------------------
# SETTINGS
# -----------------------------
RESUME_FOLDER = Path("resumes")   # folder containing resumes

# -----------------------------
# STYLING
# -----------------------------
st.markdown("""
<style>
.main {background-color:#020617;}
h1,h2,h3 {color:#22d3ee;}

.stButton button{
    background:#22d3ee;
    color:black;
    font-weight:bold;
    border-radius:8px;
}

textarea{
    background:#0f172a !important;
    color:white !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HELPERS
# -----------------------------
def extract_text_from_pdf(file):
    text = ""
    if pdfplumber:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + " "
    return text


def load_text(file):
    if str(file).lower().endswith(".pdf"):
        return extract_text_from_pdf(file)
    return file.read_text(errors="ignore")


def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else "Not Found"


def extract_phone(text):
    match = re.search(r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', text)
    return match.group(0) if match else "Not Found"


def clean_words(text):
    return re.findall(r'\w+', text.lower())


def calculate_match(resume_text, job_desc):
    job_words = clean_words(job_desc)
    resume_words = clean_words(resume_text)

    if not job_words:
        return 0

    matches = sum(1 for word in job_words if word in resume_words)
    score = round((matches / len(job_words)) * 100)

    return min(score, 100)


def get_match_info(resume_text, job_desc):
    job_words = set(clean_words(job_desc))
    resume_words = set(clean_words(resume_text))

    strong = sorted(job_words.intersection(resume_words))
    weak = sorted(job_words - resume_words)

    strong_txt = ", ".join(strong[:10]) if strong else "None Found"
    weak_txt = ", ".join(weak[:10]) if weak else "No Missing Keywords"

    return f"Strong: {strong_txt} | Weak: {weak_txt}"


# -----------------------------
# HEADER
# -----------------------------
st.title("📄 Resume Matcher AI")
st.write("Compare resumes stored in your resume folder.")

# -----------------------------
# JOB DESCRIPTION INPUT
# -----------------------------
st.subheader("Job Description")

job_desc = st.text_area(
    "Paste Job Description",
    height=250,
    placeholder="Enter required skills, qualifications, experience..."
)

# NEW: Upload Job Description File
jd_file = st.file_uploader(
    "Or Upload Job Description File (TXT / PDF)",
    type=["txt", "pdf"]
)

# If uploaded, use file text
if jd_file:
    if jd_file.name.lower().endswith(".pdf"):
        job_desc = extract_text_from_pdf(jd_file)
    else:
        job_desc = str(jd_file.read(), "utf-8")

    st.success("Job description file uploaded successfully.")

# -----------------------------
# HOW MANY TO DISPLAY
# -----------------------------
num_display = st.number_input(
    "How many resumes should be displayed?",
    min_value=1,
    max_value=500,
    value=10
)

# -----------------------------
# COMPARE BUTTON
# -----------------------------
if st.button("Compare Resumes"):

    if not job_desc.strip():
        st.warning("Please paste or upload a job description.")
        st.stop()

    if not RESUME_FOLDER.exists():
        st.error("Resume folder not found.")
        st.stop()

    files = list(RESUME_FOLDER.glob("*.pdf")) + list(RESUME_FOLDER.glob("*.txt"))

    if not files:
        st.warning("No resumes found in the folder.")
        st.stop()

    results = []
    progress = st.progress(0)

    for i, file in enumerate(files):

        text = load_text(file)

        email = extract_email(text)
        phone = extract_phone(text)
        score = calculate_match(text, job_desc)
        info = get_match_info(text, job_desc)

        results.append({
            "Email": email,
            "Phone Number": phone,
            "File Name": file.name,
            "Match Score": score,
            "Get Match Info": info
        })

        progress.progress((i + 1) / len(files))

    # SORT BEST MATCHES
    df = pd.DataFrame(results)
    df = df.sort_values(by="Match Score", ascending=False).head(num_display)

    st.success("Comparison Complete ✅")
    st.subheader("Top Resume Matches")

    st.dataframe(
        df,
        use_container_width=True,
        height=500
    )
