import flask
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

from routes import routes  # blueprint
from config.mailConfig import mail
from config.supabaseConfig import SECRET_KEY

# Load env
load_dotenv()

WEB_URL1 = os.getenv("WEB_URL1")
WEB_URL2 = os.getenv("WEB_URL2")
WEB_URL3 = os.getenv("WEB_URL3")

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

# 🔥 CORS — solid config
CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://localhost:3002",
        "http://127.0.0.1:3002",
        "http://localhost:3001", 
        "http://127.0.0.1:3001",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        WEB_URL1,
        WEB_URL2,
        WEB_URL3
    ]
)

# 🔥 CRITICAL: Handle preflight BEFORE anything else
@app.before_request
def handle_preflight():
    if flask.request.method == "OPTIONS":
        return "", 200

# Init mail
mail.init_app(app)

# Register blueprint
app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
