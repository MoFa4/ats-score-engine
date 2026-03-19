import re
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os

# Optional PDF/TXT extraction
# Optional PDF support
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"


# -------------------------------
# 🔥 Master Skill Array (500+)
# 🔥 Skill List
# -------------------------------
SKILLS = [
    # --- IT & SOFTWARE DEVELOPMENT ---
@@ -64,60 +60,72 @@
def extract_skills(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]+", " ", text)

    found = set()
    for skill in SKILLS:
        if skill.lower() in text:
        if skill in text:
            found.add(skill)

    return found

def extract_text_from_file(file_path):
    if file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif file_path.lower().endswith(".pdf") and PyPDF2:
# -------------------------------
# 📄 PDF/TXT Extraction
# -------------------------------
def extract_text_from_file(file):
    if not file:
        return ""

    filename = file.filename.lower()

    if filename.endswith(".txt"):
        return file.read().decode("utf-8")

    elif filename.endswith(".pdf") and PyPDF2:
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    return ""

# -------------------------------
# 🚀 Main Route
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    # Initialize empty results by default

    matched, missing, extra = [], [], []
    score = 0
    chances = "N/A"

    if request.method == "POST":

        resume_text = request.form.get("resume", "")
        jd_text = request.form.get("jobdesc", "")

        # 🔥 Handle file upload (resume only)
        resume_file = request.files.get("resume_file")
        if resume_file and resume_file.filename != "":
            resume_text += " " + extract_text_from_file(resume_file)

        # Extract skills
        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)

        matched = sorted(list(resume_skills & jd_skills))
        missing = sorted(list(jd_skills - resume_skills))
        extra = sorted(list(resume_skills - jd_skills))
        matched = sorted(resume_skills & jd_skills)
        missing = sorted(jd_skills - resume_skills)
        extra = sorted(resume_skills - jd_skills)

        if jd_skills:
            score = int(len(matched) / len(jd_skills) * 100)
            score = int((len(matched) / len(jd_skills)) * 100)

            if score >= 80:
                chances = "High"
            elif score >= 50:
                chances = "Medium"
            else:
                chances = "Low"
    else:
        # GET request → reset everything
        matched, missing, extra = [], [], []
        score = 0
        chances = "N/A"

    return render_template(
        "index.html",
@@ -127,5 +135,7 @@ def home():
        score=score,
        chances=chances
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
    app.run(debug=True)
