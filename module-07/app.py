from flask import Flask, render_template

app = Flask(__name__)

SAMPLE_DATA = {
    "kpis": [
        {"label": "KPI 1", "sublabel": "Total Notes", "value": "128"},
        {"label": "KPI 2", "sublabel": "Active Tasks", "value": "42"},
        {"label": "KPI 3", "sublabel": "Days Active", "value": "7d"},
    ],
    "recent_items": [
        {"name": "Q1 Planning Notes", "value": "Apr 2"},
        {"name": "Sprint Retrospective", "value": "Apr 5"},
        {"name": "Design Review", "value": "Apr 8"},
        {"name": "Budget Forecast", "value": "Apr 10"},
        {"name": "Release Checklist", "value": "Apr 12"},
    ],
    "nav_items": ["Overview", "Notes", "Tasks", "Reports", "Settings"],
    "version": "v1.0.0",
}


@app.route("/")
def index():
    return render_template("index.html", **SAMPLE_DATA)


if __name__ == "__main__":
    app.run(debug=True)
