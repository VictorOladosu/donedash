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
                role="provider"
            )
            provider.set_password("password123")
            db.session.add(provider)
            
            # Create sample customer for reviews
            customer = User(
                username="alice_customer",
                email="customer@example.com",
                role="customer"
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
                    availability_days="1,2,3,4,5"   # Monday to Friday
                ),
                Service(
                    provider_id=provider.id,
                    title="Lawn Mowing",
                    description="Complete lawn care service including mowing, edging, and cleanup.",
                    rate=40.00,
                    category="gardening",
                    availability_start=time(8, 0),
                    availability_end=time(18, 0),
                    availability_days="1,2,3,4,5,6"
                ),
                Service(
                    provider_id=provider.id,
                    title="Computer Repair",
                    description="Expert computer repair and maintenance services.",
                    rate=75.00,
                    category="technology",
                    availability_start=time(10, 0),
                    availability_end=time(20, 0),
                    availability_days="1,2,3,4,5,6,7"
                ),
                Service(
                    provider_id=provider.id,
                    title="Math Tutoring",
                    description="Private math tutoring for all levels.",
                    rate=45.00,
                    category="education",
                    availability_start=time(15, 0),
                    availability_end=time(21, 0),
                    availability_days="2,4,6"
                ),
                Service(
                    provider_id=provider.id,
                    title="Dog Walking",
                    description="Professional dog walking and pet care services.",
                    rate=30.00,
                    category="pet_care",
                    availability_start=time(8, 0),
                    availability_end=time(18, 0),
                    availability_days="1,2,3,4,5,6,7"
                ),
                Service(
                    provider_id=provider.id,
                    title="Hair Styling",
                    description="Professional hair styling and cutting services.",
                    rate=60.00,
                    category="personal_care",
                    availability_start=time(9, 0),
                    availability_end=time(19, 0),
                    availability_days="2,3,4,5,6"
                )
            ]
            
            for service in services:
                db.session.add(service)
                # Add some sample reviews
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
