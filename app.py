from flask import (
    Flask,
    render_template,
    request,
    send_from_directory
)

from main import preprocess
from module3_analysis import analyze
from visualizer import visualize

from prompts import (
    QUALITY_ANALYSIS_PROMPT,
    ANALYSIS_PROMPT
)

from llm_factory import create_llm

import os
import json
import shutil
import markdown


app = Flask(__name__)

llm = create_llm()

INPUT_FOLDER = "input"
OUTPUT_FOLDER = "outputs"


def generate(dataset_name):

    dataset_path = os.path.join(INPUT_FOLDER, dataset_name)

    shutil.rmtree(OUTPUT_FOLDER, ignore_errors=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    quality_report = preprocess(dataset_path)

    analysis_report = analyze(dataset_path)

    visualize(dataset_path)

    quality_output = llm.invoke(
        QUALITY_ANALYSIS_PROMPT + json.dumps(quality_report)
    ).content

    analysis_output = llm.invoke(
        ANALYSIS_PROMPT + json.dumps(analysis_report)
    ).content

    quality_html = markdown.markdown(
        quality_output,
        extensions=["tables", "fenced_code"]
    )

    analysis_html = markdown.markdown(
        analysis_output,
        extensions=["tables", "fenced_code"]
    )

    image_files = [
        file
        for file in os.listdir(OUTPUT_FOLDER)
        if file.endswith((".png", ".jpg", ".jpeg"))
    ]

    return {
        "quality_analysis": quality_html,
        "trend_analysis": analysis_html,
        "images": image_files
    }


@app.route("/")
def index():

    datasets = sorted(
        [
            file
            for file in os.listdir(INPUT_FOLDER)
            if file.endswith(".csv")
        ]
    )

    return render_template(
        "index.html",
        datasets=datasets
    )


@app.route("/analyze", methods=["POST"])
def analyze_dataset():

    dataset_name = request.form.get("dataset")

    result = generate(dataset_name)

    return render_template(
        "dashboard.html",
        dataset_name=dataset_name,
        quality_analysis=result["quality_analysis"],
        trend_analysis=result["trend_analysis"],
        images=result["images"]
    )


@app.route("/outputs/<path:filename>")
def serve_output_image(filename):

    return send_from_directory(
        OUTPUT_FOLDER,
        filename
    )


if __name__ == "__main__":

    app.run(
        debug=True
    )