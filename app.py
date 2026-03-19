import re
from flask import Flask, render_template, request

# Optional PDF support
try:
    from pypdf import PdfReader  # ← modern successor (pypdf), more reliable than PyPDF2
except ImportError:
    try:
        import PyPDF2
    except ImportError:
        PyPDF2 = None
        PdfReader = None

app = Flask(__name__)

# -------------------------------
# 🔥 Skill List (unchanged)
# -------------------------------
SKILLS = [
    "Full Stack Development", "JavaScript", "Python", "Java", "C#", "C++", "TypeScript",
    "React.js", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring Boot",
    "SQL", "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS", "Azure",
    "Google Cloud Platform (GCP)", "Git/GitHub", "CI/CD Pipelines", "REST APIs",
    "GraphQL", "Microservices", "Unit Testing", "System Architecture", "Agile/Scrum",
    "Machine Learning", "Deep Learning", "Natural Language Processing (NLP)",
    "Computer Vision", "Reinforcement Learning", "PyTorch", "TensorFlow", "Keras",
    "Scikit-learn", "Pandas", "NumPy", "Data Visualization", "Tableau", "PowerBI",
    "R Programming", "Predictive Analytics", "Large Language Models (LLMs)",
    "Prompt Engineering", "Data Engineering", "Feature Engineering", "A/B Testing",
    "Statistical Modeling", "Hadoop", "Spark",
    "PCB Design", "FPGA", "Embedded Systems", "VLSI", "Circuit Analysis", "Arduino",
    "Raspberry Pi", "VHDL/Verilog", "Microcontrollers", "Robotics", "MATLAB",
    "AutoCAD", "SolidWorks", "Signal Processing", "Firmware Development",
    "PLC Programming", "Hardware Troubleshooting", "Mechatronics",
    "Ethical Hacking", "Penetration Testing", "Network Security", "Firewall Administration",
    "Identity & Access Management (IAM)", "SIEM", "Incident Response",
    "Vulnerability Assessment", "Cloud Security", "Cryptography", "TCP/IP Networking",
    "Wireshark", "Intrusion Detection Systems (IDS)", "CompTIA Security+",
    "Project Management", "Strategic Planning", "SEO/SEM", "Content Strategy",
    "Email Marketing", "Social Media Management", "Google Analytics", "Salesforce",
    "Customer Relationship Management (CRM)", "Financial Modeling", "Budgeting",
    "Supply Chain Management", "Logistics", "Human Resources (HRIS)", "Public Speaking",
    "Market Research", "Change Management", "Negotiation", "Operations Analysis",
    "Six Sigma", "Lean Manufacturing",
    "UI/UX Design", "Figma", "Adobe Photoshop", "Adobe Illustrator", "Adobe After Effects",
    "Wireframing", "Prototyping", "User Research", "Interaction Design", "Graphic Design",
    "Typography", "Motion Graphics", "Video Editing", "Premiere Pro", "Final Cut Pro",
    "3D Modeling", "Blender", "Maya", "Unity 3D",
    "Team Leadership", "Emotional Intelligence", "Conflict Resolution", "Critical Thinking",
    "Adaptability", "Time Management", "Intercultural Communication", "Mentoring",
    "Decision Making", "Problem Solving"
]

# -------------------------------
# 🔍 Skill Extraction (case-insensitive, better matching)
# -------------------------------
def extract_skills(text):
    if not text:
        return set()
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\+\.#]+", " ", text)  # keep +, ., # (C#, .NET, etc.)
    text = re.sub(r"\s+", " ", text).strip()

    found = set()
    for skill in SKILLS:
        # More flexible: allow minor variations (react js → React.js)
        pattern = r"\b" + re.escape(skill.lower().replace(".", r"\.").replace("+", r"\+")) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            found.add(skill)
    return found


# -------------------------------
# 📄 Text extraction from file (PDF or TXT) – in-memory only
# -------------------------------
def extract_text_from_file(file_storage):
    if not file_storage or not file_storage.filename:
        return ""

    filename = file_storage.filename.lower().strip()

    try:
        content = file_storage.read()           # read bytes once
        file_storage.seek(0)                    # reset for safety (though not needed here)

        if filename.endswith(".txt"):
            try:
                return content.decode("utf-8")
            except UnicodeDecodeError:
                return content.decode("latin-1", errors="replace")

        elif filename.endswith(".pdf"):
            if PdfReader:
                reader = PdfReader(file_storage)
                return "\n".join(page.extract_text() or "" for page in reader.pages)
            elif PyPDF2:
                reader = PyPDF2.PdfReader(file_storage)
                return "\n".join(page.extract_text() or "" for page in reader.pages)

    except Exception as e:
        print(f"File extraction error ({filename}): {e}")
        return ""

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

        # Extract skills
        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)

        matched = sorted(list(resume_skills & jd_skills))
        missing = sorted(list(jd_skills - resume_skills))
        extra = sorted(list(resume_skills - jd_skills))

        if jd_skills:
            score = int(len(matched) / len(jd_skills) * 100)
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
        matched=matched,
        missing=missing,
        extra=extra,
        score=score,
        chances=chances
    )

if __name__ == "__main__":
    app.run(debug=True)
