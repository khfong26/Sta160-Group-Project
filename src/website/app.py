from flask import Flask, render_template, jsonify
import os
import sys
#from api.data_loader import load_salary_data, load_skills_data

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from api.data_loader import load_salary_data, load_skills_data

app = Flask(__name__)

# front end

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/salary")
def salary_page():
    return render_template("salary.html")

@app.route("/skills")
def skills_page():
    return render_template("skills.html")

@app.route("/trends")
def trends_page():
    return render_template("trends.html")

@app.route("/methodology")
def methodology_page():
    return render_template("methodology.html")

@app.route("/team")
def team_page():
    return render_template("team.html")


# API Routes (JSON Data for Charts)

@app.route("/api/salary")
def salary_api():
    df = load_salary_data()
    return jsonify(df.to_dict(orient="list"))

@app.route("/api/skills")
def skills_api():
    df = load_skills_data()
    return jsonify(df.to_dict(orient="list"))



if __name__ == "__main__":
    app.run(debug=True)