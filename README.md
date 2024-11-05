# DoneDash - Service Marketplace Platform

DoneDash is a TaskRabbit-inspired service marketplace platform that enables users to list, book, and manage services. Built with Flask and Bootstrap, it provides a complete solution for service providers and customers.

## Features

- User Authentication (Provider/Customer roles)
- Service Management (Create, Read, Update, Delete)
- Booking System with Secure Payment Processing
- Real-time Messaging between Providers and Customers
- Review and Rating System
- Mobile-responsive Design with Bootstrap Dark Theme
- Secure Payment Integration with Stripe

## Tech Stack

- Backend: Flask (Python 3.11)
- Frontend: Vanilla JavaScript, Bootstrap 5 (Dark Theme)
- Database: PostgreSQL
- Payment Processing: Stripe API
- Security: CSRF Protection, Secure Session Management

## Prerequisites

Before you begin, ensure you have:

- Python 3.11 or higher installed
- PostgreSQL database server running
- Stripe account with API keys
- Git for version control

## Required Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database
PGUSER=your_postgres_user
PGPASSWORD=your_postgres_password
PGDATABASE=your_database_name
PGHOST=your_database_host
PGPORT=your_database_port

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/donedash.git
cd donedash
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
python init_db.py
```

5. Start the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Development Setup

1. Database Setup:
   - Create a new PostgreSQL database
   - Update the database configuration in your `.env` file
   - Run database migrations: `python init_db.py`

2. Stripe Setup:
   - Create a Stripe account at https://stripe.com
   - Get your API keys from the Stripe Dashboard
   - Add the keys to your `.env` file
   - Set up webhooks in Stripe Dashboard pointing to `/webhook`

3. Testing:
   - Use the provided test account or create a new one:
     - Email: provider@example.com
     - Password: password123

## API Endpoints

### Payment Integration

- POST `/create-payment-intent/<booking_id>`: Creates a Stripe payment intent
- POST `/webhook`: Handles Stripe webhook events

### Service Management

- GET `/services`: Lists all available services
- GET `/service/<id>`: Shows service details
- POST `/service/create`: Creates a new service (providers only)

### Booking System

- POST `/booking/create/<service_id>`: Creates a new booking
- GET `/booking-confirmation/<booking_id>`: Shows booking confirmation

## Security Features

1. CSRF Protection:
   - All forms are protected against CSRF attacks
   - Secure token validation

2. Session Security:
   - Secure session management
   - HTTP-only cookies
   - Session timeout configuration

3. Payment Security:
   - Stripe integration for secure payment processing
   - Webhook signature verification
   - Payment intent verification

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
