from flask import Flask, request, render_template
from deep_translator import GoogleTranslator

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def translate():
    translated_text = ""
    if request.method == "POST":
        text = request.form["text"]
        direction = request.form["direction"]
        if direction == "en_to_fr":
            translated_text = GoogleTranslator(source='en', target='fr').translate(text)
        else:
            translated_text = GoogleTranslator(source='fr', target='en').translate(text)
    return render_template("index.html", translated_text=translated_text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
