from shopwave import app, db  # Make sure to import your Flask app and db

with app.app_context():
    db.create_all()
