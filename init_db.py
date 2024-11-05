from main import app, db
from models import User, Service
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if we already have sample data
        if User.query.first() is None:
            # Create sample provider
            provider = User(
                username="john_provider",
                email="provider@example.com",
                role="provider"
            )
            provider.set_password("password123")
            db.session.add(provider)
            db.session.commit()

            # Create sample services
            services = [
                Service(
                    provider_id=provider.id,
                    title="House Cleaning",
                    description="Professional house cleaning service. Deep cleaning of all rooms, bathrooms, and kitchen.",
                    rate=50.00,
                    category="cleaning"
                ),
                Service(
                    provider_id=provider.id,
                    title="Lawn Mowing",
                    description="Complete lawn care service including mowing, edging, and cleanup.",
                    rate=40.00,
                    category="gardening"
                ),
                Service(
                    provider_id=provider.id,
                    title="Furniture Assembly",
                    description="Expert assembly of all types of furniture. Quick and professional service.",
                    rate=45.00,
                    category="handyman"
                )
            ]
            
            for service in services:
                db.session.add(service)
            
            db.session.commit()
            print("Sample data initialized successfully!")
        else:
            print("Database already contains data!")

if __name__ == "__main__":
    init_db()
