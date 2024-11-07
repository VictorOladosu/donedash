from main import app
from extensions import db

def drop_all_tables():
    with app.app_context():
        db.drop_all()
        print("All tables dropped successfully!")

if __name__ == "__main__":
    drop_all_tables()