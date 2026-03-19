import re
from flask import Flask, render_template, request

# Optional PDF support
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

app = Flask(__name__)

# -------------------------------
# 🔥 Skill List
# -------------------------------
SKILLS = [
    # --- IT & SOFTWARE DEVELOPMENT ---
    "Full Stack Development","JavaScript","Python","Java","C#","C++","TypeScript",
    "React.js","Angular","Vue.js","Node.js","Django","Flask","Spring Boot",
    "SQL","PostgreSQL","MongoDB","Redis","Docker","Kubernetes","AWS","Azure",
    "Google Cloud Platform (GCP)","Git/GitHub","CI/CD Pipelines","REST APIs", 
    "GraphQL","Microservices","Unit Testing","System Architecture","Agile/Scrum",
    # --- AI & DATA ---
    "Machine Learning","Deep Learning","Natural Language Processing (NLP)",
    "Computer Vision","Reinforcement Learning","PyTorch","TensorFlow","Keras",
    "Scikit-learn","Pandas","NumPy","Data Visualization","Tableau","PowerBI",
    "R Programming","Predictive Analytics","Large Language Models (LLMs)",
    "Prompt Engineering","Data Engineering","Feature Engineering","A/B Testing",
    "Statistical Modeling","Hadoop","Spark",
    # --- Hardware & Electronics ---
    "PCB Design","FPGA","Embedded Systems","VLSI","Circuit Analysis","Arduino",
    "Raspberry Pi","VHDL/Verilog","Microcontrollers","Robotics","MATLAB",
    "AutoCAD","SolidWorks","Signal Processing","Firmware Development",
    "PLC Programming","Hardware Troubleshooting","Mechatronics",
    # --- Cybersecurity & Networking ---
    "Ethical Hacking","Penetration Testing","Network Security","Firewall Administration",
    "Identity & Access Management (IAM)","SIEM","Incident Response",
    "Vulnerability Assessment","Cloud Security","Cryptography","TCP/IP Networking",
    "Wireshark","Intrusion Detection Systems (IDS)","CompTIA Security+",
    # --- Business & Ops ---
    "Project Management","Strategic Planning","SEO/SEM","Content Strategy",
    "Email Marketing","Social Media Management","Google Analytics","Salesforce",
    "Customer Relationship Management (CRM)","Financial Modeling","Budgeting",
    "Supply Chain Management","Logistics","Human Resources (HRIS)","Public Speaking",
    "Market Research","Change Management","Negotiation","Operations Analysis",
    "Six Sigma","Lean Manufacturing",
    # --- Design ---
    "UI/UX Design","Figma","Adobe Photoshop","Adobe Illustrator","Adobe After Effects",
    "Wireframing","Prototyping","User Research","Interaction Design","Graphic Design",
    "Typography","Motion Graphics","Video Editing","Premiere Pro","Final Cut Pro",
    "3D Modeling","Blender","Maya","Unity 3D",
    # --- Soft Skills ---
    "Team Leadership","Emotional Intelligence","Conflict Resolution","Critical Thinking",
    "Adaptability","Time Management","Intercultural Communication","Mentoring",
    "Decision Making","Problem Solving"
]

# -------------------------------
# 🔍 Skill Extraction
# -------------------------------
def extract_skills(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]+", " ", text)

    found = set()
    for skill in SKILLS:
        if skill in text:
            found.add(skill)

    return found

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

        matched = sorted(resume_skills & jd_skills)
        missing = sorted(jd_skills - resume_skills)
        extra = sorted(resume_skills - jd_skills)

        if jd_skills:
            score = int((len(matched) / len(jd_skills)) * 100)

            if score >= 80:
                chances = "High"
            elif score >= 50:
                chances = "Medium"
            else:
                chances = "Low"

    return render_template(
        "index.html",
        matched=matched,
        missing=missing,
        extra=extra,
        score=score,
        chances=chances
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
