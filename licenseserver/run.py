import os
from app import app  
from config import config  

def main():
    env = os.getenv("FLASK_ENV", "default")
    print(f"Starting app in {env} mode...")

   
    app.config.from_object(config[env])

    app.run(debug=app.config.get('DEBUG', False))

if __name__ == "__main__":
    main()
