# DoneDash - Service Marketplace Platform

DoneDash is a TaskRabbit-inspired service marketplace platform that enables users to list, book, and manage services. Built with Flask and Bootstrap, it provides a complete solution for service providers and customers.

## Features

- User Authentication (Provider/Customer roles)
- Service Management
- Booking System
- Secure Payment Processing (Stripe)
- Real-time Messaging
- Review System
- Mobile-responsive Design

## Tech Stack

- Backend: Flask (Python)
- Frontend: Vanilla JavaScript, Bootstrap (Dark Theme)
- Database: PostgreSQL
- Payment Processing: Stripe

## Prerequisites

- Python 3.11 or higher
- PostgreSQL
- Stripe Account

## Required Environment Variables

```
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

3. Initialize the database:
```bash
python init_db.py
```

4. Start the application:
```bash
python app.py
```

## Development

The application will be available at `http://localhost:5000`

### Default Test Accounts

- Provider Account:
  - Email: provider@example.com
  - Password: password123

## API Documentation

### Stripe Webhooks

The application listens for Stripe webhooks at `/webhook`. Configure your Stripe webhook settings to point to:
```
https://your-domain.com/webhook
```

Required webhook events:
- payment_intent.succeeded

## Security Considerations

- All sensitive information is stored in environment variables
- CSRF protection enabled for all forms
- Secure session management
- Payment processing through Stripe's secure infrastructure

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
