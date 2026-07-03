from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)

# File storage folders
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file uploaded!", 400

        file = request.files["file"]

        if file.filename == "":
            return "No file selected!", 400

        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Create PDF
        pdf_filename = filename.rsplit(".", 1)[0] + ".pdf"
        pdf_path = os.path.join(OUTPUT_FOLDER, pdf_filename)

        with open(filepath, "r", encoding="utf-8") as f:
            text_content = f.read()

        c = canvas.Canvas(pdf_path)
        c.setFont("Helvetica", 12)
        c.drawString(50, 800, "Converted PDF:")
        y = 780
        for line in text_content.splitlines():
            c.drawString(50, y, line)
            y -= 15
        c.save()

        return redirect(url_for("download_file", filename=pdf_filename))

    return render_template("index.html")

@app.route("/download/<filename>")
def download_file(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
