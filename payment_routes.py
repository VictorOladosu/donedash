import stripe
import os
from flask import jsonify, request
from main import app, db
from models import Booking
from flask_login import login_required, current_user

stripe.api_key = os.environ['STRIPE_SECRET_KEY']

@app.route('/create-payment-intent/<int:booking_id>', methods=['POST'])
@login_required
def create_payment_intent(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Ensure the current user is the customer
        if booking.customer_id != current_user.id:
            return jsonify({"error": "Unauthorized"}), 403
            
        # Calculate amount in cents
        amount = int(booking.total_amount * 100)
        
        # Create a PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            metadata={
                'booking_id': booking_id,
                'customer_id': current_user.id
            }
        )
        
        # Update booking with payment intent ID
        booking.payment_intent_id = intent.id
        db.session.commit()
        
        return jsonify({
            'clientSecret': intent.client_secret
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/payment-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ['STRIPE_SECRET_KEY']
        )
    except ValueError as e:
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({"error": "Invalid signature"}), 400

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        booking_id = payment_intent['metadata']['booking_id']
        
        # Update booking payment status
        booking = Booking.query.get(booking_id)
        if booking:
            booking.payment_status = 'paid'
            booking.status = 'confirmed'
            db.session.commit()

    return jsonify({"status": "success"})
