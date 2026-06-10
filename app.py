from flask import Flask, render_template, request
import os
import cv2

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def analyze_wound(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return "Unable to Analyze", 0

    height, width, _ = image.shape

    red_pixels = 0

    for row in image:
        for pixel in row:

            b, g, r = pixel

            if r > 120 and r > g + 20 and r > b + 20:
                red_pixels += 1

    wound_percentage = round(
        (red_pixels / (height * width)) * 100,
        2
    )

    if wound_percentage > 40:
        severity = "Severe"

    elif wound_percentage > 15:
        severity = "Moderate"

    else:
        severity = "Mild"

    return severity, wound_percentage


def detect_wound_type(severity):

    if severity == "Mild":
        return "Normal Wound"

    elif severity == "Moderate":
        return "Infected Wound"

    elif severity == "Severe":
        return "Severe/Open Wound"

    return "Unknown"


def generate_chart(wound_percentage):

    healthy_percentage = round(
        100 - wound_percentage,
        2
    )

    plt.figure(figsize=(5, 5))

    plt.pie(
        [wound_percentage, healthy_percentage],
        labels=["Wound Area", "Healthy Area"],
        autopct="%1.1f%%"
    )

    plt.title("Wound Analysis Chart")

    chart_path = "static/chart.png"

    plt.savefig(chart_path)

    plt.close()

    return "chart.png"


@app.route("/", methods=["GET", "POST"])
def home():

    image_path = None
    severity = None
    wound_type = None
    suggestion = ""
    wound_percentage = 0
    chart_image = None

    if request.method == "POST":

        file = request.files.get("image")

        if file and file.filename != "":

            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                file.filename
            )

            file.save(filepath)

            image_path = "uploads/" + file.filename

            severity, wound_percentage = analyze_wound(filepath)

            wound_type = detect_wound_type(severity)

            chart_image = generate_chart(
                wound_percentage
            )

            if severity == "Mild":
                suggestion = (
                    "Clean wound daily and monitor healing."
                )

            elif severity == "Moderate":
                suggestion = (
                    "Apply dressing and monitor regularly."
                )

            elif severity == "Severe":
                suggestion = (
                    "Seek medical attention immediately."
                )

    return render_template(
        "index.html",
        image_path=image_path,
        severity=severity,
        wound_type=wound_type,
        suggestion=suggestion,
        wound_percentage=wound_percentage,
        chart_image=chart_image
    )


if __name__ == "__main__":
    app.run(debug=True)