from dotenv import load_dotenv

load_dotenv()  # Read settings from the local .env file, when present.

from app import create_app, db

app = create_app()


@app.get("/api")
def health_check():
    return {
        "message": "Welcome to the Store API",
        "status": 200,
        "data": None,
    }, 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Convenient for this learning project; use migrations in production.

    app.run(debug=True)
