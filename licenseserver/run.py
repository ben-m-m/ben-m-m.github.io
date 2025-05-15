import os
from app import app  # Your Flask app instance
from config import config

def main():
    env = os.getenv("FLASK_ENV", "development")
    print(f"Starting app in {env} mode...")
    app.config.from_object(config[env])
    app.run(debug=(env=="development"))

if __name__ == "__main__":
    main()
