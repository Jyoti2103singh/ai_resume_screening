from flask import Flask, render_template, request
import os
import pdfplumber

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("dashboard.html")


# ---------------- UPLOAD ----------------
@app.route("/upload", methods=["POST"])
def upload():

    try:
        file = request.files["resume"]

        if file.filename == "":
            return "No file selected"

        path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(path)

        text = ""

        # -------- PDF --------
        if file.filename.endswith(".pdf"):
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""

        # -------- DOCX --------
        elif file.filename.endswith(".docx"):
            from docx import Document
            doc = Document(path)
            for p in doc.paragraphs:
                text += p.text + "\n"

        else:
            return "Unsupported file format (use PDF or DOCX)"

        # ---------------- ANALYSIS ----------------
        resume_text = text.lower()

        keywords = [
            "python",
            "sql",
            "django",
            "flask",
            "pandas",
            "machine learning",
            "communication"
        ]

        skills = []

        for k in keywords:
            if k in resume_text:
                skills.append(k.title())

        ats_score = min(100, len(skills) * 12 + 30)

        missing_skills = [
            k.title() for k in keywords if k not in resume_text
        ]

        job_roles = []

        if "python" in resume_text:
            job_roles.append("Python Developer")

        if "django" in resume_text:
            job_roles.append("Backend Developer")

        if "flask" in resume_text:
            job_roles.append("Flask Developer")

        if "pandas" in resume_text:
            job_roles.append("Data Analyst")

        ai_feedback = (
            "Excellent profile" if ats_score > 80
            else "Good profile" if ats_score > 50
            else "Needs improvement"
        )

        return render_template(
            "result.html",
            ats_score=ats_score,
            skills=skills,
            missing_skills=missing_skills,
            job_roles=job_roles,
            ai_feedback=ai_feedback
        )

    except Exception as e:
        return f"ERROR OCCURRED: {str(e)}"


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)