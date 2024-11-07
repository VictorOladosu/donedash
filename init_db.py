from main import app, db
from models import User, Service, Review
from werkzeug.security import generate_password_hash
from datetime import time, datetime, timedelta
import random

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
                role="provider",
                latitude=37.7749,
                longitude=-122.4194,
                address="San Francisco, CA"
            )
            provider.set_password("password123")
            db.session.add(provider)
            
            # Create sample customer
            customer = User(
                username="alice_customer",
                email="customer@example.com",
                role="customer",
                latitude=37.7833,
                longitude=-122.4167,
                address="San Francisco, CA"
            )
            customer.set_password("password123")
            db.session.add(customer)
            db.session.commit()

            # Create sample services with availability
            services = [
                Service(
                    provider_id=provider.id,
                    title="House Cleaning",
                    description="Professional house cleaning service. Deep cleaning of all rooms, bathrooms, and kitchen.",
                    rate=50.00,
                    category="cleaning",
                    availability_start=time(9, 0),  # 9 AM
                    availability_end=time(17, 0),   # 5 PM
                    availability_days="1,2,3,4,5",   # Monday to Friday
                    service_area=20.0,
                    location_flexible=True,
                    experience_years=5,
                    qualifications="Certified Professional Cleaner",
                    languages="English, Spanish",
                    tags="cleaning,housekeeping,deep cleaning,sanitization",
                    featured=True
                ),
                Service(
                    provider_id=provider.id,
                    title="Lawn Mowing",
                    description="Complete lawn care service including mowing, edging, and cleanup.",
                    rate=40.00,
                    category="gardening",
                    availability_start=time(8, 0),
                    availability_end=time(18, 0),
                    availability_days="1,2,3,4,5,6",
                    service_area=15.0,
                    location_flexible=True,
                    experience_years=3,
                    languages="English",
                    tags="gardening,lawn care,yard work,landscaping"
                ),
                Service(
                    provider_id=provider.id,
                    title="Computer Repair",
                    description="Expert computer repair and maintenance services.",
                    rate=75.00,
                    category="technology",
                    availability_start=time(10, 0),
                    availability_end=time(20, 0),
                    availability_days="1,2,3,4,5,6,7",
                    service_area=25.0,
                    location_flexible=True,
                    experience_years=8,
                    qualifications="CompTIA A+ Certified",
                    languages="English",
                    tags="computer repair,tech support,IT services,virus removal",
                    featured=True
                )
            ]
            
            # Add services and reviews
            for service in services:
                db.session.add(service)
                # Add sample reviews
                for _ in range(random.randint(3, 7)):
                    review = Review(
                        service_id=service.id,
                        customer_id=customer.id,
                        rating=random.randint(3, 5),
                        comment="Great service, very professional!",
                        created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                    )
                    db.session.add(review)
            
            db.session.commit()
            print("Sample data initialized successfully!")
        else:
            print("Database already contains data!")

if __name__ == "__main__":
    init_db()
