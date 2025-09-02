from flask import Flask, request, render_template
from deep_translator import GoogleTranslator
import pymysql
import redis
from datetime import datetime

# --- MySQL config ---
MYSQL_HOST = "192.168.56.109"
MYSQL_DB = "translator_db"
MYSQL_USER = "translator_user"
MYSQL_PASSWORD = "test1234"

# --- Redis config ---
REDIS_HOST = "192.168.56.109"
REDIS_PORT = 6379
REDIS_PASSWORD = "test1234"

app = Flask(__name__)

# --- MySQL connector ---
def get_db():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

# --- Redis connector ---
def get_redis():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True,
        socket_timeout=3
    )

@app.route("/", methods=["GET", "POST"])
def translate():
    translated_text = ""
    if request.method == "POST":
        text = request.form.get("text", "").strip()
        direction = request.form.get("direction", "en_to_fr")

        if not text:
            return render_template("index.html", translated_text="Error: No text provided")

        # Translate text
        if direction == "en_to_fr":
            translated_text = GoogleTranslator(source='en', target='fr').translate(text)
        else:
            translated_text = GoogleTranslator(source='fr', target='en').translate(text)

        # --- Save to MySQL ---
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO translations (source_lang, target_lang, original_text, translated_text, timestamp)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (direction.split("_")[0], direction.split("_")[2], text, translated_text, datetime.utcnow())
                    )
            print("Inserted into MySQL:", text, "->", translated_text)
        except Exception as e:
            print("MySQL Error:", e)

        # --- Update Redis counters ---
        try:
            r = get_redis()
            words = len(text.split())
            r.incrby("total_translated_words", words)
            if direction == "en_to_fr":
                r.incr("en_to_fr_count")
            else:
                r.incr("fr_to_en_count")
            print("Updated Redis counters:", words, direction)
        except Exception as e:
            print("Redis Error:", e)

    return render_template("index.html", translated_text=translated_text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
