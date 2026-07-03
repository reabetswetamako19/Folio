from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas
import os

app = Flask(__name__, template_folder="templates", static_folder="static")

# File storage folders
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return render_template("index.html", error="No file uploaded.", success=False)

        file = request.files["file"]

        if file.filename == "":
            return render_template("index.html", error="Please choose a file first.", success=False)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        pdf_filename = filename.rsplit(".", 1)[0] + ".pdf"
        pdf_path = os.path.join(app.config["OUTPUT_FOLDER"], pdf_filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text_content = f.read()
        except UnicodeDecodeError:
            return render_template("index.html", error="Please upload a plain text file.", success=False)

        c = canvas.Canvas(pdf_path)
        c.setFont("Helvetica", 12)
        c.drawString(50, 800, "Converted PDF:")
        y = 780
        for line in text_content.splitlines():
            if y < 50:
                break
            c.drawString(50, y, line)
            y -= 15
        c.save()

        return render_template(
            "index.html",
            success=True,
            original_name=filename,
            download_url=url_for("download_file", filename=pdf_filename),
        )

    return render_template("index.html", success=False)

@app.route("/download/<filename>")
def download_file(filename):
    return send_file(os.path.join(app.config["OUTPUT_FOLDER"], filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
