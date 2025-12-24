from flask import Flask  # type: ignore
from flask_cors import CORS  # type: ignore
from config.supabaseConfig import supabase, SECRET_KEY
from config.mailConfig import mail
import routes
from dotenv import load_dotenv  # type: ignore
import os


# Load environment variables
load_dotenv()
WEB_URL1 = os.getenv("WEB_URL1")
WEB_URL2 = os.getenv("WEB_URL2")
WEB_URL3 = os.getenv("WEB_URL3")


app = Flask(__name__, static_url_path='/static')
CORS(app, resources={r"/*": {"origins": "[WEB_URL1, WEB_URL2, WEB_URL3]"}})

app.config["SECRET_KEY"] = SECRET_KEY  # Use imported SECRET_KEY

# Initialize Flask-Mail
mail.init_app(app)

# Register all routes from routes.py
app.register_blueprint(routes.routes)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)